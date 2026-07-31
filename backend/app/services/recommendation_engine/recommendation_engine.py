"""
Layer Isolation Orchestrator for Generalized Recommendation Engine (Stage 3.1).
Executes Layer 0 -> Layer 1 -> Layer 2 -> Layer 3 -> Layer 4 -> Layer 5 -> Layer 6 -> Layer 7 via RecommendationExecution.
Centralizes telemetry summary output using TelemetryLogger.
"""

import time
from typing import List, Optional
from app.services.catalog_service import CatalogService
from app.services.recommendation_engine.candidate_retriever import CandidateRetriever
from app.services.recommendation_engine.models import (
    CandidateEvaluation,
    EffectiveRecommendationRequest,
    PipelineDebugInfo,
    RecommendationExecution,
    RecommendationReason,
    RecommendationRequest,
    RecommendationResult,
    RecommendationScore,
    ResponseState,
    ValidationResult,
)
from app.services.recommendation_engine.ranking_engine import RankingEngine
from app.services.recommendation_engine.reason_builder import DecisionReasonBuilder
from app.services.recommendation_engine.recommendation_validator import RecommendationValidator
from app.services.recommendation_engine.request_normalizer import RequestNormalizer
from app.services.recommendation_engine.schema_field_matcher import SchemaFieldMatcher
from app.services.recommendation_engine.strategy_chain import RecommendationStrategyChain
from app.services.recommendation_engine.telemetry import TelemetryLogger


class RecommendationEngine:
    """Stage 3.3 Pipeline Orchestrator enforcing Layer 0 through Layer 7 isolation via RecommendationExecution."""

    def __init__(self, catalog_service: Optional[CatalogService] = None) -> None:
        from app.services.session_manager import ConstraintLifecycleEngine
        self.catalog_service = catalog_service or CatalogService()
        self.normalizer = RequestNormalizer()
        self.field_matcher = SchemaFieldMatcher()
        self.retriever = CandidateRetriever(self.catalog_service)
        self.strategy_chain = RecommendationStrategyChain()
        self.ranker = RankingEngine()
        self.validator = RecommendationValidator()
        self.reason_builder = DecisionReasonBuilder()
        self.lifecycle_engine = ConstraintLifecycleEngine()

    def generate_recommendations(
        self, request: RecommendationRequest, execution: Optional[RecommendationExecution] = None
    ) -> List[RecommendationResult]:
        """
        Executes isolated pipeline steps:
        Layer 2 (Effective Request Resolution) -> Layer 3 (Field Matcher) -> Layer 4 (Retriever) -> Layer 5 (Ranker) -> Layer 6 (Validator)
        Updates RecommendationExecution object cleanly and logs final telemetry summary.
        """
        start_time = time.perf_counter()

        # Layer 2: Resolve Effective Request if raw request was passed directly
        if not isinstance(request, EffectiveRecommendationRequest):
            from app.services.session_manager import RecommendationContextMemory
            effective_request = self.lifecycle_engine.process_lifecycle(
                raw_request=request,
                session_memory=RecommendationContextMemory(),
            )
        else:
            effective_request = request

        if execution is None:
            execution = RecommendationExecution(recommendation_request=effective_request)
        else:
            execution.recommendation_request = effective_request

        # Layer 3: Schema Field Matcher
        field_plan = self.field_matcher.build_field_match_plan(effective_request)
        execution.field_match_plan = field_plan

        # Layer 4: Candidate Retriever
        candidates, strategy_used, counts_debug = self.strategy_chain.execute_chain(
            self.retriever, effective_request
        )
        execution.candidate_pool = candidates

        if not candidates:
            exec_time = round((time.perf_counter() - start_time) * 1000.0, 1)
            TelemetryLogger.log_pipeline_summary(
                request_query=request.context.raw_query or "",
                retrieved_count=0,
                ranked_count=0,
                validated_count=0,
                returned_count=0,
                llm_calls=execution.llm_calls_count,
                execution_time_ms=exec_time,
            )
            return []

        # Layer 5: Ranking Engine
        rank_start = time.perf_counter()
        evaluations = self.ranker.evaluate_candidates(candidates, effective_request)
        ranking_duration_ms = round((time.perf_counter() - rank_start) * 1000.0, 3)
        execution.candidate_evaluations = evaluations

        # Layer 6: Recommendation Validator
        validated_evals, val_res = self.validator.validate_evaluations(evaluations, effective_request)
        execution.validated_candidates = validated_evals
        execution.validation_result = val_res
        execution.pipeline_trace.append(f"Validation Status: {'PASS' if val_res.is_valid else 'FAIL'}")

        if not val_res.is_valid or not validated_evals:
            exec_time = round((time.perf_counter() - start_time) * 1000.0, 1)
            TelemetryLogger.log_pipeline_summary(
                request_query=effective_request.context.raw_query or "",
                retrieved_count=len(candidates),
                ranked_count=len(evaluations),
                validated_count=0,
                returned_count=0,
                llm_calls=execution.llm_calls_count,
                execution_time_ms=exec_time,
            )
            return []

        top_evals = validated_evals[: effective_request.top_k]
        pipeline_duration_ms = round((time.perf_counter() - start_time) * 1000.0, 3)
        matched_constraints = [c.type for c in effective_request.constraints if c.is_hard]

        results: List[RecommendationResult] = []
        for ev in top_evals:
            rec_score = RecommendationScore(
                total_score=ev.score,
                score_breakdown=ev.score_breakdown,
            )
            reason = self.reason_builder.build_reason(ev.candidate, effective_request, rec_score)

            debug_info = None
            if effective_request.context.debug_mode:
                debug_info = PipelineDebugInfo(
                    strategy=strategy_used,
                    matched_constraints=matched_constraints,
                    candidate_counts=counts_debug,
                    ranking_duration_ms=ranking_duration_ms,
                    pipeline_duration_ms=pipeline_duration_ms,
                )

            results.append(
                RecommendationResult(
                    candidate=ev.candidate,
                    score=rec_score,
                    reason=reason,
                    debug=debug_info,
                )
            )

        exec_time = round((time.perf_counter() - start_time) * 1000.0, 1)
        TelemetryLogger.log_pipeline_summary(
            request_query=request.context.raw_query or "",
            retrieved_count=len(candidates),
            ranked_count=len(evaluations),
            validated_count=len(validated_evals),
            returned_count=len(results),
            llm_calls=execution.llm_calls_count,
            execution_time_ms=exec_time,
        )

        return results
