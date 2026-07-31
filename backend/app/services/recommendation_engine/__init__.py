"""
Recommendation Engine Package Exports.
Exposes Stage 2C - Stage 4F.1 Recommendation Engine components.
"""

from app.services.recommendation_engine.models import (
    Constraint,
    RecommendationCandidate,
    RecommendationContext,
    RecommendationRequest,
    EffectiveRecommendationRequest,
    CandidateEvaluation,
    RecommendationExplanation,
    RecommendationScore,
    RecommendationReason,
    RecommendationResult,
)
from app.services.recommendation_engine.request_normalizer import RequestNormalizer
from app.services.recommendation_engine.schema_field_matcher import SchemaFieldMatcher
from app.services.recommendation_engine.candidate_retriever import CandidateRetriever
from app.services.recommendation_engine.ranking_engine import RankingEngine
from app.services.recommendation_engine.recommendation_validator import RecommendationValidator
Validator = RecommendationValidator

from app.services.recommendation_engine.reason_builder import DecisionReasonBuilder
ReasonBuilder = DecisionReasonBuilder

from app.services.recommendation_engine.explanation_builder import ExplanationBuilder
from app.services.recommendation_engine.strategy_chain import BaseRecommendationStrategy, RecommendationStrategyChain
StrategyChain = RecommendationStrategyChain

from app.services.recommendation_engine.recommendation_engine import RecommendationEngine

# Stage 4F & 4F.1 Semantic Recommendation Components
from app.services.recommendation_engine.semantic_profile_resolver import SemanticProfile, SemanticProfileResolver
from app.services.recommendation_engine.semantic_policy_resolver import SemanticPolicy, SemanticPolicyResolver
from app.services.recommendation_engine.semantic_evaluator import SemanticEvidence, SemanticEvaluator
from app.services.recommendation_engine.semantic_calibrator import SemanticCalibration, SemanticCalibrator
from app.services.recommendation_engine.suitability_estimator import SuitabilityEstimator
from app.services.recommendation_engine.decision_engine import SemanticDecision, AdaptiveDecisionEngine
from app.services.recommendation_engine.semantic_metrics import SemanticMetricsCalculator, MetricReport
from app.services.recommendation_engine.semantic_explanation_engine import CandidateExplanation, SemanticExplanationEngine
from app.services.recommendation_engine.semantic_recommendation_engine import (
    SemanticCandidateEvaluation,
    SemanticTelemetry,
    SemanticRecommendationEngine,
)

__all__ = [
    "Constraint",
    "RecommendationCandidate",
    "RecommendationContext",
    "RecommendationRequest",
    "EffectiveRecommendationRequest",
    "CandidateEvaluation",
    "RecommendationExplanation",
    "RecommendationScore",
    "RecommendationReason",
    "RecommendationResult",
    "RequestNormalizer",
    "SchemaFieldMatcher",
    "CandidateRetriever",
    "RankingEngine",
    "RecommendationValidator",
    "Validator",
    "DecisionReasonBuilder",
    "ReasonBuilder",
    "ExplanationBuilder",
    "BaseRecommendationStrategy",
    "RecommendationStrategyChain",
    "StrategyChain",
    "RecommendationEngine",
    "SemanticProfile",
    "SemanticProfileResolver",
    "SemanticPolicy",
    "SemanticPolicyResolver",
    "SemanticEvidence",
    "SemanticEvaluator",
    "SemanticCalibration",
    "SemanticCalibrator",
    "SuitabilityEstimator",
    "SemanticDecision",
    "AdaptiveDecisionEngine",
    "SemanticMetricsCalculator",
    "MetricReport",
    "CandidateExplanation",
    "SemanticExplanationEngine",
    "SemanticCandidateEvaluation",
    "SemanticTelemetry",
    "SemanticRecommendationEngine",
]
