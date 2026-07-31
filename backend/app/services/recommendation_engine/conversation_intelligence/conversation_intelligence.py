"""
Stage 4E Main Conversation Intelligence Engine Module.
Positioned between Layer 2 (State Lifecycle) and Layer 3 (Schema Matcher).
Orchestrates RefinementDetector, ConversationResetDetector, ConstraintPolicyEngine,
RecoveryEngine, and ClarificationEngine.
"""

from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel

from app.services.recommendation_engine.models import Constraint, RecommendationCandidate, RecommendationRequest
from app.services.recommendation_engine.conversation_intelligence.refinement_detector import RefinementDetector, TransitionType
from app.services.recommendation_engine.conversation_intelligence.conversation_reset_detector import ConversationResetDetector
from app.services.recommendation_engine.conversation_intelligence.constraint_policy_engine import ConstraintPolicyEngine
from app.services.recommendation_engine.conversation_intelligence.recovery_engine import RecoveryEngine
from app.services.recommendation_engine.conversation_intelligence.clarification_engine import ClarificationEngine, ClarificationResponse


class ConversationIntelligenceTelemetry(BaseModel):
    previous_state: Dict[str, Any] = {}
    current_state: Dict[str, Any] = {}
    transition_type: str = "REFINEMENT"
    conversation_action: str = "Merge"
    removed_constraints: List[str] = []
    retained_constraints: List[str] = []
    effective_constraints: List[str] = []
    recovery_attempt: str = "None"


class ConversationIntelligenceEngine:
    """Main orchestrator for Layer 2.5 Conversation Intelligence & Recovery Pipeline."""

    def __init__(self) -> None:
        self.refinement_detector = RefinementDetector()
        self.reset_detector = ConversationResetDetector()
        self.policy_engine = ConstraintPolicyEngine()
        self.recovery_engine = RecoveryEngine()
        self.clarification_engine = ClarificationEngine()

    def process(
        self,
        raw_query: str,
        request: RecommendationRequest,
        session_memory: Any,
        candidate_retriever: Any,
        previous_domain: Optional[str] = None,
        current_domain: Optional[str] = None,
    ) -> Tuple[RecommendationRequest, Optional[ClarificationResponse], ConversationIntelligenceTelemetry]:
        """
        Processes conversation intelligence between Layer 2 and Layer 3.
        Returns: (effective_request, clarification_response_if_any, telemetry)
        """
        telemetry = ConversationIntelligenceTelemetry()
        telemetry.previous_state = session_memory.to_dict() if hasattr(session_memory, "to_dict") else {}

        # 1. Classify Transition Type
        cands, _ = candidate_retriever.retrieve_candidates(request)
        cand_count = len(cands)
        active_ctx = session_memory.to_dict() if hasattr(session_memory, "to_dict") else None
        
        transition = self.refinement_detector.classify_transition(
            raw_query,
            request.constraints,
            current_domain or "recommendations",
            previous_domain,
            cand_count,
            active_context=active_ctx,
        )
        
        # Override with Reset Detector if reset phrase is detected
        if self.reset_detector.should_reset_context(raw_query, request.constraints):
            transition = TransitionType.NEW_SEARCH

        telemetry.transition_type = transition.value

        # 2. Handle NEW_SEARCH Context Reset
        removed_context: List[str] = []
        if transition == TransitionType.NEW_SEARCH:
            if hasattr(session_memory, "clear_recommendation_context"):
                removed_context = session_memory.clear_recommendation_context()
            elif hasattr(session_memory, "clear_session"):
                session_memory.clear_session()
                session_memory.clear_ephemeral()
            telemetry.conversation_action = "Reset"
            telemetry.removed_constraints = removed_context

        # 3. Check for Ambiguity & Clarification
        clarification = self.clarification_engine.check_ambiguity(raw_query, request.constraints)
        if clarification and transition not in (TransitionType.NEW_SEARCH, TransitionType.RECOVERY):
            telemetry.transition_type = TransitionType.CLARIFICATION.value
            telemetry.conversation_action = "Clarify"
            telemetry.current_state = session_memory.to_dict() if hasattr(session_memory, "to_dict") else {}
            telemetry.effective_constraints = [f"{c.type}={c.value}" for c in request.constraints]
            self._print_telemetry(raw_query, telemetry, session_memory)
            return request, clarification, telemetry

        # 4. Handle Recovery if 0 candidates returned
        if cand_count == 0:
            rec_cands, rec_constraints, rec_expl = self.recovery_engine.attempt_recovery(request, candidate_retriever)
            rec_request = RecommendationRequest(constraints=rec_constraints, top_k=request.top_k)
            rec_request.context = request.context
            telemetry.conversation_action = "Recover"
            telemetry.recovery_attempt = rec_expl
            telemetry.effective_constraints = [f"{c.type}={c.value}" for c in rec_constraints]
            telemetry.current_state = session_memory.to_dict() if hasattr(session_memory, "to_dict") else {}
            self._print_telemetry(raw_query, telemetry, session_memory)
            return rec_request, None, telemetry

        if transition != TransitionType.NEW_SEARCH:
            telemetry.conversation_action = "Merge"

        telemetry.effective_constraints = [f"{c.type}={c.value}" for c in request.constraints]
        telemetry.current_state = session_memory.to_dict() if hasattr(session_memory, "to_dict") else {}
        self._print_telemetry(raw_query, telemetry, session_memory)
        return request, None, telemetry

    def _print_telemetry(self, raw_query: str, telemetry: ConversationIntelligenceTelemetry, session_memory: Any) -> None:
        """Emits structured Conversation Intelligence telemetry block per Objective 7."""
        # Calculate retained context & persistent user preferences
        mem_dict = session_memory.to_dict() if hasattr(session_memory, "to_dict") else {}
        retained_context = [f"{k}={v}" for k, v in mem_dict.items() if v is not None and k not in ("diet", "vegan", "gluten_free", "allergies", "location")]
        retained_user_prefs = [f"{k}={v}" for k, v in mem_dict.items() if v is not None and k in ("diet", "vegan", "gluten_free", "allergies", "location")]

        print("\n=================================")
        print("Conversation Transition")
        print(f"Input                  : {raw_query}")
        print(f"Classification         : {telemetry.transition_type}")
        print(f"Recommendation Context Removed : {telemetry.removed_constraints if telemetry.removed_constraints else 'None'}")
        print(f"Recommendation Context Retained: {retained_context if retained_context else 'None'}")
        print(f"User Preferences Retained      : {retained_user_prefs if retained_user_prefs else 'None'}")
        print(f"Effective Request      : {telemetry.effective_constraints}")
        print("=================================\n")

