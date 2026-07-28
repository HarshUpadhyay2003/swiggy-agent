"""Unit tests for RankingEngine."""

import unittest
from app.services.recommendation_engine.models import RecommendationCandidate, RecommendationRequest
from app.services.recommendation_engine.ranking_engine import RankingEngine


class TestRankingEngine(unittest.TestCase):
    def setUp(self):
        self.ranker = RankingEngine()

    def test_scoring_comfort_food(self):
        candidate = RecommendationCandidate(
            item_id=101,
            name="McAloo Tikki Burger",
            description="Crispy potato burger",
            price=65,
            available=True,
            category="veg",
            meal_type="lunch",
            healthy=False,
            spicy=False,
        )
        req = RecommendationRequest(mood="comfort", preference="veg", max_budget=100)
        score = self.ranker.compute_score(candidate, req)

        self.assertGreater(score.total_score, 0)
        self.assertGreater(score.budget_score, 0)
        self.assertGreater(score.preference_score, 0)
        self.assertGreater(score.mood_score, 0)

    def test_scoring_high_protein_and_spicy(self):
        candidate = RecommendationCandidate(
            item_id=201,
            name="1 Pc Hot & Crispy Chicken",
            description="Spicy fried chicken",
            price=115,
            available=True,
            category="non-veg",
            meal_type="lunch",
            healthy=True,
            high_protein=True,
            spicy=True,
        )
        req = RecommendationRequest(
            preference="non-veg",
            high_protein=True,
            spicy=True,
            healthy_only=True,
        )
        score = self.ranker.compute_score(candidate, req)
        self.assertGreater(score.attribute_score, 0)
        self.assertGreater(score.health_score, 0)

    def test_empty_candidates_scoring(self):
        scored = self.ranker.score_candidates([], RecommendationRequest())
        self.assertEqual(len(scored), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
