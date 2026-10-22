# import os

# from dotenv import load_dotenv
# from google import genai
# from pydantic import BaseModel, ValidationError

# load_dotenv()

# MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")


# def generate_structured_output(
#     prompt: str,
#     output_model: type[BaseModel],
# ) -> BaseModel:
#     api_key = os.getenv("GEMINI_API_KEY")

#     if not api_key:
#         raise RuntimeError("GEMINI_API_KEY is missing from .env.")

#     client = genai.Client(api_key=api_key)

#     response = client.models.generate_content(
#         model=MODEL_NAME,
#         contents=prompt,
#         config={
#             "temperature": 0.2,
#             "response_mime_type": "application/json",
#             "response_json_schema": output_model.model_json_schema(),
#         },
#     )

#     if not response.text:
#         raise ValueError("Gemini returned an empty response.")

#     try:
#         return output_model.model_validate_json(response.text)
#     except ValidationError as exc:
#         raise ValueError(
#             f"Gemini output failed {output_model.__name__} validation."
#         ) from exc


import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import AzureOpenAI
from pydantic import BaseModel

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_ROOT / "AZURE.env"

if ENV_FILE.exists():
    load_dotenv(ENV_FILE, override=True)


AZURE_OPENAI_ENDPOINT = os.getenv("MODEL_ENDPOINT")
SERVICE_LINE=os.getenv("SERVICE_LINE") 
BRAND=os.getenv("BRAND")
API_VERSION=os.getenv("api_version")
APIVERSION=os.getenv("APIVERSION")

CHAT_DEPLOYMENT_NAME = os.getenv("CHAT_MODEL_NAME")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
PROJECT=os.getenv("PROJECT")
DEPLOYMENT=os.getenv("DEPLOYMENT")


def _get_client() -> AzureOpenAI:
    required_settings = {
        "MODEL_ENDPOINT": AZURE_OPENAI_ENDPOINT,
        "AZURE_OPENAI_API_KEY": AZURE_OPENAI_API_KEY,
        "api_version": API_VERSION,
        "CHAT_MODEL_NAME": CHAT_DEPLOYMENT_NAME,
    }

    missing = [
        key for key, value in required_settings.items()
        if not value
    ]

    if missing:
        raise RuntimeError(
            f"Missing Azure configuration in AZURE.env: {', '.join(missing)}"
        )

    extra_headers = text_headers = {
        'x-service-line': SERVICE_LINE,
        'x-brand': BRAND,
        'x-project': PROJECT,
        'Content-Type': 'application/json',
        'Cache-Control': 'no-cache',
        'Ocp-Apim-Subscription-Key': AZURE_OPENAI_API_KEY,
        'api-version': APIVERSION
    }

    return AzureOpenAI(
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_API_KEY,
        api_version=API_VERSION,
        default_headers=extra_headers,
    )


def generate_structured_output(
    prompt: str,
    output_model: type[BaseModel],
) -> BaseModel:
    """
    Generate output using Azure OpenAI Structured Outputs.

    The supplied Pydantic model defines the expected JSON schema.
    The returned result is parsed into that same model.
    """

    client = _get_client()

    completion = client.beta.chat.completions.parse(
        model=CHAT_DEPLOYMENT_NAME,
        messages=[
            {
                "role": "system",
                "content": (
                    "Follow the instructions carefully. Return an output "
                    "that conforms to the supplied response schema. "
                    "Use only evidence provided in the prompt."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.2,
        response_format=output_model,
    )

    message = completion.choices[0].message

    if message.refusal:
        raise ValueError(
            f"Azure OpenAI refused the request: {message.refusal}"
        )

    if message.parsed is None:
        raise ValueError(
            f"Azure OpenAI returned no parsed output for "
            f"{output_model.__name__}."
        )

    return message.parsed
