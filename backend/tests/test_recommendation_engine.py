"""Unit tests for full RecommendationEngine orchestrator pipeline."""

import unittest
from app.services.catalog_service import CatalogService
from app.services.recommendation_engine.models import RecommendationRequest
from app.services.recommendation_engine.recommendation_engine import RecommendationEngine


class TestRecommendationEngine(unittest.TestCase):
    def setUp(self):
        self.catalog = CatalogService()
        self.engine = RecommendationEngine(self.catalog)

    def test_scenario_healthy_lunch_under_300(self):
        req = RecommendationRequest(
            preference="non-veg",
            meal_type="lunch",
            max_budget=300,
            healthy_only=True,
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
            self.assertGreater(len(res.explanation.reasons), 0)

    def test_scenario_vegetarian_breakfast(self):
        req = RecommendationRequest(
            preference="veg",
            meal_type="breakfast",
            top_k=5,
        )
        results = self.engine.generate_recommendations(req)
        self.assertGreater(len(results), 0)
        for res in results:
            self.assertEqual(res.candidate.category, "veg")
            self.assertEqual(res.candidate.meal_type, "breakfast")

    def test_scenario_comfort_food(self):
        req = RecommendationRequest(mood="comfort", top_k=5)
        results = self.engine.generate_recommendations(req)
        self.assertGreater(len(results), 0)

    def test_scenario_budget_meal(self):
        req = RecommendationRequest(max_budget=100, top_k=5)
        results = self.engine.generate_recommendations(req)
        self.assertGreater(len(results), 0)
        for res in results:
            self.assertLessEqual(res.candidate.price, 100)

    def test_scenario_high_protein_request(self):
        req = RecommendationRequest(high_protein=True, top_k=5)
        results = self.engine.generate_recommendations(req)
        self.assertGreater(len(results), 0)

    def test_scenario_invalid_restaurant(self):
        req = RecommendationRequest(restaurant_id=99999)
        results = self.engine.generate_recommendations(req)
        self.assertEqual(len(results), 0)

    def test_scenario_no_matching_items(self):
        req = RecommendationRequest(max_budget=5)
        results = self.engine.generate_recommendations(req)
        self.assertEqual(len(results), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
