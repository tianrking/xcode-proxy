
import json
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse
from app.services.factory import ProviderFactory
from app.core.config import settings
from app.core.logger import setup_logging

router = APIRouter()
logger = setup_logging()

@router.post("/chat/completions")
async def chat_completions(request: Request):
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    model_id = body.get("model")
    
    # Fallback logic if model not specified or not found
    if not model_id or model_id not in settings.models:
        default_model = settings.default_model
        if default_model and default_model in settings.models:
            logger.info(f"Model '{model_id}' not found using default: {default_model}")
            model_id = default_model
        else:
            # If no default, pick the first one
            if settings.models:
                model_id = next(iter(settings.models))
                logger.info(f"Model '{body.get('model')}' not found, using first available: {model_id}")
            else:
                logger.error("No models configured")
                raise HTTPException(status_code=500, detail="No models configured")
    
    provider = ProviderFactory.get_provider(model_id)
    if not provider:
         raise HTTPException(status_code=500, detail=f"Failed to initialize provider for {model_id}")


    logger.info(f"Routing request to {model_id} ({settings.models[model_id].type})")

    try:
        if body.get("stream", False):
            return StreamingResponse(
                provider.stream_chat_completion(body),
                media_type="text/event-stream"
            )
        else:
            return await provider.chat_completion(body)
    except Exception as e:
        # If it's an HTTPStatusError (from httpx), extract the status code
        if hasattr(e, 'response') and hasattr(e.response, 'status_code'):
             error_detail = e.response.text
             logger.error(f"Upstream provider error: {e.response.status_code} - {error_detail}")
             raise HTTPException(status_code=e.response.status_code, detail=f"Upstream Error: {error_detail}")
        
        logger.error(f"Internal Proxy Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

