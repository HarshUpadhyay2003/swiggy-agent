"""
Centralized Schema Mapping dictionary for menu_items.json fields (Stage 2C).
Maps logical constraint keys to candidate dataset fields.
"""

from typing import Dict, List

FIELD_MAPPING: Dict[str, List[str]] = {
    "cuisine": ["cuisine_type", "secondary_cuisines"],
    "cuisine_type": ["cuisine_type", "secondary_cuisines"],
    "budget": ["price"],
    "max_budget": ["price"],
    "min_budget": ["price"],
    "meal_type": ["meal_type"],
    "taste": ["taste_preference"],
    "taste_preference": ["taste_preference"],
    "diet": ["category", "dietary_safety"],
    "preference": ["category", "dietary_safety"],
    "category": ["parent_category", "category_name"],
    "item_category": ["parent_category", "category_name"],
    "restaurant": ["restaurant_name", "restaurant_code"],
    "restaurant_id": ["restaurant_id", "restaurant_code"],
    "health": ["recommended_for", "health_goal"],
    "health_goal": ["recommended_for", "health_goal"],
    "query_type": ["query_type", "parent_category"],
}
