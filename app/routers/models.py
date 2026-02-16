
from fastapi import APIRouter
from app.core.config import settings
from datetime import datetime

router = APIRouter()

@router.get("/models")
async def list_models():
    """Return available models for Xcode"""
    model_list = []
    
    for model_id, config in settings.models.items():
        model_list.append({
            "id": model_id,
            "object": "model",
            "created": int(datetime.now().timestamp()),
            "owned_by": config.type,
            "name": config.name or model_id
        })
    
    return {"object": "list", "data": model_list}
