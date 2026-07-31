"""
Stage 4F.1 Phase 4 — Adaptive Decision Engine Module.
Calculates distribution-aware adaptive thresholds and makes ACCEPT / REJECT / BORDERLINE decisions.
"""

from typing import List, Tuple
from pydantic import BaseModel
from app.services.recommendation_engine.semantic_evaluator import SemanticEvidence
from app.services.recommendation_engine.semantic_calibrator import SemanticCalibration


class SemanticDecision(BaseModel):
    """Structured decision output for a candidate."""

    candidate_id: int
    decision: str  # ACCEPT, REJECT, BORDERLINE
    semantic_similarity: float
    suitability: float
    confidence: float
    adaptive_threshold: float
    decision_reason: str


class AdaptiveDecisionEngine:
    """Makes distribution-aware recommendation decisions using dynamic thresholds."""

    def evaluate_decisions(
        self,
        calibrated_evals: List[Tuple[SemanticEvidence, SemanticCalibration, float]],
        policy_minimum_threshold: float = 0.70,
    ) -> List[SemanticDecision]:
        if not calibrated_evals:
            return []

        similarities = [cal.overall_similarity for _, cal, _ in calibrated_evals]
        similarities_sorted = sorted(similarities)

        # 70th percentile calculation
        idx_70 = int(len(similarities_sorted) * 0.70)
        perc_70 = similarities_sorted[min(idx_70, len(similarities_sorted) - 1)]

        mean_sim = sum(similarities) / len(similarities)
        variance = sum((s - mean_sim) ** 2 for s in similarities) / len(similarities)
        stddev = variance ** 0.5

        # Dynamic distribution adjustment
        dist_adj = mean_sim - (0.5 * stddev)

        # Adaptive threshold: max(policy_minimum, 70th_percentile, dist_adj), capped at 0.95 max
        raw_thresh = max(policy_minimum_threshold, min(perc_70, policy_minimum_threshold + 0.10), dist_adj)
        adaptive_threshold = round(min(max(raw_thresh, policy_minimum_threshold), 0.95), 4)


        decisions: List[SemanticDecision] = []
        for ev, cal, suit in calibrated_evals:
            sim = cal.overall_similarity
            conf = round(min(max((sim * 0.5) + (suit * 0.3) + (ev.constraint_coverage * 0.2), 0.10), 0.99), 4)

            decision = "REJECT"
            reason = ""

            if ev.forbidden_context:
                decision = "REJECT"
                reason = f"Rejected: Matches forbidden domain '{', '.join(ev.forbidden_context)}'"
            elif ev.diet_match == 0.0:
                decision = "REJECT"
                reason = "Rejected: Violates protected dietary constraint"
            elif sim >= adaptive_threshold and suit >= 0.60:
                decision = "ACCEPT"
                reason = f"Accepted: High semantic similarity ({sim*100:.1f}%) & suitability ({suit*100:.1f}%)"
            elif sim >= (adaptive_threshold - 0.08) and suit >= 0.50:
                decision = "BORDERLINE"
                reason = f"Borderline: Moderate similarity ({sim*100:.1f}%) near threshold ({adaptive_threshold*100:.1f}%)"
            else:
                decision = "REJECT"
                reason = f"Rejected: Similarity ({sim*100:.1f}%) below threshold ({adaptive_threshold*100:.1f}%)"

            decisions.append(
                SemanticDecision(
                    candidate_id=ev.candidate_id,
                    decision=decision,
                    semantic_similarity=sim,
                    suitability=suit,
                    confidence=conf,
                    adaptive_threshold=adaptive_threshold,
                    decision_reason=reason,
                )
            )

        return decisions
