"""
Stage 4F Semantic Policy Resolver Module.
Resolves domain-level policies and attribute filtering thresholds.
Operates strictly on dataset metadata attributes (query_type, parent_category, cuisine_type,
meal_type, category, health_goal, context_tags, decision_factors), never item names.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.services.recommendation_engine.semantic_profile_resolver import SemanticProfile, SemanticProfileResolver


class SemanticPolicy(BaseModel):
    """Dataset-attribute-based recommendation policy."""

    policy_name: str
    semantic_threshold: float = 0.70
    suitability_threshold: float = 0.60
    profile: SemanticProfile
    allow_secondary_domain: bool = True
    enforce_meal_context: bool = False
    diversity_diversity_strategy: str = "balanced"


class SemanticPolicyResolver:
    """Resolves policy configuration per recommendation request."""

    def __init__(self) -> None:
        self.profile_resolver = SemanticProfileResolver()

    def resolve_policy(self, query_text: str, constraints: List[Any]) -> SemanticPolicy:
        profile = self.profile_resolver.resolve_profile(query_text, constraints)

        enforce_meal = any(c.type == "meal_type" for c in constraints) or "dinner" in query_text.lower() or "lunch" in query_text.lower()

        return SemanticPolicy(
            policy_name=f"Policy for {profile.profile_name}",
            semantic_threshold=profile.minimum_semantic_score,
            suitability_threshold=profile.minimum_suitability_score,
            profile=profile,
            allow_secondary_domain=True,
            enforce_meal_context=enforce_meal,
            diversity_diversity_strategy="balanced",
        )
