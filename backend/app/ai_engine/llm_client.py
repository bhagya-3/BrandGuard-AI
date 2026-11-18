
import json

import httpx

from app.core.config import settings


class LLMClient:
    def __init__(self):
        self.api_key = settings.LLM_API_KEY
        self.base_url = settings.LLM_BASE_URL.rstrip("/")
        self.model = settings.LLM_MODEL
        self.timeout = 60.0

    async def generate_json(
        self,
        messages: list[dict[str, str]],
    ) -> dict:
        """
        Send a request to an OpenAI-compatible chat API
        and return a JSON response.
        """

        if not self.api_key:
            raise RuntimeError(
                "LLM_API_KEY is not configured."
            )

        url = f"{self.base_url}/chat/completions"

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.1,
            "response_format": {
                "type": "json_object"
            },
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(
            timeout=self.timeout
        ) as client:
            response = await client.post(
                url,
                headers=headers,
                json=payload,
            )

            response.raise_for_status()

        response_data = response.json()

        content = (
            response_data["choices"][0]["message"]["content"]
        )

        try:
            result = json.loads(content)
        except (json.JSONDecodeError, TypeError) as exc:
            raise ValueError(
                "The AI returned invalid JSON."
            ) from exc

        if not isinstance(result, dict):
            raise ValueError(
                "The AI response must be a JSON object."
            )

        return result
