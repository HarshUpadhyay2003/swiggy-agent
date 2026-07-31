"""
Stage 4F.1 Semantic Recommendation Intelligence Engine (Layer 5.5).
Orchestrates candidate evaluation through SemanticEvaluator, SemanticCalibrator,
SuitabilityEstimator, AdaptiveDecisionEngine, SemanticMetricsCalculator, and SemanticExplanationEngine.
"""

from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field

from app.services.recommendation_engine.models import (
    CandidateEvaluation,
    RecommendationCandidate,
    RecommendationRequest,
)
from app.services.recommendation_engine.semantic_profile_resolver import SemanticProfile
from app.services.recommendation_engine.semantic_policy_resolver import SemanticPolicy, SemanticPolicyResolver
from app.services.recommendation_engine.semantic_evaluator import SemanticEvaluator, SemanticEvidence
from app.services.recommendation_engine.semantic_calibrator import SemanticCalibrator, SemanticCalibration
from app.services.recommendation_engine.suitability_estimator import SuitabilityEstimator
from app.services.recommendation_engine.decision_engine import AdaptiveDecisionEngine, SemanticDecision
from app.services.recommendation_engine.semantic_metrics import SemanticMetricsCalculator, MetricReport
from app.services.recommendation_engine.semantic_explanation_engine import SemanticExplanationEngine, CandidateExplanation
from app.services.recommendation_engine.conversation_intelligence.recovery_engine import RecoveryEngine


class SemanticCandidateEvaluation(BaseModel):
    """Structured Layer 5.5 evaluation for a candidate."""

    candidate: RecommendationCandidate
    ranking_rank: int
    ranking_score: float
    evidence: SemanticEvidence
    calibration: SemanticCalibration
    suitability_score: float
    decision: SemanticDecision
    explanation: CandidateExplanation


class SemanticTelemetry(BaseModel):
    total_candidates: int = 0
    accepted_candidates: int = 0
    rejected_candidates: int = 0
    borderline_candidates: int = 0
    domain_leakage_count: int = 0
    context_leakage_count: int = 0
    recovery_triggered: bool = False
    avg_semantic_score: float = 0.0
    avg_suitability_score: float = 0.0
    adaptive_threshold: float = 0.70


class SemanticRecommendationEngine:
    """Layer 5.5 Calibrated Semantic Recommendation Decision Engine."""

    def __init__(self) -> None:
        self.policy_resolver = SemanticPolicyResolver()
        self.evaluator = SemanticEvaluator()
        self.calibrator = SemanticCalibrator()
        self.suitability_estimator = SuitabilityEstimator()
        self.decision_engine = AdaptiveDecisionEngine()
        self.metrics_calculator = SemanticMetricsCalculator()
        self.explanation_engine = SemanticExplanationEngine()
        self.recovery_engine = RecoveryEngine()

    def evaluate_and_filter(
        self,
        ranked_evaluations: List[CandidateEvaluation],
        request: RecommendationRequest,
        candidate_retriever: Optional[Any] = None,
        ranking_engine: Optional[Any] = None,
    ) -> Tuple[List[CandidateEvaluation], SemanticTelemetry]:
        query_text = (request.context.raw_query or "").lower()
        policy = self.policy_resolver.resolve_policy(query_text, request.constraints)

        recovery_triggered = False

        if not ranked_evaluations and candidate_retriever:
            recovery_triggered = True
            rec_cands, rec_constraints, _ = self.recovery_engine.attempt_recovery(request, candidate_retriever)
            if rec_cands and ranking_engine:
                rec_req = RecommendationRequest(constraints=rec_constraints, top_k=request.top_k)
                rec_req.context = request.context
                ranked_evaluations = ranking_engine.evaluate_candidates(rec_cands, rec_req)
                request = rec_req

        calibrated_tuples = []
        full_semantic_evals: List[SemanticCandidateEvaluation] = []
        eval_dicts: List[Dict[str, Any]] = []

        for ev in ranked_evaluations:
            cand = ev.candidate
            evidence = self.evaluator.evaluate_evidence(cand, request, policy)
            calibration = self.calibrator.calibrate(evidence, ev.score)
            suitability = self.suitability_estimator.estimate_suitability(evidence, calibration)

            calibrated_tuples.append((evidence, calibration, suitability))

        decisions = self.decision_engine.evaluate_decisions(calibrated_tuples, policy.semantic_threshold)

        accepted_evals: List[CandidateEvaluation] = []
        rejected_evals: List[SemanticCandidateEvaluation] = []

        for idx, ev in enumerate(ranked_evaluations):
            evidence, calibration, suitability = calibrated_tuples[idx]
            decision = decisions[idx]
            explanation = self.explanation_engine.build_explanation(evidence, calibration, decision)

            sem_eval = SemanticCandidateEvaluation(
                candidate=ev.candidate,
                ranking_rank=ev.rank,
                ranking_score=ev.score,
                evidence=evidence,
                calibration=calibration,
                suitability_score=suitability,
                decision=decision,
                explanation=explanation,
            )
            full_semantic_evals.append(sem_eval)

            eval_dicts.append({
                "candidate_id": ev.candidate.item_id,
                "candidate_name": ev.candidate.name,
                "decision": decision.decision,
                "semantic_similarity": calibration.overall_similarity,
                "suitability": suitability,
                "is_forbidden": bool(evidence.forbidden_context),
                "violations": evidence.policy_violations,
            })

            if decision.decision == "ACCEPT":
                ev.ranking_reason = explanation.explanation_text
                accepted_evals.append(ev)
            else:
                rejected_evals.append(sem_eval)

        # Recovery integration if no candidates accepted
        if not accepted_evals and candidate_retriever:
            recovery_triggered = True
            rec_cands, rec_constraints, _ = self.recovery_engine.attempt_recovery(request, candidate_retriever)
            if rec_cands and ranking_engine:
                rec_req = RecommendationRequest(constraints=rec_constraints, top_k=request.top_k)
                rec_req.context = request.context
                rec_ranked = ranking_engine.evaluate_candidates(rec_cands, rec_req)
                for ev in rec_ranked:
                    cand = ev.candidate
                    evidence = self.evaluator.evaluate_evidence(cand, rec_req, policy)
                    if not evidence.forbidden_context:
                        ev.ranking_reason = "Recommended via recovery fallback"
                        accepted_evals.append(ev)

        # Apply semantic diversity reranking on accepted items
        accepted_evals = self._apply_semantic_diversity(accepted_evals)

        for idx, ev in enumerate(accepted_evals, 1):
            ev.rank = idx

        metric_report = self.metrics_calculator.compute_full_report(eval_dicts)

        telemetry = SemanticTelemetry(
            total_candidates=metric_report.total_evaluated,
            accepted_candidates=metric_report.total_accepted,
            rejected_candidates=metric_report.total_rejected,
            borderline_candidates=metric_report.total_borderline,
            domain_leakage_count=metric_report.domain_leakage_count,
            context_leakage_count=metric_report.context_leakage_count,
            recovery_triggered=recovery_triggered,
            avg_semantic_score=metric_report.similarity_mean,
            avg_suitability_score=metric_report.suitability_mean,
            adaptive_threshold=decisions[0].adaptive_threshold if decisions else policy.semantic_threshold,
        )

        self._print_layer_5_5_telemetry(full_semantic_evals, telemetry, policy)

        return accepted_evals, telemetry

    def _apply_semantic_diversity(self, evaluations: List[CandidateEvaluation]) -> List[CandidateEvaluation]:
        if len(evaluations) <= 2:
            return evaluations

        diversified: List[CandidateEvaluation] = []
        pool = list(evaluations)

        seen_restaurants = set()
        seen_parent_categories = set()

        while pool:
            best_idx = 0
            best_score = -999.0

            for idx, ev in enumerate(pool):
                cand = ev.candidate
                penalty = 0.0
                if cand.restaurant_id in seen_restaurants:
                    penalty += 5.0
                if cand.parent_category and cand.parent_category.lower() in seen_parent_categories:
                    penalty += 5.0

                adj_score = ev.score - penalty
                if adj_score > best_score:
                    best_score = adj_score
                    best_idx = idx

            chosen = pool.pop(best_idx)
            diversified.append(chosen)
            seen_restaurants.add(chosen.candidate.restaurant_id)
            if chosen.candidate.parent_category:
                seen_parent_categories.add(chosen.candidate.parent_category.lower())

        return diversified

    def _print_layer_5_5_telemetry(
        self,
        evaluations: List[SemanticCandidateEvaluation],
        telemetry: SemanticTelemetry,
        policy: SemanticPolicy,
    ) -> None:
        print("\n========================================")
        print("SEMANTIC DECISION ENGINE (LAYER 5.5)")
        print("Status: EXECUTED")
        print(f"Active Policy       : {policy.policy_name} (Adaptive Threshold: {telemetry.adaptive_threshold:.4f})")
        print("Candidate Decisions:")
        print(f"  {'Candidate':32s} | {'RankScore':9s} | {'Similarity':10s} | {'Suitability':11s} | {'Confidence':10s} | {'Decision':8s} | Reason")
        print("  " + "-"*110)
        for ev in evaluations[:8]:
            c_name = ev.candidate.name[:32]
            print(f"  {c_name:32s} | {ev.ranking_score:9.1f} | {ev.calibration.overall_similarity*100:9.1f}% | {ev.suitability_score*100:10.1f}% | {ev.decision.confidence*100:9.1f}% | {ev.decision.decision:8s} | {ev.decision.decision_reason[:40]}")

        print("\n----------------------------------------")
        print("LAYER 5.5 TELEMETRY SUMMARY")
        print(f"Total Evaluated     : {telemetry.total_candidates}")
        print(f"Accepted Candidates : {telemetry.accepted_candidates}")
        print(f"Rejected Candidates : {telemetry.rejected_candidates}")
        print(f"Borderline          : {telemetry.borderline_candidates}")
        print(f"Domain Leakage      : {telemetry.domain_leakage_count}")
        print(f"Context Leakage     : {telemetry.context_leakage_count}")
        print(f"Recovery Triggered  : {telemetry.recovery_triggered}")
        print(f"Average Similarity  : {telemetry.avg_semantic_score * 100:.1f}%")
        print(f"Average Suitability : {telemetry.avg_suitability_score * 100:.1f}%")
        print("========================================\n")
