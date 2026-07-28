"""KnowledgeBaseService orchestrator for Knowledge Base V3.3 dataset access."""

from typing import Any, Dict, List, Optional
from app.services.knowledge_base.cache import KnowledgeBaseCache
from app.services.knowledge_base.indexes import KnowledgeBaseIndexes
from app.services.knowledge_base.json_loader import KnowledgeBaseJSONLoader
from app.services.knowledge_base.validators import KnowledgeBaseValidator


class KnowledgeBaseService:
    """Orchestrates JSON loading, validation, indexing, and cached lookup for KB V3.3."""

    def __init__(self, base_dir: Optional[str] = None, auto_load: bool = True) -> None:
        self.loader = KnowledgeBaseJSONLoader(base_dir=base_dir)
        self.validator = KnowledgeBaseValidator()
        self.cache = KnowledgeBaseCache()

        if auto_load:
            self.load()

    def load(self) -> None:
        """Load datasets from disk, perform validation, build indexes, and cache."""
        restaurants = self.loader.load_restaurants()
        menu_items = self.loader.load_menu_items()
        combos = self.loader.load_combos()
        categories = self.loader.load_category_registry()

        # Perform strict validation
        self.validator.validate_all(restaurants, menu_items, combos, categories)

        # Build indexes
        indexes = KnowledgeBaseIndexes()
        indexes.build_indexes(restaurants, menu_items, combos, categories)

        # Cache in memory
        self.cache.store(restaurants, menu_items, combos, categories, indexes)

    def reload(self) -> None:
        """Reload datasets from disk and rebuild cache/indexes."""
        self.cache.clear()
        self.load()

    def get_restaurant(self, restaurant_id: int) -> Optional[Dict[str, Any]]:
        """Fetch a restaurant by integer ID in O(1)."""
        return self.cache.indexes.restaurant_by_id.get(restaurant_id)

    def get_restaurant_by_code(self, restaurant_code: str) -> Optional[Dict[str, Any]]:
        """Fetch a restaurant by uppercase code (e.g. 'MCD', 'KFC') in O(1)."""
        return self.cache.indexes.restaurant_by_code.get(restaurant_code.upper())

    def get_all_restaurants(self) -> List[Dict[str, Any]]:
        """Return raw list of all restaurants."""
        return self.cache.restaurants

    def get_item(self, item_id: int) -> Optional[Dict[str, Any]]:
        """Fetch a menu item by integer ID in O(1)."""
        return self.cache.indexes.item_by_id.get(item_id)

    def get_item_by_code(self, item_code: str) -> Optional[Dict[str, Any]]:
        """Fetch a menu item by code (e.g. 'MCD_BURGER_001') in O(1)."""
        return self.cache.indexes.item_by_code.get(item_code.upper())

    def get_all_menu_items(self) -> List[Dict[str, Any]]:
        """Return raw list of all menu items."""
        return self.cache.menu_items

    def get_items_for_restaurant(self, restaurant_id: int) -> List[Dict[str, Any]]:
        """Return all menu items belonging to a restaurant in O(1)."""
        return self.cache.indexes.restaurant_to_items.get(restaurant_id, [])

    def get_items_for_category(self, category_id: str) -> List[Dict[str, Any]]:
        """Return all menu items belonging to a category_id in O(1)."""
        return self.cache.indexes.category_to_items.get(category_id.upper(), [])

    def get_combo(self, combo_id: int) -> Optional[Dict[str, Any]]:
        """Fetch a combo by integer ID in O(1)."""
        return self.cache.indexes.combo_by_id.get(combo_id)

    def get_all_combos(self) -> List[Dict[str, Any]]:
        """Return raw list of all combos."""
        return self.cache.combos

    def get_all_categories(self) -> List[Dict[str, Any]]:
        """Return raw list of all categories."""
        return self.cache.categories

    def search_alias(self, alias: str) -> List[Dict[str, Any]]:
        """Search items matching a search alias in O(1)."""
        return self.cache.indexes.alias_index.get(alias.strip().lower(), [])

    def get_statistics(self) -> Dict[str, Any]:
        """Return metadata & coverage statistics of loaded Knowledge Base."""
        return {
            "is_loaded": self.cache.is_loaded,
            "total_restaurants": len(self.cache.restaurants),
            "total_menu_items": len(self.cache.menu_items),
            "total_combos": len(self.cache.combos),
            "total_categories": len(self.cache.categories),
            "total_search_aliases": len(self.cache.indexes.alias_index),
        }
