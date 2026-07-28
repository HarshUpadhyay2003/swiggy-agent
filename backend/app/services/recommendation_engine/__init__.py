"""Recommendation Engine package (Stage 2B)."""

from app.services.recommendation_engine.candidate_retriever import CandidateRetriever
from app.services.recommendation_engine.models import (
    ComponentScore,
    Constraint,
    PipelineDebugInfo,
    RecommendationCandidate,
    RecommendationContext,
    RecommendationReason,
    RecommendationRequest,
    RecommendationResult,
    RecommendationScore,
)
from app.services.recommendation_engine.ranking_engine import (
    AttributeScorer,
    BaseComponentScorer,
    BudgetScorer,
    HealthScorer,
    HistoryScorer,
    MealTypeScorer,
    MoodScorer,
    PopularityScorer,
    PreferenceScorer,
    RankingEngine,
)
from app.services.recommendation_engine.reason_builder import DecisionReasonBuilder, ReasonBuilder
from app.services.recommendation_engine.recommendation_engine import RecommendationEngine
from app.services.recommendation_engine.strategy_chain import RecommendationStrategyChain

__all__ = [
    "Constraint",
    "RecommendationContext",
    "RecommendationRequest",
    "RecommendationCandidate",
    "ComponentScore",
    "RecommendationScore",
    "RecommendationReason",
    "PipelineDebugInfo",
    "RecommendationResult",
    "CandidateRetriever",
    "BaseComponentScorer",
    "BudgetScorer",
    "PreferenceScorer",
    "MealTypeScorer",
    "MoodScorer",
    "PopularityScorer",
    "HealthScorer",
    "AttributeScorer",
    "HistoryScorer",
    "RankingEngine",
    "DecisionReasonBuilder",
    "ReasonBuilder",
    "RecommendationStrategyChain",
    "RecommendationEngine",
]
