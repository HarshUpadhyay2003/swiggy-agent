"""Ranking Engine module for multi-vector deterministic item scoring."""

from typing import Dict, List, Tuple
from app.services.recommendation_engine.models import (
    RecommendationCandidate,
    RecommendationRequest,
    RecommendationScore,
)


class RankingEngine:
    """Computes multi-dimensional deterministic scores for recommendation candidates using configurable weights."""

    # Configurable Weight Constants
    WEIGHT_BUDGET_MATCH: float = 15.0
    WEIGHT_PREFERENCE_MATCH: float = 20.0
    WEIGHT_MEAL_TYPE_MATCH: float = 15.0
    WEIGHT_MOOD_MATCH: float = 25.0
    WEIGHT_MOOD_PENALTY: float = -15.0
    WEIGHT_POPULARITY: float = 10.0
    WEIGHT_HEALTH_SIGNAL: float = 15.0
    WEIGHT_HIGH_PROTEIN: float = 15.0
    WEIGHT_SPICY_MATCH: float = 10.0
    WEIGHT_VEGAN_MATCH: float = 15.0
    WEIGHT_GLUTEN_FREE_MATCH: float = 15.0

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

    def score_candidates(
        self, candidates: List[RecommendationCandidate], request: RecommendationRequest
    ) -> List[Tuple[RecommendationCandidate, RecommendationScore]]:
        """Score each candidate and return sorted list in descending order of total score."""
        scored_pairs: List[Tuple[RecommendationCandidate, RecommendationScore]] = []

        for candidate in candidates:
            score = self.compute_score(candidate, request)
            scored_pairs.append((candidate, score))

        scored_pairs.sort(key=lambda pair: pair[1].total_score, reverse=True)
        return scored_pairs

    def compute_score(
        self, candidate: RecommendationCandidate, req: RecommendationRequest
    ) -> RecommendationScore:
        """Compute score breakdown for a single candidate."""
        breakdown: Dict[str, float] = {}

        # 1. Budget Match Score
        budget_score = 0.0
        if req.max_budget is not None and candidate.price <= req.max_budget:
            # Higher score for items well within budget
            savings_ratio = 1.0 - (candidate.price / float(req.max_budget + 1))
            budget_score = self.WEIGHT_BUDGET_MATCH + (savings_ratio * 5.0)
        breakdown["budget_score"] = round(budget_score, 2)

        # 2. Preference Match Score
        pref_score = 0.0
        if req.preference:
            norm_pref = req.preference.strip().lower()
            if norm_pref in {"nonveg", "non veg"}:
                norm_pref = "non-veg"
            if candidate.category == norm_pref:
                pref_score = self.WEIGHT_PREFERENCE_MATCH
        breakdown["preference_score"] = round(pref_score, 2)

        # 3. Meal Type Match Score
        meal_type_score = 0.0
        if req.meal_type and candidate.meal_type == req.meal_type.strip().lower():
            meal_type_score = self.WEIGHT_MEAL_TYPE_MATCH
        breakdown["meal_type_score"] = round(meal_type_score, 2)

        # 4. Mood Match Score
        mood_score = 0.0
        if req.mood:
            norm_mood = req.mood.strip().lower()
            item_text = f"{candidate.name} {candidate.category} {candidate.meal_type} {candidate.description}".lower()

            target_mood_key = "comfort"
            if "healthy" in norm_mood:
                target_mood_key = "healthy"
            elif "late" in norm_mood or "night" in norm_mood:
                target_mood_key = "late night"

            boost_terms = self.MOOD_KEYWORDS.get(target_mood_key, [])
            penalty_terms = self.MOOD_PENALTIES.get(target_mood_key, [])

            if any(term in item_text for term in boost_terms):
                mood_score += self.WEIGHT_MOOD_MATCH
            if any(term in item_text for term in penalty_terms):
                mood_score += self.WEIGHT_MOOD_PENALTY
        breakdown["mood_score"] = round(mood_score, 2)

        # 5. Popularity Score (from KB V3.3 metadata or default)
        pop_score = 0.0
        comm = candidate.raw_item.get("commerce_intelligence", {}) if isinstance(candidate.raw_item, dict) else {}
        popularity_percentile = comm.get("popularity_percentile", 90.0) if isinstance(comm, dict) else 90.0
        pop_score = (float(popularity_percentile) / 100.0) * self.WEIGHT_POPULARITY
        breakdown["popularity_score"] = round(pop_score, 2)

        # 6. Health Signal Score
        health_score = 0.0
        if candidate.healthy or (req.healthy_only and candidate.healthy):
            health_score = self.WEIGHT_HEALTH_SIGNAL
        breakdown["health_score"] = round(health_score, 2)

        # 7. Additional Attribute Scores (Protein, Spicy, Vegan, Gluten Free)
        attr_score = 0.0
        if req.high_protein and candidate.high_protein:
            attr_score += self.WEIGHT_HIGH_PROTEIN
        if req.spicy is True and candidate.spicy:
            attr_score += self.WEIGHT_SPICY_MATCH
        elif req.spicy is False and not candidate.spicy:
            attr_score += self.WEIGHT_SPICY_MATCH
        if req.vegan and candidate.vegan:
            attr_score += self.WEIGHT_VEGAN_MATCH
        if req.gluten_free and candidate.gluten_free:
            attr_score += self.WEIGHT_GLUTEN_FREE_MATCH
        breakdown["attribute_score"] = round(attr_score, 2)

        # Calculate total score sum
        total_score = (
            budget_score
            + pref_score
            + meal_type_score
            + mood_score
            + pop_score
            + health_score
            + attr_score
        )

        return RecommendationScore(
            total_score=round(total_score, 2),
            budget_score=round(budget_score, 2),
            preference_score=round(pref_score, 2),
            meal_type_score=round(meal_type_score, 2),
            mood_score=round(mood_score, 2),
            popularity_score=round(pop_score, 2),
            health_score=round(health_score, 2),
            attribute_score=round(attr_score, 2),
            breakdown=breakdown,
        )
