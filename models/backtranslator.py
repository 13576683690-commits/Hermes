"""Backtranslate Lean statements to natural language and check equivalence.

Used as a sanity check on the autoformalizer's output: if the formal
statement, when paraphrased back into English, matches the original
informal statement, we trust the formalization.
"""
from __future__ import annotations

from models.auxiliary_llm import AuxiliaryLLM


BACKTRANS_PROMPT = '''Rewrite the following Lean statement in natural language. Output only the rewritten statement and nothing else.

```lean
{formal_statement}
```
'''

VERIFICATION_PROMPT = '''
Your job is to determine whether the Backtranslated Statement is logically equivalent to the Original Statement.

Logical equivalence means:
- Both statements assert the same final mathematical claims,
- Extra intermediate steps, explanations, or justifications **DO NOT** affect equivalence,
- Different wording, order, or level of detail also **DO NOT** affect equivalence.

They are **NOT** equivalent only if the final mathematical claims differ.

Return exactly one word: True or False. Do **NOT** provide explanations.

Original Statement:
<original>

Backtranslated Statement:
<backtranslated>

Does the backtranslated statement match the original statement?:
'''


class BackTranslator:
    def __init__(self, llm: AuxiliaryLLM) -> None:
        """Use the same :class:`AuxiliaryLLM` instance as translator / agent config."""
        self.llm = llm

    def backtranslate(self, formal_statement: str) -> str:
        prompt = BACKTRANS_PROMPT.format(formal_statement=formal_statement)
        return self.llm.chat(prompt, temperature=0.8)

    def check_answer(self, original_statement: str, backtrans_statement: str) -> bool:
        if backtrans_statement.strip() == '':
            return False

        prompt = VERIFICATION_PROMPT.replace("<original>", original_statement)
        prompt = prompt.replace("<backtranslated>", backtrans_statement)

        response = self.llm.chat(prompt, temperature=0.8)
        return bool(response and "true" in response.lower())

    def backtranslate_and_verify(self, orig: str, lean_statement: str):
        backtranslated_statement = self.backtranslate(lean_statement)
        response = self.check_answer(
            original_statement=orig,
            backtrans_statement=backtranslated_statement,
        )
        return response, backtranslated_statement


if __name__ == "__main__":
    from prover.utils import load_config

    cfg = load_config("configs/translators/deepseek_v4_flash.py")
    llm = AuxiliaryLLM.from_config(cfg)
    verifier = BackTranslator(llm=llm)
    print("Auxiliary LLM base_url:", llm.client.base_url, "model:", llm.model_path)
