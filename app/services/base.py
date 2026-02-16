
from abc import ABC, abstractmethod
from typing import AsyncGenerator, Dict, Any, Optional

class BaseProvider(ABC):
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url

    @abstractmethod
    async def chat_completion(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Non-streaming chat completion"""
        pass

    @abstractmethod
    async def stream_chat_completion(self, request_data: Dict[str, Any]) -> AsyncGenerator[bytes, None]:
        """Streaming chat completion"""
        pass
