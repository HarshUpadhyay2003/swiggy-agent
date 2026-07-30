import json
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from app.services.knowledge_base.knowledge_base_service import KnowledgeBaseService
    from app.services.catalog.catalog_adapter import CatalogAdapter
except ImportError:
    from .knowledge_base.knowledge_base_service import KnowledgeBaseService
    from .catalog.catalog_adapter import CatalogAdapter


class CatalogService:
    """Service layer for querying food catalog data backed by Knowledge Base V3.3."""

    def __init__(self, catalog_path: Optional[str] = None, kb_service: Optional[KnowledgeBaseService] = None) -> None:
        if kb_service:
            self.kb_service = kb_service
        else:
            base_dir = Path(catalog_path).resolve().parent if catalog_path else None
            self.kb_service = KnowledgeBaseService(base_dir=str(base_dir) if base_dir else None)

        self._flattened_menu = self._flatten_menu_items()

    def _flatten_menu_items(self) -> List[Dict[str, Any]]:
        """Flatten Knowledge Base menu items into legacy item records with restaurant context."""
        flattened: List[Dict[str, Any]] = []
        for item in self.kb_service.get_all_menu_items():
            restaurant = self.kb_service.get_restaurant(item.get("restaurant_id", 0))
            legacy_item = CatalogAdapter.to_legacy_item(item, restaurant)
            flattened.append(legacy_item)
        return flattened

    def _normalize_str(self, value: str) -> str:
        return value.strip().lower()

    def _filter_items(
        self,
        available_only: bool = True,
        **criteria: Any,
    ) -> List[Dict[str, Any]]:
        """Filter flattened menu items by arbitrary criteria."""
        items = self._flattened_menu

        if available_only:
            items = [item for item in items if item.get("available") is True]

        for key, expected in criteria.items():
            if isinstance(expected, str):
                normalized_expected = self._normalize_str(expected)
                items = [
                    item
                    for item in items
                    if self._normalize_str(str(item.get(key, ""))) == normalized_expected
                ]
            else:
                items = [item for item in items if item.get(key) == expected]

        return items

    def get_all_restaurants(self) -> List[Dict[str, Any]]:
        """Return all restaurants in legacy catalog format."""
        legacy_restaurants = []
        for restaurant in self.kb_service.get_all_restaurants():
            rid = restaurant.get("restaurant_id", 0)
            kb_items = self.kb_service.get_items_for_restaurant(rid)
            legacy_items = [CatalogAdapter.to_legacy_item(it, restaurant) for it in kb_items]
            legacy_restaurants.append(CatalogAdapter.to_legacy_restaurant(restaurant, legacy_items))
        return legacy_restaurants

    def get_available_items(self) -> List[Dict[str, Any]]:
        """Return all currently available menu items."""
        return self._filter_items(available_only=True)

    def get_available_combos(self) -> List[Dict[str, Any]]:
        """Return all active combo bundles from Knowledge Base."""
        combos = []
        for combo in self.kb_service.get_all_combos():
            rid = combo.get("restaurant_id", 0)
            restaurant = self.kb_service.get_restaurant(rid) or {}
            combos.append({
                "combo_id": combo.get("combo_id"),
                "combo_code": combo.get("combo_code"),
                "name": combo.get("combo_name"),
                "description": combo.get("description", ""),
                "price": combo.get("discounted_price", combo.get("price", 0)),
                "original_price": combo.get("price", 0),
                "savings_amount": combo.get("savings_amount", 0),
                "restaurant_id": rid,
                "restaurant_name": restaurant.get("name", combo.get("restaurant_code", "")),
                "cuisine": restaurant.get("primary_cuisine", ""),
                "secondary_cuisines": restaurant.get("secondary_cuisines", []),
                "category": "veg" if "veg" in combo.get("combo_name", "").lower() else "non-veg",
                "meal_type": "lunch",
                "available": True,
                "is_combo": True,
                "raw_combo": combo,
            })
        return combos

    def get_budget_meals(self, max_price: int) -> List[Dict[str, Any]]:
        """Return available items priced at or below max_price."""
        return [
            item
            for item in self.get_available_items()
            if isinstance(item.get("price"), (int, float)) and item["price"] <= max_price
        ]

    def get_healthy_items(self) -> List[Dict[str, Any]]:
        """Return available items marked as healthy."""
        return self._filter_items(available_only=True, healthy=True)

    def get_items_by_preference(self, preference: str) -> List[Dict[str, Any]]:
        """Return available items matching the veg/non-veg preference."""
        normalized = self._normalize_str(preference)
        if normalized not in {"veg", "non-veg", "nonveg", "non veg"}:
            raise ValueError("preference must be 'veg' or 'non-veg'")

        if normalized in {"nonveg", "non veg"}:
            normalized = "non-veg"

        return self._filter_items(available_only=True, category=normalized)

    def get_items_by_meal_type(self, meal_type: str) -> List[Dict[str, Any]]:
        """Return available items by meal type."""
        normalized = self._normalize_str(meal_type)
        supported = {"breakfast", "lunch", "dinner", "snacks"}
        if normalized not in supported:
            raise ValueError(f"meal_type must be one of {sorted(supported)}")

        return self._filter_items(available_only=True, meal_type=normalized)

    def get_restaurants_by_cuisine(self, cuisine: str) -> List[Dict[str, Any]]:
        """Return restaurants matching the given cuisine."""
        normalized = self._normalize_str(cuisine)
        return [
            restaurant
            for restaurant in self.get_all_restaurants()
            if self._normalize_str(restaurant.get("cuisine", "")) == normalized
        ]

    def search_items(self, keyword: str) -> List[Dict[str, Any]]:
        """Return available items whose name, category, or search_aliases match the keyword."""
        normalized_keyword = self._normalize_str(keyword)
        
        # Check direct O(1) search alias matches from KB
        alias_matches = self.kb_service.search_alias(normalized_keyword)
        alias_item_ids = {it.get("item_id") for it in alias_matches}

        return [
            item
            for item in self.get_available_items()
            if normalized_keyword in self._normalize_str(item.get("name", ""))
            or normalized_keyword in self._normalize_str(item.get("category", ""))
            or normalized_keyword in self._normalize_str(item.get("meal_type", ""))
            or normalized_keyword in self._normalize_str(item.get("cuisine", ""))
            or item.get("item_id") in alias_item_ids
        ]

    def get_item_by_id(self, item_id: int) -> Dict[str, Any]:
        """Return item details and restaurant context for a given item_id."""
        for item in self._flattened_menu:
            if item.get("item_id") == item_id:
                return item

        raise ValueError(f"Item not found for item_id={item_id}")

    def get_recommended_items(
        self,
        healthy_only: bool = False,
        max_price: Optional[int] = None,
        preference: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Return recommended items using combined filters."""
        items = self.get_available_items()

        if healthy_only:
            items = [item for item in items if item.get("healthy") is True]

        if max_price is not None:
            items = [
                item
                for item in items
                if isinstance(item.get("price"), (int, float)) and item["price"] <= max_price
            ]

        if preference:
            normalized = self._normalize_str(preference)
            if normalized in {"nonveg", "non veg"}:
                normalized = "non-veg"
            if normalized not in {"veg", "non-veg"}:
                raise ValueError("preference must be 'veg' or 'non-veg'")
            items = [item for item in items if self._normalize_str(item.get("category", "")) == normalized]

        return items


if __name__ == "__main__":
    service = CatalogService()

    healthy_items = service.get_healthy_items()
    budget_meals = service.get_budget_meals(max_price=150)
    veg_items = service.get_items_by_preference("veg")
    search_results = service.search_items("burger")

    print(f"Healthy Items ({len(healthy_items)}):", [i["name"] for i in healthy_items[:3]])
    print(f"Budget Meals <=150 ({len(budget_meals)}):", [i["name"] for i in budget_meals[:3]])
    print(f"Veg Items ({len(veg_items)}):", [i["name"] for i in veg_items[:3]])
    print(f"Search Results for 'burger' ({len(search_results)}):", [i["name"] for i in search_results[:3]])
