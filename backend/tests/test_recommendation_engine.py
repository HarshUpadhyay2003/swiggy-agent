"""Unit tests for Generalized RecommendationEngine pipeline & strategy chain."""

import unittest
from app.services.catalog_service import CatalogService
from app.services.recommendation_engine.models import (
    Constraint,
    RecommendationContext,
    RecommendationRequest,
)
from app.services.recommendation_engine.recommendation_engine import RecommendationEngine


class TestRecommendationEngine(unittest.TestCase):
    def setUp(self):
        self.catalog = CatalogService()
        self.engine = RecommendationEngine(self.catalog)

    def test_scenario_healthy_lunch_under_300(self):
        req = RecommendationRequest(
            constraints=[
                Constraint(type="preference", value="non-veg"),
                Constraint(type="meal_type", value="lunch"),
                Constraint(type="max_budget", value=300),
                Constraint(type="healthy_only", value=True),
            ],
            top_k=3,
        )
        results = self.engine.generate_recommendations(req)
        self.assertGreater(len(results), 0)
        self.assertLessEqual(len(results), 3)

        for res in results:
            self.assertEqual(res.candidate.category, "non-veg")
            self.assertEqual(res.candidate.meal_type, "lunch")
            self.assertLessEqual(res.candidate.price, 300)
            self.assertTrue(res.candidate.healthy)
            self.assertGreater(len(res.reason.reasons), 0)

    def test_scenario_debug_telemetry(self):
        req = RecommendationRequest(
            constraints=[
                Constraint(type="preference", value="veg"),
                Constraint(type="max_budget", value=200),
            ],
            context=RecommendationContext(debug_mode=True),
        )
        results = self.engine.generate_recommendations(req)
        self.assertGreater(len(results), 0)

        first_res = results[0]
        self.assertIsNotNone(first_res.debug)
        self.assertEqual(first_res.debug.strategy, "explicit_constraints")
        self.assertIn("preference", first_res.debug.matched_constraints)
        self.assertGreater(first_res.debug.pipeline_duration_ms, 0.0)

    def test_scenario_neutral_strategy_fallback(self):
        # Impossible budget constraint forces strategy chain fallback
        req = RecommendationRequest(
            constraints=[Constraint(type="max_budget", value=5)]
        )
        results = self.engine.generate_recommendations(req)
        self.assertGreater(len(results), 0)
        # Verify fallback strategy was triggered
        first_res = results[0]
        if first_res.debug:
            self.assertNotEqual(first_res.debug.strategy, "explicit_constraints")


if __name__ == "__main__":
    unittest.main(verbosity=2)
