"""Pydantic data models for Generalized Recommendation Engine (Stage 2B)."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class Constraint(BaseModel):
    """Generalized constraint representing a single eligibility filter."""
    type: str  # e.g., "budget", "preference", "meal_type", "health_goal", "restaurant", "spicy", "vegan", "gluten_free"
    value: Any
    is_hard: bool = True


class RecommendationContext(BaseModel):
    """Contextual signal information that influences ranking without restricting eligibility."""
    session_id: Optional[str] = None
    time_of_day: Optional[str] = None  # "morning", "afternoon", "evening", "late_night"
    conversation_state: Dict[str, Any] = Field(default_factory=dict)
    order_history: List[int] = Field(default_factory=list)
    favorite_restaurant_ids: List[int] = Field(default_factory=list)
    debug_mode: bool = False


class RecommendationRequest(BaseModel):
    """Structured recommendation request containing generalized constraints & context."""
    constraints: List[Constraint] = Field(default_factory=list)
    context: RecommendationContext = Field(default_factory=RecommendationContext)
    top_k: int = 5

    def get_constraint(self, constraint_type: str) -> Optional[Constraint]:
        """Utility to retrieve constraint by type if present."""
        for c in self.constraints:
            if c.type == constraint_type:
                return c
        return None

    def get_constraint_value(self, constraint_type: str, default: Any = None) -> Any:
        """Utility to retrieve constraint value by type."""
        c = self.get_constraint(constraint_type)
        return c.value if c is not None else default


class RecommendationCandidate(BaseModel):
    """Raw candidate item retrieved from catalog."""
    item_id: int
    name: str
    description: str = ""
    price: int
    available: bool = True
    category: str  # "veg" or "non-veg"
    meal_type: str
    healthy: bool = False
    vegetarian: bool = True
    high_protein: bool = False
    spicy: bool = False
    vegan: bool = False
    low_calorie: bool = False
    gluten_free: bool = False
    restaurant_id: Optional[int] = None
    restaurant_name: str = ""
    cuisine: str = ""
    raw_item: Dict[str, Any] = Field(default_factory=dict)


class ComponentScore(BaseModel):
    """Individually computed score component."""
    component: str
    score: float
    reason: Optional[str] = None


class RecommendationScore(BaseModel):
    """Aggregated score payload for a candidate item."""
    total_score: float
    score_breakdown: List[ComponentScore] = Field(default_factory=list)


class RecommendationReason(BaseModel):
    """Structured decision reasons and trade-offs for recommendation output."""
    reasons: List[str] = Field(default_factory=list)
    tradeoffs: List[str] = Field(default_factory=list)


class PipelineDebugInfo(BaseModel):
    """Developer debug telemetry for testing and evaluation."""
    strategy: str
    matched_constraints: List[str] = Field(default_factory=list)
    candidate_counts: Dict[str, int] = Field(default_factory=dict)
    ranking_duration_ms: float = 0.0
    pipeline_duration_ms: float = 0.0


class RecommendationResult(BaseModel):
    """Final ranked item payload returned by Recommendation Engine."""
    candidate: RecommendationCandidate
    score: RecommendationScore
    reason: RecommendationReason
    debug: Optional[PipelineDebugInfo] = None
