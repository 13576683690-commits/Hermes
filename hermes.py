# import compat  # noqa: F401  # must run before langchain / langgraph imports

import re

from typing import Annotated, Optional, Tuple

from langchain_core.tools import BaseTool
from langgraph.store.memory import InMemoryStore
from langchain_huggingface.embeddings import HuggingFaceEmbeddings

from pydantic import ConfigDict
from easydict import EasyDict

from utils import call_scheduler_with_timeout

from prover.utils import load_config
from prover.lean.verifier import Lean4ServerScheduler

from models.translator_model import TranslatorModel
from models.prover_model import ProverModel
from models.base_llm import BaseLLM
from models.backtranslator import BackTranslator
from models.auxiliary_llm import AuxiliaryLLM


LLM_VERIFIER_PROMPT = '''You are a rigorous mathematical proof checker.

Your task is to analyze the following proof step and decide whether it is mathematically correct (valid and sound), given the context.

Proof step to evaluate:
{}

Instructions:

1. Carefully reason through the mathematics of the step.
   - Check whether the step logically follows from the context and known facts.
   - Check for hidden assumptions, invalid algebraic manipulations, or misuse of theorems.
   - If the step is incomplete, misleading, or only conditionally true, treat it as incorrect.

2. You may think step by step and use intermediate reasoning.

3. At the very end of your answer, you MUST output exactly two things, in this exact order and format:
   - First, the verdict token, which MUST be either:
       - `||true||`  if the proof step is correct, or
       - `||false||` if the proof step is incorrect.
     No other spelling, capitalization, or extra symbols are allowed.
   - Second, a short justification enclosed in double square brackets, like:
       - `[[This step is valid because ...]]`
       - `[[This step is incorrect because ...]]`

4. The justification should:
   - Be concise (1-3 sentences),
   - Explain *why* the step is correct or incorrect,
   - Not introduce new proof steps, only evaluate the given one.

5. Do NOT output anything after the justification.
   The last tokens of your response must be:
   - the verdict token (||true|| or ||false||), followed immediately by
   - the justification in `[[...]]`.

Now analyze the proof step and then give your final verdict and justification in the required format.'''


DESCRIPTION = """
Formally validates a **single** reasoning step using a formal Lean4 verifier. Invoke this function when facing a step that potentially involves a hallucination. Make sure to verify EVERY critical mathematical proof step.

Args:
    proof_step (str): A proof step that includes both the goal to be proven and the relevant context (e.g., variables, assumptions, and previously proven statements). Always explicitly specify the relevant context, such as domains, data types, and any other necessary details. Make sure to state the proof step in English.

Returns:
    str: A status string indicating the verification result:
        - **CORRECT**: Step verified by the theorem prover.
        - **INCORRECT**: Step rejected by the theorem prover (e.g., the prover proved a contradiction or the opposite statement).
        - **VERIFICATION FAILURE**: Step could not be verified by Lean 4 (e.g., the prover was unable to prove the statement or find contradictory arguments)

Notes:
    - Treat **CORRECT** steps as reliable within the given formalization.
    - Treat **INCORRECT** steps as requiring revision; a suggested correction is returned with this label.
    - Use **VERIFICATION FAILURE** to indicate inconclusive or ill-formed steps that Lean 4 was unable to prove or disprove."""


class HermesReasoner(BaseTool):
    name: str = "verify_one_mathematical_step"
    description: str = DESCRIPTION
    response_format: str = "content_and_artifact"
    parse_docstring: bool = True
    model_config = ConfigDict(arbitrary_types_allowed=True)
    user_id: str = '1'
    memory_buffer_n: int = 3
    backwards_check: bool = True

    # Pass configs to let the agent know which prover and translator to use
    MAX_RECURSION_LIMIT: int = 100
    translator_config: str = 'configs/translators/goedel_translator.py'  # default config
    prover_config: str = 'configs/provers/goedel_prover_v2.py'  # default config
    # Optional: config dict/path for backtranslation, memory summarization, etc.
    # If unset, falls back to ``translator_config`` (same API as formalizer).
    auxiliary_llm_config: Optional[object] = None

    # Pass scheduler here, otherwise Lean is not accessible
    scheduler: Optional[Lean4ServerScheduler] = None
    embedding_model: Optional[HuggingFaceEmbeddings] = None

    # Initialized from configs, do not modify or pass anything to these vars
    translator_cfg: Optional[EasyDict] = None
    prover_cfg: Optional[EasyDict] = None
    auxiliary_llm_cfg: Optional[EasyDict] = None
    _auxiliary_llm: Optional[AuxiliaryLLM] = None

    # Additional params, do not modify!
    in_memory_store: Optional[InMemoryStore] = None
    namespace_for_memory: Optional[Tuple] = None
    memory_count: int = 0
    save_all: bool = True
    global_buffer: str = ''

    # ------------------------------------------------------------------
    # Tool entry point
    # ------------------------------------------------------------------
    def _run(self, proof_step: Annotated[str, "mathematical proof step"]) -> str:
        self.translator_cfg = load_config(self.translator_config)
        self.prover_cfg = load_config(self.prover_config)
        self._auxiliary_llm = None  # rebuild if configs changed between tool calls

        if self.scheduler is None:
            print('SCHEDULER FAILURE')
            return "**VERIFICATION FAILURE**\nReason: Lean4 server is not available.", ""

        if self.embedding_model is not None and self.namespace_for_memory is None:
            self.init_memory_buffer()

        lean_feedback, lean_proof = self.verify_one_step(proof_step)

        return lean_feedback, lean_proof

    # ------------------------------------------------------------------
    # MAIN FUNCTIONS
    # ------------------------------------------------------------------
    def verify_one_step(self, proof_step):
        buffer = f'Given that:\n<prerequisites>\n\nProve that:\n{proof_step}'
        if self.embedding_model is not None:
            prereqs = self.search_prereqs(proof_step)
            if prereqs:
                buffer = buffer.replace('<prerequisites>', prereqs)
            else:
                buffer = proof_step
        else:
            if self.save_all and self.global_buffer:
                # TODO: Replace this by a modifiable parameter
                buffer = buffer.replace('<prerequisites>', self.global_buffer)
            else:
                buffer = proof_step

        lean_code, comment, backtrans = self.solve_with_prover(buffer, self.backwards_check)

        if "**CORRECT**" in comment and self.in_memory_store is not None:
            print('Recording correct step...')
            self.record_proof_step(proof_step)

        lean_proof = (
            f'/-\n{buffer}\n-/'
            + f'\n\n--LEAN BLOCK\n\n{lean_code}\n\n--BACKTRANSLATION\n\n'
            + f'/-\n{backtrans}\n-/'
        )

        return comment, lean_proof

    def _resolve_auxiliary_llm_cfg(self) -> EasyDict:
        """Config for backtranslation / memory LLM calls (defaults to translator)."""
        if self.auxiliary_llm_cfg is not None:
            return self.auxiliary_llm_cfg
        if self.auxiliary_llm_config is not None:
            if isinstance(self.auxiliary_llm_config, str):
                return load_config(self.auxiliary_llm_config)
            return EasyDict(self.auxiliary_llm_config)
        if self.translator_cfg is not None:
            return self.translator_cfg
        return load_config(self.translator_config)

    def _make_auxiliary_llm(self) -> AuxiliaryLLM:
        if self._auxiliary_llm is None:
            if self.translator_cfg is None:
                self.translator_cfg = load_config(self.translator_config)
            self.auxiliary_llm_cfg = self._resolve_auxiliary_llm_cfg()
            self._auxiliary_llm = AuxiliaryLLM.from_config(self.auxiliary_llm_cfg)
        return self._auxiliary_llm

    def solve_with_prover(self, problem, backwards_check=False):
        autoformalizer = TranslatorModel(
            model_path=self.translator_cfg.get('model_path', None),
            sampling_params=self.translator_cfg.get('model_args', None),
            template=self.translator_cfg.get('translation_prompt', None),
            api_key=self.translator_cfg.get('api_key', None),
            base_url=self.translator_cfg.get('base_url', None),
            port=self.translator_cfg.get('port', None),
            api_mode=self.translator_cfg.get('api_mode', None),
        )

        prover = ProverModel(
            model_path=self.prover_cfg.get('model_path', None),
            sampling_params=self.prover_cfg.get('model_args', None),
            template=self.prover_cfg.get('theorem_prompt', None),
            api_key=self.prover_cfg.get('api_key', None),
            base_url=self.prover_cfg.get('base_url', None),
            port=self.prover_cfg.get('port', None),
            api_mode=self.prover_cfg.get('api_mode', None),
        )

        proof_state = self.translator_module(
            autoformalizer=autoformalizer,
            problem=problem,
            backwards_check=backwards_check,
        )

        lean_code = ''
        backtrans = proof_state['backtrans']

        if not proof_state['translation_success']:
            return self.feedback_module(problem, 'unverified', lean_code, backtrans)

        lean_code = proof_state['statement_to_prove']

        proof_state = self.prover_module(
            autoformalizer=autoformalizer,
            prover=prover,
            proof_state=proof_state,
        )

        if proof_state['prover_success'] is None:
            print('PROVER FAILED, RESORTING TO LLM VERIFIER')
            return self.feedback_module(problem, 'unverified', lean_code, backtrans)
        elif proof_state['prover_success'] is True:
            lean_code = proof_state['lean_proof']
            return self.feedback_module(problem, 'correct', lean_code, backtrans)
        elif proof_state['prover_success'] is False:
            lean_code = proof_state['lean_proof']
            return self.feedback_module(problem, 'incorrect', lean_code, backtrans)
        else:
            raise ValueError("proof_state['prover_success'] should be one of [True, False, None]")

    def translator_module(self, autoformalizer, problem: str, backwards_check: bool = False):
        output = {
            'statement_to_prove': '',
            'repl_output': None,
            'translation_success': False,
            'backtrans': '',
        }

        backtranslator = BackTranslator(llm=self._make_auxiliary_llm())

        translator_passk = self.translator_cfg.get('pass_k', 4)
        formalized_problems = autoformalizer.autoformalize(problem, translator_passk)

        if all(x is None for x in formalized_problems):
            return output

        formalized_problem_check = call_scheduler_with_timeout(formalized_problems, self.scheduler)

        backtrans = ''
        if backwards_check:
            idxs = self.check_if_pass_repl(formalized_problem_check, key='pass', return_first_correct=False) or []
            idx = None
            for i in idxs:
                res, candidate_backtrans = backtranslator.backtranslate_and_verify(problem, formalized_problems[i])
                if res:
                    idx = i
                    backtrans = candidate_backtrans
                    break
        else:
            idx = self.check_if_pass_repl(formalized_problem_check, key='pass', return_first_correct=True)

        output['backtrans'] = backtrans

        if idx is None:
            return output

        output['statement_to_prove'] = formalized_problems[idx]
        output['repl_output'] = formalized_problem_check[idx]
        output['translation_success'] = True

        return output

    def prover_module(self, autoformalizer, prover, proof_state):
        prover_passk = self.prover_cfg.get('pass_k', 1)

        proofs = prover.prove(proof_state['statement_to_prove'], prover_passk, without_prover_model=False)

        proof_state['prover_success'] = None
        proof_state['lean_proof'] = ''

        if all(x is None for x in proofs):
            print('PROVER UNAVAILABLE')
            return proof_state

        proof_check = call_scheduler_with_timeout(proofs, self.scheduler)

        idx = self.check_if_pass_repl(proof_check, key='complete', return_first_correct=True)

        if idx is None:
            opposite_statement_to_prove = autoformalizer.negate_statement(
                proof_state['statement_to_prove'], proof_state['repl_output']
            )
            opposite_repl = call_scheduler_with_timeout(
                [opposite_statement_to_prove], self.scheduler
            )
            if not opposite_repl:
                return proof_state
            opposite_statement_to_prove_repl = opposite_repl[0]

            opp_idx = self.check_if_pass_repl(
                [opposite_statement_to_prove_repl], key='pass', return_first_correct=True
            )

            if opp_idx is None:
                return proof_state

            opposite_statement_to_prove = autoformalizer.construct_from_repl(
                opposite_statement_to_prove, opposite_statement_to_prove_repl
            )

            proofs = prover.prove(opposite_statement_to_prove, prover_passk, without_prover_model=False)
            if all(x is None for x in proofs):
                print('PROVER MODEL FAILED, SCHEDULER ISSUE')
                return proof_state

            proof_check = call_scheduler_with_timeout(proofs, self.scheduler)

            opp_idx = self.check_if_pass_repl(proof_check, key='complete', return_first_correct=True)

            if opp_idx is None:
                return proof_state

            proof_state['prover_success'] = False
            proof_state['lean_proof'] = proofs[opp_idx]
            return proof_state

        proof_state['prover_success'] = True
        proof_state['lean_proof'] = proofs[idx]

        return proof_state

    def feedback_module(self, step: str, status: str, lean_code: str, backtrans: str):
        if status == 'correct':
            return lean_code, "**CORRECT**\nProceed to generate the next proof step.", backtrans
        elif status == 'incorrect':
            return lean_code, "**INCORRECT**\nPlease revise your reasoning and adjust your current proof trajectory.", backtrans
        elif status == 'unverified':
            ans = f'**VERIFICATION FAILURE**\nSelf-verify the reasoning step: {step}.'
            return lean_code, ans, backtrans
        else:
            raise ValueError("Invalid status variable passed. Should be one of ['correct', 'incorrect', 'unverified']")

    def verify_step_with_llm(self, step: str):
        llm_prover = BaseLLM(LLM_VERIFIER_PROMPT, llm=self._make_auxiliary_llm())
        ans = llm_prover.generate_response(step)

        verdict = self.extract_bold_text(ans, enclosure="||||")
        justification = self.extract_bold_text(ans, enclosure="[[]]")

        return verdict, justification

    # ------------------------------------------------------------------
    # HELPER FUNCTIONS
    # ------------------------------------------------------------------
    def check_if_pass_repl(self, outputs, key='pass', return_first_correct=False):
        idxs = []
        for i, o in enumerate(outputs):
            if o.get(key):
                if return_first_correct:
                    return i
                idxs.append(i)
        if len(idxs) > 0:
            return idxs
        return None

    def init_memory_buffer(self):
        self.in_memory_store = InMemoryStore(
            index={
                "embed": self.embedding_model,
                "dims": 1024,
                "fields": ["verified_proof_step", "$"],
            }
        )
        self.namespace_for_memory = (self.user_id, "memories")
        self.memory_count = 0

    def record_proof_step(self, proof_step):
        template = (
            'Rewrite the following proposition as a single sentence stating one claim, '
            'preserving essential content. Exclude intermediate computations - state only '
            'the final result.\n\n{}\n\nRespond with the claim only - no preface, labels, '
            'quotes, or commentary.'
        )

        prop_converter = BaseLLM(template, llm=self._make_auxiliary_llm())
        converted_prop_to_claim = prop_converter.generate_response(proof_step)

        memory = {'verified_proof_step': converted_prop_to_claim}
        memory_id = f'step_{str(self.memory_count)}'
        self.in_memory_store.put(self.namespace_for_memory, memory_id, memory)

        self.memory_count += 1

    def search_prereqs(self, query):
        mems = self.in_memory_store.search(
            self.namespace_for_memory,
            query=query,
            limit=self.memory_buffer_n,
        )
        memories = self.in_memory_store.search(self.namespace_for_memory)
        print(f'All memories: {memories}')
        print(f'Retrieved memories: {mems}')

        prereqs = ''
        for m in mems:
            prereqs += f"- {m.dict()['value']['verified_proof_step']}\n"

        return prereqs

    def update_global_buffer(self, proof_step):
        self.global_buffer += f'- {proof_step}\n'

    def get_global_buffer(self):
        return self.global_buffer

    @staticmethod
    def extract_bold_text(output, enclosure='||||'):
        """
        Extract text enclosed in a specific delimiter pair.

        Parameters
        ----------
        output : str
            The string to search within.

        enclosure : str
            Delimiter format. Must be either:
            - '||||' for text enclosed in ||...||
            - '[[]]' for text enclosed in [[...]]

        Returns
        -------
        str
            The extracted text if found, otherwise "null".
        """
        if enclosure == '||||':
            match = re.search(r"\|\|(.*?)\|\|", output)
        elif enclosure == '[[]]':
            match = re.search(r"\[\[(.*?)\]\]", output)
        else:
            raise ValueError("format must be either '||||' or '[[]]'")

        return match.group(1) if match else "null"


if __name__ == '__main__':
    LEANSERVER_CONFIG = 'configs/lean4_server.py'
    lean4server_cfg = load_config(LEANSERVER_CONFIG)

    scheduler = Lean4ServerScheduler(
        max_concurrent_requests=lean4server_cfg.get("lean_max_concurrent_requests", 4),
        timeout=lean4server_cfg.get("lean_timeout", 60),
        memory_limit=lean4server_cfg.get("lean_memory_limit", 10),
        name=lean4server_cfg.get("name", 'test-server'),
    )

    TRANSLATOR_CONFIG: str = 'configs/translators/goedel_translator.py'
    PROVER_CONFIG: str = 'configs/provers/goedel_prover_v2.py'

    embedding_model = HuggingFaceEmbeddings(model_name="Qwen/Qwen3-Embedding-0.6B")

    reasoner = HermesReasoner(
        scheduler=scheduler,
        translator_config=TRANSLATOR_CONFIG,
        prover_config=PROVER_CONFIG,
        embedding_model=embedding_model,
        user_id='some_id',
    )

    step = "Prove that 2+2=5."

    out = reasoner.invoke(
        {
            "name": "verify_one_mathematical_step",
            "args": {"proof_step": step},
            "id": "123",
            "type": "tool_call",
        }
    )
    print(out)

    scheduler.close()
