"""Recommendation Engine orchestrator pipeline module."""

from typing import List, Optional
from app.services.catalog_service import CatalogService
from app.services.recommendation_engine.candidate_retriever import CandidateRetriever
from app.services.recommendation_engine.explanation_builder import ExplanationBuilder
from app.services.recommendation_engine.models import (
    RecommendationRequest,
    RecommendationResult,
)
from app.services.recommendation_engine.ranking_engine import RankingEngine


class RecommendationEngine:
    """Orchestrates deterministic candidate retrieval, multi-vector ranking, and structured explanation generation."""

    def __init__(self, catalog_service: Optional[CatalogService] = None) -> None:
        self.catalog_service = catalog_service or CatalogService()
        self.retriever = CandidateRetriever(self.catalog_service)
        self.ranker = RankingEngine()
        self.explanation_builder = ExplanationBuilder()

    def generate_recommendations(self, request: RecommendationRequest) -> List[RecommendationResult]:
        """
        Execute full recommendation pipeline:
        Retrieve -> Filter -> Rank -> Build Explanations -> Return Ranked Results
        """
        # Step 1 & 2: Retrieve & Filter candidates
        candidates = self.retriever.retrieve_candidates(request)
        if not candidates:
            return []

        # Step 3: Rank candidates
        scored_pairs = self.ranker.score_candidates(candidates, request)

        # Slice top_k requested
        top_pairs = scored_pairs[: request.top_k]

        # Step 4: Build structured explanations & format output
        results: List[RecommendationResult] = []
        for candidate, score in top_pairs:
            explanation = self.explanation_builder.build_explanation(candidate, request, score)
            results.append(
                RecommendationResult(
                    candidate=candidate,
                    score=score,
                    explanation=explanation,
                )
            )

        return results
