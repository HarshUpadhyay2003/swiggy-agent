"""
Stage 4F Semantic Profile Resolver Module.
Defines reusable dataset-attribute-driven SemanticProfile structures.
Maps request intent to primary, secondary, and forbidden semantic domains,
required contexts, and minimum semantic quality thresholds without hardcoding product names.
"""

from typing import Any, Dict, List, Optional, Set
from pydantic import BaseModel, Field


class SemanticProfile(BaseModel):
    """Dataset-attribute-driven semantic domain profile."""

    profile_name: str
    primary_domains: Set[str] = Field(default_factory=set)
    secondary_domains: Set[str] = Field(default_factory=set)
    forbidden_domains: Set[str] = Field(default_factory=set)
    required_context: Dict[str, str] = Field(default_factory=dict)
    optional_context: Dict[str, str] = Field(default_factory=dict)
    minimum_semantic_score: float = 0.70
    minimum_suitability_score: float = 0.60


class SemanticProfileResolver:
    """Resolves semantic domain profiles based on dataset metadata attributes."""

    PROFILES: Dict[str, SemanticProfile] = {
        "coffee": SemanticProfile(
            profile_name="Coffee & Cafe Profile",
            primary_domains={"beverage", "beverages", "coffee", "cafe", "cold coffee", "espresso", "latte"},
            secondary_domains={"milkshake", "tea", "bakery", "snack"},
            forbidden_domains={"pizza", "burger", "burgers", "meal", "meals", "rice bowl", "thali", "curry", "main course"},
            minimum_semantic_score=0.85,
            minimum_suitability_score=0.80,
        ),
        "dessert": SemanticProfile(
            profile_name="Dessert & Sweet Profile",
            primary_domains={"dessert", "desserts", "cake", "ice cream", "sundae", "pastry", "sweet", "waffle"},
            secondary_domains={"beverage", "shake", "bakery"},
            forbidden_domains={"pizza", "burger", "burgers", "meal", "meals", "biryani", "curry", "salad"},
            minimum_semantic_score=0.80,
            minimum_suitability_score=0.75,
        ),
        "healthy": SemanticProfile(
            profile_name="Healthy & Fitness Profile",
            primary_domains={"healthy", "salad", "grain bowl", "protein bowl", "soup", "smoothie"},
            secondary_domains={"grilled chicken", "wrap", "sub", "oats"},
            forbidden_domains={"deep fried", "dessert", "desserts", "soft drink", "large burger", "junk food", "heavy curry"},
            required_context={"healthy": "true"},
            minimum_semantic_score=0.75,
            minimum_suitability_score=0.70,
        ),
        "italian": SemanticProfile(
            profile_name="Italian Cuisine Profile",
            primary_domains={"italian", "pizza", "pizzas", "pasta", "garlic bread", "risotto"},
            secondary_domains={"beverage", "salad", "dessert"},
            forbidden_domains={"biryani", "thali", "dosa", "tacos", "chinese", "noodle", "curry"},
            minimum_semantic_score=0.75,
            minimum_suitability_score=0.70,
        ),
        "indian": SemanticProfile(
            profile_name="Indian Cuisine Profile",
            primary_domains={"indian", "thali", "curry", "paneer", "biryani", "naan", "dal", "tikka"},
            secondary_domains={"beverage", "dessert", "bread"},
            forbidden_domains={"pizza", "pasta", "burger", "burgers", "tacos", "chinese"},
            minimum_semantic_score=0.75,
            minimum_suitability_score=0.70,
        ),
        "beverage": SemanticProfile(
            profile_name="Beverages Profile",
            primary_domains={"beverage", "beverages", "drink", "drinks", "juice", "soda", "coffee", "tea", "shake"},
            secondary_domains={"dessert", "snack"},
            forbidden_domains={"pizza", "burger", "burgers", "meal", "meals", "curry"},
            minimum_semantic_score=0.80,
            minimum_suitability_score=0.75,
        ),
        "pizza": SemanticProfile(
            profile_name="Pizza Domain Profile",
            primary_domains={"pizza", "pizzas", "garlic bread", "calzone"},
            secondary_domains={"beverage", "dessert", "pasta"},
            forbidden_domains={"burger", "burgers", "biryani", "curry", "thali", "tacos", "soup"},
            minimum_semantic_score=0.80,
            minimum_suitability_score=0.75,
        ),
        "breakfast": SemanticProfile(
            profile_name="Breakfast Meal Profile",
            primary_domains={"breakfast", "mcmuffin", "hash brown", "pancake", "hotcakes", "toast", "oats", "paratha"},
            secondary_domains={"coffee", "tea", "juice", "beverage"},
            forbidden_domains={"dinner", "heavy curry", "biryani", "pizza", "thali"},
            required_context={"meal_type": "breakfast"},
            minimum_semantic_score=0.75,
            minimum_suitability_score=0.70,
        ),
        "standard": SemanticProfile(
            profile_name="Standard Food Profile",
            primary_domains=set(),
            secondary_domains=set(),
            forbidden_domains=set(),
            minimum_semantic_score=0.50,
            minimum_suitability_score=0.50,
        ),
    }

    def resolve_profile(self, query_text: str, constraints: List[Any]) -> SemanticProfile:
        q_lower = (query_text or "").lower()
        c_terms = [str(c.value).lower() for c in constraints]
        all_text = " ".join([q_lower] + c_terms)

        if "coffee" in all_text:
            return self.PROFILES["coffee"]
        if "dessert" in all_text or "cake" in all_text or "ice cream" in all_text:
            return self.PROFILES["dessert"]
        if "healthy" in all_text or "fit" in all_text or "salad" in all_text:
            return self.PROFILES["healthy"]
        if "pizza" in all_text:
            return self.PROFILES["pizza"]
        if "italian" in all_text:
            return self.PROFILES["italian"]
        if "indian" in all_text:
            return self.PROFILES["indian"]
        if "breakfast" in all_text:
            return self.PROFILES["breakfast"]
        if "beverage" in all_text or "drink" in all_text:
            return self.PROFILES["beverage"]

        return self.PROFILES["standard"]
