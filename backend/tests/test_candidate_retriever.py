"""Unit tests for CandidateRetriever."""

import unittest
from app.services.catalog_service import CatalogService
from app.services.recommendation_engine.candidate_retriever import CandidateRetriever
from app.services.recommendation_engine.models import RecommendationRequest


class TestCandidateRetriever(unittest.TestCase):
    def setUp(self):
        self.catalog = CatalogService()
        self.retriever = CandidateRetriever(self.catalog)

    def test_filter_healthy_lunch_under_300(self):
        req = RecommendationRequest(
            preference="non-veg",
            meal_type="lunch",
            max_budget=300,
            healthy_only=True,
        )
        candidates = self.retriever.retrieve_candidates(req)
        self.assertGreater(len(candidates), 0)
        for c in candidates:
            self.assertEqual(c.category, "non-veg")
            self.assertEqual(c.meal_type, "lunch")
            self.assertLessEqual(c.price, 300)
            self.assertTrue(c.healthy)

    def test_filter_vegetarian_breakfast(self):
        req = RecommendationRequest(
            preference="veg",
            meal_type="breakfast",
        )
        candidates = self.retriever.retrieve_candidates(req)
        self.assertGreater(len(candidates), 0)
        for c in candidates:
            self.assertEqual(c.category, "veg")
            self.assertEqual(c.meal_type, "breakfast")

    def test_filter_invalid_restaurant(self):
        req = RecommendationRequest(restaurant_id=99999)
        candidates = self.retriever.retrieve_candidates(req)
        self.assertEqual(len(candidates), 0)

    def test_filter_no_matching_items(self):
        req = RecommendationRequest(max_budget=10)  # Impossible budget
        candidates = self.retriever.retrieve_candidates(req)
        self.assertEqual(len(candidates), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
