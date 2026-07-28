"""Unit tests for ExplanationBuilder."""

import unittest
from app.services.recommendation_engine.explanation_builder import ExplanationBuilder
from app.services.recommendation_engine.models import (
    RecommendationCandidate,
    RecommendationRequest,
    RecommendationScore,
)


class TestExplanationBuilder(unittest.TestCase):
    def setUp(self):
        self.builder = ExplanationBuilder()

    def test_build_explanation_healthy_high_protein(self):
        candidate = RecommendationCandidate(
            item_id=101,
            name="Fit Chicken Bowl",
            description="Grilled chicken with quinoa",
            price=250,
            category="non-veg",
            meal_type="lunch",
            healthy=True,
            high_protein=True,
        )
        req = RecommendationRequest(
            preference="non-veg",
            max_budget=300,
            healthy_only=True,
            high_protein=True,
        )
        score = RecommendationScore(total_score=85.0, popularity_score=8.5)

        explanation = self.builder.build_explanation(candidate, req, score)
        self.assertIn("Within budget limit", explanation.reasons)
        self.assertIn("Healthy choice (Health Score >= 6.0)", explanation.reasons)
        self.assertIn("High protein content (>= 15g protein)", explanation.reasons)
        self.assertEqual(len(explanation.tradeoffs), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
