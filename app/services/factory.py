
from typing import Optional
from app.core.config import settings, ModelConfig
from .base import BaseProvider
from .openai import OpenAIProvider
from .zhipu import ZhipuProvider

class ProviderFactory:
    @staticmethod
    def get_provider(model_id: str) -> Optional[BaseProvider]:
        config: ModelConfig = settings.models.get(model_id)
        if not config:
            return None
        
        provider_type = config.type.lower()
        
        # Determine API Base
        if provider_type == "zhipu":
            base_url = config.api_base or "https://open.bigmodel.cn/api/paas/v4"
            return ZhipuProvider(
                api_key=config.api_key, 
                base_url=base_url
            )
        elif provider_type == "openai" or provider_type == "anthropic":
            # Anthropic here assumes we are using an OpenAI-compatible adapter or direct API 
            # (But original code used anthropic generic config, let's assume OpenAI protocol for Xcode Proxy mostly)
            # OR we can add real Anthropic client if needed. 
            # For now, following the original design which seemed to rely on HTTPX generic calls.
            # If "Anthropic" type is strict Anthropic API, we need a separate implementation.
            # However, looking at original DIY_server.py: 
            # It constructed a request to `cc_env.get("ANTHROPIC_BASE_URL")` which implies OpenAI integration 
            # or a proxy that accepts OpenAI format.
            # Let's treat 'anthropic' as 'openai' compatible with custom URL for now, as Xcode likely sends OpenAI format
            # OR Xcode sends Anthropic format? 
            # Wait, Xcode sends whatever format. 
            # The original `DIY_server.py` re-routed to Zhipu (OpenAI format).
            # If type is 'anthropic', let's use OpenAIProvider but with Anthropic base URL? 
            # Actually, standard Anthropic API is different. 
            # BUT, if Xcode is expecting OpenAI format back, we might need translation?
            # original DIY_server.py:
            # if type == 'zhipu' -> handle_zhipu_request (OpenAI format)
            # else -> Error (only Zhipu/OpenAI protocol implemented)
            # So I will stick to OpenAI protocol for now.
            base_url = config.api_base or "https://api.openai.com/v1"
            return OpenAIProvider(
                api_key=config.api_key,
                base_url=base_url
            )
        
        return None
