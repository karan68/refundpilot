"""ZhipuAI GLM service — LLM calls for reasoning, vision, sentiment, NL queries.

Replaces AWS Bedrock with ZhipuAI GLM-5 (OpenAI-compatible API).
"""

import httpx
import json
import base64
from config import ZHIPU_API_KEY, ZHIPU_BASE_URL, ZHIPU_MODEL, ZHIPU_CHAT_MODEL


def _headers():
    return {
        "Authorization": f"Bearer {ZHIPU_API_KEY}",
        "Content-Type": "application/json",
    }


def _extract_content(result: dict) -> str:
    """Extract content from GLM response — handles GLM-5 reasoning_content."""
    msg = result["choices"][0]["message"]
    content = msg.get("content", "")
    if content:
        return content
    # GLM-5 may put content in reasoning_content if max_tokens too low
    return msg.get("reasoning_content", "")


async def invoke_llm(prompt: str, system: str = "", max_tokens: int = 2048) -> str:
    """Call ZhipuAI GLM for text-based reasoning."""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    body = {
        "model": ZHIPU_CHAT_MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.3,
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{ZHIPU_BASE_URL}/chat/completions",
            headers=_headers(),
            json=body,
        )
        response.raise_for_status()
        result = response.json()
        return _extract_content(result)


async def invoke_vision(prompt: str, image_bytes: bytes, media_type: str = "image/jpeg") -> str:
    """Call ZhipuAI GLM-4V for image analysis."""
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{media_type};base64,{image_b64}",
                    },
                },
                {"type": "text", "text": prompt},
            ],
        }
    ]

    body = {
        "model": ZHIPU_MODEL,
        "messages": messages,
        "max_tokens": 1024,
        "temperature": 0.3,
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{ZHIPU_BASE_URL}/chat/completions",
            headers=_headers(),
            json=body,
        )
        response.raise_for_status()
        result = response.json()
        return _extract_content(result)


async def invoke_json(prompt: str, system: str = "") -> dict:
    """Call GLM and parse JSON response. Retries once if parsing fails."""
    raw = await invoke_llm(prompt, system)

    # Try to extract JSON from response
    try:
        # Handle markdown code blocks
        if "```json" in raw:
            raw = raw.split("```json")[1].split("```")[0]
        elif "```" in raw:
            raw = raw.split("```")[1].split("```")[0]
        return json.loads(raw.strip())
    except (json.JSONDecodeError, IndexError):
        # Retry with stricter prompt
        retry_prompt = f"{prompt}\n\nIMPORTANT: Return ONLY valid JSON. No markdown, no explanation, just the JSON object."
        raw2 = await invoke_llm(retry_prompt, system)
        try:
            if "```json" in raw2:
                raw2 = raw2.split("```json")[1].split("```")[0]
            elif "```" in raw2:
                raw2 = raw2.split("```")[1].split("```")[0]
            return json.loads(raw2.strip())
        except (json.JSONDecodeError, IndexError):
            return {"error": "Failed to parse JSON", "raw": raw2[:500]}
