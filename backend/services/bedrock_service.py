"""AWS Bedrock service — LLM calls for reasoning, vision, sentiment, NL queries."""

import boto3
import json
from config import AWS_REGION, BEDROCK_MODEL_ID, BEDROCK_VISION_MODEL_ID


def get_bedrock_client():
    return boto3.client("bedrock-runtime", region_name=AWS_REGION)


async def invoke_llm(prompt: str, system: str = "", max_tokens: int = 2048) -> str:
    """Call AWS Bedrock Claude for text-based reasoning."""
    client = get_bedrock_client()

    messages = [{"role": "user", "content": prompt}]

    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "messages": messages,
    }
    if system:
        body["system"] = system

    response = client.invoke_model(
        modelId=BEDROCK_MODEL_ID,
        contentType="application/json",
        accept="application/json",
        body=json.dumps(body),
    )

    result = json.loads(response["body"].read())
    return result["content"][0]["text"]


async def invoke_vision(prompt: str, image_bytes: bytes, media_type: str = "image/jpeg") -> str:
    """Call AWS Bedrock Claude Vision for image analysis."""
    import base64

    client = get_bedrock_client()

    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": media_type,
                        "data": image_b64,
                    },
                },
                {"type": "text", "text": prompt},
            ],
        }
    ]

    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1024,
        "messages": messages,
    }

    response = client.invoke_model(
        modelId=BEDROCK_VISION_MODEL_ID,
        contentType="application/json",
        accept="application/json",
        body=json.dumps(body),
    )

    result = json.loads(response["body"].read())
    return result["content"][0]["text"]
