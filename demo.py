"""End-to-end demo running a Hermes-augmented react agent on a single problem.

This script wires together:
- the Lean4 verification scheduler,
- the Hermes verification tool, and
- a chat LLM driving the agent loop.

It is intentionally minimal so it can be used as a template for batch
evaluation on full datasets (which would replace the single ``problem``
string below with a data-loader iterator).
"""
# import compat  # noqa: F401  # must run before langchain / langgraph imports

import json
import os

from langgraph.prebuilt import create_react_agent
from langchain_deepseek import ChatDeepSeek
# from langchain_huggingface.embeddings import HuggingFaceEmbeddings

from prover.utils import load_config, AttrDict
from prover.lean.verifier import Lean4ServerScheduler

from hermes import HermesReasoner
from utils import timeout_handler


MAX_RECURSION_LIMIT = 100
LEANSERVER_CONFIG = 'configs/lean4_server.py'

setting = 'zero_shot'

with open(f'prompts/{setting}_cot.txt', 'r') as f:
    prompt_schema = f.read()

with open('setup.json', 'r') as f:
    setup = json.load(f)
TRANSLATOR_CONFIG = setup['translator']
PROVER_CONFIG = setup['prover']


def run_agent(prompt, agent):
    return agent.invoke(
        {"messages": [{"role": "user", "content": prompt}]},
        {"recursion_limit": MAX_RECURSION_LIMIT},
    )


def attempt_problem_with_lean(problem, agent):
    return run_agent(prompt_schema.replace('<question>', problem), agent)


def build_auxiliary_llm_config(model_name: str):
    """Same API + model as the LangGraph reasoning agent (e.g. deepseek-reasoner)."""
    return {
        "model_path": model_name,
        "api_key": os.getenv("DEEPSEEK_API_KEY"),
        "base_url": "https://api.deepseek.com",
        "api_mode": True,
        "model_args": AttrDict(
            temperature=0.95,
            max_tokens=8192,
            top_p=0.95,
            timeout=300,
        ),
    }


def predict_helper(data_sample, embedding_model, scheduler, llm, model_name: str):
    reasoner = HermesReasoner(
        scheduler=scheduler,
        translator_config=TRANSLATOR_CONFIG,
        prover_config=PROVER_CONFIG,
        embedding_model=embedding_model,
        auxiliary_llm_config=build_auxiliary_llm_config(model_name),
        user_id='abc123',
    )

    system_prompt = (
        "You are a helpful assistant who is proficient in mathematics and "
        "uses verification tools to make sure every step is correct."
    )
    agent = create_react_agent(
        model=llm,
        tools=[reasoner],
        prompt=system_prompt,
    )

    return timeout_handler(
        attempt_problem_with_lean,
        args=(data_sample, agent),
        timeout_duration=1500,
    )


if __name__ == '__main__':
    lean4server_cfg = load_config(LEANSERVER_CONFIG)
    translator_cfg = load_config(TRANSLATOR_CONFIG)
    prover_cfg = load_config(PROVER_CONFIG)

    scheduler = Lean4ServerScheduler(
        max_concurrent_requests=lean4server_cfg.get("lean_max_concurrent_requests", 4),
        timeout=lean4server_cfg.get("lean_timeout", 120),
        memory_limit=lean4server_cfg.get("lean_memory_limit", 10),
        name=lean4server_cfg.get("name", 'test-server'),
    )

    # Init Agent - Deepseek V3 (configure DEEPSEEK_API_KEY in your environment)
    model_name = 'deepseek-chat'
    llm = ChatDeepSeek(
        model=model_name,
        temperature=0.95,
        max_tokens=8192,
        timeout=300,
        max_retries=20,
    )

    # embedding_model = HuggingFaceEmbeddings(
    #     model_name="Qwen/Qwen3-Embedding-0.6B",
    #     model_kwargs={'device': 'cuda:0'},
    #     encode_kwargs={"normalize_embeddings": True},
    # )
    embedding_model=None

    problem = 'Prove that 2+2=5'
    try:
        answer = predict_helper(
            problem,
            embedding_model=embedding_model,
            scheduler=scheduler,
            llm=llm,
            model_name=model_name,
        )
        print(answer)
    finally:
        scheduler.close()
