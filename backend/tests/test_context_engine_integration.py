"""Integration & regression tests for ContextEngine migration to RecommendationEngine."""

import unittest
from app.services.catalog_service import CatalogService
from app.services.context_engine import ContextEngine


class TestContextEngineIntegration(unittest.TestCase):
    def setUp(self):
        self.catalog = CatalogService()
        self.context_engine = ContextEngine(self.catalog)

    def test_context_engine_healthy_lunch_recommendation(self):
        ctx = {
            "preference": "non-veg",
            "meal_type": "lunch",
            "max_budget": 300,
            "healthy_only": True,
        }
        res = self.context_engine.recommend_food(ctx, include_scores=True)

        self.assertIn("recommendations", res)
        self.assertIn("fallback_used", res)
        self.assertIn("reasoning", res)
        self.assertGreater(len(res["recommendations"]), 0)

        first_rec = res["recommendations"][0]
        self.assertIn("item_id", first_rec)
        self.assertIn("item_name", first_rec)
        self.assertIn("restaurant", first_rec)
        self.assertIn("price", first_rec)
        self.assertIn("score", first_rec)
        self.assertLessEqual(first_rec["price"], 300)
        self.assertTrue(first_rec["healthy"])

    def test_context_engine_debug_mode_output(self):
        ctx = {
            "preference": "veg",
            "max_budget": 200,
            "debug_mode": True,
        }
        res = self.context_engine.recommend_food(ctx)
        self.assertGreater(len(res["recommendations"]), 0)
        first_rec = res["recommendations"][0]
        self.assertIn("debug", first_rec)
        self.assertIn("strategy", first_rec["debug"])
        self.assertIn("pipeline_duration_ms", first_rec["debug"])

    def test_context_engine_legacy_wrapper_methods(self):
        items = self.catalog.get_available_items()
        budget_items = self.context_engine.filter_by_budget(items, max_budget=100)
        self.assertTrue(all(i["price"] <= 100 for i in budget_items))

        veg_items = self.context_engine.filter_by_preference(items, "veg")
        self.assertTrue(all(i["category"] == "veg" for i in veg_items))

        item_score = self.context_engine.score_item(items[0], mood="comfort")
        self.assertIsInstance(item_score, float)
        self.assertGreater(item_score, 0.0)

        reason = self.context_engine.generate_reason(items[0])
        self.assertIsInstance(reason, str)
        self.assertGreater(len(reason), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
