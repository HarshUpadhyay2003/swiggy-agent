"""Explanation Builder module for structured, non-LLM decision reasons and trade-offs."""

from typing import List
from app.services.recommendation_engine.models import (
    RecommendationCandidate,
    RecommendationExplanation,
    RecommendationRequest,
    RecommendationScore,
)


class ExplanationBuilder:
    """Builds structured decision explanations (reasons and trade-offs) without LLMs."""

    def build_explanation(
        self,
        candidate: RecommendationCandidate,
        req: RecommendationRequest,
        score: RecommendationScore,
    ) -> RecommendationExplanation:
        """Construct structured reasons and trade-offs lists."""
        reasons: List[str] = []
        tradeoffs: List[str] = []

        # 1. Budget Reasons & Trade-offs
        if req.max_budget is not None:
            if candidate.price <= req.max_budget:
                reasons.append("Within budget limit")
                if candidate.price <= (req.max_budget * 0.5):
                    reasons.append("Great value price")
            else:
                tradeoffs.append("Slightly higher price than requested budget")

        # 2. Dietary Safety & Preference Reasons
        if req.preference:
            if candidate.category == "veg":
                reasons.append("100% Vegetarian")
            elif candidate.category == "non-veg":
                reasons.append("Non-Vegetarian protein option")

        if candidate.vegan:
            reasons.append("100% Vegan certified")
        if candidate.gluten_free:
            reasons.append("Gluten-free choice")

        # 3. Meal Type Reasons
        if req.meal_type and candidate.meal_type == req.meal_type.lower():
            reasons.append(f"Ideal for {candidate.meal_type.capitalize()}")

        # 4. Nutrition & Health Reasons & Trade-offs
        if candidate.healthy:
            reasons.append("Healthy choice (Health Score >= 6.0)")
        elif req.healthy_only:
            tradeoffs.append("Contains higher calorie or sodium content")

        if candidate.high_protein:
            reasons.append("High protein content (>= 15g protein)")

        if candidate.low_calorie:
            reasons.append("Low calorie option (<= 350 kcal)")

        # 5. Mood Reasons
        if req.mood:
            if "healthy" in req.mood.lower() and candidate.healthy:
                reasons.append("Nourishing healthy option")
            elif "comfort" in req.mood.lower() and not candidate.healthy:
                reasons.append("Comfort food favorite")
            elif "late" in req.mood.lower():
                reasons.append("Quick & convenient snack")

        # 6. Popularity Reasons
        if score.popularity_score > 7.0:
            reasons.append("Popular top-rated item")

        # Fallback default reason if none triggered
        if not reasons:
            reasons.append("Matches your dining criteria")

        return RecommendationExplanation(
            reasons=reasons,
            tradeoffs=tradeoffs,
        )
