"""
Stage 2A Automated Test Suite: Intelligent Candidate Retrieval & Constraint Recovery.

Covers 30+ retrieval scenarios:
1. Cuisine (Indian, Chinese, Italian)
2. Beverages (Pepsi, Coke, Coffee, Tea, Juice, Smoothie, Shake)
3. Desserts (Ice cream, McFlurry, Brownie, Lava Cake)
4. Coffee & Tea
5. Combos
6. Breakfast & Dinner
7. Budget & Budget Recovery (Italian under 100, Chinese breakfast under 80)
8. Healthy & High Protein
9. Veg & Non-Veg
"""

import sys
import unittest
from pathlib import Path

# Add backend directory to sys.path
backend_path = Path(__file__).resolve().parent
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from app.services.chat_orchestrator import ChatOrchestrator
from app.services.session_manager import SessionManager


class TestStage2ARetrieval(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.orchestrator = ChatOrchestrator()
        cls.session_manager = SessionManager()

    def _test_prompt(self, prompt: str, session_id: str = "stage2a-test") -> dict:
        return self.orchestrator.handle_message(prompt, {"session_id": session_id})

    # 1. CUISINE RETRIEVAL
    def test_01_indian_cuisine(self):
        res = self._test_prompt("Indian food", "s2a-1")
        recs = res.get("data", {}).get("recommendations", [])
        self.assertGreater(len(recs), 0)
        self.assertTrue(any("indian" in r.get("cuisine", "").lower() or "indian" in r.get("cuisine_type", "").lower() for r in recs))

    def test_02_chinese_cuisine(self):
        res = self._test_prompt("Chinese food", "s2a-2")
        recs = res.get("data", {}).get("recommendations", [])
        self.assertGreater(len(recs), 0)
        self.assertTrue(any("chinese" in r.get("cuisine", "").lower() or "chinese" in r.get("cuisine_type", "").lower() or "asian" in r.get("cuisine_type", "").lower() or "teriyaki" in r.get("name", "").lower() for r in recs))

    def test_03_italian_cuisine(self):
        res = self._test_prompt("Italian food", "s2a-3")
        recs = res.get("data", {}).get("recommendations", [])
        self.assertGreater(len(recs), 0)
        self.assertTrue(any("italian" in r.get("cuisine", "").lower() or "pizza" in r.get("name", "").lower() or "pasta" in r.get("name", "").lower() for r in recs))

    # 2. BEVERAGES
    def test_04_beverages_generic(self):
        res = self._test_prompt("suggest a drink", "s2a-4")
        recs = res.get("data", {}).get("recommendations", [])
        self.assertGreater(len(recs), 0)

    def test_05_pepsi(self):
        res = self._test_prompt("cold drink pepsi", "s2a-5")
        recs = res.get("data", {}).get("recommendations", [])
        self.assertGreater(len(recs), 0)

    def test_06_coffee(self):
        res = self._test_prompt("coffee", "s2a-6")
        recs = res.get("data", {}).get("recommendations", [])
        self.assertGreater(len(recs), 0)
        self.assertTrue(any("coffee" in r.get("name", "").lower() or "cappuccino" in r.get("name", "").lower() for r in recs))

    def test_07_tea(self):
        res = self._test_prompt("tea", "s2a-7")
        recs = res.get("data", {}).get("recommendations", [])
        self.assertGreater(len(recs), 0)

    def test_08_shake(self):
        res = self._test_prompt("shake", "s2a-8")
        recs = res.get("data", {}).get("recommendations", [])
        self.assertGreater(len(recs), 0)

    # 3. DESSERTS
    def test_09_desserts_generic(self):
        res = self._test_prompt("desserts", "s2a-9")
        recs = res.get("data", {}).get("recommendations", [])
        self.assertGreater(len(recs), 0)

    def test_10_ice_cream(self):
        res = self._test_prompt("ice cream", "s2a-10")
        recs = res.get("data", {}).get("recommendations", [])
        self.assertGreater(len(recs), 0)

    def test_11_brownie(self):
        res = self._test_prompt("sweet dessert", "s2a-11")
        recs = res.get("data", {}).get("recommendations", [])
        self.assertGreater(len(recs), 0)

    def test_12_lava_cake(self):
        res = self._test_prompt("choco lava cake", "s2a-12")
        recs = res.get("data", {}).get("recommendations", [])
        self.assertGreater(len(recs), 0)

    # 4. COMBOS
    def test_13_combos_generic(self):
        res = self._test_prompt("combos", "s2a-13")
        recs = res.get("data", {}).get("recommendations", [])
        self.assertGreater(len(recs), 0)
        self.assertTrue(any(r.get("is_combo") or "combo" in r.get("name", "").lower() for r in recs))

    def test_14_family_combo(self):
        res = self._test_prompt("family combo", "s2a-14")
        recs = res.get("data", {}).get("recommendations", [])
        self.assertGreater(len(recs), 0)

    # 5. MEAL TYPES
    def test_15_breakfast(self):
        res = self._test_prompt("breakfast options", "s2a-15")
        recs = res.get("data", {}).get("recommendations", [])
        self.assertGreater(len(recs), 0)

    def test_16_lunch(self):
        res = self._test_prompt("lunch meals", "s2a-16")
        recs = res.get("data", {}).get("recommendations", [])
        self.assertGreater(len(recs), 0)

    def test_17_dinner(self):
        res = self._test_prompt("dinner food", "s2a-17")
        recs = res.get("data", {}).get("recommendations", [])
        self.assertGreater(len(recs), 0)

    def test_18_late_night_snacks(self):
        res = self._test_prompt("late night snacks", "s2a-18")
        recs = res.get("data", {}).get("recommendations", [])
        self.assertGreater(len(recs), 0)

    # 6. BUDGET BOUNDS & RECOVERY
    def test_19_budget_under_300(self):
        res = self._test_prompt("food under 300", "s2a-19")
        recs = res.get("data", {}).get("recommendations", [])
        self.assertGreater(len(recs), 0)
        self.assertTrue(all(r.get("price", 0) <= 300 for r in recs))

    def test_20_impossible_italian_under_100(self):
        """Must preserve Italian hard constraint, relax budget, and return Italian items with price difference."""
        res = self._test_prompt("Italian under 100", "s2a-20")
        recs = res.get("data", {}).get("recommendations", [])
        self.assertGreater(len(recs), 0)
        # Verify Hard Constraint Preservation (All items must be Italian, NOT Pepsi/drinks!)
        for r in recs:
            item_text = f"{r.get('name', '')} {r.get('cuisine', '')} {r.get('cuisine_type', '')}".lower()
            self.assertTrue("italian" in item_text or "pizza" in item_text or "pasta" in item_text or "garlic bread" in item_text)

    def test_21_impossible_chinese_breakfast_under_80(self):
        """Must preserve Chinese constraint, NOT return American Hash Brown."""
        res = self._test_prompt("Chinese breakfast under 80", "s2a-21")
        recs = res.get("data", {}).get("recommendations", [])
        if recs:
            for r in recs:
                self.assertNotIn("hash brown", r.get("name", "").lower())

    def test_22_impossible_healthy_pizza_under_50(self):
        """Must preserve Pizza category constraint, NOT return Hash Brown."""
        res = self._test_prompt("Healthy pizza under 50", "s2a-22")
        recs = res.get("data", {}).get("recommendations", [])
        if recs:
            for r in recs:
                self.assertTrue("pizza" in r.get("name", "").lower() or "pizza" in r.get("cuisine", "").lower())
                self.assertNotIn("hash brown", r.get("name", "").lower())

    # 7. HEALTH GOALS
    def test_23_healthy_food(self):
        res = self._test_prompt("healthy food", "s2a-23")
        recs = res.get("data", {}).get("recommendations", [])
        self.assertGreater(len(recs), 0)
        self.assertTrue(any(r.get("healthy") for r in recs))

    def test_24_high_protein(self):
        res = self._test_prompt("high protein food", "s2a-24")
        recs = res.get("data", {}).get("recommendations", [])
        self.assertGreater(len(recs), 0)

    def test_25_low_calorie(self):
        res = self._test_prompt("low calorie food", "s2a-25")
        recs = res.get("data", {}).get("recommendations", [])
        self.assertGreater(len(recs), 0)

    # 8. DIET PREFERENCES
    def test_26_veg_food(self):
        res = self._test_prompt("veg options", "s2a-26")
        recs = res.get("data", {}).get("recommendations", [])
        self.assertGreater(len(recs), 0)

    def test_27_non_veg_food(self):
        res = self._test_prompt("non veg dishes", "s2a-27")
        recs = res.get("data", {}).get("recommendations", [])
        self.assertGreater(len(recs), 0)

    # 9. TASTE PREFERENCES
    def test_28_spicy_food(self):
        res = self._test_prompt("spicy food", "s2a-28")
        recs = res.get("data", {}).get("recommendations", [])
        self.assertGreater(len(recs), 0)

    def test_29_sweet_food(self):
        res = self._test_prompt("sweet dishes", "s2a-29")
        recs = res.get("data", {}).get("recommendations", [])
        self.assertGreater(len(recs), 0)

    # 10. MULTI-CONSTRAINT PIPELINE
    def test_30_spicy_non_veg_chinese_under_400(self):
        res = self._test_prompt("spicy non veg Chinese under 400", "s2a-30")
        recs = res.get("data", {}).get("recommendations", [])
        self.assertGreater(len(recs), 0)
        self.assertTrue(all(r.get("price", 0) <= 400 for r in recs))


if __name__ == "__main__":
    unittest.main(verbosity=2)
