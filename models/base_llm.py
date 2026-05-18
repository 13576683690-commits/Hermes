"""Template-based prompts on top of :class:`AuxiliaryLLM`."""
from __future__ import annotations

from typing import Optional

from models.auxiliary_llm import AuxiliaryLLM


class BaseLLM:
    def __init__(
        self,
        template: str = "{}",
        llm: Optional[AuxiliaryLLM] = None,
    ) -> None:
        if llm is None:
            raise ValueError(
                "BaseLLM requires an AuxiliaryLLM instance. "
                "Construct it via HermesReasoner._make_auxiliary_llm() or AuxiliaryLLM.from_config()."
            )
        self.llm = llm
        self.template = template
        assert template.count("{}") == 1, "BaseLLM template must contain exactly one '{}' placeholder"

    def generate_response(self, prompt: str) -> str:
        return self.llm.chat(self.template.format(prompt))
