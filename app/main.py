

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import models, proxy
from app.core.config import settings
from app.core.logger import setup_logging

logger = setup_logging()

app = FastAPI(
    title="Xcode AI Proxy",
    description="Universal LLM Proxy for Xcode",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(models.router, prefix="/v1", tags=["models"])
app.include_router(proxy.router, prefix="/v1", tags=["chat"])

@app.get("/health")
async def health_check():
    return {"status": "ok", "models_loaded": len(settings.models)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.server.host, port=settings.server.port)
