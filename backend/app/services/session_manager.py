"""Lightweight in-memory session memory manager."""

from datetime import datetime
from typing import Any, Dict, List, Optional


class SessionManager:
    """Manage lightweight in-memory conversational session state."""

    def __init__(self) -> None:
        self.sessions: Dict[str, Dict[str, Any]] = {}

    def create_session(self, session_id: str) -> Dict[str, Any]:
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "session_id": session_id,
                "messages": [],
                "last_intent": None,
                "last_order": None,
                "last_recommendations": [],
                "last_meal_plan": None,
                "active_cart": None,
                "last_cart_action": None,
            }
        return self.sessions[session_id]

    def clear_session(self, session_id: str) -> None:
        self.sessions.pop(session_id, None)

    def add_interaction(
        self,
        session_id: str,
        user_message: str,
        assistant_response: str,
        intent: str,
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        session = self.create_session(session_id)
        self._append_message(session, "user", user_message)
        self._append_message(session, "assistant", assistant_response)
        session["last_intent"] = intent

        if intent in ("place_order", "checkout_cart"):
            session["last_order"] = data.get("order") or session.get("last_order")
        elif intent in ("food_recommendation", "healthy_suggestions"):
            session["last_recommendations"] = data.get("recommendations", [])
        elif intent == "meal_planning":
            session["last_meal_plan"] = data.get("meal_plan")

        if "active_cart" in data:
            session["active_cart"] = data.get("active_cart")
        if "last_cart_action" in data:
            session["last_cart_action"] = data.get("last_cart_action")

        return session

    def get_session_context(self, session_id: str) -> Optional[Dict[str, Any]]:
        return self.sessions.get(session_id)

    def _append_message(self, session: Dict[str, Any], role: str, text: str) -> None:
        session["messages"].append(
            {
                "role": role,
                "text": text,
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }
        )
        if len(session["messages"]) > 20:
            session["messages"] = session["messages"][-20:]
