# backend/app/utils/runtime_config.py

"""
Runtime Configuration Persistence

Saves runtime configuration changes to a JSON file so they persist across backend restarts.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)

# Config file location
RUNTIME_CONFIG_FILE = Path(__file__).parent.parent.parent / "runtime_config.json"


def load_runtime_config() -> Dict[str, Any]:
    """
    Load runtime configuration from JSON file
    
    Returns:
        Dictionary of runtime config values
    """
    if not RUNTIME_CONFIG_FILE.exists():
        logger.info("No runtime config file found, using defaults")
        return {}
    
    try:
        with open(RUNTIME_CONFIG_FILE, 'r') as f:
            config = json.load(f)
        logger.info(f"Loaded runtime config: {config}")
        return config
    except Exception as e:
        logger.error(f"Error loading runtime config: {e}")
        return {}


def save_runtime_config(config: Dict[str, Any]):
    """
    Save runtime configuration to JSON file
    
    Args:
        config: Dictionary of config values to save
    """
    try:
        with open(RUNTIME_CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        logger.info(f"Saved runtime config: {config}")
    except Exception as e:
        logger.error(f"Error saving runtime config: {e}")


def update_runtime_config(key: str, value: Any):
    """
    Update a single runtime config value
    
    Args:
        key: Config key to update
        value: New value
    """
    config = load_runtime_config()
    config[key] = value
    save_runtime_config(config)


def get_runtime_config(key: str, default: Any = None) -> Any:
    """
    Get a single runtime config value
    
    Args:
        key: Config key to get
        default: Default value if key not found
        
    Returns:
        Config value or default
    """
    config = load_runtime_config()
    return config.get(key, default)
