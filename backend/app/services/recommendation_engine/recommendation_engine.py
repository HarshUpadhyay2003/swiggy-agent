"""Generalized Recommendation Engine Orchestrator with Developer Debug Telemetry."""

import time
from typing import List, Optional
from app.services.catalog_service import CatalogService
from app.services.recommendation_engine.candidate_retriever import CandidateRetriever
from app.services.recommendation_engine.models import (
    PipelineDebugInfo,
    RecommendationRequest,
    RecommendationResult,
)
from app.services.recommendation_engine.ranking_engine import RankingEngine
from app.services.recommendation_engine.reason_builder import DecisionReasonBuilder
from app.services.recommendation_engine.strategy_chain import RecommendationStrategyChain


class RecommendationEngine:
    """Orchestrates strategy chain retrieval, generalized constraint filtering, ranking, and debug telemetry."""

    def __init__(self, catalog_service: Optional[CatalogService] = None) -> None:
        self.catalog_service = catalog_service or CatalogService()
        self.retriever = CandidateRetriever(self.catalog_service)
        self.strategy_chain = RecommendationStrategyChain()
        self.ranker = RankingEngine()
        self.reason_builder = DecisionReasonBuilder()

    def generate_recommendations(self, request: RecommendationRequest) -> List[RecommendationResult]:
        """
        Execute full recommendation pipeline:
        Strategy Chain Retrieval -> Filter -> Rank -> Build Reasons -> Debug Telemetry -> Results
        """
        start_time = time.perf_counter()

        # Step 1: Strategy Chain candidate retrieval
        candidates, strategy_used, counts_debug = self.strategy_chain.execute_chain(
            self.retriever, request
        )

        if not candidates:
            return []

        # Step 2: Ranking Engine multi-vector scoring
        rank_start = time.perf_counter()
        scored_pairs = self.ranker.score_candidates(candidates, request)
        ranking_duration_ms = round((time.perf_counter() - rank_start) * 1000.0, 3)

        top_pairs = scored_pairs[: request.top_k]

        pipeline_duration_ms = round((time.perf_counter() - start_time) * 1000.0, 3)

        matched_constraints = [c.type for c in request.constraints if c.is_hard]

        results: List[RecommendationResult] = []
        for candidate, score in top_pairs:
            reason = self.reason_builder.build_reason(candidate, request, score)

            debug_info = None
            if request.context.debug_mode:
                debug_info = PipelineDebugInfo(
                    strategy=strategy_used,
                    matched_constraints=matched_constraints,
                    candidate_counts=counts_debug,
                    ranking_duration_ms=ranking_duration_ms,
                    pipeline_duration_ms=pipeline_duration_ms,
                )

            results.append(
                RecommendationResult(
                    candidate=candidate,
                    score=score,
                    reason=reason,
                    debug=debug_info,
                )
            )

        return results
