"""Translator config for an OpenAI-compatible API (e.g. DeepSeek).

Use this template when the translator model is hosted behind an
OpenAI-compatible HTTP API rather than a local vLLM server. Set
``DEEPSEEK_API_KEY`` (or another env var of your choice) before running.
"""
import os

from prover.utils import AttrDict


# model
batch_size = 4
pass_k = 1
model_path = 'deepseek-chat'
model_args = AttrDict(
    mode='cot',  # `cot` or `non-cot`
    temperature=0.6,
    max_tokens=8192,
    top_p=0.95,
    timeout=300,
)

api_key = os.getenv('DEEPSEEK_API_KEY', '<your-deepseek-api-key>')
base_url = 'https://api.deepseek.com'
api_mode = True  # hosted DeepSeek API (do NOT use vLLM http://host:port URL builder)
# ``port`` is intentionally unset for hosted APIs - only used for vLLM (e.g. port=2000).


translation_prompt = (
    "Please autoformalize the following natural language problem statement in Lean 4. "
    "Use the following theorem name: test\n"
    "The natural language statement is:\n"
    "<question>\n"
    "Think before you provide the lean statement, then enclose the final Lean 4 "
    "statement in a ```lean4 ... ``` block."
)
