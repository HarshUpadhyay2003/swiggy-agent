"""Dedicated checkout regression unit test suite."""

import sys
import unittest
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parents[1]
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.services.cart_service import CartService
from app.services.catalog_service import CatalogService
from app.services.order_service import OrderService
from app.services.chat_orchestrator import ChatOrchestrator


class TestCheckoutRegression(unittest.TestCase):
    def setUp(self):
        self.catalog = CatalogService()
        self.cart_service = CartService(self.catalog)
        self.order_service = OrderService(self.catalog)
        self.orchestrator = ChatOrchestrator()
        self.session_id = "test_checkout_session_101"
        self.cart_service.clear_cart(self.session_id)

    def tearDown(self):
        self.cart_service.clear_cart(self.session_id)

    def test_01_checkout_with_populated_cart(self):
        """Verify checkout succeeds when items exist in cart."""
        item_101 = self.catalog.get_item_by_id(101)
        self.cart_service.add_to_cart(self.session_id, item_101, quantity=2)

        cart = self.cart_service.get_cart(self.session_id)
        self.assertEqual(len(cart["items"]), 1)
        self.assertEqual(cart["items"][0]["quantity"], 2)

        item_ids = self.cart_service.get_cart_item_ids(self.session_id)
        self.assertEqual(len(item_ids), 2)

        order = self.order_service.place_order(item_ids)
        self.assertIn("order_id", order)
        self.assertEqual(order["status"], "confirmed")
        self.assertGreater(order["total"], 0)

        # Clear cart post checkout
        self.cart_service.clear_cart(self.session_id)
        empty_cart = self.cart_service.get_cart(self.session_id)
        self.assertEqual(len(empty_cart["items"]), 0)

    def test_02_checkout_with_empty_cart(self):
        """Verify placing order with empty cart raises ValueError."""
        item_ids = self.cart_service.get_cart_item_ids(self.session_id)
        self.assertEqual(len(item_ids), 0)

        with self.assertRaises(ValueError) as ctx:
            self.order_service.place_order(item_ids)
        self.assertIn("item_ids must be a non-empty list", str(ctx.exception))

    def test_03_cross_instance_cart_synchronization(self):
        """Verify items added via ChatOrchestrator instance are present in CartService route instance."""
        chat_cart_service = self.orchestrator.cart_service
        route_cart_service = CartService()

        # Add item via chat orchestrator's cart service
        item_201 = self.catalog.get_item_by_id(201)
        chat_cart_service.add_to_cart(self.session_id, item_201, quantity=1)

        # Retrieve cart via route cart service instance
        route_cart = route_cart_service.get_cart(self.session_id)
        self.assertEqual(len(route_cart["items"]), 1)
        self.assertEqual(route_cart["items"][0]["item_id"], 201)

        # Execute checkout via route cart service instance
        item_ids = route_cart_service.get_cart_item_ids(self.session_id)
        order = route_cart_service.order_service.place_order(item_ids)
        self.assertIn("order_id", order)

        # Clear cart via route service
        route_cart_service.clear_cart(self.session_id)
        self.assertEqual(len(chat_cart_service.get_cart(self.session_id)["items"]), 0)

    def test_04_invalid_item_id_handling(self):
        """Verify invalid item ID raises ValueError."""
        with self.assertRaises(ValueError):
            self.order_service.place_order([999999])

    def test_05_duplicate_checkout_request(self):
        """Verify checkout on an already checked out / cleared cart fails gracefully."""
        item_101 = self.catalog.get_item_by_id(101)
        self.cart_service.add_to_cart(self.session_id, item_101, quantity=1)

        # First checkout
        item_ids = self.cart_service.get_cart_item_ids(self.session_id)
        order_1 = self.order_service.place_order(item_ids)
        self.assertIn("order_id", order_1)
        self.cart_service.clear_cart(self.session_id)

        # Second duplicate checkout
        item_ids_2 = self.cart_service.get_cart_item_ids(self.session_id)
        with self.assertRaises(ValueError):
            self.order_service.place_order(item_ids_2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
