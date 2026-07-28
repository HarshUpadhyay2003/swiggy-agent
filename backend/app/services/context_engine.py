"""ContextEngine adapter layer delegating recommendation decisioning to RecommendationEngine."""

from typing import Any, Dict, List, Optional
from app.services.catalog_service import CatalogService
from app.services.recommendation_engine import (
    Constraint,
    RecommendationContext,
    RecommendationEngine,
    RecommendationRequest,
)


class ContextEngine:
    """Orchestration layer delegating recommendation decisions to RecommendationEngine while preserving public contracts."""

    def __init__(
        self,
        catalog_service: Optional[CatalogService] = None,
        recommendation_engine: Optional[RecommendationEngine] = None,
    ) -> None:
        self.catalog_service = catalog_service or CatalogService()
        self.recommendation_engine = recommendation_engine or RecommendationEngine(self.catalog_service)

    def recommend_food(
        self, context: Dict[str, Any], include_scores: bool = False
    ) -> Dict[str, Any]:
        """
        Generate food recommendations by translating dict context into RecommendationRequest
        and delegating execution to RecommendationEngine.
        """
        constraints: List[Constraint] = []

        # Extract budget constraints
        max_budget = context.get("max_budget") or context.get("budget_max") or context.get("budget")
        if max_budget is not None and isinstance(max_budget, (int, float)):
            constraints.append(Constraint(type="max_budget", value=max_budget))

        min_budget = context.get("min_budget") or context.get("budget_min")
        if min_budget is not None and isinstance(min_budget, (int, float)):
            constraints.append(Constraint(type="min_budget", value=min_budget))

        # Extract preference constraint
        preference = context.get("preference") or context.get("category")
        if preference:
            constraints.append(Constraint(type="preference", value=preference))

        # Extract meal type constraint
        meal_type = context.get("meal_type")
        if meal_type:
            constraints.append(Constraint(type="meal_type", value=meal_type))

        # Extract health constraint
        health_goal = context.get("health_goal") or context.get("healthy_only") or context.get("healthy")
        if health_goal:
            constraints.append(Constraint(type="health_goal", value=True))

        # Extract mood constraint
        mood = context.get("mood")
        if mood:
            constraints.append(Constraint(type="mood", value=mood))

        # Extract additional attribute constraints
        if context.get("high_protein") or context.get("protein_rich"):
            constraints.append(Constraint(type="high_protein", value=True))
        if context.get("spicy") is not None:
            constraints.append(Constraint(type="spicy", value=context.get("spicy")))
        if context.get("vegan"):
            constraints.append(Constraint(type="vegan", value=True))
        if context.get("gluten_free"):
            constraints.append(Constraint(type="gluten_free", value=True))
        if context.get("restaurant_id"):
            constraints.append(Constraint(type="restaurant_id", value=context.get("restaurant_id")))

        top_k = int(context.get("top_k", 5))
        debug_mode = bool(context.get("debug_mode", False))

        rec_context = RecommendationContext(
            session_id=context.get("session_id"),
            debug_mode=debug_mode,
        )

        req = RecommendationRequest(
            constraints=constraints,
            context=rec_context,
            top_k=top_k,
        )

        # Delegate to RecommendationEngine
        results = self.recommendation_engine.generate_recommendations(req)

        # Format output payload expected by ChatOrchestrator and legacy callers
        formatted_recs: List[Dict[str, Any]] = []
        fallback_used = False

        for res in results:
            if res.debug and res.debug.strategy != "explicit_constraints":
                fallback_used = True

            # Formulate natural language reason string from structured reasons
            reason_str = ", ".join(res.reason.reasons) if res.reason.reasons else "Matches criteria"

            rec_item: Dict[str, Any] = {
                "item_id": res.candidate.item_id,
                "item_name": res.candidate.name,
                "restaurant": res.candidate.restaurant_name,
                "price": res.candidate.price,
                "cuisine": res.candidate.cuisine,
                "healthy": res.candidate.healthy,
                "reason": reason_str,
            }

            if include_scores:
                rec_item["score"] = res.score.total_score

            if debug_mode and res.debug:
                rec_item["debug"] = res.debug.model_dump()

            formatted_recs.append(rec_item)

        reasoning = (
            "Found items matching your criteria."
            if not fallback_used
            else "Relaxed constraints to suggest popular matching meals."
        )

        return {
            "recommendations": formatted_recs,
            "fallback_used": fallback_used,
            "reasoning": reasoning,
        }

    # Backward Compatibility Delegating Wrapper Methods
    def filter_by_budget(
        self, items: List[Dict[str, Any]], min_budget: Optional[int] = None, max_budget: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Legacy helper for budget filtering."""
        filtered = items
        if min_budget is not None:
            filtered = [i for i in filtered if isinstance(i.get("price"), (int, float)) and i["price"] >= min_budget]
        if max_budget is not None:
            filtered = [i for i in filtered if isinstance(i.get("price"), (int, float)) and i["price"] <= max_budget]
        return filtered

    def filter_by_preference(
        self, items: List[Dict[str, Any]], preference: str
    ) -> List[Dict[str, Any]]:
        """Legacy helper for preference filtering."""
        norm_pref = preference.strip().lower()
        if norm_pref in {"nonveg", "non veg"}:
            norm_pref = "non-veg"
        return [i for i in items if i.get("category", "").lower() == norm_pref]

    def filter_by_healthy(
        self, items: List[Dict[str, Any]], healthy: bool = True
    ) -> List[Dict[str, Any]]:
        """Legacy helper for health filtering."""
        return [i for i in items if bool(i.get("healthy")) == healthy]

    def prioritize_healthy(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Legacy helper sorting healthy items first."""
        return sorted(items, key=lambda i: 0 if i.get("healthy") else 1)

    def apply_mood_logic(
        self, items: List[Dict[str, Any]], mood: str
    ) -> List[Dict[str, Any]]:
        """Legacy helper for mood logic."""
        return items

    def score_item(
        self, item: Dict[str, Any], mood: Optional[str] = None, context: Optional[Dict[str, Any]] = None
    ) -> float:
        """Legacy helper for single item scoring."""
        cand = self.recommendation_engine.retriever._map_to_candidate(item)
        req_ctx = context or {}
        if mood and "mood" not in req_ctx:
            req_ctx["mood"] = mood
        constraints = [Constraint(type=k, value=v) for k, v in req_ctx.items()]
        req = RecommendationRequest(constraints=constraints)
        rec_score = self.recommendation_engine.ranker.score_candidates([cand], req)[0][1]
        return rec_score.total_score

    def generate_reason(
        self, item: Dict[str, Any], context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Legacy helper for reason string generation."""
        cand = self.recommendation_engine.retriever._map_to_candidate(item)
        req = RecommendationRequest()
        rec_score = self.recommendation_engine.ranker.score_candidates([cand], req)[0][1]
        reason_obj = self.recommendation_engine.reason_builder.build_reason(cand, req, rec_score)
        return ", ".join(reason_obj.reasons) if reason_obj.reasons else "Matches your request"
