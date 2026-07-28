"""Pydantic data models for Recommendation Engine inputs, intermediate states, and results."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class RecommendationRequest(BaseModel):
    """Structured request input for recommendation generation."""
    preference: Optional[str] = None  # "veg" or "non-veg"
    meal_type: Optional[str] = None    # "breakfast", "lunch", "dinner", "snacks"
    min_budget: Optional[int] = None
    max_budget: Optional[int] = None
    healthy_only: bool = False
    mood: Optional[str] = None        # "comfort", "healthy", "late night", etc.
    high_protein: bool = False
    spicy: Optional[bool] = None
    vegan: bool = False
    gluten_free: bool = False
    restaurant_id: Optional[int] = None
    top_k: int = 5


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


class RecommendationScore(BaseModel):
    """Detailed score breakdown for a candidate item."""
    total_score: float
    budget_score: float = 0.0
    preference_score: float = 0.0
    meal_type_score: float = 0.0
    mood_score: float = 0.0
    popularity_score: float = 0.0
    health_score: float = 0.0
    attribute_score: float = 0.0
    breakdown: Dict[str, float] = Field(default_factory=dict)


class RecommendationExplanation(BaseModel):
    """Structured explanation reasons and trade-offs for recommendation decisioning."""
    reasons: List[str] = Field(default_factory=list)
    tradeoffs: List[str] = Field(default_factory=list)


class RecommendationResult(BaseModel):
    """Final ranked item payload returned by Recommendation Engine."""
    candidate: RecommendationCandidate
    score: RecommendationScore
    explanation: RecommendationExplanation
