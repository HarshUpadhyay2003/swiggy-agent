"""
Stage 4E / RC1 Refinement Detector Module.
Deterministically classifies conversation transition types into REFINEMENT, NEW_SEARCH,
DOMAIN_SWITCH, RECOVERY, or CLARIFICATION without LLM dependency.
"""

from typing import Any, Dict, List, Optional
from enum import Enum


class TransitionType(str, Enum):
    REFINEMENT = "REFINEMENT"
    NEW_SEARCH = "NEW_SEARCH"
    DOMAIN_SWITCH = "DOMAIN_SWITCH"
    RECOVERY = "RECOVERY"
    CLARIFICATION = "CLARIFICATION"


class RefinementDetector:
    """Deterministic transition classifier for user inputs."""

    RESET_PHRASES = [
        "never mind",
        "forget that",
        "actually",
        "recommend",
        "find",
        "show me",
        "i'm hungry",
        "give me",
        "suggest",
        "anything good",
        "start over",
        "reset",
        "clear",
        "new search",
        "suggest meals",
        "recommend dinner",
        "show popular meals",
    ]

    REFINEMENT_CONNECTORS = [
        "instead",
        "under",
        "below",
        "less than",
        "cheaper",
        "more expensive",
        "make it",
        "only",
        "also",
        "with",
        "without",
        "add",
        "extra",
        "spicy",
        "budget",
    ]

    def classify_transition(
        self,
        new_query: str,
        new_constraints: List[Any],
        current_domain: str,
        previous_domain: Optional[str] = None,
        candidate_count: int = 1,
        active_context: Optional[Dict[str, Any]] = None,
    ) -> TransitionType:
        query_text = (new_query or "").lower().strip()

        # 1. Recovery Check (candidate pool = 0)
        if candidate_count == 0:
            return TransitionType.RECOVERY

        # 2. Domain Switch Check
        if previous_domain and current_domain and previous_domain != current_domain and current_domain not in ("FOOD", "recommendations"):
            return TransitionType.DOMAIN_SWITCH

        # 3. Explicit Reset Phrases Check -> NEW_SEARCH
        if any(phrase in query_text for phrase in self.RESET_PHRASES):
            # Check if this reset phrase is part of a refinement (e.g. "recommend dinner under 300" when active context exists)
            has_refinement_connector = any(conn in query_text for conn in self.REFINEMENT_CONNECTORS)
            if not has_refinement_connector and ("recommend dinner" in query_text or "suggest meals" in query_text or "show popular" in query_text or "never mind" in query_text or "forget that" in query_text or "i'm hungry" in query_text or "anything good" in query_text):
                return TransitionType.NEW_SEARCH

        # 4. Ambiguity / Clarification Check
        ambiguous_prompts = {"food", "something", "anything"}
        if query_text in ambiguous_prompts and not new_constraints and not active_context:
            return TransitionType.CLARIFICATION

        # 5. Check if query is a pure refinement on active context
        has_connector = any(conn in query_text for conn in self.REFINEMENT_CONNECTORS)
        
        # Check extracted constraint types
        extracted_types = {c.type if hasattr(c, "type") else str(c) for c in new_constraints} if new_constraints else set()

        # If user specifies explicit refinement markers (e.g., "instead", "under 300", "make it spicy", "only veg")
        if has_connector or (extracted_types and extracted_types.issubset({"max_budget", "min_budget", "budget", "taste_preference", "spicy"})):
            return TransitionType.REFINEMENT

        # 6. Check for primary concept switch (e.g. "Dessert under 100" -> "Italian meals", or "Italian meals" -> "Desserts", or "Pizza" -> "Coffee")
        if active_context and any(v is not None for k, v in active_context.items() if k in ("cuisine_type", "category", "restaurant", "budget")):
            # If new primary constraints are introduced without refinement connectors ("instead", "make it", "under")
            new_primary = extracted_types.intersection({"cuisine_type", "category", "restaurant", "meal_type"})
            if new_primary and not has_connector:
                # E.g. "Italian meals" after "Dessert under 100", or "Desserts" after "Italian meals"
                return TransitionType.NEW_SEARCH

        # Fallback for fresh search without prior context
        if not active_context or not any(v is not None for v in active_context.values()):
            return TransitionType.NEW_SEARCH

        return TransitionType.REFINEMENT

