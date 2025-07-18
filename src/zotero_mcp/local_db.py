"""
Local Zotero database reader for semantic search.

Provides direct SQLite access to Zotero's local database for faster semantic search
when running in local mode.
"""

import os
import sqlite3
import platform
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

from .utils import is_local_mode


@dataclass
class ZoteroItem:
    """Represents a Zotero item with text content for semantic search."""
    item_id: int
    key: str
    item_type_id: int
    title: Optional[str] = None
    abstract: Optional[str] = None
    creators: Optional[str] = None
    fulltext: Optional[str] = None
    notes: Optional[str] = None
    extra: Optional[str] = None
    date_added: Optional[str] = None
    date_modified: Optional[str] = None
    
    def get_searchable_text(self) -> str:
        """
        Combine all text fields into a single searchable string.
        
        Returns:
            Combined text content for semantic search indexing.
        """
        parts = []
        
        if self.title:
            parts.append(f"Title: {self.title}")
        
        if self.creators:
            parts.append(f"Authors: {self.creators}")
            
        if self.abstract:
            parts.append(f"Abstract: {self.abstract}")
            
        if self.extra:
            parts.append(f"Extra: {self.extra}")
            
        if self.notes:
            parts.append(f"Notes: {self.notes}")
            
        if self.fulltext:
            # Truncate fulltext to avoid overly long documents
            truncated_fulltext = self.fulltext[:5000] + "..." if len(self.fulltext) > 5000 else self.fulltext
            parts.append(f"Content: {truncated_fulltext}")
            
        return "\n\n".join(parts)


class LocalZoteroReader:
    """
    Direct SQLite reader for Zotero's local database.
    
    Provides fast access to item metadata and fulltext for semantic search
    without going through the Zotero API.
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the local database reader.
        
        Args:
            db_path: Optional path to zotero.sqlite. If None, auto-detect.
        """
        self.db_path = db_path or self._find_zotero_db()
        self._connection: Optional[sqlite3.Connection] = None
        
    def _find_zotero_db(self) -> str:
        """
        Auto-detect the Zotero database location based on OS.
        
        Returns:
            Path to zotero.sqlite file.
            
        Raises:
            FileNotFoundError: If database cannot be located.
        """
        system = platform.system()
        
        if system == "Darwin":  # macOS
            db_path = Path.home() / "Zotero" / "zotero.sqlite"
        elif system == "Windows":
            # Try Windows 7+ location first
            db_path = Path.home() / "Zotero" / "zotero.sqlite"
            if not db_path.exists():
                # Fallback to XP/2000 location
                db_path = Path(os.path.expanduser("~/Documents and Settings")) / os.getenv("USERNAME", "") / "Zotero" / "zotero.sqlite"
        else:  # Linux and others
            db_path = Path.home() / "Zotero" / "zotero.sqlite"
            
        if not db_path.exists():
            raise FileNotFoundError(
                f"Zotero database not found at {db_path}. "
                "Please ensure Zotero is installed and has been run at least once."
            )
            
        return str(db_path)
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection, creating if needed."""
        if self._connection is None:
            # Open in read-only mode for safety
            uri = f"file:{self.db_path}?mode=ro"
            self._connection = sqlite3.connect(uri, uri=True)
            self._connection.row_factory = sqlite3.Row
        return self._connection
    
    def close(self):
        """Close database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def get_item_count(self) -> int:
        """
        Get total count of non-attachment items.
        
        Returns:
            Number of items in the library.
        """
        conn = self._get_connection()
        cursor = conn.execute(
            "SELECT COUNT(*) FROM items WHERE itemTypeID != 14"  # 14 = attachment
        )
        return cursor.fetchone()[0]
    
    def get_items_with_text(self, limit: Optional[int] = None) -> List[ZoteroItem]:
        """
        Get all items with their text content for semantic search.
        
        Args:
            limit: Optional limit on number of items to return.
            
        Returns:
            List of ZoteroItem objects with text content.
        """
        conn = self._get_connection()
        
        # Query to get items with their text content (simplified for now)
        query = """
        SELECT 
            i.itemID,
            i.key,
            i.itemTypeID,
            i.dateAdded,
            i.dateModified,
            title_val.value as title,
            abstract_val.value as abstract,
            extra_val.value as extra,
            GROUP_CONCAT(n.note, ' ') as notes,
            GROUP_CONCAT(
                CASE 
                    WHEN c.firstName IS NOT NULL AND c.lastName IS NOT NULL 
                    THEN c.lastName || ', ' || c.firstName
                    WHEN c.lastName IS NOT NULL 
                    THEN c.lastName
                    ELSE NULL
                END, '; '
            ) as creators
        FROM items i
        
        -- Get title
        LEFT JOIN itemData title_data ON i.itemID = title_data.itemID AND title_data.fieldID = 1
        LEFT JOIN itemDataValues title_val ON title_data.valueID = title_val.valueID
        
        -- Get abstract  
        LEFT JOIN itemData abstract_data ON i.itemID = abstract_data.itemID AND abstract_data.fieldID = 2
        LEFT JOIN itemDataValues abstract_val ON abstract_data.valueID = abstract_val.valueID
        
        -- Get extra field
        LEFT JOIN itemData extra_data ON i.itemID = extra_data.itemID AND extra_data.fieldID = 16
        LEFT JOIN itemDataValues extra_val ON extra_data.valueID = extra_val.valueID
        
        -- Get notes
        LEFT JOIN itemNotes n ON i.itemID = n.parentItemID OR i.itemID = n.itemID
        
        -- Get creators
        LEFT JOIN itemCreators ic ON i.itemID = ic.itemID
        LEFT JOIN creators c ON ic.creatorID = c.creatorID
        
        WHERE i.itemTypeID != 14  -- Exclude attachments
        
        GROUP BY i.itemID, i.key, i.itemTypeID, i.dateAdded, i.dateModified,
                 title_val.value, abstract_val.value, extra_val.value
        
        ORDER BY i.dateModified DESC
        """
        
        if limit:
            query += f" LIMIT {limit}"
        
        cursor = conn.execute(query)
        items = []
        
        for row in cursor:
            item = ZoteroItem(
                item_id=row['itemID'],
                key=row['key'],
                item_type_id=row['itemTypeID'],
                title=row['title'],
                abstract=row['abstract'],
                creators=row['creators'],
                fulltext=None,  # TODO: Implement fulltext extraction
                notes=row['notes'],
                extra=row['extra'],
                date_added=row['dateAdded'],
                date_modified=row['dateModified']
            )
            items.append(item)
            
        return items
    
    def get_item_by_key(self, key: str) -> Optional[ZoteroItem]:
        """
        Get a specific item by its Zotero key.
        
        Args:
            key: The Zotero item key.
            
        Returns:
            ZoteroItem if found, None otherwise.
        """
        items = self.get_items_with_text()
        for item in items:
            if item.key == key:
                return item
        return None
    
    def search_items_by_text(self, query: str, limit: int = 50) -> List[ZoteroItem]:
        """
        Simple text search through item content.
        
        Args:
            query: Search query string.
            limit: Maximum number of results.
            
        Returns:
            List of matching ZoteroItem objects.
        """
        items = self.get_items_with_text()
        matching_items = []
        
        query_lower = query.lower()
        
        for item in items:
            searchable_text = item.get_searchable_text().lower()
            if query_lower in searchable_text:
                matching_items.append(item)
                if len(matching_items) >= limit:
                    break
                    
        return matching_items


def get_local_zotero_reader() -> Optional[LocalZoteroReader]:
    """
    Get a LocalZoteroReader instance if in local mode.
    
    Returns:
        LocalZoteroReader instance if in local mode and database exists,
        None otherwise.
    """
    if not is_local_mode():
        return None
        
    try:
        return LocalZoteroReader()
    except FileNotFoundError:
        return None


def is_local_db_available() -> bool:
    """
    Check if local Zotero database is available.
    
    Returns:
        True if local database can be accessed, False otherwise.
    """
    reader = get_local_zotero_reader()
    if reader:
        reader.close()
        return True
    return False