"""Unit tests for Generalized CandidateRetriever."""

import unittest
from app.services.catalog_service import CatalogService
from app.services.recommendation_engine.candidate_retriever import CandidateRetriever
from app.services.recommendation_engine.models import Constraint, RecommendationRequest


class TestCandidateRetriever(unittest.TestCase):
    def setUp(self):
        self.catalog = CatalogService()
        self.retriever = CandidateRetriever(self.catalog)

    def test_filter_healthy_lunch_under_300(self):
        req = RecommendationRequest(
            constraints=[
                Constraint(type="preference", value="non-veg"),
                Constraint(type="meal_type", value="lunch"),
                Constraint(type="max_budget", value=300),
                Constraint(type="healthy_only", value=True),
            ]
        )
        candidates, debug_counts = self.retriever.retrieve_candidates(req)
        self.assertGreater(len(candidates), 0)
        self.assertIn("initial_candidates", debug_counts)
        for c in candidates:
            self.assertEqual(c.category, "non-veg")
            self.assertEqual(c.meal_type, "lunch")
            self.assertLessEqual(c.price, 300)
            self.assertTrue(c.healthy)

    def test_filter_vegetarian_breakfast(self):
        req = RecommendationRequest(
            constraints=[
                Constraint(type="preference", value="veg"),
                Constraint(type="meal_type", value="breakfast"),
            ]
        )
        candidates, _ = self.retriever.retrieve_candidates(req)
        self.assertGreater(len(candidates), 0)
        for c in candidates:
            self.assertEqual(c.category, "veg")
            self.assertEqual(c.meal_type, "breakfast")

    def test_filter_invalid_restaurant(self):
        req = RecommendationRequest(
            constraints=[Constraint(type="restaurant_id", value=99999)]
        )
        candidates, _ = self.retriever.retrieve_candidates(req)
        self.assertEqual(len(candidates), 0)

    def test_filter_no_matching_items(self):
        req = RecommendationRequest(
            constraints=[Constraint(type="max_budget", value=5)]
        )
        candidates, _ = self.retriever.retrieve_candidates(req)
        self.assertEqual(len(candidates), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
