import json
from pathlib import Path
from typing import Any, Dict, List, Optional


class CatalogService:
    """Service layer for querying food catalog data."""

    def __init__(self, catalog_path: Optional[str] = None) -> None:
        self.catalog_path = (
            Path(catalog_path).resolve()
            if catalog_path
            else Path(__file__).resolve().parents[2] / "data" / "mock_catalog.json"
        )
        self.catalog = self._load_catalog()
        self._flattened_menu = self._flatten_menu_items()

    def _load_catalog(self) -> List[Dict[str, Any]]:
        """Load restaurant catalog from JSON file."""
        if not self.catalog_path.exists():
            raise FileNotFoundError(f"Catalog file not found: {self.catalog_path}")

        with self.catalog_path.open("r", encoding="utf-8") as catalog_file:
            return json.load(catalog_file)

    def _flatten_menu_items(self) -> List[Dict[str, Any]]:
        """Flatten restaurant menus into item records with restaurant context."""
        flattened: List[Dict[str, Any]] = []
        for restaurant in self.catalog:
            restaurant_name = restaurant.get("name")
            cuisine = restaurant.get("cuisine")
            restaurant_id = restaurant.get("restaurant_id")
            for item in restaurant.get("menu", []):
                flattened.append(
                    {
                        **item,
                        "restaurant_id": restaurant_id,
                        "restaurant_name": restaurant_name,
                        "cuisine": cuisine,
                    }
                )
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
        """Return all restaurants in the catalog."""
        return self.catalog

    def get_available_items(self) -> List[Dict[str, Any]]:
        """Return all currently available menu items."""
        return self._filter_items(available_only=True)

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

        if normalized == "nonveg":
            normalized = "non-veg"
        if normalized == "non veg":
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
            for restaurant in self.catalog
            if self._normalize_str(restaurant.get("cuisine", "")) == normalized
        ]

    def search_items(self, keyword: str) -> List[Dict[str, Any]]:
        """Return available items whose name or category matches the keyword."""
        normalized_keyword = self._normalize_str(keyword)
        return [
            item
            for item in self.get_available_items()
            if normalized_keyword in self._normalize_str(item.get("name", ""))
            or normalized_keyword in self._normalize_str(item.get("category", ""))
            or normalized_keyword in self._normalize_str(item.get("meal_type", ""))
            or normalized_keyword in self._normalize_str(item.get("cuisine", ""))
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


def _print_section(title: str, data: List[Dict[str, Any]], limit: int = 5) -> None:
    print(f"\n=== {title} ({len(data)} results) ===")
    for item in data[:limit]:
        print(json.dumps(item, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    service = CatalogService()

    healthy_items = service.get_healthy_items()
    budget_meals = service.get_budget_meals(max_price=150)
    veg_items = service.get_items_by_preference("veg")
    search_results = service.search_items("burger")

    _print_section("Healthy Items", healthy_items)
    _print_section("Budget Meals (<= 150)", budget_meals)
    _print_section("Veg Items", veg_items)
    _print_section("Search Results for 'burger'", search_results)
