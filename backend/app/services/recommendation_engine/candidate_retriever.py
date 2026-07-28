"""Candidate Retriever module for deterministic candidate filtering."""

from typing import Any, Dict, List, Optional
from app.services.catalog_service import CatalogService
from app.services.recommendation_engine.models import RecommendationCandidate, RecommendationRequest


class CandidateRetriever:
    """Retrieves and applies deterministic filters on catalog items."""

    def __init__(self, catalog_service: CatalogService) -> None:
        self.catalog_service = catalog_service

    def retrieve_candidates(self, request: RecommendationRequest) -> List[RecommendationCandidate]:
        """Fetch available catalog items and apply deterministic filtering rules."""
        raw_items = self.catalog_service.get_available_items()

        candidates: List[RecommendationCandidate] = []
        for raw in raw_items:
            candidate = self._map_to_candidate(raw)
            if self._matches_criteria(candidate, request):
                candidates.append(candidate)

        return candidates

    def _map_to_candidate(self, raw: Dict[str, Any]) -> RecommendationCandidate:
        """Map legacy catalog item dict to RecommendationCandidate model."""
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

    def _matches_criteria(self, item: RecommendationCandidate, req: RecommendationRequest) -> bool:
        """Check if candidate satisfies deterministic constraints."""
        if not item.available:
            return False

        # Budget filtering
        if req.min_budget is not None and item.price < req.min_budget:
            return False
        if req.max_budget is not None and item.price > req.max_budget:
            return False

        # Dietary preference filtering
        if req.preference:
            norm_pref = req.preference.strip().lower()
            if norm_pref in {"nonveg", "non veg"}:
                norm_pref = "non-veg"
            if item.category != norm_pref:
                return False

        # Meal type filtering
        if req.meal_type:
            if item.meal_type != req.meal_type.strip().lower():
                return False

        # Healthy only filter
        if req.healthy_only and not item.healthy:
            return False

        # Specific restaurant filter
        if req.restaurant_id is not None and item.restaurant_id != req.restaurant_id:
            return False

        return True
