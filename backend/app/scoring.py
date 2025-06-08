from openai import OpenAI
import os

SYSTEM_PROMPT = (
    "You are a grader. Score the user's answer from 1 to 5 based on the question and optional guidlines."
)

_client = None

def get_client() -> OpenAI:
    global _client
    if _client is None:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise RuntimeError('OPENAI_API_KEY missing')
        _client = OpenAI(api_key=api_key)
    return _client


def score_answer(question: str, answer: str, guidlines: str | None = None) -> int:
    prompt = SYSTEM_PROMPT
    if guidlines:
        prompt += f" Guideline: {guidlines}"
    prompt += f" Question: {question} Answer: {answer}"

    client = get_client()
    resp = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
        messages=[{"role": "system", "content": prompt}]
    )
    content = resp.choices[0].message.content
    try:
        return int(content.strip()[0])
    except Exception:
        return 3
