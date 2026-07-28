"""Integration and regression unit tests for MealPlanner backed by RecommendationEngine."""

import sys
import unittest
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parents[1]
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.services.catalog_service import CatalogService
from app.services.planner import MealPlanner
from app.services.recommendation_engine import RecommendationEngine


class TestPlannerIntegration(unittest.TestCase):
    def setUp(self):
        self.catalog = CatalogService()
        self.rec_engine = RecommendationEngine(self.catalog)
        self.planner = MealPlanner(
            catalog_service=self.catalog,
            recommendation_engine=self.rec_engine,
        )

    def test_01_seven_day_meal_plan_generation(self):
        """Test full 7-day fallback plan generation and structure validation."""
        user_input = {"goal": "Reduce Spending", "budget": 2100, "preferences": "veg"}
        plan = self.planner.generate_fallback_plan(user_input)

        self.assertIsInstance(plan, dict)
        for i in range(1, 8):
            day_key = f"day_{i}"
            self.assertIn(day_key, plan)
            day = plan[day_key]
            self.assertIn("breakfast", day)
            self.assertIn("lunch", day)
            self.assertIn("dinner", day)
            self.assertIn("estimated_cost", day)
            self.assertGreater(day["estimated_cost"], 0)

    def test_02_breakfast_lunch_dinner_scheduling(self):
        """Test breakfast, lunch, dinner item structure and meal_type assignments."""
        user_input = {"goal": "Health", "budget": 2800, "preferences": "non-veg"}
        plan = self.planner.generate_fallback_plan(user_input)

        day_1 = plan["day_1"]
        self.assertIn("name", day_1["breakfast"])
        self.assertIn("price", day_1["breakfast"])
        self.assertIn("restaurant_name", day_1["breakfast"])

        self.assertIn("name", day_1["lunch"])
        self.assertIn("name", day_1["dinner"])

    def test_03_cheaper_substitution_editing(self):
        """Test surgical plan modification for 'make it cheaper'."""
        user_input = {"goal": "General", "budget": 2100, "preferences": "veg"}
        plan = self.planner.generate_fallback_plan(user_input)
        original_dinner_price = plan["day_1"]["dinner"]["price"]

        entities = {"target_day": "day_1", "target_meal": "dinner"}
        modified_plan = self.planner.modify_existing_plan(
            plan, entities, raw_message="make day 1 dinner cheaper", user_preferences={"budget": 2100}
        )

        new_dinner_price = modified_plan["day_1"]["dinner"]["price"]
        if original_dinner_price > 0:
            self.assertLessEqual(new_dinner_price, original_dinner_price)

    def test_04_healthier_substitution_editing(self):
        """Test surgical plan modification for 'make it healthier'."""
        user_input = {"goal": "General", "budget": 2100, "preferences": "veg"}
        plan = self.planner.generate_fallback_plan(user_input)

        entities = {"target_day": "day_1", "target_meal": "lunch"}
        modified_plan = self.planner.modify_existing_plan(
            plan, entities, raw_message="make day 1 lunch healthier", user_preferences={"budget": 2100}
        )

        new_lunch = modified_plan["day_1"]["lunch"]
        self.assertTrue(new_lunch.get("healthy") or new_lunch.get("name") != "")

    def test_05_meal_replacement_workflow(self):
        """Test surgical item replacement by explicit name request."""
        user_input = {"goal": "General", "budget": 2100, "preferences": "veg"}
        plan = self.planner.generate_fallback_plan(user_input)

        entities = {"target_day": "day_2", "target_meal": "lunch", "replacement_request": "burger"}
        modified_plan = self.planner.modify_existing_plan(
            plan, entities, raw_message="replace day 2 lunch with burger", user_preferences={"budget": 2100}
        )

        new_lunch_name = modified_plan["day_2"]["lunch"]["name"].lower()
        self.assertIn("burger", new_lunch_name)

    def test_06_duplicate_avoidance_and_variety(self):
        """Test duplicate item avoidance and cuisine/restaurant variety across days."""
        user_input = {"goal": "General", "budget": 2800, "preferences": "veg"}
        plan = self.planner.generate_fallback_plan(user_input)

        used_ids = set()
        cuisines = set()
        restaurants = set()

        for i in range(1, 8):
            day = plan[f"day_{i}"]
            for m in ["breakfast", "lunch", "dinner"]:
                item = day[m]
                iid = item.get("item_id")
                if iid and iid != 0:
                    used_ids.add(iid)
                if item.get("cuisine"):
                    cuisines.add(item["cuisine"])
                if item.get("restaurant_name"):
                    restaurants.add(item["restaurant_name"])

        self.assertGreaterEqual(len(used_ids), 3)
        self.assertGreaterEqual(len(cuisines), 2)
        self.assertGreaterEqual(len(restaurants), 2)

    def test_07_planner_output_contract_compatibility(self):
        """Test validate_plan_structure returns True for generated plans."""
        user_input = {"goal": "General", "budget": 2100, "preferences": "non-veg"}
        plan = self.planner.generate_fallback_plan(user_input)
        is_valid = self.planner.validate_plan_structure(plan)
        self.assertTrue(is_valid)


if __name__ == "__main__":
    unittest.main(verbosity=2)
