"""CatalogAdapter translates KB V3.3 rich entities into legacy CatalogService data contracts."""

from typing import Any, Dict, List, Optional


class CatalogAdapter:
    """Pure field mapper translating Knowledge Base V3.3 structures into legacy catalog dictionaries."""

    @staticmethod
    def to_legacy_item(
        item: Dict[str, Any],
        restaurant: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Map a KB V3.3 menu item entity into a legacy catalog item dictionary.
        
        Legacy callers expect:
        - item_id (int)
        - name (str)
        - price (int/float)
        - available (bool)
        - category (str: 'veg' or 'non-veg')
        - meal_type (str)
        - healthy (bool)
        - vegetarian (bool)
        - high_protein (bool)
        - spicy (bool)
        - vegan (bool)
        - low_calorie (bool)
        - gluten_free (bool)
        - restaurant_id (int)
        - restaurant_name (str)
        - cuisine (str)
        """
        dietary = item.get("dietary_safety", {})
        is_veg = bool(dietary.get("is_veg", False))
        category_str = "veg" if is_veg else "non-veg"

        health_scores = item.get("health_scores", {})
        overall_health_score = health_scores.get("overall_health_score", 0.0)
        is_healthy = bool(overall_health_score >= 6.0)

        nutrition = item.get("nutrition", {})
        macros = nutrition.get("macronutrients", {})
        protein_g = macros.get("protein_g", 0.0)
        calories_kcal = macros.get("calories_kcal", 0.0)
        is_high_protein = bool(protein_g >= 15.0)
        is_low_calorie = bool(calories_kcal <= 350.0)

        mood_sensory = item.get("mood_sensory", {})
        is_spicy = bool(mood_sensory.get("spicy", False))

        # Resolve restaurant name and cuisine
        rest_name = ""
        cuisine_str = ""
        if restaurant:
            rest_name = restaurant.get("name", "")
            cuisine_str = restaurant.get("primary_cuisine", "")

        commerce = item.get("commerce_intelligence", {})
        price = commerce.get("price", item.get("price", 0))

        return {
            "item_id": item.get("item_id"),
            "name": item.get("name", ""),
            "description": item.get("description", ""),
            "price": int(price),
            "available": bool(item.get("available", True)),
            "category": category_str,
            "meal_type": str(item.get("meal_type", "")).lower(),
            "healthy": is_healthy,
            "vegetarian": is_veg,
            "high_protein": is_high_protein,
            "spicy": is_spicy,
            "vegan": bool(dietary.get("is_vegan", False)),
            "low_calorie": is_low_calorie,
            "gluten_free": bool(dietary.get("is_gluten_free", False)),
            "restaurant_id": item.get("restaurant_id"),
            "restaurant_name": rest_name,
            "cuisine": cuisine_str,
            "cuisine_type": item.get("cuisine_type", cuisine_str),
            "taste_preference": item.get("taste_preference", ""),
            "category_intelligence": item.get("category_intelligence", {}),
            "parent_category": item.get("category_intelligence", {}).get("parent_category", ""),
            "secondary_cuisines": restaurant.get("secondary_cuisines", []) if restaurant else [],
            "nutrition": nutrition,
            "health_scores": health_scores,
            "dietary_safety": dietary,
        }

    @staticmethod
    def to_legacy_restaurant(
        restaurant: Dict[str, Any],
        legacy_items: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Map a KB V3.3 restaurant entity into a legacy restaurant dictionary.
        
        Legacy callers (e.g. OrderService) expect:
        - restaurant_id (int)
        - name (str)
        - cuisine (str)
        - rating (float)
        - delivery_time (int) -> mapped from delivery_time_mins
        - menu (List of legacy_items)
        """
        return {
            "restaurant_id": restaurant.get("restaurant_id"),
            "name": restaurant.get("name", ""),
            "cuisine": restaurant.get("primary_cuisine", ""),
            "rating": float(restaurant.get("rating", 0.0)),
            "delivery_time": int(restaurant.get("delivery_time_mins", 30)),
            "menu": legacy_items,
        }
