
import httpx
import json
from typing import AsyncGenerator, Dict, Any
from .base import BaseProvider
from app.core.logger import setup_logging

logger = setup_logging()

class OpenAIProvider(BaseProvider):
    def __init__(self, api_key: str, base_url: str):
        super().__init__(api_key, base_url)

    async def chat_completion(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    json=request_data,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    }
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"OpenAI Provider Error: {e.response.text}")
                raise e

    async def stream_chat_completion(self, request_data: Dict[str, Any]) -> AsyncGenerator[bytes, None]:
        request_data["stream"] = True

        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                json=request_data,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
            ) as response:
                if response.status_code != 200:
                    error_text = await response.read()
                    logger.error(f"OpenAI Stream Error: {error_text.decode()}")
                    yield error_text
                    return

                async for chunk in response.aiter_bytes():
                    yield chunk
