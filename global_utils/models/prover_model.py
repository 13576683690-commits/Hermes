from __future__ import annotations

import re
from pathlib import Path
from typing import List, Optional, Union

from openai import (
    APIConnectionError,
    APITimeoutError,
)

from models.llm_client import build_openai_client, is_deepseek_endpoint


class ProverModel:
    def __init__(
        self,
        model_path: Optional[str],
        sampling_params,
        template: Optional[Union[str, Path]] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        port: Optional[int] = None,
        api_mode: Optional[bool] = None,
    ) -> None:
        """
        Parameters
        ----------
        model_path : str
            Either a hosted-model identifier (e.g. ``deepseek-chat``) or a
            local model identifier exposed by a vLLM server.
        sampling_params : Mapping
            EasyDict-like object with sampling parameters
            (``temperature``, ``max_tokens``, ``top_p``, ``timeout``).
        template : str | Path, optional
            Filesystem path to a prompt template, or a raw template string.
            Should contain ``<header>`` and ``<body>`` placeholders.
        api_key : str, optional
            API key used by the OpenAI client.
        base_url : str, optional
            Either a full URL (``https://api.deepseek.com``) for hosted APIs,
            or a host/IP (``0.0.0.0``) for a vLLM server.
        port : int, optional
            Port for the vLLM server. Ignored when ``base_url`` is already a
            full URL.
        api_mode : bool, optional
            When True, always treat ``base_url`` as a hosted API URL (e.g.
            ``https://api.deepseek.com``). Set this in DeepSeek/OpenAI configs.
        """
        self.model_path = model_path
        self.sampling_params = sampling_params
        self.api_key = api_key
        self.base_url = base_url
        self.port = port
        self.api_mode = api_mode

        # Load template from file if it's a path; otherwise treat as raw text.
        self.template_text = self._read_template(template)

        self._load_model()

        # Default header if not passed
        self.header = (
            "import Mathlib\n"
            "import Aesop\n\n"
            "set_option maxHeartbeats 0\n\n"
            "open BigOperators Real Nat Topology Rat\n\n"
        )

        self.error_feedback = ''

    @staticmethod
    def _read_template(template: Optional[Union[str, Path]]) -> str:
        if template is None:
            return ""
        if isinstance(template, Path):
            return template.read_text(encoding="utf-8")
        text = str(template)
        # Only treat as a filesystem path when it looks like one (not inline prompt text).
        if len(text) < 260 and "\n" not in text:
            path = Path(text)
            if path.is_file():
                return path.read_text(encoding="utf-8")
        return text

    # ------------------------------------------------------------------
    # Client construction / API call helpers
    # ------------------------------------------------------------------
    def _load_model(self) -> None:
        self.client = build_openai_client(
            api_key=self.api_key,
            base_url=self.base_url,
            port=self.port,
            api_mode=self.api_mode,
        )

    def completions_with_backoff(self, model: str, **kwargs):
        return self.client.chat.completions.create(model=model, **kwargs)

    def _api_supports_multi_n(self) -> bool:
        # vLLM-style local servers (no scheme in base_url) support n > 1; the
        # DeepSeek hosted API does not.
        return not is_deepseek_endpoint(self.base_url)

    def run_llm(self, prompt: str, n: int) -> List[str]:
        """Generate ``n`` completions, working around APIs limited to n=1."""
        messages = [{"role": "user", "content": prompt}]

        outputs: List[str] = []
        remaining = n
        per_call = n if self._api_supports_multi_n() else 1
        while remaining > 0:
            cnt = min(remaining, per_call)
            res = self.completions_with_backoff(
                model=self.model_path,
                messages=messages,
                temperature=self.sampling_params.temperature,
                max_tokens=self.sampling_params.max_tokens,
                n=cnt,
                top_p=self.sampling_params.top_p,
                timeout=self.sampling_params.timeout,
            )
            outputs.extend(r.message.content for r in res.choices)
            remaining -= cnt
        return outputs

    # ------------------------------------------------------------------
    # Core functionality
    # ------------------------------------------------------------------
    def render_prompt(self, question: str, header: str) -> str:
        """Fill the template with provided values; fall back to a minimal default."""
        tpl = self.template_text or (
            "Question:\n<header>\n<body>\n"
            "Prove this theorem in Lean4. Lean4 code should be wrapped as follows:\n"
            "```lean4\n[your code goes here]\n```"
        )
        return tpl.replace("<header>", header).replace("<body>", question)

    def extract_code(self, text_input: str) -> str:
        """Extract the last Lean 4 code block from the model's output, removing headers."""
        try:
            matches = re.findall(r'```lean4\n(.*?)\n```', text_input, re.DOTALL)

            code = matches[-1].strip() if matches else "No Lean 4 code block found."

            code_without_header: List[str] = []
            for l in code.splitlines():
                if any(l.lstrip().startswith(h) for h in ['import', 'set_option', 'open']):
                    continue
                if not l.strip():
                    continue
                code_without_header.append(l)

            return '\n'.join(code_without_header)
        except Exception:
            return "Error during code extraction."

    def prove(
        self,
        question: str,
        n: int,
        header: Optional[str] = None,
        without_prover_model: bool = False,
    ) -> List[Optional[str]]:
        if header is None:
            header = self.header
        prompt = self.render_prompt(question, header)

        if without_prover_model:
            auto_solver = (
                'try omega ; try decide ; try norm_cast ; try norm_num ; try simp_all ; '
                'try ring_nf at * ; try native_decide ; try linarith ; try nlinarith'
            )
            proofs = [question.replace('sorry', auto_solver)]
            print(proofs)
        else:
            try:
                proofs = self.run_llm(prompt, n)
            except APITimeoutError:
                self.error_feedback = (
                    'Prover timed out, the step is too complex. '
                    'Try to break it down and prove smaller steps.'
                )
                return [None] * n
            except APIConnectionError:
                self.error_feedback = 'Network error, try again.'
                return [None] * n
            except Exception as e:
                self.error_feedback = f'{e}, try again.'
                return [None] * n

        for i, proof in enumerate(proofs):
            proofs[i] = f'{header}\n\n{self.extract_code(proof)}'

        return proofs
