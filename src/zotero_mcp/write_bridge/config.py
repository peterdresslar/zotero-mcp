from __future__ import annotations

import json
from pathlib import Path
from typing import Optional


def get_config_path() -> Path:
    """Return the semantic search config path used by zotero-mcp.

    Currently: ~/.config/zotero-mcp/config.json
    """
    return Path.home() / ".config" / "zotero-mcp" / "config.json"


def _load_config(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def _save_config(path: Path, cfg: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(cfg, indent=2))


def get_bridge_token(path: Optional[Path] = None) -> Optional[str]:
    """Read the write-bridge shared secret from config, if present."""
    path = path or get_config_path()
    cfg = _load_config(path)
    return cfg.get("semantic_search", {}).get("write", {}).get("token")


def set_bridge_token(token: str, path: Optional[Path] = None) -> None:
    """Persist the write-bridge shared secret to config."""
    path = path or get_config_path()
    cfg = _load_config(path)
    if "semantic_search" not in cfg:
        cfg["semantic_search"] = {}
    if "write" not in cfg["semantic_search"]:
        cfg["semantic_search"]["write"] = {}
    cfg["semantic_search"]["write"]["token"] = token
    _save_config(path, cfg)


def get_bridge_endpoint() -> str:
    """Return the default loopback endpoint base for the Zotero plugin."""
    return "http://127.0.0.1:23119/zotero-mcp/v1"
