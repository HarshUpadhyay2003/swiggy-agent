"""Candidate Retriever applying generalized polymorphic constraint filters."""

from typing import Any, Callable, Dict, List, Tuple
from app.services.catalog_service import CatalogService
from app.services.recommendation_engine.models import (
    Constraint,
    RecommendationCandidate,
    RecommendationRequest,
)


class CandidateRetriever:
    """Retrieves menu items and filters candidates by evaluating constraints polymorphically."""

    def __init__(self, catalog_service: CatalogService) -> None:
        self.catalog_service = catalog_service
        self._handlers: Dict[str, Callable[[RecommendationCandidate, Any], bool]] = {
            "budget": self._filter_budget,
            "max_budget": self._filter_max_budget,
            "min_budget": self._filter_min_budget,
            "preference": self._filter_preference,
            "meal_type": self._filter_meal_type,
            "health_goal": self._filter_health_goal,
            "healthy_only": self._filter_health_goal,
            "restaurant_id": self._filter_restaurant_id,
            "spicy": self._filter_spicy,
            "vegan": self._filter_vegan,
            "gluten_free": self._filter_gluten_free,
            "high_protein": self._filter_high_protein,
        }

    def retrieve_candidates(
        self, request: RecommendationRequest
    ) -> Tuple[List[RecommendationCandidate], Dict[str, int]]:
        """
        Fetch available catalog items, iterate through constraints,
        and return candidates alongside per-stage candidate count telemetry.
        """
        raw_items = self.catalog_service.get_available_items()
        candidates = [self._map_to_candidate(raw) for raw in raw_items]

        counts_debug: Dict[str, int] = {"initial_candidates": len(candidates)}

        for constraint in request.constraints:
            if not constraint.is_hard:
                continue

            handler = self._handlers.get(constraint.type)
            if handler:
                candidates = [c for c in candidates if handler(c, constraint.value)]
                counts_debug[f"remaining_after_{constraint.type}"] = len(candidates)

        return candidates, counts_debug

    def _map_to_candidate(self, raw: Dict[str, Any]) -> RecommendationCandidate:
        """Map legacy catalog item dictionary to RecommendationCandidate model."""
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

    def _filter_preference(self, c: RecommendationCandidate, val: Any) -> bool:
        norm_val = str(val).strip().lower()
        if norm_val in {"nonveg", "non veg"}:
            norm_val = "non-veg"
        return c.category == norm_val

    def _filter_meal_type(self, c: RecommendationCandidate, val: Any) -> bool:
        return c.meal_type == str(val).strip().lower()

    def _filter_health_goal(self, c: RecommendationCandidate, val: Any) -> bool:
        return c.healthy if bool(val) else True

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
