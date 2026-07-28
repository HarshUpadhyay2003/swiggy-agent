"""Neutral recommendation strategy chain for candidate retrieval and fallback resolution."""

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
    strategy_name = "explicit_constraints"

    def execute(
        self, retriever: CandidateRetriever, request: RecommendationRequest
    ) -> Tuple[List[RecommendationCandidate], Dict[str, int]]:
        return retriever.retrieve_candidates(request)


class ConversationalContextStrategy(BaseRecommendationStrategy):
    strategy_name = "conversational_context"

    def execute(
        self, retriever: CandidateRetriever, request: RecommendationRequest
    ) -> Tuple[List[RecommendationCandidate], Dict[str, int]]:
        # Relax constraints: keep budget and preference, drop meal_type and health_goal
        relaxed_constraints = [
            c for c in request.constraints
            if c.type in {"budget", "max_budget", "min_budget", "preference"}
        ]
        relaxed_request = RecommendationRequest(
            constraints=relaxed_constraints,
            context=request.context,
            top_k=request.top_k,
        )
        return retriever.retrieve_candidates(relaxed_request)


class OrderHistoryStrategy(BaseRecommendationStrategy):
    strategy_name = "order_history_fallback"

    def execute(
        self, retriever: CandidateRetriever, request: RecommendationRequest
    ) -> Tuple[List[RecommendationCandidate], Dict[str, int]]:
        if not request.context.order_history:
            return [], {}
        raw_items = retriever.catalog_service.get_available_items()
        candidates = [
            retriever._map_to_candidate(raw)
            for raw in raw_items
            if raw.get("item_id") in request.context.order_history
        ]
        return candidates, {"order_history_matches": len(candidates)}


class PopularityStrategy(BaseRecommendationStrategy):
    strategy_name = "popularity_fallback"

    def execute(
        self, retriever: CandidateRetriever, request: RecommendationRequest
    ) -> Tuple[List[RecommendationCandidate], Dict[str, int]]:
        raw_items = retriever.catalog_service.get_available_items()
        candidates = [retriever._map_to_candidate(raw) for raw in raw_items]
        return candidates, {"popularity_candidates": len(candidates)}


class CatalogueFallbackStrategy(BaseRecommendationStrategy):
    strategy_name = "catalogue_fallback"

    def execute(
        self, retriever: CandidateRetriever, request: RecommendationRequest
    ) -> Tuple[List[RecommendationCandidate], Dict[str, int]]:
        raw_items = retriever.catalog_service.get_available_items()
        candidates = [retriever._map_to_candidate(raw) for raw in raw_items]
        return candidates, {"fallback_candidates": len(candidates)}


class RecommendationStrategyChain:
    """Orchestrates strategy chain execution sequentially until non-empty candidates are found."""

    def __init__(self, strategies: Optional[List[BaseRecommendationStrategy]] = None) -> None:
        self.strategies: List[BaseRecommendationStrategy] = strategies or [
            ExplicitConstraintsStrategy(),
            ConversationalContextStrategy(),
            OrderHistoryStrategy(),
            PopularityStrategy(),
            CatalogueFallbackStrategy(),
        ]

    def execute_chain(
        self, retriever: CandidateRetriever, request: RecommendationRequest
    ) -> Tuple[List[RecommendationCandidate], str, Dict[str, int]]:
        """Run strategies in order. Return first non-empty candidate list, strategy name, and debug metrics."""
        for strategy in self.strategies:
            candidates, debug_metrics = strategy.execute(retriever, request)
            if candidates:
                return candidates, strategy.strategy_name, debug_metrics

        return [], "no_matching_items", {}
