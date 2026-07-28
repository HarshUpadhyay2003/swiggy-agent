"""End-to-end smoke test runner for Stage 1B migration validation."""

import json
import sys
import unittest
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parents[1]
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.services.catalog_service import CatalogService
from app.services.context_engine import ContextEngine
from app.services.planner import MealPlanner
from app.services.cart_service import CartService
from app.services.order_service import OrderService
from app.services.chat_orchestrator import ChatOrchestrator


class TestStage1BSmokeTest(unittest.TestCase):
    """End-to-end runtime smoke test for Knowledge Base migration."""

    def test_01_catalog_restaurants_and_items_lookup(self):
        """Smoke test 1: CatalogService restaurant and item lookups."""
        catalog = CatalogService()
        restaurants = catalog.get_all_restaurants()
        self.assertGreaterEqual(len(restaurants), 6)

        mcd_item = catalog.get_item_by_id(101)
        self.assertEqual(mcd_item["name"], "McAloo Tikki Burger")
        self.assertEqual(mcd_item["restaurant_name"], "McDonald's")

        kfc_item = catalog.get_item_by_id(201)
        self.assertEqual(kfc_item["name"], "1 Pc Hot & Crispy Chicken")
        self.assertEqual(kfc_item["restaurant_name"], "KFC")

        search_res = catalog.search_items("pizza")
        self.assertGreaterEqual(len(search_res), 1)

    def test_02_recommendation_engine_runtime(self):
        """Smoke test 2: ContextEngine recommendation logic."""
        context_engine = ContextEngine()
        context = {"preference": "non-veg", "meal_type": "lunch", "max_budget": 300}
        recs = context_engine.recommend_food(context)
        self.assertIn("recommendations", recs)
        self.assertGreater(len(recs["recommendations"]), 0)

    def test_03_meal_planner_runtime(self):
        """Smoke test 3: MealPlanner fallback plan generation."""
        planner = MealPlanner()
        plan = planner.generate_fallback_plan({"preferences": "veg", "budget": 2100})
        self.assertIn("day_1", plan)
        self.assertIn("day_7", plan)

    def test_04_cart_and_order_transaction_runtime(self):
        """Smoke test 4: CartService and OrderService transactions."""
        catalog = CatalogService()
        cart_service = CartService(catalog)
        order_service = OrderService(catalog)

        session_id = "smoke_test_session"
        item_101 = catalog.get_item_by_id(101)
        item_201 = catalog.get_item_by_id(201)

        cart_service.add_to_cart(session_id, item_101, 1)
        cart_service.add_to_cart(session_id, item_201, 2)

        cart = cart_service.get_cart(session_id)
        self.assertEqual(len(cart["items"]), 2)
        self.assertGreater(cart["total"], 0)

        order = order_service.place_order([101, 201])
        self.assertIn("order_id", order)
        self.assertEqual(order["status"], "confirmed")

    def test_05_chat_orchestrator_initialization(self):
        """Smoke test 5: ChatOrchestrator end-to-end chat message handling."""
        orchestrator = ChatOrchestrator()
        user_ctx = {"session_id": "smoke_chat_session"}

        # Test recommendation chat
        res_rec = orchestrator.handle_message("Suggest some healthy lunch under 300", user_ctx)
        self.assertIn("response", res_rec)
        self.assertIsNotNone(res_rec["response"])

        # Test add to cart chat
        res_cart = orchestrator.handle_message("Add McAloo Tikki to cart", user_ctx)
        self.assertIn("response", res_cart)


if __name__ == "__main__":
    unittest.main(verbosity=2)
