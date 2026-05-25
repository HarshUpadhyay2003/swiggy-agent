"""Lightweight in-memory session memory manager."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class PlannerState(BaseModel):
    active_plan: Optional[Dict[str, Any]] = None
    preferences: Dict[str, Any] = Field(default_factory=dict)
    rejected_items: List[str] = Field(default_factory=list)

class SessionState(BaseModel):
    session_id: str
    active_domain: str = "general" # "general", "planner", "cart", "recommendations"
    planner_state: PlannerState = Field(default_factory=PlannerState)
    active_cart: Optional[Dict[str, Any]] = None
    last_intent: Optional[str] = None
    last_action: Optional[str] = None
    user_preferences: Dict[str, Any] = Field(default_factory=dict)
    pending_constraints: Dict[str, Any] = Field(default_factory=dict)
    messages: List[Dict[str, Any]] = Field(default_factory=list)
    last_order: Optional[Dict[str, Any]] = None
    last_recommendations: List[Dict[str, Any]] = Field(default_factory=list)
    last_meal_plan: Optional[Dict[str, Any]] = None
    last_cart_action: Optional[str] = None
    last_cart_items: List[Dict[str, Any]] = Field(default_factory=list)
    last_checkout: Optional[Dict[str, Any]] = None
    favorite_items: List[str] = Field(default_factory=list)
    frequently_ordered: List[str] = Field(default_factory=list)

    def switch_domain(self, domain: str) -> None:
        if domain in ["general", "planner", "cart", "recommendations"]:
            self.active_domain = domain

    # Dictionary compatibility methods for backward compatibility
    def __getitem__(self, item: str) -> Any:
        return getattr(self, item)
        
    def __setitem__(self, key: str, value: Any) -> None:
        setattr(self, key, value)
        
    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key, default)

class SessionManager:
    """Manage lightweight in-memory conversational session state."""

    def __init__(self) -> None:
        self.sessions: Dict[str, SessionState] = {}

    def create_session(self, session_id: str) -> SessionState:
        if session_id not in self.sessions:
            self.sessions[session_id] = SessionState(session_id=session_id)
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
    ) -> SessionState:
        session = self.create_session(session_id)
        self._append_message(session, "user", user_message)
        self._append_message(session, "assistant", assistant_response)
        session.last_intent = intent
        session.last_action = intent

        # Active Domain Switching
        if intent in ("place_order", "checkout_cart", "add_to_cart", "remove_from_cart", "view_cart", "reorder_action"):
            session.switch_domain("cart")
            if data.get("order"):
                session.last_order = data["order"]
                if intent in ("place_order", "checkout_cart"):
                    session.last_checkout = data["order"]
                for item in data["order"].get("items", []):
                    name = item.get("name")
                    if name and name not in session.frequently_ordered:
                        session.frequently_ordered.append(name)
                        session.favorite_items.append(name)
            if data.get("cart") and data["cart"].get("items"):
                session.last_cart_items = data["cart"]["items"]
        elif intent in ("food_recommendation", "healthy_suggestions"):
            session.switch_domain("recommendations")
            session.last_recommendations = data.get("recommendations", [])
        elif intent in ("meal_planning", "modify_meal_plan", "show_meal_plan"):
            session.switch_domain("planner")
            session.last_meal_plan = data.get("meal_plan") or session.last_meal_plan
            if session.last_meal_plan:
                session.planner_state.active_plan = session.last_meal_plan

        if "active_cart" in data:
            session.active_cart = data.get("active_cart")
        if "last_cart_action" in data:
            session.last_cart_action = data.get("last_cart_action")

        return session

    def get_session_context(self, session_id: str) -> Optional[SessionState]:
        return self.sessions.get(session_id)

    def _append_message(self, session: SessionState, role: str, text: str) -> None:
        session.messages.append(
            {
                "role": role,
                "text": text,
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }
        )
        if len(session.messages) > 20:
            session.messages = session.messages[-20:]
