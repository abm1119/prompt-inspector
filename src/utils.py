import os
import json
from typing import Type, TypeVar
from openai import OpenAI
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from dotenv import load_dotenv

load_dotenv()

PRIMARY_MODEL = "llama-3.3-70b-versatile"
FALLBACK_MODEL = "llama-3.1-8b-instant"
BASE_URL = "https://api.groq.com/openai/v1"

T = TypeVar("T", bound=BaseModel)

def get_client():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found. Please set it in your .env file.")
    return OpenAI(base_url=BASE_URL, api_key=api_key)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(Exception),
    reraise=True
)
def call_llm(system_prompt: str, user_prompt: str, response_model: Type[T], model: str = PRIMARY_MODEL) -> T:
    client = get_client()
    schema_str = json.dumps(response_model.model_json_schema(), indent=2)
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": (
                    f"{system_prompt}\n\n"
                    f"OUTPUT FORMAT: You must return a single JSON object that conforms strictly to this JSON Schema:\n"
                    f"```json\n{schema_str}\n```\n"
                    f"IMPORTANT: Do not wrap the output in any other keys like 'analysis' or 'result'. "
                    f"The root of your JSON response must contain the keys defined in the schema."
                )},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
        )
        content = completion.choices[0].message.content
        return response_model.model_validate_json(content)
    except Exception as e:
        if model == PRIMARY_MODEL:
            print(f"Primary model ({model}) failed, trying fallback... ({e})")
            return call_llm(system_prompt, user_prompt, response_model, model=FALLBACK_MODEL)
        raise e
