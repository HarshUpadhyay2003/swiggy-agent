"""
Stage 4F.1 Phase 6 — Evidence-Based Explanation Engine.
Generates structured candidate explanations derived solely from evaluated SemanticEvidence.
"""

from typing import List
from pydantic import BaseModel
from app.services.recommendation_engine.semantic_evaluator import SemanticEvidence
from app.services.recommendation_engine.semantic_calibrator import SemanticCalibration
from app.services.recommendation_engine.decision_engine import SemanticDecision


class CandidateExplanation(BaseModel):
    candidate_id: int
    candidate_name: str
    decision: str
    explanation_text: str
    intent_similarity_pct: float
    meal_context_pct: float
    budget_fitness_pct: float
    conversation_consistency_pct: float
    protected_constraints_satisfied: bool
    semantic_confidence_pct: float
    evidence_items: List[str]


class SemanticExplanationEngine:
    """Generates 100% evidence-based explanations directly from SemanticEvidence."""

    def build_explanation(
        self,
        evidence: SemanticEvidence,
        calibration: SemanticCalibration,
        decision: SemanticDecision,
    ) -> CandidateExplanation:
        evidence_items = []
        if evidence.policy_matches:
            evidence_items.extend(evidence.policy_matches)

        if evidence.constraint_coverage >= 0.80:
            evidence_items.append(f"Satisfied {evidence.constraint_coverage*100:.0f}% of active request constraints")

        if evidence.diet_match == 1.00:
            evidence_items.append("Protected dietary constraints satisfied")

        if decision.decision == "ACCEPT":
            exp_text = f"Recommended based on {calibration.intent_similarity*100:.0f}% intent match and {decision.suitability*100:.0f}% suitability. Matches: {', '.join(evidence_items[:2])}."
        elif decision.decision == "BORDERLINE":
            exp_text = f"Borderline recommendation ({calibration.overall_similarity*100:.0f}% similarity). Reviewing near threshold ({decision.adaptive_threshold*100:.0f}%)."
        else:
            violations_str = ", ".join(evidence.policy_violations) if evidence.policy_violations else "Below dynamic semantic threshold"
            exp_text = f"Not recommended: {violations_str}."

        return CandidateExplanation(
            candidate_id=evidence.candidate_id,
            candidate_name=evidence.candidate_name,
            decision=decision.decision,
            explanation_text=exp_text,
            intent_similarity_pct=round(calibration.intent_similarity * 100.0, 1),
            meal_context_pct=round(evidence.meal_match * 100.0, 1),
            budget_fitness_pct=round(evidence.constraint_coverage * 100.0, 1),
            conversation_consistency_pct=round(evidence.conversation_match * 100.0, 1),
            protected_constraints_satisfied=evidence.diet_match == 1.00,
            semantic_confidence_pct=round(decision.confidence * 100.0, 1),
            evidence_items=evidence_items,
        )
