"""Decision Reason Builder module producing structured reasons and trade-offs without LLMs."""

from typing import List
from app.services.recommendation_engine.models import (
    RecommendationCandidate,
    RecommendationReason,
    RecommendationRequest,
    RecommendationScore,
)


class DecisionReasonBuilder:
    """Produces structured decision reasoning objects (reasons & trade-offs) without conversational English."""

    def build_reason(
        self,
        candidate: RecommendationCandidate,
        req: RecommendationRequest,
        score: RecommendationScore,
    ) -> RecommendationReason:
        """Construct structured reasons and trade-offs lists."""
        reasons: List[str] = []
        tradeoffs: List[str] = []

        max_b = req.get_constraint_value("max_budget") or req.get_constraint_value("budget")
        pref = req.get_constraint_value("preference")
        meal_type = req.get_constraint_value("meal_type")
        healthy_req = req.get_constraint_value("healthy_only") or req.get_constraint_value("health_goal")
        mood = req.get_constraint_value("mood")

        # 1. Budget Reasons & Trade-offs
        if max_b is not None and isinstance(max_b, (int, float)):
            if candidate.price <= max_b:
                reasons.append("Within budget limit")
                if candidate.price <= (max_b * 0.5):
                    reasons.append("Great value price")
            else:
                tradeoffs.append("Slightly higher price than requested budget")

        # 2. Dietary Safety & Preference Reasons
        if pref:
            norm_pref = str(pref).strip().lower()
            if candidate.category == "veg":
                reasons.append("100% Vegetarian")
            elif candidate.category == "non-veg":
                reasons.append("Non-Vegetarian protein option")

        if candidate.vegan:
            reasons.append("100% Vegan certified")
        if candidate.gluten_free:
            reasons.append("Gluten-free choice")

        # 3. Meal Type Reasons
        if meal_type and candidate.meal_type == str(meal_type).lower():
            reasons.append(f"Ideal for {candidate.meal_type.capitalize()}")

        # 4. Nutrition & Health Reasons & Trade-offs
        if candidate.healthy:
            reasons.append("Healthy choice (Health Score >= 6.0)")
        elif healthy_req:
            tradeoffs.append("Contains higher calorie or sodium content")

        if candidate.high_protein:
            reasons.append("High protein content (>= 15g protein)")

        if candidate.low_calorie:
            reasons.append("Low calorie option (<= 350 kcal)")

        # 5. Mood Reasons
        if mood:
            norm_mood = str(mood).lower()
            if "healthy" in norm_mood and candidate.healthy:
                reasons.append("Nourishing healthy option")
            elif "comfort" in norm_mood and not candidate.healthy:
                reasons.append("Comfort food favorite")
            elif "late" in norm_mood:
                reasons.append("Quick & convenient snack")

        # 6. Scorer Component Reasons
        for comp in score.score_breakdown:
            if comp.reason and comp.score > 0 and comp.reason not in reasons:
                reasons.append(comp.reason)

        # Default fallback reason
        if not reasons:
            reasons.append("Matches your dining criteria")

        return RecommendationReason(
            reasons=reasons,
            tradeoffs=tradeoffs,
        )


# Export alias for compatibility
ReasonBuilder = DecisionReasonBuilder
