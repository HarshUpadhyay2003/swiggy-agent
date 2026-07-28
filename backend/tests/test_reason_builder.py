"""Unit tests for DecisionReasonBuilder."""

import unittest
from app.services.recommendation_engine.models import (
    Constraint,
    RecommendationCandidate,
    RecommendationRequest,
    RecommendationScore,
)
from app.services.recommendation_engine.reason_builder import DecisionReasonBuilder


class TestReasonBuilder(unittest.TestCase):
    def setUp(self):
        self.builder = DecisionReasonBuilder()

    def test_build_reason_healthy_high_protein(self):
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
            constraints=[
                Constraint(type="preference", value="non-veg"),
                Constraint(type="max_budget", value=300),
                Constraint(type="healthy_only", value=True),
            ]
        )
        score = RecommendationScore(total_score=85.0)

        reason = self.builder.build_reason(candidate, req, score)
        self.assertIn("Within budget limit", reason.reasons)
        self.assertIn("Healthy choice (Health Score >= 6.0)", reason.reasons)
        self.assertIn("High protein content (>= 15g protein)", reason.reasons)
        self.assertEqual(len(reason.tradeoffs), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
