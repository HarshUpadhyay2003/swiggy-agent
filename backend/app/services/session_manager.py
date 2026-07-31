"""Lightweight in-memory session memory manager."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

try:
    from app.services.recommendation_engine.models import (
        Constraint,
        ConstraintExpiration,
        ConstraintPriority,
        ConstraintScope,
        ConstraintSource,
        EffectiveRecommendationRequest,
        RecommendationContext,
        RecommendationRequest,
    )
except ImportError:
    from recommendation_engine.models import (
        Constraint,
        ConstraintExpiration,
        ConstraintPriority,
        ConstraintScope,
        ConstraintSource,
        EffectiveRecommendationRequest,
        RecommendationContext,
        RecommendationRequest,
    )

class PlannerState(BaseModel):
    active_plan: Optional[Dict[str, Any]] = None
    preferences: Dict[str, Any] = Field(default_factory=dict)
    rejected_items: List[str] = Field(default_factory=list)

class RecommendationContextMemory(BaseModel):
    query_type: Optional[str] = None
    query_type_source: Optional[str] = None
    query_type_confidence: Optional[float] = None
    meal_type: Optional[str] = None
    budget: Optional[float] = None
    diet: Optional[str] = None
    taste_preference: Optional[str] = None
    cuisine_type: Optional[str] = None
    category: Optional[str] = None
    restaurant: Optional[str] = None
    health_goal: Optional[str] = None
    occasion: Optional[str] = None
    serving: Optional[str] = None
    popularity: Optional[str] = None
    last_recommendations: List[Dict[str, Any]] = Field(default_factory=list)

    def clear_recommendation_context(self) -> List[str]:
        """
        Clears Recommendation Context fields (cuisine, restaurant, meal type, category,
        budget, taste, temporary health goals) while preserving persistent User Preferences
        (vegetarian, vegan, allergies, location).
        Returns list of removed field strings for telemetry audit.
        """
        removed = []
        fields = [
            ("query_type", self.query_type),
            ("meal_type", self.meal_type),
            ("budget", self.budget),
            ("taste_preference", self.taste_preference),
            ("cuisine_type", self.cuisine_type),
            ("category", self.category),
            ("restaurant", self.restaurant),
            ("health_goal", self.health_goal),
            ("occasion", self.occasion),
            ("serving", self.serving),
            ("popularity", self.popularity),
        ]
        for name, val in fields:
            if val is not None:
                removed.append(f"{name}={val}")
                setattr(self, name, None)
        self.query_type_source = None
        self.query_type_confidence = None
        self.last_recommendations = []
        return removed

    def clear_ephemeral(self) -> None:
        """Clear Ephemeral constraints (meal_type, taste_preference, category, health_goal)."""
        self.meal_type = None
        self.taste_preference = None
        self.category = None
        self.health_goal = None

    def clear_session(self) -> None:
        """Clear Session constraints (cuisine_type, diet, restaurant, occasion)."""
        self.cuisine_type = None
        self.diet = None
        self.restaurant = None
        self.occasion = None

    def clear(self) -> None:
        """Reset recommendation memory completely."""
        self.query_type = None
        self.query_type_source = None
        self.query_type_confidence = None
        self.meal_type = None
        self.budget = None
        self.diet = None
        self.taste_preference = None
        self.cuisine_type = None
        self.category = None
        self.restaurant = None
        self.health_goal = None
        self.occasion = None
        self.serving = None
        self.popularity = None
        self.last_recommendations = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query_type": self.query_type,
            "query_type_source": self.query_type_source,
            "query_type_confidence": self.query_type_confidence,
            "meal_type": self.meal_type,
            "budget": self.budget,
            "diet": self.diet,
            "taste_preference": self.taste_preference,
            "cuisine_type": self.cuisine_type,
            "category": self.category,
            "restaurant": self.restaurant,
            "health_goal": self.health_goal,
            "occasion": self.occasion,
            "serving": self.serving,
            "popularity": self.popularity,
        }


class SessionState(BaseModel):
    session_id: str
    active_domain: str = "general" # "general", "planner", "cart", "recommendations"
    planner_state: PlannerState = Field(default_factory=PlannerState)
    recommendation_memory: RecommendationContextMemory = Field(default_factory=RecommendationContextMemory)
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

    def switch_domain(self, domain: str, reason: str = "Intent routing") -> None:
        if domain in ["general", "planner", "cart", "recommendations"] and domain != self.active_domain:
            prev = self.active_domain
            self.active_domain = domain
            print("\n========================================")
            print("DOMAIN TRANSITION REPORT")
            print(f"Previous Domain: {prev}")
            print(f"New Domain     : {domain}")
            print(f"Reason         : {reason}")
            print("========================================\n")

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


class ConstraintLifecycleEngine:
    """
    Stage 3.3 Layer 2 Lifecycle Engine.
    Manages constraint metadata, scopes (EPHEMERAL, SESSION, PERSISTENT),
    expiration rules, and builds the EffectiveRecommendationRequest.
    """

    CONSTRAINT_METADATA: Dict[str, Dict[str, Any]] = {
        "meal_type": {
            "scope": ConstraintScope.SESSION,
            "expires": ConstraintExpiration.DOMAIN_SWITCH,
            "priority": ConstraintPriority.HARD,
        },
        "taste_preference": {
            "scope": ConstraintScope.SESSION,
            "expires": ConstraintExpiration.DOMAIN_SWITCH,
            "priority": ConstraintPriority.HARD,
        },
        "category": {
            "scope": ConstraintScope.SESSION,
            "expires": ConstraintExpiration.DOMAIN_SWITCH,
            "priority": ConstraintPriority.HARD,
        },
        "health_goal": {
            "scope": ConstraintScope.SESSION,
            "expires": ConstraintExpiration.DOMAIN_SWITCH,
            "priority": ConstraintPriority.HARD,
        },
        "serving": {
            "scope": ConstraintScope.SESSION,
            "expires": ConstraintExpiration.DOMAIN_SWITCH,
            "priority": ConstraintPriority.HARD,
        },
        "cuisine_type": {
            "scope": ConstraintScope.SESSION,
            "expires": ConstraintExpiration.DOMAIN_SWITCH,
            "priority": ConstraintPriority.HARD,
        },
        "diet": {
            "scope": ConstraintScope.SESSION,
            "expires": ConstraintExpiration.DOMAIN_SWITCH,
            "priority": ConstraintPriority.HARD,
        },
        "restaurant": {
            "scope": ConstraintScope.SESSION,
            "expires": ConstraintExpiration.DOMAIN_SWITCH,
            "priority": ConstraintPriority.HARD,
        },
        "restaurant_id": {
            "scope": ConstraintScope.SESSION,
            "expires": ConstraintExpiration.DOMAIN_SWITCH,
            "priority": ConstraintPriority.HARD,
        },
        "occasion": {
            "scope": ConstraintScope.SESSION,
            "expires": ConstraintExpiration.DOMAIN_SWITCH,
            "priority": ConstraintPriority.SOFT,
        },
        "query_type": {
            "scope": ConstraintScope.SESSION,
            "expires": ConstraintExpiration.DOMAIN_SWITCH,
            "priority": ConstraintPriority.HARD,
        },
        "max_budget": {
            "scope": ConstraintScope.SESSION,
            "expires": ConstraintExpiration.DOMAIN_SWITCH,
            "priority": ConstraintPriority.HARD,
        },
        "min_budget": {
            "scope": ConstraintScope.SESSION,
            "expires": ConstraintExpiration.DOMAIN_SWITCH,
            "priority": ConstraintPriority.HARD,
        },
        "budget": {
            "scope": ConstraintScope.SESSION,
            "expires": ConstraintExpiration.DOMAIN_SWITCH,
            "priority": ConstraintPriority.HARD,
        },
        "vegan": {
            "scope": ConstraintScope.PERSISTENT,
            "expires": ConstraintExpiration.NEVER,
            "priority": ConstraintPriority.HARD,
        },
        "gluten_free": {
            "scope": ConstraintScope.PERSISTENT,
            "expires": ConstraintExpiration.NEVER,
            "priority": ConstraintPriority.HARD,
        },
        "preference": {
            "scope": ConstraintScope.PERSISTENT,
            "expires": ConstraintExpiration.NEVER,
            "priority": ConstraintPriority.HARD,
        },
        "allergies": {
            "scope": ConstraintScope.PERSISTENT,
            "expires": ConstraintExpiration.NEVER,
            "priority": ConstraintPriority.HARD,
        },
        "location": {
            "scope": ConstraintScope.PERSISTENT,
            "expires": ConstraintExpiration.NEVER,
            "priority": ConstraintPriority.HARD,
        },
    }

    def process_lifecycle(
        self,
        raw_request: RecommendationRequest,
        session_memory: RecommendationContextMemory,
        current_turn: int = 1,
        active_domain: str = "recommendations",
    ) -> EffectiveRecommendationRequest:
        """
        Executes lifecycle rules:
        1. Expire past ephemeral constraints not present in user input.
        2. Execute domain/semantic cleanups.
        3. Merge retained memory constraints with new user explicit constraints.
        4. Update session_memory state.
        5. Return EffectiveRecommendationRequest.
        """
        user_constraints = {c.type: c for c in raw_request.constraints}
        retained_memory_constraints: Dict[str, Constraint] = {}
        ephemeral_cleaned: List[str] = []

        # Convert memory dict into active constraints
        mem_dict = session_memory.to_dict()
        for key, val in mem_dict.items():
            if val is None or key in ["query_type_source", "query_type_confidence"]:
                continue

            c_key = "max_budget" if key == "budget" else key

            meta = self.CONSTRAINT_METADATA.get(
                c_key,
                {
                    "scope": ConstraintScope.SESSION,
                    "expires": ConstraintExpiration.DOMAIN_SWITCH,
                    "priority": ConstraintPriority.HARD,
                },
            )

            # Rule 1: Ephemeral constraints expire on NEXT_TURN unless re-asserted in user_constraints
            if meta["scope"] == ConstraintScope.EPHEMERAL:
                if key not in user_constraints and c_key not in user_constraints:
                    ephemeral_cleaned.append(f"{key} (ephemeral expired)")
                    setattr(session_memory, key, None)
                    continue

            # Rule 2: Session constraints expire on DOMAIN_SWITCH if active_domain changed
            if meta["expires"] == ConstraintExpiration.DOMAIN_SWITCH and active_domain != "recommendations":
                setattr(session_memory, key, None)
                continue

            retained_memory_constraints[c_key] = Constraint(
                type=c_key,
                value=val,
                is_hard=True,
                source=ConstraintSource.MEMORY,
                priority=meta["priority"],
                scope=meta["scope"],
                expires=meta["expires"],
                created_turn=1,
            )

        # Rule 3: Semantic Cleanup
        # If user explicitly specifies a specific item category (e.g., "burgers", "pizzas", "coffee"),
        # clear session cuisine & health_goal if not explicitly re-asserted in current turn.
        new_category = user_constraints.get("category")
        if new_category and str(new_category.value).lower() not in {"meal", "meals", "food"}:
            if "cuisine_type" in retained_memory_constraints and "cuisine_type" not in user_constraints:
                ephemeral_cleaned.append(f"cuisine_type cleared by category '{new_category.value}'")
                retained_memory_constraints.pop("cuisine_type", None)
                session_memory.cuisine_type = None
            if "health_goal" in retained_memory_constraints and "health_goal" not in user_constraints:
                ephemeral_cleaned.append(f"health_goal cleared by category '{new_category.value}'")
                retained_memory_constraints.pop("health_goal", None)
                session_memory.health_goal = None

        # Rule 4: Merge Memory & User constraints (User explicit constraints override memory)
        effective_constraints_map: Dict[str, Constraint] = dict(retained_memory_constraints)

        for key, user_c in user_constraints.items():
            meta = self.CONSTRAINT_METADATA.get(
                key,
                {
                    "scope": ConstraintScope.SESSION,
                    "expires": ConstraintExpiration.DOMAIN_SWITCH,
                    "priority": ConstraintPriority.HARD,
                },
            )
            # Ensure source and metadata are set correctly
            updated_c = Constraint(
                type=user_c.type,
                value=user_c.value,
                is_hard=user_c.is_hard,
                source=ConstraintSource.USER,
                priority=meta["priority"],
                scope=meta["scope"],
                expires=meta["expires"],
                created_turn=current_turn,
            )
            effective_constraints_map[key] = updated_c

            # Update session memory for persistent/session/ephemeral properties
            if hasattr(session_memory, key):
                setattr(session_memory, key, user_c.value)
            elif key == "max_budget":
                session_memory.budget = user_c.value

        effective_list = list(effective_constraints_map.values())

        # Stage 3.4 Part 2 & Part 3 Layer 2 Observability
        print("\n========================================")
        print("LAYER 2: State Lifecycle & Effective Request")
        print("Status: EXECUTED")
        print(f"Memory Before: {mem_dict}")
        print(f"Incoming User: {[f'{c.type}={c.value}' for c in user_constraints.values()]}")
        print(f"Added Constraints: {[f'{c.type}={c.value}' for c in user_constraints.values()]}")
        print(f"Removed Constraints: {ephemeral_cleaned if ephemeral_cleaned else 'none'}")
        print(f"Expired Constraints: {[k for k in ephemeral_cleaned if 'expired' in k] or 'none'}")
        print(f"Retained Constraints: {[f'{k}={c.value}' for k, c in retained_memory_constraints.items()]}")
        print("Constraint Provenance Details:")
        for c in effective_list:
            src_val = c.source.value if hasattr(c.source, "value") else str(c.source)
            scp_val = c.scope.value if hasattr(c.scope, "value") else str(c.scope)
            exp_val = c.expires.value if hasattr(c.expires, "value") else str(c.expires)
            print(f"  - {c.type}: {c.value} | Source: {src_val} | Scope: {scp_val} | Expires: {exp_val}")
        print(f"Memory After: {session_memory.to_dict()}")
        print(f"Effective Request: {[f'{c.type}={c.value}' for c in effective_list]}")
        print("========================================\n")

        return EffectiveRecommendationRequest(
            constraints=effective_list,
            context=raw_request.context,
            top_k=raw_request.top_k,
            raw_user_request=raw_request,
            ephemeral_cleaned=ephemeral_cleaned,
            turn_number=current_turn,
        )

