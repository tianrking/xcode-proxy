
import uvicorn
import os
import sys
import argparse
from app.core.config import settings

def main():
    """Development runner for Xcode Proxy Server"""
    parser = argparse.ArgumentParser(description="Xcode AI Proxy Server")
    parser.add_argument("--host", default=settings.server.host, help="Bind host")
    parser.add_argument("--port", type=int, default=settings.server.port, help="Bind port")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    
    args = parser.parse_args()
    
    # Update environment variables so config.py can pick them up if needed
    # (Although config.py loads from settings, we want CLIargs to potentially override 
    # or just be used by uvicorn directly. In this architecture, uvicorn bind address 
    # is passed here directly.)
    
    print(f"🚀 Starting Xcode Proxy Server on http://{args.host}:{args.port}")
    uvicorn.run("app.main:app", host=args.host, port=args.port, reload=args.reload)

if __name__ == "__main__":
    main()
