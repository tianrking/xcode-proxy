
import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from pydantic_settings import BaseSettings
from app.core.logger import setup_logging

# Setup logging
logger = setup_logging()

class ModelConfig(BaseModel):
    type: str = Field(..., description="Provider type: zhipu, anthropic, openai")
    api_key: str
    api_base: Optional[str] = None
    name: Optional[str] = None # Display name

class ServerConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 3000

class AppSettings(BaseSettings):
    models: Dict[str, ModelConfig] = {}
    default_model: Optional[str] = None
    server: ServerConfig = ServerConfig()

    class Config:
        env_prefix = "XCODE_PROXY_"
        case_sensitive = False


try:
    import tomllib
except ImportError:
    # Fallback for older python if needed, though 3.12 has it
    import tomli as tomllib

def load_claude_cli_settings() -> Dict[str, Any]:
    """Load settings from ~/.claude/settings.json"""
    settings_path = Path.home() / ".claude" / "settings.json"
    if not settings_path.exists():
        logger.debug(f"Claude CLI settings not found at {settings_path}")
        return {}
    
    try:
        with open(settings_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("env", {})
    except Exception as e:
        logger.error(f"Failed to load Claude CLI settings: {e}")
        return {}

def load_local_toml_settings() -> Dict[str, Any]:
    """Load settings from local settings.toml"""
    settings_path = Path.cwd() / "settings.toml"
    if not settings_path.exists():
        return {}
    
    try:
        with open(settings_path, 'rb') as f:
            return tomllib.load(f)
    except Exception as e:
        logger.error(f"Failed to load local settings.toml: {e}")
        return {}

def get_settings() -> AppSettings:
    """
    Load and merge settings from multiple sources with precedence:
    1. Local settings.toml
    2. ~/.claude/settings.json (adapted for Xcode Proxy)
    3. Defaults
    """
    
    # 1. Load Claude CLI Env (Base Layer)
    claude_env = load_claude_cli_settings()
    
    # Adapt Claude Env to AppSettings structure
    api_key = claude_env.get("ANTHROPIC_API_KEY")
    model_name = claude_env.get("ANTHROPIC_DEFAULT_OPUS_MODEL", "GLM-4.7") # Default fallback
    
    initial_models = {}
    default_model = None

    if api_key:
        if "." in api_key: # Detect Zhipu format
             initial_models[model_name] = {
                "type": "zhipu",
                "api_key": api_key,
                "api_base": "https://open.bigmodel.cn/api/paas/v4",
                "name": f"{model_name} (Claude CLI)"
            }
        else:
            initial_models[model_name] = {
                "type": "anthropic",
                "api_key": api_key,
                "name": f"{model_name} (Claude CLI)"
            }
        default_model = model_name

    # 2. Load Local TOML Settings (Overlay Layer)
    local_config = load_local_toml_settings()
    
    # Merge Logic
    merged_models = initial_models.copy()
    
    # Check for [models] section in TOML
    if "models" in local_config:
        merged_models.update(local_config["models"])
    
    # Check for [server.models] default
    final_default_model = default_model
    if "server" in local_config and "models" in local_config["server"]:
         final_default_model = local_config["server"]["models"].get("default", default_model)
    elif "default_model" in local_config: # Legacy/Fallback support if user puts it at root
         final_default_model = local_config["default_model"]

    server_config = local_config.get("server", {"host": "0.0.0.0", "port": 3000})

    # Auto-Configuration: If the requested default model is NOT in merged_models,
    # but we have a base API credential from Claude CLI,
    # we create a VALID model entry for the new default model using those credentials.
    if final_default_model and final_default_model not in merged_models:
        if default_model and default_model in merged_models:
            logger.info(f"Auto-configuring model '{final_default_model}' using credentials from '{default_model}'")
            
            existing_config = merged_models[default_model]
            
            # Create a new model config for the requested default
            if isinstance(existing_config, dict):
                new_model_config = existing_config.copy()
            else:
                new_model_config = existing_config.dict() # Convert Pydantic to dict for manipulation
            
            # Update name to be the ID itself or custom
            new_model_config["name"] = final_default_model
            
            merged_models[final_default_model] = new_model_config
        else:
            logger.warning(f"Default model '{final_default_model}' not found and no base credentials available.")

    # Construct final config dict
    final_config_dict = {
        "models": merged_models,
        "default_model": final_default_model,
        "server": server_config
    }
    
    return AppSettings(**final_config_dict)

settings = get_settings()
