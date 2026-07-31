"""
Stage 4E Constraint Policy Engine Module.
Defines centralized Priority, Scope, Lifetime, Reset Policy, and Recovery Policy
for every constraint type without hardcoding special cases.
"""

from typing import Any, Dict, List, Optional
from enum import Enum


class ConstraintScope(str, Enum):
    EPHEMERAL = "EPHEMERAL"       # Next turn expiration
    SESSION = "SESSION"           # Domain switch expiration
    PERSISTENT = "PERSISTENT"     # Never expires automatically


class ConstraintLifetime(str, Enum):
    NEXT_TURN = "NEXT_TURN"
    DOMAIN_SWITCH = "DOMAIN_SWITCH"
    NEVER = "NEVER"


class ConstraintPolicy:
    """Policy definition for a single constraint type."""

    def __init__(
        self,
        constraint_type: str,
        scope: ConstraintScope,
        lifetime: ConstraintLifetime,
        priority: int,
        is_recoverable: bool,
        is_protected_dietary: bool = False,
    ):
        self.constraint_type = constraint_type
        self.scope = scope
        self.lifetime = lifetime
        self.priority = priority
        self.is_recoverable = is_recoverable
        self.is_protected_dietary = is_protected_dietary


class ConstraintPolicyEngine:
    """Centralized policy engine managing constraint lifecycles and recovery rules."""

    POLICIES: Dict[str, ConstraintPolicy] = {
        "cuisine_type": ConstraintPolicy("cuisine_type", ConstraintScope.SESSION, ConstraintLifetime.DOMAIN_SWITCH, priority=80, is_recoverable=True),
        "cuisine": ConstraintPolicy("cuisine", ConstraintScope.SESSION, ConstraintLifetime.DOMAIN_SWITCH, priority=80, is_recoverable=True),
        "meal_type": ConstraintPolicy("meal_type", ConstraintScope.EPHEMERAL, ConstraintLifetime.NEXT_TURN, priority=60, is_recoverable=True),
        "max_budget": ConstraintPolicy("max_budget", ConstraintScope.PERSISTENT, ConstraintLifetime.NEVER, priority=90, is_recoverable=True),
        "budget": ConstraintPolicy("budget", ConstraintScope.PERSISTENT, ConstraintLifetime.NEVER, priority=90, is_recoverable=True),
        "health_goal": ConstraintPolicy("health_goal", ConstraintScope.EPHEMERAL, ConstraintLifetime.NEXT_TURN, priority=70, is_recoverable=True),
        "healthy_only": ConstraintPolicy("healthy_only", ConstraintScope.EPHEMERAL, ConstraintLifetime.NEXT_TURN, priority=70, is_recoverable=True),
        "category": ConstraintPolicy("category", ConstraintScope.SESSION, ConstraintLifetime.DOMAIN_SWITCH, priority=75, is_recoverable=True),
        "taste_preference": ConstraintPolicy("taste_preference", ConstraintScope.EPHEMERAL, ConstraintLifetime.NEXT_TURN, priority=50, is_recoverable=True),
        "taste": ConstraintPolicy("taste", ConstraintScope.EPHEMERAL, ConstraintLifetime.NEXT_TURN, priority=50, is_recoverable=True),
        "diet": ConstraintPolicy("diet", ConstraintScope.PERSISTENT, ConstraintLifetime.NEVER, priority=100, is_recoverable=False, is_protected_dietary=True),
        "preference": ConstraintPolicy("preference", ConstraintScope.PERSISTENT, ConstraintLifetime.NEVER, priority=100, is_recoverable=False, is_protected_dietary=True),
        "vegan": ConstraintPolicy("vegan", ConstraintScope.PERSISTENT, ConstraintLifetime.NEVER, priority=100, is_recoverable=False, is_protected_dietary=True),
        "gluten_free": ConstraintPolicy("gluten_free", ConstraintScope.PERSISTENT, ConstraintLifetime.NEVER, priority=100, is_recoverable=False, is_protected_dietary=True),
        "restaurant_id": ConstraintPolicy("restaurant_id", ConstraintScope.SESSION, ConstraintLifetime.DOMAIN_SWITCH, priority=85, is_recoverable=True),
        "restaurant": ConstraintPolicy("restaurant", ConstraintScope.SESSION, ConstraintLifetime.DOMAIN_SWITCH, priority=85, is_recoverable=True),
    }

    def get_policy(self, constraint_type: str) -> ConstraintPolicy:
        c_key = str(constraint_type).lower()
        return self.POLICIES.get(c_key, ConstraintPolicy(c_key, ConstraintScope.EPHEMERAL, ConstraintLifetime.NEXT_TURN, priority=50, is_recoverable=True))

    def is_protected_dietary(self, constraint_type: str) -> bool:
        return self.get_policy(constraint_type).is_protected_dietary
