"""Shared OpenAI client construction for hosted APIs and local vLLM servers."""
from __future__ import annotations

from typing import Optional

import openai


def normalize_base_url(base_url: str) -> str:
    """Normalize a base URL string (strip, fix common typos, drop trailing slash)."""
    url = base_url.strip()
    # Common copy-paste typos seen behind corporate proxies
    if url.startswith("https//"):
        url = "https://" + url[len("https//") :]
    if url.startswith("http//"):
        url = "http://" + url[len("http//") :]
    return url.rstrip("/")


def looks_like_full_url(base_url: Optional[str]) -> bool:
    """Return True if ``base_url`` already includes an HTTP(S) scheme."""
    if not isinstance(base_url, str) or not base_url.strip():
        return False
    url = normalize_base_url(base_url)
    return url.startswith("http://") or url.startswith("https://")


def is_deepseek_endpoint(base_url: Optional[str]) -> bool:
    if not isinstance(base_url, str):
        return False
    return "api.deepseek.com" in base_url


def build_openai_client(
    *,
    api_key: Optional[str],
    base_url: Optional[str],
    port: Optional[int] = None,
    api_mode: Optional[bool] = None,
) -> openai.OpenAI:
    """
    Build an OpenAI-compatible client for either:

    * **Hosted API** (DeepSeek, OpenAI, etc.): ``base_url`` is a full URL such as
      ``https://api.deepseek.com``. Set ``api_mode=True`` in the config to force
      this path even if detection heuristics fail.
    * **Local vLLM**: ``base_url`` is a bare host (``0.0.0.0``) and ``port`` is set
      (e.g. ``2000``). The client URL becomes ``http://<host>:<port>/v1``.
    """
    normalized = normalize_base_url(base_url) if base_url else None

    use_hosted = bool(api_mode) or looks_like_full_url(normalized)

    if use_hosted:
        if not normalized:
            raise ValueError(
                "Hosted API mode requires base_url (e.g. 'https://api.deepseek.com'). "
                "Set api_mode=True and base_url in your translator/prover config."
            )
        return openai.OpenAI(api_key=api_key, base_url=normalized)

    # vLLM / local OpenAI-compatible server
    host = (base_url or "").strip()
    if not host:
        raise ValueError("vLLM mode requires base_url (e.g. '0.0.0.0').")
    if port is None:
        raise ValueError(
            f"Misconfigured client: base_url={base_url!r} port={port!r}. "
            "This looks like vLLM settings but port is missing. "
            "For DeepSeek API use api_mode=True and base_url='https://api.deepseek.com' "
            "(do not set port). For vLLM use base_url='0.0.0.0' and port=2000."
        )
    return openai.OpenAI(
        api_key=api_key,
        base_url=f"http://{host}:{port}/v1",
    )
