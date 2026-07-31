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

        # Extract cuisine constraint
        cuisine = context.get("cuisine_type") or context.get("cuisine")
        if cuisine:
            constraints.append(Constraint(type="cuisine_type", value=cuisine))

        # Extract taste constraint
        taste = context.get("taste_preference") or context.get("taste")
        if taste:
            constraints.append(Constraint(type="taste_preference", value=taste))

        # Extract category constraint
        category = context.get("category") or context.get("item_category")
        if category:
            constraints.append(Constraint(type="category", value=category))

        # Extract diet constraint
        diet = context.get("diet") or context.get("preference")
        if diet:
            constraints.append(Constraint(type="diet", value=diet))

        # Extract serving constraint
        serving = context.get("serving")
        if serving:
            constraints.append(Constraint(type="serving", value=serving))

        # Extract combo constraint
        if context.get("is_combo") or (category and str(category).lower() in {"combo", "combos", "meal deal", "family combo"}):
            constraints.append(Constraint(type="is_combo", value=True))

        # Extract meal_type constraint
        meal_type = context.get("meal_type")
        if meal_type:
            constraints.append(Constraint(type="meal_type", value=meal_type))

        # Extract health constraint
        health_goal = context.get("health_goal") or context.get("healthy_only") or context.get("healthy")
        if health_goal:
            constraints.append(Constraint(type="health_goal", value=health_goal))

        # Extract mood constraint
        mood = context.get("mood")
        if mood:
            constraints.append(Constraint(type="mood", value=mood))

        # Extract additional attribute constraints
        if context.get("high_protein") or context.get("protein_rich") or health_goal == "high_protein":
            constraints.append(Constraint(type="high_protein", value=True))
        if context.get("low_calorie") or health_goal == "low_calorie":
            constraints.append(Constraint(type="low_calorie", value=True))
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
            raw_query=str(context.get("message") or context.get("query") or ""),
            debug_mode=debug_mode,
        )

        req = RecommendationRequest(
            constraints=constraints,
            context=rec_context,
            top_k=top_k,
        )

        session_state = context.get("session_state")
        rec_memory = session_state.recommendation_memory if session_state and hasattr(session_state, "recommendation_memory") else None

        if rec_memory:
            from app.services.recommendation_engine.conversation_intelligence import ConversationIntelligenceEngine
            from app.services.session_manager import ConstraintLifecycleEngine

            intelligence_engine = ConversationIntelligenceEngine()
            lifecycle_engine = ConstraintLifecycleEngine()

            eff_req, _, telemetry = intelligence_engine.process(
                raw_query=str(context.get("message") or context.get("query") or ""),
                request=req,
                session_memory=rec_memory,
                candidate_retriever=self.recommendation_engine.retriever,
            )

            effective_req = lifecycle_engine.process_lifecycle(
                raw_request=eff_req,
                session_memory=rec_memory,
                active_domain=getattr(session_state, "active_domain", "recommendations"),
            )
        else:
            effective_req = req

        # Delegate to RecommendationEngine
        results = self.recommendation_engine.generate_recommendations(effective_req)

        # Format output payload expected by ChatOrchestrator and legacy callers
        formatted_recs: List[Dict[str, Any]] = []
        fallback_used = False

        req_max_budget = max_budget if (max_budget and isinstance(max_budget, (int, float))) else None

        for res in results:
            if res.debug and res.debug.strategy != "explicit_constraints":
                fallback_used = True

            price_diff = 0
            if req_max_budget and res.candidate.price > req_max_budget:
                price_diff = int(res.candidate.price - req_max_budget)

            # Formulate natural language reason string from structured reasons
            reason_str = ", ".join(res.reason.reasons) if res.reason.reasons else "Matches criteria"

            rec_item: Dict[str, Any] = {
                "item_id": res.candidate.item_id,
                "item_name": res.candidate.name,
                "name": res.candidate.name,
                "restaurant": res.candidate.restaurant_name,
                "restaurant_name": res.candidate.restaurant_name,
                "price": res.candidate.price,
                "cuisine": res.candidate.cuisine or res.candidate.cuisine_type,
                "cuisine_type": res.candidate.cuisine_type or res.candidate.cuisine,
                "parent_category": res.candidate.parent_category,
                "healthy": res.candidate.healthy,
                "is_combo": res.candidate.is_combo,
                "price_difference": price_diff,
                "budget_exceeded": bool(price_diff > 0),
                "reason": reason_str,
            }

            if include_scores:
                rec_item["score"] = res.score.total_score

            if debug_mode and res.debug:
                rec_item["debug"] = res.debug.model_dump()

            formatted_recs.append(rec_item)

        cuisine_label = str(cuisine or category or "requested").title()
        if not formatted_recs:
            reasoning = "No exact matches satisfy every requested constraint."
        elif fallback_used and req_max_budget:
            reasoning = f"No {cuisine_label} meals are available under ₹{int(req_max_budget)}. Closest available options:"
        elif fallback_used:
            reasoning = f"Relaxed flexible criteria to find matching {cuisine_label} options."
        else:
            reasoning = "Found items matching your criteria."

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
