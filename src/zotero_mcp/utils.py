import os
from typing import List, Dict

def format_creators(creators: List[Dict[str, str]]) -> str:
    """
    Format creator names into a string.
    
    Args:
        creators: List of creator objects from Zotero.
        
    Returns:
        Formatted string with creator names.
    """
    names = []
    for creator in creators:
        if "firstName" in creator and "lastName" in creator:
            names.append(f"{creator['lastName']}, {creator['firstName']}")
        elif "name" in creator:
            names.append(creator["name"])
    return "; ".join(names) if names else "No authors listed"


def is_local_mode() -> bool:
    """
    Check if Zotero MCP is configured for local mode.
    
    Returns:
        True if ZOTERO_LOCAL is set to "true", "yes", or "1", False otherwise.
    """
    return os.getenv("ZOTERO_LOCAL", "").lower() in ["true", "yes", "1"]


def is_remote_mode() -> bool:
    """
    Check if Zotero MCP is configured for remote mode.
    
    Returns:
        True if not in local mode, False otherwise.
    """
    return not is_local_mode()
