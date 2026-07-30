"""Candidate Retriever applying generalized polymorphic constraint filters."""

from typing import Any, Callable, Dict, List, Tuple
from app.services.catalog_service import CatalogService
from app.services.recommendation_engine.models import (
    Constraint,
    RecommendationCandidate,
    RecommendationRequest,
)


class CandidateRetriever:
    """Retrieves menu items & combos and filters candidates by evaluating constraints polymorphically."""

    def __init__(self, catalog_service: CatalogService) -> None:
        self.catalog_service = catalog_service
        self._handlers: Dict[str, Callable[[RecommendationCandidate, Any], bool]] = {
            "budget": self._filter_budget,
            "max_budget": self._filter_max_budget,
            "min_budget": self._filter_min_budget,
            "preference": self._filter_diet,
            "diet": self._filter_diet,
            "meal_type": self._filter_meal_type,
            "health_goal": self._filter_health_goal,
            "healthy_only": self._filter_health_goal,
            "healthy": self._filter_health_goal,
            "restaurant_id": self._filter_restaurant_id,
            "spicy": self._filter_spicy,
            "vegan": self._filter_vegan,
            "gluten_free": self._filter_gluten_free,
            "high_protein": self._filter_high_protein,
            "cuisine": self._filter_cuisine,
            "cuisine_type": self._filter_cuisine,
            "taste": self._filter_taste,
            "taste_preference": self._filter_taste,
            "category": self._filter_item_category,
            "item_category": self._filter_item_category,
            "is_combo": self._filter_is_combo,
            "serving": self._filter_serving,
        }

    def retrieve_candidates(
        self, request: RecommendationRequest
    ) -> Tuple[List[RecommendationCandidate], Dict[str, int]]:
        """
        Fetch available catalog menu items and combo bundles, iterate through constraints,
        and return candidates alongside per-stage candidate count telemetry.
        """
        raw_items = self.catalog_service.get_available_items()
        raw_combos = self.catalog_service.get_available_combos()

        candidates = [self._map_to_candidate(raw) for raw in raw_items]
        candidates.extend([self._map_combo_to_candidate(combo) for combo in raw_combos])

        counts_debug: Dict[str, int] = {"initial_candidates": len(candidates)}

        for constraint in request.constraints:
            if not constraint.is_hard:
                continue

            handler = self._handlers.get(constraint.type)
            if handler:
                filtered = [c for c in candidates if handler(c, constraint.value)]
                # Keep filtered if non-empty, otherwise retain candidates to allow soft ranking scoring
                if filtered:
                    candidates = filtered
                counts_debug[f"remaining_after_{constraint.type}"] = len(candidates)

        return candidates, counts_debug

    def _map_to_candidate(self, raw: Dict[str, Any]) -> RecommendationCandidate:
        """Map catalog item dictionary to RecommendationCandidate model."""
        cat_intel = raw.get("category_intelligence", {}) if isinstance(raw.get("category_intelligence"), dict) else {}
        parent_cat = str(cat_intel.get("parent_category", "")) if cat_intel else ""

        return RecommendationCandidate(
            item_id=int(raw.get("item_id", 0)),
            name=str(raw.get("name", "")),
            description=str(raw.get("description", "")),
            price=int(raw.get("price", 0)),
            available=bool(raw.get("available", True)),
            category=str(raw.get("category", "")).lower(),
            meal_type=str(raw.get("meal_type", "")).lower(),
            healthy=bool(raw.get("healthy", False)),
            vegetarian=bool(raw.get("vegetarian", True)),
            high_protein=bool(raw.get("high_protein", False)),
            spicy=bool(raw.get("spicy", False)),
            vegan=bool(raw.get("vegan", False)),
            low_calorie=bool(raw.get("low_calorie", False)),
            gluten_free=bool(raw.get("gluten_free", False)),
            restaurant_id=raw.get("restaurant_id"),
            restaurant_name=str(raw.get("restaurant_name", "")),
            cuisine=str(raw.get("cuisine", "")),
            cuisine_type=str(raw.get("cuisine_type", raw.get("cuisine", ""))),
            taste_preference=str(raw.get("taste_preference", "")),
            parent_category=parent_cat,
            is_combo=False,
            raw_item=raw,
        )

    def _map_combo_to_candidate(self, raw: Dict[str, Any]) -> RecommendationCandidate:
        """Map combo dictionary to RecommendationCandidate model."""
        return RecommendationCandidate(
            item_id=int(raw.get("combo_id", 0)),
            name=str(raw.get("name", "")),
            description=str(raw.get("description", "")),
            price=int(raw.get("price", 0)),
            available=bool(raw.get("available", True)),
            category=str(raw.get("category", "")).lower(),
            meal_type="lunch",
            healthy=False,
            vegetarian=raw.get("category") == "veg",
            restaurant_id=raw.get("restaurant_id"),
            restaurant_name=str(raw.get("restaurant_name", "")),
            cuisine=str(raw.get("cuisine", "")),
            cuisine_type=str(raw.get("cuisine", "")),
            parent_category="Combos",
            is_combo=True,
            combo_id=raw.get("combo_id"),
            savings_amount=raw.get("savings_amount", 0),
            raw_item=raw,
        )

    # Constraint Handlers
    def _filter_budget(self, c: RecommendationCandidate, val: Any) -> bool:
        if isinstance(val, (int, float)):
            return c.price <= val
        if isinstance(val, (list, tuple)) and len(val) == 2:
            return val[0] <= c.price <= val[1]
        return True

    def _filter_max_budget(self, c: RecommendationCandidate, val: Any) -> bool:
        return c.price <= val if isinstance(val, (int, float)) else True

    def _filter_min_budget(self, c: RecommendationCandidate, val: Any) -> bool:
        return c.price >= val if isinstance(val, (int, float)) else True

    def _filter_diet(self, c: RecommendationCandidate, val: Any) -> bool:
        if not val:
            return True
        norm_val = str(val).strip().lower()
        if norm_val in {"nonveg", "non veg", "non-veg"}:
            return c.category in {"non-veg", "nonveg"} or not c.vegetarian
        if norm_val in {"veg", "vegetarian"}:
            return c.category in {"veg", "vegetarian"} or c.vegetarian
        return True

    def _filter_meal_type(self, c: RecommendationCandidate, val: Any) -> bool:
        if not val:
            return True
        norm_val = str(val).strip().lower()
        return c.meal_type == norm_val or norm_val in f"{c.name} {c.description}".lower()

    def _filter_health_goal(self, c: RecommendationCandidate, val: Any) -> bool:
        if not val:
            return True
        norm_val = str(val).strip().lower()
        if norm_val == "high_protein":
            return c.high_protein or (c.raw_item.get("nutrition", {}).get("macronutrients", {}).get("protein_g", 0) >= 15)
        if norm_val == "low_calorie":
            return c.low_calorie or (c.raw_item.get("nutrition", {}).get("macronutrients", {}).get("calories_kcal", 999) <= 400)
        return c.healthy or c.high_protein or c.low_calorie

    def _filter_cuisine(self, c: RecommendationCandidate, val: Any) -> bool:
        if not val:
            return True
        norm_val = str(val).strip().lower()
        item_text = f"{c.cuisine} {c.cuisine_type} {c.restaurant_name} {c.name} {c.description}".lower()
        sec_cuisines = [str(x).lower() for x in c.raw_item.get("secondary_cuisines", [])]
        return norm_val in item_text or any(norm_val in x for x in sec_cuisines)

    def _filter_taste(self, c: RecommendationCandidate, val: Any) -> bool:
        if not val:
            return True
        norm_val = str(val).strip().lower()
        item_text = f"{c.taste_preference} {c.name} {c.description}".lower()
        return norm_val in item_text or (norm_val == "spicy" and c.spicy)

    def _filter_item_category(self, c: RecommendationCandidate, val: Any) -> bool:
        if not val:
            return True
        norm_val = str(val).strip().lower()

        # Beverage matching
        if norm_val in {"beverage", "beverages", "drink", "drinks", "coffee", "tea", "juice", "smoothie", "shake", "cold drink"}:
            if c.parent_category.lower() in {"beverages", "coffee", "mccafe"}:
                return True
            return any(k in f"{c.name} {c.description} {c.meal_type}".lower() for k in ["pepsi", "coke", "cappuccino", "coffee", "tea", "beverage", "shake", "smoothie", "juice", "drink"])

        # Dessert matching
        if norm_val in {"dessert", "desserts", "sweet", "sweets", "ice cream", "icecream", "brownie", "cake"}:
            if c.parent_category.lower() in {"desserts", "sweets"}:
                return True
            return any(k in f"{c.name} {c.description} {c.meal_type}".lower() for k in ["dessert", "mcflurry", "lava cake", "ice cream", "cake", "sweet", "pastry", "brownie", "churma"])

        # Combo matching
        if norm_val in {"combo", "combos", "meal deal", "family combo", "kids combo"}:
            return c.is_combo or "combo" in f"{c.name} {c.description}".lower()

        # Burger, Pizza, Rice, Noodle, Wrap, Meal
        item_text = f"{c.name} {c.parent_category} {c.description}".lower()
        return norm_val in item_text

    def _filter_is_combo(self, c: RecommendationCandidate, val: Any) -> bool:
        return c.is_combo if bool(val) else True

    def _filter_serving(self, c: RecommendationCandidate, val: Any) -> bool:
        if not val:
            return True
        norm_val = str(val).strip().lower()
        item_text = f"{c.name} {c.description}".lower()
        if norm_val in {"family", "party"}:
            return c.is_combo or any(k in item_text for k in ["family", "bucket", "bundle", "box", "party", "large"])
        if norm_val == "kids":
            return any(k in item_text for k in ["kids", "small", "mini", "regular"])
        return True

    def _filter_restaurant_id(self, c: RecommendationCandidate, val: Any) -> bool:
        return c.restaurant_id == val

    def _filter_spicy(self, c: RecommendationCandidate, val: Any) -> bool:
        return c.spicy == bool(val)

    def _filter_vegan(self, c: RecommendationCandidate, val: Any) -> bool:
        return c.vegan if bool(val) else True

    def _filter_gluten_free(self, c: RecommendationCandidate, val: Any) -> bool:
        return c.gluten_free if bool(val) else True

    def _filter_high_protein(self, c: RecommendationCandidate, val: Any) -> bool:
        return c.high_protein if bool(val) else True
