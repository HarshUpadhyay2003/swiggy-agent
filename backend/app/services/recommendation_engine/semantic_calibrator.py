"""
Stage 4F.1 Phase 2 — Semantic Calibrator Module.
Transforms raw SemanticEvidence into smooth, continuous similarity curves, eliminating score clustering.
"""

import math
from pydantic import BaseModel
from app.services.recommendation_engine.semantic_evaluator import SemanticEvidence


class SemanticCalibration(BaseModel):
    """Continuous similarity metrics calculated from SemanticEvidence."""

    domain_similarity: float
    context_similarity: float
    conversation_similarity: float
    intent_similarity: float
    constraint_similarity: float
    overall_similarity: float


class SemanticCalibrator:
    """Computes continuous, non-clustered similarity curves from SemanticEvidence."""

    def calibrate(self, evidence: SemanticEvidence, ranking_score: float = 70.0) -> SemanticCalibration:
        # Smooth continuous domain curve
        raw_d = evidence.domain_match
        if evidence.forbidden_context:
            domain_sim = 0.08 + (0.04 * (ranking_score / 100.0))
        elif raw_d >= 0.95:
            domain_sim = 0.90 + (0.10 * (ranking_score / 100.0))
        elif raw_d >= 0.70:
            domain_sim = 0.75 + (0.15 * (ranking_score / 100.0))
        else:
            domain_sim = 0.35 + (0.25 * (ranking_score / 100.0))

        domain_sim = round(min(max(domain_sim, 0.05), 1.00), 4)

        # Smooth continuous context curve
        raw_ctx = (evidence.meal_match * 0.6) + (evidence.cuisine_match * 0.4)
        context_sim = round(min(max(raw_ctx * (0.85 + 0.15 * (ranking_score / 100.0)), 0.10), 1.00), 4)

        # Smooth continuous conversation curve
        conv_sim = round(evidence.conversation_match * (0.90 + 0.10 * (ranking_score / 100.0)), 4)

        # Smooth continuous intent similarity
        intent_sim = round((domain_sim * 0.50) + (context_sim * 0.30) + (evidence.health_match * 0.20), 4)

        # Constraint similarity
        constraint_sim = round((evidence.constraint_coverage * 0.70) + (evidence.diet_match * 0.30), 4)

        # Weighted aggregate overall similarity
        overall_sim = round(
            (domain_sim * 0.35)
            + (context_sim * 0.25)
            + (intent_sim * 0.20)
            + (constraint_sim * 0.10)
            + (conv_sim * 0.10),
            4
        )

        return SemanticCalibration(
            domain_similarity=domain_sim,
            context_similarity=context_sim,
            conversation_similarity=conv_sim,
            intent_similarity=intent_sim,
            constraint_similarity=constraint_sim,
            overall_similarity=overall_sim,
        )
