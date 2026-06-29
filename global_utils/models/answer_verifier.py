"""LLM-based answer/step checking utilities.

These are *outside* the formal Lean verification path; they're used to
decide which steps need to be sent to the Lean prover and to compare a
final answer to a ground truth.
"""
import json
import os
import re
from typing import List

import backoff
import openai


class AnswerVerifier:
    def __init__(self):
        api_key = os.getenv("DEEPSEEK_API_KEY", "")
        base_url = os.getenv("DEEPSEEK_BASE_URL", "") or None
        self.model = os.getenv("HERMES_VERIFIER_MODEL", "deepseek-chat")

        self.client = openai.OpenAI(api_key=api_key, base_url=base_url)

    @backoff.on_exception(backoff.expo, openai.APIError)
    def completions_with_backoff(self, model: str, **kwargs):
        return self.client.chat.completions.create(model=model, **kwargs)

    def llm_checker(self, prompt: str) -> str:
        messages = [{"role": "user", "content": prompt}]
        res = self.completions_with_backoff(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=8192,
            n=1,
            top_p=0.95,
            timeout=300,
        )
        return res.choices[0].message.content

    def check_answer(self, question: str, answer, ground_truth: str) -> bool:
        """Compare ``answer`` against ``ground_truth`` for ``question``.

        Returns True if the LLM grader says they match.
        """
        if isinstance(answer, list):
            answer = '\n'.join(answer)

        if not isinstance(answer, str) or answer.strip() == '':
            return False

        with open("prompts/check_answer.txt", "r") as f:
            prompt = f.read()

        prompt = prompt.replace("<question>", question)
        prompt = prompt.replace("<answer>", answer)
        prompt = prompt.replace("<ground_truth>", ground_truth)

        response = self.llm_checker(prompt)
        if isinstance(response, list):
            response = response[0]

        return bool(response and "true" in response.lower())


class StepVerifier(AnswerVerifier):
    def divide_step(self, solution: str) -> List[str]:
        """Split a solution into individual steps via the LLM."""
        with open("prompts/divide_steps.txt", "r") as f:
            prompt = f.read()

        prompt = prompt.replace("<solution>", solution)

        if_pass = False
        try_count = 0
        steps: List[str] = []
        while not if_pass and try_count < 3:
            try:
                response = self.llm_checker(prompt)
                # The response may be surrounded by ``` or ```json
                response = re.sub(r"```(json|JSON)", "", response).replace("```", "").strip()
                steps = json.loads(response)
                if_pass = True
                break
            except Exception as e:
                try_count += 1
                print(e)
                continue

        fallback_steps = [step for step in solution.split("\n") if step.strip() != ""]
        if not fallback_steps:
            fallback_steps = [""]

        if not if_pass:
            print("Warning: Failed to divide the solution into steps.")
            return fallback_steps
        if not steps:
            return fallback_steps
        return steps

    def check_answer(self, question: str, answer: str, divide_into_steps: bool = True):
        """Decide which steps in ``answer`` need Lean4 verification.

        Returns a list of dicts, one per step, each with a
        ``requires_verification`` boolean.
        """
        if divide_into_steps:
            p = "prompts/formalize.txt"
        else:
            p = "prompts/formalize_single_step.txt"

        with open(p, "r") as f:
            prompt_base = f.read()

        if divide_into_steps:
            steps = self.divide_step(answer)
        else:
            steps = [answer]

        checked_steps = []
        buffer = ''

        for step in steps:
            prompt = (
                prompt_base
                .replace("<question>", question)
                .replace('<step>', step)
                .replace('<buffer>', buffer)
            )

            response = self.llm_checker(prompt)
            if isinstance(response, list):
                response = response[0]

            res = bool(response and "true" in response.lower().strip())

            checked_steps.append({
                'question': question,
                'previous_steps': buffer,
                'step': step,
                'requires_verification': res,
            })
            buffer += f'{step}\n'
        return checked_steps

    def check_single_step(self, step: str):
        with open("prompts/formalize_single_step.txt", "r") as f:
            prompt_base = f.read()

        prompt = prompt_base.replace('<step>', step)
        response = self.llm_checker(prompt)
        if isinstance(response, list):
            response = response[0]

        res = bool(response and "true" in response.lower().strip())
        return {'step': step, 'requires_verification': res}


if __name__ == "__main__":
    question = "If $f(x)=5x^2+3x+4$, what is the value of $f(-2)$?"
    llm_answer = (
        "To find the value of \\( f(-2) \\) for the function \\( f(x) = 5x^2 + 3x + 4 \\), follow these steps:\n\n"
        "1. **Substitute \\( x = -2 \\) into the function:**\n"
        "   \\[\n   f(-2) = 5(-2)^2 + 3(-2) + 4\n   \\]\n\n"
        "2. **Calculate each term separately:**\n"
        "   - **First term:** \\( 5(-2)^2 = 5 \\times 4 = 20 \\)\n"
        "   - **Second term:** \\( 3(-2) = -6 \\)\n"
        "   - **Third term:** \\( 4 \\) remains as is.\n\n"
        "3. **Add the calculated terms together:**\n"
        "   \\[\n   f(-2) = 20 - 6 + 4\n   \\]\n"
        "   \\[\n   f(-2) = (20 - 6) + 4 = 14 + 4 = 18\n   \\]\n\n"
        "**Final Answer:**\n\\[\n\\boxed{18}\n\\]"
    )
    verifier = StepVerifier()
    res = verifier.check_answer(question, llm_answer, divide_into_steps=True)

    for p in res:
        print(f'{p["previous_steps"]}{p["step"]}\n{p["requires_verification"]}')
        print('-' * 100)
