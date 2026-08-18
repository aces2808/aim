import configparser
import os
from typing import Dict, Any, Union


def load_config() -> configparser.ConfigParser:
    """Load and return the configuration from config.ini"""
    config = configparser.ConfigParser()
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.ini")
    config.read(config_path)
    return config


def _infer_type(value: str) -> Union[str, int, float, bool]:
    """
    Infer the type of a configuration value and convert it accordingly.

    Args:
        value: String value from config file

    Returns:
        Converted value with appropriate type (str, int, float, or bool)
    """
    # Try boolean
    if value.lower() in ("true", "false", "yes", "no"):
        return value.lower() in ("true", "yes")

    # Try integer
    try:
        return int(value)
    except ValueError:
        pass

    # Try float
    try:
        return float(value)
    except ValueError:
        pass

    # Default to string
    return value


def section(config: configparser.ConfigParser, name: str) -> Dict[str, Any]:
    """
    Extract all configuration from a specific section with type inference.

    Args:
        config: ConfigParser instance
        name: Section name to extract

    Returns:
        Dictionary with all key-value pairs from the section with inferred types
    """
    if not config.has_section(name):
        return {}

    return {key: _infer_type(value) for key, value in config.items(name)}


def all_sections(config: configparser.ConfigParser, include_default: bool = True) -> Dict[str, Dict[str, Any]]:
    """
    Extract all configuration sections as nested dictionaries with type inference.

    Args:
        config: ConfigParser instance
        include_default: Whether to include the DEFAULT section

    Returns:
        Nested dictionary with all sections and their key-value pairs
    """
    result = {}

    for section_name in config.sections():
        result[section_name] = section(config, section_name)

    # Optionally include DEFAULT section
    if include_default and config.defaults():
        result["DEFAULT"] = {key: _infer_type(value) for key, value in config.defaults().items()}

    return result


def config(path: str = None) -> Dict[str, Dict[str, Any]]:
    """
    Load configuration from file and return all sections as nested dictionary.

    This is the recommended way to load configuration - single function call.

    Args:
        path: Optional custom path to config.ini file

    Returns:
        Nested dictionary with all sections and their key-value pairs
    """
    if path:
        cfg = configparser.ConfigParser()
        cfg.read(path)
        return all_sections(cfg)

    return all_sections(load_config())


def get_project_env(project_name: str = "epocket", environment: str = "dev") -> str:
    """
    Get the project environment string from config or use defaults.

    Convention: {project_name}-{environment}

    Args:
        project_name: Default project name if not in config
        environment: Default environment if not in config

    Returns:
        Project environment string (e.g., "epocket-dev")
    """
    cfg = config()
    proj = cfg.get("DEFAULT", {}).get("project_name", project_name)
    env = cfg.get("DEFAULT", {}).get("environment", environment)
    return f"{proj}-{env}"


# Public API
__all__ = [
    "config",  # Recommended: Single function to load all config
    "load_config",  # Load raw ConfigParser
    "section",  # Extract single section
    "all_sections",  # Extract all sections
    "get_project_env",  # Get project environment string
]
