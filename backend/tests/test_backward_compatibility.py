"""Backward compatibility test suite for downstream service integration."""

import unittest
from app.services.catalog_service import CatalogService
from app.services.context_engine import ContextEngine
from app.services.planner import MealPlanner
from app.services.cart_service import CartService
from app.services.order_service import OrderService


class TestBackwardCompatibility(unittest.TestCase):
    def setUp(self):
        self.catalog_service = CatalogService()
        self.context_engine = ContextEngine(self.catalog_service)
        self.meal_planner = MealPlanner(self.catalog_service)
        self.cart_service = CartService(self.catalog_service)
        self.order_service = OrderService(self.catalog_service)

    def test_context_engine_recommendations(self):
        ctx = {
            "preference": "veg",
            "meal_type": "lunch",
            "max_budget": 300,
            "health_goal": True,
        }
        res = self.context_engine.recommend_food(ctx)
        self.assertIn("recommendations", res)
        self.assertGreater(len(res["recommendations"]), 0)

        first_rec = res["recommendations"][0]
        self.assertIn("item_id", first_rec)
        self.assertIn("item_name", first_rec)
        self.assertIn("restaurant", first_rec)
        self.assertIn("price", first_rec)

    def test_meal_planner_fallback_generation(self):
        user_input = {"goal": "Reduce Spending", "budget": 2000, "preferences": "veg"}
        plan = self.meal_planner.generate_fallback_plan(user_input)
        self.assertIn("day_1", plan)
        self.assertIn("breakfast", plan["day_1"])
        self.assertIn("price", plan["day_1"]["breakfast"])

    def test_cart_service_add_and_totals(self):
        session_id = "test_compat_session"
        item = self.catalog_service.get_item_by_id(101)
        cart = self.cart_service.add_to_cart(session_id, item, quantity=2)

        self.assertEqual(len(cart["items"]), 1)
        self.assertEqual(cart["items"][0]["item_id"], 101)
        self.assertGreater(cart["total"], 0)

    def test_order_service_place_order(self):
        order = self.order_service.place_order([101, 201])
        self.assertIn("order_id", order)
        self.assertEqual(len(order["items"]), 2)
        self.assertGreater(order["total"], 0)
        self.assertGreater(order["estimated_delivery_time"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
