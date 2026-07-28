"""In-memory cache for loaded Knowledge Base data and indexes."""

from typing import Any, Dict, List, Optional
from app.services.knowledge_base.indexes import KnowledgeBaseIndexes


class KnowledgeBaseCache:
    """Stores loaded Knowledge Base data structures and indexes in memory."""

    def __init__(self) -> None:
        self.restaurants: List[Dict[str, Any]] = []
        self.menu_items: List[Dict[str, Any]] = []
        self.combos: List[Dict[str, Any]] = []
        self.categories: List[Dict[str, Any]] = []
        self.indexes: KnowledgeBaseIndexes = KnowledgeBaseIndexes()
        self.is_loaded: bool = False

    def store(
        self,
        restaurants: List[Dict[str, Any]],
        menu_items: List[Dict[str, Any]],
        combos: List[Dict[str, Any]],
        categories: List[Dict[str, Any]],
        indexes: KnowledgeBaseIndexes,
    ) -> None:
        """Cache loaded datasets and indexes."""
        self.restaurants = restaurants
        self.menu_items = menu_items
        self.combos = combos
        self.categories = categories
        self.indexes = indexes
        self.is_loaded = True

    def clear(self) -> None:
        """Purge stored cache."""
        self.restaurants.clear()
        self.menu_items.clear()
        self.combos.clear()
        self.categories.clear()
        self.indexes.clear()
        self.is_loaded = False
