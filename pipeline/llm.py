import time
from google import genai
from google.genai import types
from pipeline import config

_client = genai.Client(api_key=config.GEMINI_API_KEY)


def call_llm(prompt: str, system: str = "", temperature: float = 0.7, json_mode: bool = False) -> str:
    cfg = types.GenerateContentConfig(
        system_instruction=system or None,
        temperature=temperature,
        response_mime_type="application/json" if json_mode else "text/plain",
    )
    last_err = None
    for attempt in range(config.MAX_RETRIES):
        try:
            resp = _client.models.generate_content(
                model=config.MODEL_NAME, contents=prompt, config=cfg
            )
            if resp.text:
                return resp.text.strip()
        except Exception as e:
            last_err = e
            time.sleep(2 ** attempt)
    raise RuntimeError(f"LLM call failed after {config.MAX_RETRIES} retries: {last_err}")
