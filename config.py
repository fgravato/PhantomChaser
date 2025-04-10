import json
import os
from typing import Dict, Any, Optional, Union

# Default configuration values
DEFAULT_CONFIG = {
    "levenshtein_threshold": 2,
    "image_similarity_threshold": 0.9,
    "auto_kick": True
}

# Path to the configuration file
CONFIG_FILE = "bot_config.json"

# In-memory cache of guild configurations
_guild_configs: Dict[int, Dict[str, Any]] = {}


def _load_configs() -> Dict[int, Dict[str, Any]]:
    """Load configurations from the config file."""
    if not os.path.exists(CONFIG_FILE):
        return {}
    
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}


def _save_configs(configs: Dict[int, Dict[str, Any]]) -> None:
    """Save configurations to the config file."""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(configs, f, indent=2)


def get_guild_config(guild_id: int) -> Dict[str, Any]:
    """
    Get the configuration for a specific guild.
    
    Args:
        guild_id: The ID of the guild
        
    Returns:
        The guild's configuration, or the default configuration if not found
    """
    global _guild_configs
    
    # Load configurations if not already loaded
    if not _guild_configs:
        _guild_configs = _load_configs()
    
    # Convert guild_id to string for JSON compatibility
    guild_id_str = str(guild_id)
    
    # Return the guild's configuration, or create a new one with default values
    if guild_id_str not in _guild_configs:
        _guild_configs[guild_id_str] = DEFAULT_CONFIG.copy()
        _save_configs(_guild_configs)
    
    return _guild_configs[guild_id_str]


def set_guild_config(guild_id: int, key: str, value: Any) -> None:
    """
    Set a configuration value for a specific guild.
    
    Args:
        guild_id: The ID of the guild
        key: The configuration key
        value: The configuration value
    """
    global _guild_configs
    
    # Load configurations if not already loaded
    if not _guild_configs:
        _guild_configs = _load_configs()
    
    # Convert guild_id to string for JSON compatibility
    guild_id_str = str(guild_id)
    
    # Create guild config if it doesn't exist
    if guild_id_str not in _guild_configs:
        _guild_configs[guild_id_str] = DEFAULT_CONFIG.copy()
    
    # Set the configuration value
    _guild_configs[guild_id_str][key] = value
    
    # Save the configurations
    _save_configs(_guild_configs)


def reset_guild_config(guild_id: int) -> None:
    """
    Reset a guild's configuration to the default values.
    
    Args:
        guild_id: The ID of the guild
    """
    global _guild_configs
    
    # Load configurations if not already loaded
    if not _guild_configs:
        _guild_configs = _load_configs()
    
    # Convert guild_id to string for JSON compatibility
    guild_id_str = str(guild_id)
    
    # Reset the guild's configuration
    _guild_configs[guild_id_str] = DEFAULT_CONFIG.copy()
    
    # Save the configurations
    _save_configs(_guild_configs)