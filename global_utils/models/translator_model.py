from __future__ import annotations

import re
from pathlib import Path
from typing import List, Optional, Union

from openai import (
    APIConnectionError,
    APITimeoutError,
)

from models.llm_client import build_openai_client, is_deepseek_endpoint


class LemmaExtractor:
    def __init__(self, code: str, name: str = 'test'):
        self.code = code
        self.header = self.get_header(self.code)
        self.possible_tactics = ['nlinarith', 'norm_cast', 'norm_num', 'ring_nf', 'ring']
        self.name = name

    def get_lemma(self, state, negate_statement: bool = False):
        # Handle only first sorry, since translator does not return any other
        given_block, goal_block = self.get_statement(state['sorries'][0]['goal'], negate_statement)

        # Purely for better formatting
        if given_block == ':':
            s = self.header + f'lemma {self.name}'
            s += given_block + '\n' + goal_block
        else:
            s = self.header + f'lemma {self.name}\n'
            s += given_block + goal_block

        return s

    def get_statement(self, state, negate_statement: bool = False):
        # Split off the 'goal' part using rsplit with maxsplit=1 to ensure we
        # only split on the last '⊢'.
        if '⊢' in state:
            given, goal = state.rsplit('⊢', 1)
        else:
            # No '⊢', treat the entire string as 'given'
            given = state
            goal = ''

        lines = given.splitlines()

        # Merge multi-line statements: if a line starts with whitespace, treat
        # it as a continuation of the previous line.
        merged_lines: List[str] = []
        for line in lines:
            if line.strip() and (line[0].isspace() or line.startswith(' ')):
                merged_lines[-1] += "\n" + line
            else:
                merged_lines.append(line)

        # Wrap each non-empty merged line in parentheses.
        wrapped: List[str] = []
        for ml in merged_lines:
            ml = ml.strip()
            if ml:
                wrapped.append(f"  ({ml})")

        # Join everything with newlines and append the 'goal' part. Lean
        # typically expects " :\n" before the goal chunk.
        given_block = '\n'.join(wrapped) + ' :\n' if wrapped else ':'

        if goal.strip():
            if negate_statement:
                goal_block = '  ¬(' + goal.strip() + ') := by\n  sorry'
            else:
                goal_block = '  ' + goal.strip() + ' := by\n  sorry'
        else:
            goal_block = ''

        return given_block, goal_block

    def get_header(self, code: str) -> str:
        header: List[str] = []
        for c in code.splitlines():
            if c.lstrip().startswith('theorem'):
                break
            header.append(c)
        return '\n'.join(header) + '\n\n'


class TranslatorModel:
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
            Should contain a ``<question>`` placeholder.
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
    def render_prompt(self, question: str) -> str:
        """Fill the template with provided values; fall back to a minimal default."""
        tpl = self.template_text or (
            "Question:\n<question>\n"
            "Translate this informal mathematics statement into an equivalent "
            "Lean4 statement. Lean4 code should be wrapped as follows:\n"
            "```lean4\n[your code goes here]\n```"
        )
        return tpl.replace("<question>", question)

    def extract_code(self, text_input: str) -> str:
        """Extract the last Lean 4 code block from the model's output."""
        try:
            matches = re.findall(r'```lean4\n(.*?)\n```', text_input, re.DOTALL)
            return matches[-1].strip() if matches else text_input
        except Exception:
            return "Error during code extraction."

    def autoformalize(self, question: str, n: int) -> List[Optional[str]]:
        prompt = self.render_prompt(question)

        try:
            translations = self.run_llm(prompt, n)
        except APITimeoutError:
            self.error_feedback = (
                'Autoformalizer timed out, the step is too complex. '
                'Try to break it down and prove smaller steps.'
            )
            return [None] * n
        except APIConnectionError:
            self.error_feedback = 'Network error, try again.'
            return [None] * n
        except Exception as e:
            self.error_feedback = f'{e}, try again.'
            return [None] * n

        for i, t in enumerate(translations):
            translations[i] = self.extract_code(t)

        return translations

    def split_header_and_body(self, statement: str):
        header: List[str] = []
        body: List[str] = []

        for s in statement.splitlines():
            if any(s.lstrip().startswith(t) for t in ['open', 'import', 'set_option']):
                header.append(s)
            else:
                if s.strip():
                    body.append(s)
        header_str = '\n'.join(header) + '\n\n'
        body_str = '\n'.join(body)

        return header_str, body_str

    def negate_statement(self, statement: str, repl_output, scheduler=None) -> str:
        lemma_extractor = LemmaExtractor(statement)
        opp = lemma_extractor.get_lemma(repl_output, negate_statement=True)
        opp = opp.replace('sorry', 'push_neg ; sorry')
        return opp

    def construct_from_repl(self, statement: str, repl_output) -> str:
        # ``statement`` is needed only for header extraction.
        lemma_extractor = LemmaExtractor(statement)
        lemma = lemma_extractor.get_lemma(repl_output, negate_statement=False)
        return lemma
