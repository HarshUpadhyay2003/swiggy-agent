"""
Stage 4E Conversation Reset Detector Module.
Detects when recommendation context should disappear (e.g. generic fresh searches like
"I'm hungry", "Surprise me") while preserving persistent user preferences.
"""

from typing import Any, Dict, List, Optional


class ConversationResetDetector:
    """Detects when recommendation context memory should be cleared for fresh searches."""

    GENERIC_RESET_PHRASES = [
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
        "recommend dinner",
        "suggest meals",
        "show popular meals",
        "find me dinner",
        "find me lunch",
        "find me breakfast",
        "surprise me",
        "start over",
        "reset",
        "clear",
        "new search",
    ]

    def should_reset_context(self, raw_query: str, extracted_constraints: List[Any]) -> bool:
        """Returns True if the prompt indicates a fresh search context reset."""
        query_lower = (raw_query or "").lower().strip()
        # Do not reset if explicit refinement connector exists (e.g. "suggest dinner under 300" when active context exists)
        if any(conn in query_lower for conn in ["under", "cheaper", "below", "less than", "spicy", "instead"]):
            return False
        if any(phrase in query_lower for phrase in self.GENERIC_RESET_PHRASES):
            return True
        return False

