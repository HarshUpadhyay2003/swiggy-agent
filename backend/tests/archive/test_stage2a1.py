"""
Stage 2A.1 Comprehensive Automated Regression Test Suite.
Tests:
1. Query Type Detection & Auto-Inference
2. Mutually Exclusive Category Memory Replacement Chain
3. Protected Hard Constraint Recovery
4. Premium Ranking Balancing
5. Full System Domain Regression (Cart, Checkout, Planner, Reset)
"""

import sys
import unittest
from typing import Dict, Any

from app.services.chat_orchestrator import ChatOrchestrator


class TestStage2A1(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.orchestrator = ChatOrchestrator()

    def setUp(self):
        self.session_id = "test-session-stage2a1-unit"
        self.orchestrator.session_manager.clear_session(self.session_id)

    def _get_context(self) -> Dict[str, Any]:
        return {"session_id": self.session_id, "user_id": "test_user"}

    # 1. Query Type Auto-Inference Tests
    def test_query_type_detection(self):
        cases = [
            ("Coffee", "beverage"),
            ("Dessert", "dessert"),
            ("Indian meals", "meal"),
            ("Burger combo", "combo"),
            ("Smoothie", "beverage"),
            ("Cake", "dessert"),
            ("Tea", "beverage"),
            ("Pizza", "meal"),
            ("Breakfast", "meal"),
            ("Dinner", "meal"),
        ]
        for prompt, expected_qtype in cases:
            with self.subTest(prompt=prompt):
                ctx = self.orchestrator._extract_recommendation_context(prompt, self._get_context())
                self.assertEqual(ctx.get("query_type"), expected_qtype, f"Failed for prompt: '{prompt}'")

    # 2. Mutually Exclusive Memory Replacement Chain
    def test_mutually_exclusive_memory_chain(self):
        session_state = self.orchestrator.session_manager.create_session(self.session_id)
        rec_mem = session_state.recommendation_memory

        # Turn 1: Dessert
        self.orchestrator.handle_message("Dessert", self._get_context())
        self.assertEqual(rec_mem.query_type, "dessert")
        self.assertEqual(rec_mem.category, "desserts")

        # Turn 2: Coffee (replaces dessert with beverage)
        self.orchestrator.handle_message("Coffee", self._get_context())
        self.assertEqual(rec_mem.query_type, "beverage")
        self.assertEqual(rec_mem.category, "beverages")

        # Turn 3: Indian meal (replaces beverage with meal)
        self.orchestrator.handle_message("Indian meal", self._get_context())
        self.assertEqual(rec_mem.query_type, "meal")
        self.assertEqual(rec_mem.cuisine_type, "Indian")

        # Turn 4: Chinese meal (updates cuisine, keeps meal)
        self.orchestrator.handle_message("Chinese meal", self._get_context())
        self.assertEqual(rec_mem.query_type, "meal")
        self.assertEqual(rec_mem.cuisine_type, "Chinese")

        # Turn 5: Family combo (replaces meal with combo, clears cuisine_type)
        self.orchestrator.handle_message("Family combo", self._get_context())
        self.assertEqual(rec_mem.query_type, "combo")
        self.assertEqual(rec_mem.serving, "family")
        self.assertIsNone(rec_mem.cuisine_type)

    # 3. Protected Hard Constraint Recovery Tests
    def test_protected_constraints(self):
        # Prompt 1: Dessert under 200
        res1 = self.orchestrator.handle_message("Dessert under 200", self._get_context())
        recs1 = res1.get("data", {}).get("recommendations", [])
        for item in recs1:
            parent_cat = item.get("parent_category", "").lower()
            self.assertTrue(
                parent_cat in ["desserts", "sweets", "breakfast & healthy bowls"] or 
                "dessert" in parent_cat or 
                any(k in item.get('item_name').lower() for k in ["cone", "ice", "parfait", "sweet", "cake", "dessert", "mcflurry", "lava", "yogurt"]), 
                f"Returned non-dessert item: {item.get('item_name')}"
            )

        # Reset memory for next test
        self.orchestrator.session_manager.clear_session(self.session_id)

        # Prompt 2: Italian under 100
        res2 = self.orchestrator.handle_message("Italian under 100", self._get_context())
        recs2 = res2.get("data", {}).get("recommendations", [])
        for item in recs2:
            cuisine = item.get("cuisine_type", item.get("cuisine", "")).lower()
            print(f"[TEST DEBUG] Italian item: {item.get('item_name')}, cuisine: '{cuisine}'")
            self.assertIn("italian", cuisine, f"Returned non-Italian item: {item.get('item_name')}")

        # Reset memory
        self.orchestrator.session_manager.clear_session(self.session_id)

        # Prompt 3: Coffee under 50
        res3 = self.orchestrator.handle_message("Coffee under 50", self._get_context())
        recs3 = res3.get("data", {}).get("recommendations", [])
        for item in recs3:
            cat = item.get("parent_category", "").lower()
            print(f"[TEST DEBUG] Coffee item: {item.get('item_name')}, cat: '{cat}'")
            self.assertTrue(cat in ["beverages", "coffee", "mccafe"] or "beverage" in cat or "coffee" in item.get('item_name').lower(), f"Returned non-beverage item: {item.get('item_name')}")

    # 4. Premium Item Ranking Balancing Tests
    def test_premium_balancing(self):
        # Case A: Standard prompt "Indian dinner" -> Everyday popular dishes rank top
        self.orchestrator.session_manager.clear_session(self.session_id)
        res_std = self.orchestrator.handle_message("Indian dinner", self._get_context())
        recs_std = res_std.get("data", {}).get("recommendations", [])
        self.assertTrue(len(recs_std) > 0)
        top_std_item = recs_std[0]
        print(f"[TEST DEBUG] Standard Indian top item: {top_std_item.get('item_name')}, price: {top_std_item.get('price')}")
        self.assertLessEqual(top_std_item.get("price", 0), 800, f"Standard query returned luxury item: {top_std_item.get('item_name')} price {top_std_item.get('price')}")

        # Case B: Luxury prompt "Luxury Indian dinner" -> Fine dining Taj/Suvarna dishes rank top
        self.orchestrator.session_manager.clear_session(self.session_id)
        res_lux = self.orchestrator.handle_message("Luxury Indian dinner", self._get_context())
        recs_lux = res_lux.get("data", {}).get("recommendations", [])
        self.assertTrue(len(recs_lux) > 0)
        top_lux_item = recs_lux[0]
        print(f"[TEST DEBUG] Luxury Indian top item: {top_lux_item.get('item_name')}, price: {top_lux_item.get('price')}")
        self.assertGreaterEqual(top_lux_item.get("price", 0), 900, f"Luxury query failed to rank fine dining: {top_lux_item.get('item_name')}")

    # 5. Full System Regression Tests (Cart, Checkout, Planner, Reset)
    def test_system_regression(self):
        # Cart query
        self.orchestrator.session_manager.clear_session(self.session_id)
        res_cart = self.orchestrator.handle_message("show my cart", self._get_context())
        self.assertIn(res_cart.get("intent"), ["view_cart", "cart_action"])

        # Checkout query
        self.orchestrator.session_manager.clear_session(self.session_id)
        res_chk = self.orchestrator.handle_message("checkout", self._get_context())
        self.assertIn(res_chk.get("intent"), ["checkout", "checkout_cart"])

        # Add to cart
        self.orchestrator.session_manager.clear_session(self.session_id)
        res_add = self.orchestrator.handle_message("add 2 cokes to cart", self._get_context())
        self.assertIn(res_add.get("intent"), ["modify_cart", "add_to_cart", "cart_action"])

        # Planner query
        self.orchestrator.session_manager.clear_session(self.session_id)
        res_plan = self.orchestrator.handle_message("plan my meals for tomorrow", self._get_context())
        self.assertIn(res_plan.get("intent"), ["meal_planner", "meal_planning"])


if __name__ == "__main__":
    unittest.main()
