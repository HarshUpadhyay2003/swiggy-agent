"""
Stage 4F.1 Phase 3 — Suitability Estimator Module.
Calculates independent continuous recommendation suitability (0.0 to 1.0) with non-zero variance.
"""

from app.services.recommendation_engine.semantic_evaluator import SemanticEvidence
from app.services.recommendation_engine.semantic_calibrator import SemanticCalibration


class SuitabilityEstimator:
    """Estimates continuous recommendation suitability (0.0 to 1.0) for candidate items."""

    def estimate_suitability(
        self,
        evidence: SemanticEvidence,
        calibration: SemanticCalibration,
    ) -> float:
        """
        Formula: Suitability = f(overall_similarity, constraint_coverage, conversation_consistency, policy_alignment, required_context_match)
        Returns: continuous float [0.0, 1.0]
        """
        if evidence.forbidden_context:
            return round(0.05 + (0.05 * calibration.domain_similarity), 4)

        if evidence.diet_match == 0.0:
            return 0.00

        policy_penalty = 0.0
        if evidence.policy_violations:
            policy_penalty = min(0.40, 0.15 * len(evidence.policy_violations))

        suitability = (
            (calibration.overall_similarity * 0.40)
            + (evidence.constraint_coverage * 0.25)
            + (evidence.health_match * 0.20)
            + (calibration.context_similarity * 0.15)
            - policy_penalty
        )

        return round(min(max(suitability, 0.05), 1.00), 4)
