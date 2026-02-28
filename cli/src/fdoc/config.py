"""fdoc config - Hierarchical .fdocrc configuration loader."""

import os
from pathlib import Path
from typing import Optional

import yaml


DEFAULT_APP_ID = "a04e567f-2621-44c5-8ef6-8ff98893bbe2"


def _find_fdocrc_files() -> list[Path]:
    """Find all .fdocrc files from cwd up to root, plus ~/.fdocrc.

    Returns list ordered from nearest (cwd) to furthest (~/.fdocrc).
    """
    found = []
    current = Path.cwd().resolve()

    # Walk up from cwd to root
    for parent in [current] + list(current.parents):
        rc = parent / ".fdocrc"
        if rc.is_file():
            found.append(rc)

    # Check ~/.fdocrc
    home_rc = Path.home() / ".fdocrc"
    if home_rc.is_file() and home_rc.resolve() not in [f.resolve() for f in found]:
        found.append(home_rc)

    return found


def _load_yaml_file(path: Path) -> dict:
    """Load a YAML file, returning empty dict on failure."""
    try:
        with open(path) as f:
            data = yaml.safe_load(f)
            return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def load_config() -> dict:
    """Load merged config from all .fdocrc files and env vars.

    Nearest .fdocrc wins per key, env vars override everything.
    """
    # Start with defaults
    config = {
        "appsheet_app_id": DEFAULT_APP_ID,
    }

    # Load .fdocrc files in reverse order (furthest first, so nearest overwrites)
    rc_files = _find_fdocrc_files()
    for rc_file in reversed(rc_files):
        data = _load_yaml_file(rc_file)
        config.update(data)

    # Env vars override config
    env_api_key = os.environ.get("FDOC_APPSHEET_API_KEY")
    if env_api_key:
        config["appsheet_api_key"] = env_api_key

    env_app_id = os.environ.get("FDOC_APPSHEET_APP_ID")
    if env_app_id:
        config["appsheet_app_id"] = env_app_id

    return config


def save_fdocrc(path: Path, config: dict):
    """Write config to a .fdocrc file."""
    with open(path / ".fdocrc", "w") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)


def get_appsheet_api_key(config: Optional[dict] = None) -> Optional[str]:
    """Get AppSheet API key from config."""
    if config is None:
        config = load_config()
    return config.get("appsheet_api_key")


def get_appsheet_app_id(config: Optional[dict] = None) -> str:
    """Get AppSheet app ID from config, with default."""
    if config is None:
        config = load_config()
    return config.get("appsheet_app_id", DEFAULT_APP_ID)


def is_sync_enabled(flag: Optional[bool], config: Optional[dict] = None) -> bool:
    """Check if sync is enabled.

    flag=True (--sync): always sync.
    flag=False (--no-sync): never sync.
    flag=None (neither): fall back to sync setting in config.
    """
    if flag is not None:
        return flag
    if config is None:
        config = load_config()
    return config.get("sync", False) is True
