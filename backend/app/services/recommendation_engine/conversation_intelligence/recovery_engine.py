"""
Stage 4E / 4F Recovery Engine Module.
Multi-step recovery pipeline when CandidateRetriever returns 0 candidates:
  Attempt 1: Original request.
  Attempt 2: Relax recoverable budget/price constraint.
  Attempt 3: Relax optional constraints (taste, meal_type).
  Attempt 4: Suggest nearest valid catalog alternatives.
NEVER relaxes protected dietary safety constraints (vegetarian, vegan, gluten-free, diet).
"""

from typing import Any, Dict, List, Optional, Tuple
from app.services.recommendation_engine.models import Constraint, RecommendationCandidate, RecommendationRequest
from app.services.recommendation_engine.conversation_intelligence.constraint_policy_engine import ConstraintPolicyEngine


class RecoveryEngine:
    """Multi-attempt recovery pipeline for zero-retrieval candidate scenarios."""

    def __init__(self) -> None:
        self.policy_engine = ConstraintPolicyEngine()

    def attempt_recovery(
        self,
        request: RecommendationRequest,
        candidate_retriever: Any,
    ) -> Tuple[List[RecommendationCandidate], List[Constraint], str]:
        """
        Executes multi-step constraint relaxation recovery to find nearest valid recommendations.
        Returns: (recovered_candidates, active_constraints_after_recovery, recovery_explanation)
        """
        original_constraints = list(request.constraints)

        # Attempt 1: Original Request (already failed)

        # Attempt 2: Relax Budget constraint (e.g. increase max_budget by 50% or remove max_budget)
        relaxed_c2 = [
            c for c in original_constraints
            if c.type not in {"max_budget", "budget"}
        ]
        if len(relaxed_c2) < len(original_constraints):
            req_c2 = RecommendationRequest(constraints=relaxed_c2, top_k=request.top_k)
            req_c2.context = request.context
            cands, _ = candidate_retriever.retrieve_candidates(req_c2)
            if cands:
                return cands, relaxed_c2, "Recovered by relaxing budget constraint"

        # Attempt 3: Relax Optional constraints (taste, meal_type) while preserving protected dietary & cuisine
        relaxed_c3 = [
            c for c in original_constraints
            if c.type not in {"max_budget", "budget", "taste", "taste_preference", "meal_type"} or self.policy_engine.is_protected_dietary(c.type)
        ]
        if len(relaxed_c3) < len(original_constraints):
            req_c3 = RecommendationRequest(constraints=relaxed_c3, top_k=request.top_k)
            req_c3.context = request.context
            cands, _ = candidate_retriever.retrieve_candidates(req_c3)
            if cands:
                return cands, relaxed_c3, "Recovered by relaxing optional taste and meal constraints"

        # Attempt 4: Fallback to protected dietary safety constraints only (e.g. diet=veg)
        dietary_only = [
            c for c in original_constraints
            if self.policy_engine.is_protected_dietary(c.type)
        ]
        if dietary_only:
            req_c4 = RecommendationRequest(constraints=dietary_only, top_k=request.top_k)
            req_c4.context = request.context
            cands, _ = candidate_retriever.retrieve_candidates(req_c4)
            if cands:
                return cands, dietary_only, "Recovered by suggesting nearest valid dietary options"

        # Universal fallback to top catalog items
        req_fallback = RecommendationRequest(constraints=[], top_k=request.top_k)
        req_fallback.context = request.context
        cands, _ = candidate_retriever.retrieve_candidates(req_fallback)
        return cands, [], "Fallback to top catalog recommendations"
