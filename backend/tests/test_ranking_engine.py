"""Unit tests for Generalized RankingEngine."""

import unittest
from app.services.recommendation_engine.models import (
    Constraint,
    RecommendationCandidate,
    RecommendationContext,
    RecommendationRequest,
)
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
        req = RecommendationRequest(
            constraints=[
                Constraint(type="mood", value="comfort"),
                Constraint(type="preference", value="veg"),
                Constraint(type="max_budget", value=100),
            ]
        )
        score = self.ranker.scorers[0].compute_score(candidate, req)  # Budget
        self.assertGreater(score.score, 0)

        scored_pairs = self.ranker.score_candidates([candidate], req)
        self.assertEqual(len(scored_pairs), 1)
        total = scored_pairs[0][1].total_score
        self.assertGreater(total, 0)

    def test_scoring_order_history(self):
        candidate = RecommendationCandidate(
            item_id=101,
            name="McAloo Tikki Burger",
            price=65,
            category="veg",
            meal_type="lunch",
        )
        req = RecommendationRequest(
            context=RecommendationContext(order_history=[101])
        )
        scored_pairs = self.ranker.score_candidates([candidate], req)
        history_scores = [c for c in scored_pairs[0][1].score_breakdown if c.component == "history"]
        self.assertEqual(len(history_scores), 1)
        self.assertGreater(history_scores[0].score, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
