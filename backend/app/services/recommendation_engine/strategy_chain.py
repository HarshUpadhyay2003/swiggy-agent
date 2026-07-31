"""Stage 2A.1 Strategy Chain enforcing hard constraint protection and recovery telemetry."""

from typing import Dict, List, Optional, Tuple
from app.services.recommendation_engine.candidate_retriever import CandidateRetriever
from app.services.recommendation_engine.models import (
    Constraint,
    RecommendationCandidate,
    RecommendationRequest,
)


class BaseRecommendationStrategy:
    """Base interface for recommendation strategy chain components."""
    strategy_name: str = "base"

    def execute(
        self, retriever: CandidateRetriever, request: RecommendationRequest
    ) -> Tuple[List[RecommendationCandidate], Dict[str, int]]:
        raise NotImplementedError


class ExplicitConstraintsStrategy(BaseRecommendationStrategy):
    """Try candidate retrieval with all explicit hard + flexible constraints."""
    strategy_name = "explicit_constraints"

    def execute(
        self, retriever: CandidateRetriever, request: RecommendationRequest
    ) -> Tuple[List[RecommendationCandidate], Dict[str, int]]:
        return retriever.retrieve_candidates(request)


class BudgetRelaxationStrategy(BaseRecommendationStrategy):
    """
    Intelligent Recovery Stage 1:
    Preserve PROTECTED HARD constraints (query_type, category, cuisine, meal_type, diet).
    Relax ONLY flexible budget constraints.
    """
    strategy_name = "budget_relaxed"

    def execute(
        self, retriever: CandidateRetriever, request: RecommendationRequest
    ) -> Tuple[List[RecommendationCandidate], Dict[str, int]]:
        hard_types = {
            "query_type", "category", "item_category", "cuisine", "cuisine_type", "meal_type",
            "diet", "preference", "vegan", "gluten_free", "vegetarian", "is_combo"
        }
        relaxed_constraints = [c for c in request.constraints if c.type in hard_types]
        if len(relaxed_constraints) == len(request.constraints):
            return [], {}

        relaxed_request = RecommendationRequest(
            constraints=relaxed_constraints,
            context=request.context,
            top_k=request.top_k,
        )
        return retriever.retrieve_candidates(relaxed_request)


class TasteAndHealthRelaxationStrategy(BaseRecommendationStrategy):
    """
    Intelligent Recovery Stage 2:
    Preserve PROTECTED HARD constraints (query_type, category, cuisine, meal_type, diet).
    Relax taste, health, serving, and budget constraints.
    """
    strategy_name = "taste_health_relaxed"

    def execute(
        self, retriever: CandidateRetriever, request: RecommendationRequest
    ) -> Tuple[List[RecommendationCandidate], Dict[str, int]]:
        hard_types = {"query_type", "category", "item_category", "cuisine", "cuisine_type", "meal_type", "diet", "preference", "is_combo"}
        relaxed_constraints = [c for c in request.constraints if c.type in hard_types]

        if not relaxed_constraints:
            return [], {}

        relaxed_request = RecommendationRequest(
            constraints=relaxed_constraints,
            context=request.context,
            top_k=request.top_k,
        )
        return retriever.retrieve_candidates(relaxed_request)


class HardConstraintPopularityStrategy(BaseRecommendationStrategy):
    """
    Intelligent Recovery Stage 3:
    Preserve PROTECTED HARD constraints (query_type, category, cuisine, meal_type, diet).
    Rank candidates matching hard constraints by popularity.
    """
    strategy_name = "hard_constraint_popularity"

    def execute(
        self, retriever: CandidateRetriever, request: RecommendationRequest
    ) -> Tuple[List[RecommendationCandidate], Dict[str, int]]:
        hard_types = {"query_type", "category", "item_category", "cuisine", "cuisine_type", "meal_type", "diet", "preference", "is_combo"}
        hard_constraints = [c for c in request.constraints if c.type in hard_types]

        if not hard_constraints:
            raw_items = retriever.catalog_service.get_available_items()
            candidates = [retriever._map_to_candidate(raw) for raw in raw_items]
            return candidates, {"popularity_candidates": len(candidates)}

        relaxed_request = RecommendationRequest(
            constraints=hard_constraints,
            context=request.context,
            top_k=request.top_k,
        )
        return retriever.retrieve_candidates(relaxed_request)


class RecommendationStrategyChain:
    """Orchestrates Stage 2A.1 protected constraint recovery execution and telemetry."""

    def __init__(self, strategies: Optional[List[BaseRecommendationStrategy]] = None) -> None:
        self.strategies: List[BaseRecommendationStrategy] = strategies or [
            ExplicitConstraintsStrategy(),
            BudgetRelaxationStrategy(),
        ]

    def execute_chain(
        self, retriever: CandidateRetriever, request: RecommendationRequest
    ) -> Tuple[List[RecommendationCandidate], str, Dict[str, int]]:
        """
        Execute recovery strategies sequentially.
        NEVER relax query_type, category, cuisine, meal_type, or diet.
        Return candidates, strategy name, and telemetry metrics.
        """
        for strategy in self.strategies:
            candidates, debug_metrics = strategy.execute(retriever, request)
            if candidates:
                if strategy.strategy_name != "explicit_constraints":
                    self._log_recovery_telemetry(request, strategy.strategy_name)
                return candidates, strategy.strategy_name, debug_metrics

        self._log_recovery_telemetry(request, "no_matching_items")
        return [], "no_matching_items", {}

    def _log_recovery_telemetry(self, request: RecommendationRequest, strategy_used: str) -> None:
        """Print Component 9 structured constraint recovery telemetry log."""
        protected_types = {"query_type", "category", "item_category", "cuisine", "cuisine_type", "meal_type", "diet", "preference"}
        flexible_types = {"budget", "max_budget", "min_budget", "taste", "taste_preference", "spicy", "popularity", "health_goal", "healthy", "serving"}

        prot_constraints = {c.type: c.value for c in request.constraints if c.type in protected_types}
        rel_constraints = {c.type: c.value for c in request.constraints if c.type in flexible_types}

        reason = "Matched all explicit constraints."
        if strategy_used == "budget_relaxed":
            reason = "Relaxed budget to find closest matches preserving protected category/cuisine/meal/diet."
        elif strategy_used in ["taste_health_relaxed", "hard_constraint_popularity"]:
            reason = "Relaxed flexible taste/health/budget criteria while preserving protected category/cuisine/meal/diet."
        elif strategy_used == "no_matching_items":
            reason = "No items matched protected hard constraints."

        print("\n===================================")
        print("[CONSTRAINT RECOVERY]")
        print("Protected:")
        print(f"  Query Type: {prot_constraints.get('query_type', 'N/A')}")
        print(f"  Cuisine: {prot_constraints.get('cuisine_type', prot_constraints.get('cuisine', 'N/A'))}")
        print(f"  Meal: {prot_constraints.get('meal_type', 'N/A')}")
        print(f"  Diet: {prot_constraints.get('diet', prot_constraints.get('preference', 'N/A'))}")
        print("Relaxed:")
        print(f"  Budget: {rel_constraints.get('max_budget', rel_constraints.get('budget', 'N/A'))}")
        print(f"  Taste: {rel_constraints.get('taste_preference', rel_constraints.get('taste', 'N/A'))}")
        print(f"  Popularity: {rel_constraints.get('popularity', 'N/A')}")
        print(f"  Health: {rel_constraints.get('health_goal', 'N/A')}")
        print(f"  Serving: {rel_constraints.get('serving', 'N/A')}")
        print(f"Recovery Explanation: {reason}")
        print("===================================\n")
