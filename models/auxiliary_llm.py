"""OpenAI-compatible chat helper for auxiliary Hermes tasks.

Used for backtranslation, claim summarization (memory), and optional LLM
verification. Shares the same endpoint configuration as the translator /
prover (or the demo agent's reasoning model) via :class:`AuxiliaryLLM`.
"""
from __future__ import annotations

from typing import Any, List, Mapping, Optional

import openai

from models.llm_client import build_openai_client


def llm_settings_from_config(cfg: Mapping[str, Any]) -> dict:
    """Extract API client fields from a translator/prover-style config dict."""
    model_args = cfg.get("model_args") or {}
    return {
        "model_path": cfg.get("model_path"),
        "api_key": cfg.get("api_key"),
        "base_url": cfg.get("base_url"),
        "port": cfg.get("port"),
        "api_mode": cfg.get("api_mode"),
        "temperature": model_args.get("temperature", 0.7),
        "max_tokens": model_args.get("max_tokens", 8192),
        "top_p": model_args.get("top_p", 0.95),
        "timeout": model_args.get("timeout", 300),
    }


class AuxiliaryLLM:
    """Thin wrapper around the OpenAI chat API with shared Hermes settings."""

    def __init__(
        self,
        *,
        model_path: Optional[str],
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        port: Optional[int] = None,
        api_mode: Optional[bool] = None,
        temperature: float = 0.7,
        max_tokens: int = 8192,
        top_p: float = 0.95,
        timeout: int = 300,
    ) -> None:
        if not model_path:
            raise ValueError("AuxiliaryLLM requires model_path (e.g. 'deepseek-reasoner').")
        self.model_path = model_path
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.timeout = timeout
        self.client = build_openai_client(
            api_key=api_key,
            base_url=base_url,
            port=port,
            api_mode=api_mode,
        )

    @classmethod
    def from_config(cls, cfg: Mapping[str, Any]) -> "AuxiliaryLLM":
        return cls(**llm_settings_from_config(cfg))

    def chat(
        self,
        prompt: str,
        *,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        messages: List[dict] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        res = self.client.chat.completions.create(
            model=self.model_path,
            messages=messages,
            temperature=temperature if temperature is not None else self.temperature,
            max_tokens=max_tokens if max_tokens is not None else self.max_tokens,
            top_p=self.top_p,
            timeout=self.timeout,
        )
        return res.choices[0].message.content
