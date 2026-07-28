"""Generalized Ranking Engine using independent Component Scorers."""

from typing import Any, Dict, List, Optional, Tuple
from app.services.recommendation_engine.models import (
    ComponentScore,
    RecommendationCandidate,
    RecommendationRequest,
    RecommendationScore,
)


class BaseComponentScorer:
    """Base interface for independent component scorers."""
    component_name: str = "base"
    weight: float = 10.0

    def compute_score(
        self, candidate: RecommendationCandidate, request: RecommendationRequest
    ) -> ComponentScore:
        raise NotImplementedError


class BudgetScorer(BaseComponentScorer):
    component_name = "budget"
    weight = 15.0

    def compute_score(
        self, candidate: RecommendationCandidate, request: RecommendationRequest
    ) -> ComponentScore:
        max_b = request.get_constraint_value("max_budget") or request.get_constraint_value("budget")
        if max_b and isinstance(max_b, (int, float)) and candidate.price <= max_b:
            savings_ratio = 1.0 - (candidate.price / float(max_b + 1))
            score = self.weight + (savings_ratio * 5.0)
            return ComponentScore(component=self.component_name, score=round(score, 2), reason="Within budget limit")
        return ComponentScore(component=self.component_name, score=0.0)


class PreferenceScorer(BaseComponentScorer):
    component_name = "preference"
    weight = 20.0

    def compute_score(
        self, candidate: RecommendationCandidate, request: RecommendationRequest
    ) -> ComponentScore:
        pref = request.get_constraint_value("preference")
        if pref:
            norm_pref = str(pref).strip().lower()
            if norm_pref in {"nonveg", "non veg"}:
                norm_pref = "non-veg"
            if candidate.category == norm_pref:
                return ComponentScore(component=self.component_name, score=self.weight, reason=f"Matches {norm_pref} preference")
        return ComponentScore(component=self.component_name, score=0.0)


class MealTypeScorer(BaseComponentScorer):
    component_name = "meal_type"
    weight = 15.0

    def compute_score(
        self, candidate: RecommendationCandidate, request: RecommendationRequest
    ) -> ComponentScore:
        meal_type = request.get_constraint_value("meal_type")
        if meal_type and candidate.meal_type == str(meal_type).strip().lower():
            return ComponentScore(component=self.component_name, score=self.weight, reason=f"Suitable for {candidate.meal_type}")
        return ComponentScore(component=self.component_name, score=0.0)


class MoodScorer(BaseComponentScorer):
    component_name = "mood"
    weight = 25.0
    penalty = -15.0

    MOOD_KEYWORDS: Dict[str, List[str]] = {
        "comfort": ["biryani", "burger", "dosa", "noodle", "fries", "mcmuffin", "pizza", "nuggets"],
        "healthy": ["salad", "grilled", "bowl", "protein", "quinoa", "wrap", "grain"],
        "late night": ["snacks", "wrap", "momos", "roll", "fries", "burger", "quick", "nuggets"],
    }

    MOOD_PENALTIES: Dict[str, List[str]] = {
        "comfort": ["salad", "quinoa"],
        "healthy": ["fried", "biryani", "burger", "pizza"],
        "late night": ["salad", "quinoa", "heavy", "lunch"],
    }

    def compute_score(
        self, candidate: RecommendationCandidate, request: RecommendationRequest
    ) -> ComponentScore:
        mood = request.get_constraint_value("mood")
        if not mood:
            return ComponentScore(component=self.component_name, score=0.0)

        norm_mood = str(mood).strip().lower()
        item_text = f"{candidate.name} {candidate.category} {candidate.meal_type} {candidate.description}".lower()

        target_mood = "comfort"
        if "healthy" in norm_mood:
            target_mood = "healthy"
        elif "late" in norm_mood or "night" in norm_mood:
            target_mood = "late night"

        score = 0.0
        reason = None
        boost_terms = self.MOOD_KEYWORDS.get(target_mood, [])
        penalty_terms = self.MOOD_PENALTIES.get(target_mood, [])

        if any(term in item_text for term in boost_terms):
            score += self.weight
            reason = f"Matches {target_mood} mood"
        if any(term in item_text for term in penalty_terms):
            score += self.penalty

        return ComponentScore(component=self.component_name, score=round(score, 2), reason=reason)


class PopularityScorer(BaseComponentScorer):
    component_name = "popularity"
    weight = 10.0

    def compute_score(
        self, candidate: RecommendationCandidate, request: RecommendationRequest
    ) -> ComponentScore:
        comm = candidate.raw_item.get("commerce_intelligence", {}) if isinstance(candidate.raw_item, dict) else {}
        popularity_percentile = comm.get("popularity_percentile", 90.0) if isinstance(comm, dict) else 90.0
        score = (float(popularity_percentile) / 100.0) * self.weight
        return ComponentScore(component=self.component_name, score=round(score, 2), reason="Popular item")


class HealthScorer(BaseComponentScorer):
    component_name = "health"
    weight = 15.0

    def compute_score(
        self, candidate: RecommendationCandidate, request: RecommendationRequest
    ) -> ComponentScore:
        is_healthy_req = request.get_constraint_value("health_goal") or request.get_constraint_value("healthy_only")
        if candidate.healthy or is_healthy_req:
            return ComponentScore(component=self.component_name, score=self.weight, reason="Healthy choice")
        return ComponentScore(component=self.component_name, score=0.0)


class AttributeScorer(BaseComponentScorer):
    component_name = "attribute"
    weight_high_protein = 15.0
    weight_spicy = 10.0
    weight_vegan = 15.0
    weight_gluten_free = 15.0

    def compute_score(
        self, candidate: RecommendationCandidate, request: RecommendationRequest
    ) -> ComponentScore:
        score = 0.0
        reasons = []

        if request.get_constraint_value("high_protein") and candidate.high_protein:
            score += self.weight_high_protein
            reasons.append("High protein option")
        if request.get_constraint_value("spicy") is True and candidate.spicy:
            score += self.weight_spicy
            reasons.append("Spicy option")
        if request.get_constraint_value("vegan") and candidate.vegan:
            score += self.weight_vegan
            reasons.append("Vegan option")
        if request.get_constraint_value("gluten_free") and candidate.gluten_free:
            score += self.weight_gluten_free
            reasons.append("Gluten-free option")

        return ComponentScore(
            component=self.component_name,
            score=round(score, 2),
            reason=", ".join(reasons) if reasons else None,
        )


class HistoryScorer(BaseComponentScorer):
    component_name = "history"
    weight = 10.0

    def compute_score(
        self, candidate: RecommendationCandidate, request: RecommendationRequest
    ) -> ComponentScore:
        if candidate.item_id in request.context.order_history:
            return ComponentScore(component=self.component_name, score=self.weight, reason="Previously ordered item")
        return ComponentScore(component=self.component_name, score=0.0)


class RankingEngine:
    """Combines independent component scorers into aggregated candidate scores."""

    def __init__(self, scorers: Optional[List[BaseComponentScorer]] = None) -> None:
        self.scorers: List[BaseComponentScorer] = scorers or [
            BudgetScorer(),
            PreferenceScorer(),
            MealTypeScorer(),
            MoodScorer(),
            PopularityScorer(),
            HealthScorer(),
            AttributeScorer(),
            HistoryScorer(),
        ]

    def score_candidates(
        self, candidates: List[RecommendationCandidate], request: RecommendationRequest
    ) -> List[Tuple[RecommendationCandidate, RecommendationScore]]:
        """Compute component scores for candidates and return sorted descending by total score."""
        scored_pairs: List[Tuple[RecommendationCandidate, RecommendationScore]] = []

        for candidate in candidates:
            breakdown: List[ComponentScore] = []
            total_score = 0.0

            for scorer in self.scorers:
                comp_score = scorer.compute_score(candidate, request)
                breakdown.append(comp_score)
                total_score += comp_score.score

            rec_score = RecommendationScore(
                total_score=round(total_score, 2),
                score_breakdown=breakdown,
            )
            scored_pairs.append((candidate, rec_score))

        scored_pairs.sort(key=lambda pair: pair[1].total_score, reverse=True)
        return scored_pairs
