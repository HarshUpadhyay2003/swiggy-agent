"""Standard unittest test runner for Stage 1A and Stage 1B backend test suites."""

import sys
import unittest
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parents[1]
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Stage 1A Imports
from app.services.knowledge_base.json_loader import KnowledgeBaseJSONLoader, KnowledgeBaseLoadError
from app.services.knowledge_base.validators import KnowledgeBaseValidator, KnowledgeBaseValidationError
from app.services.knowledge_base.indexes import KnowledgeBaseIndexes
from app.services.knowledge_base.knowledge_base_service import KnowledgeBaseService

# Stage 1B Imports
from app.services.catalog.catalog_adapter import CatalogAdapter
from app.services.catalog_service import CatalogService
from app.services.context_engine import ContextEngine
from app.services.planner import MealPlanner
from app.services.cart_service import CartService
from app.services.order_service import OrderService


# STAGE 1A TEST SUITES
class TestJSONLoader(unittest.TestCase):
    def test_load_real_knowledge_base(self):
        loader = KnowledgeBaseJSONLoader()
        restaurants = loader.load_restaurants()
        menu_items = loader.load_menu_items()
        combos = loader.load_combos()
        categories = loader.load_category_registry()

        self.assertIsInstance(restaurants, list)
        self.assertGreaterEqual(len(restaurants), 6)
        self.assertIsInstance(menu_items, list)
        self.assertGreaterEqual(len(menu_items), 35)

    def test_missing_file_raises_error(self):
        loader = KnowledgeBaseJSONLoader(base_dir="non_existent_directory_xyz")
        with self.assertRaises(KnowledgeBaseLoadError):
            loader.load_restaurants()


class TestValidator(unittest.TestCase):
    def test_validator_passes_on_real_data(self):
        loader = KnowledgeBaseJSONLoader()
        restaurants = loader.load_restaurants()
        menu_items = loader.load_menu_items()
        combos = loader.load_combos()
        categories = loader.load_category_registry()

        validator = KnowledgeBaseValidator()
        validator.validate_all(restaurants, menu_items, combos, categories)

    def test_duplicate_restaurant_id_fails(self):
        validator = KnowledgeBaseValidator()
        restaurants = [
            {"restaurant_id": 1, "restaurant_code": "MCD", "name": "McD", "primary_cuisine": "Fast Food", "operating_hours": {}, "confidence": {}},
            {"restaurant_id": 1, "restaurant_code": "MCD2", "name": "McD2", "primary_cuisine": "Fast Food", "operating_hours": {}, "confidence": {}},
        ]
        with self.assertRaises(KnowledgeBaseValidationError):
            validator.validate_all(restaurants, [], [], [])


class TestIndexes(unittest.TestCase):
    def test_indexing_and_o1_lookup(self):
        indexes = KnowledgeBaseIndexes()
        restaurants = [{"restaurant_id": 1, "restaurant_code": "MCD", "name": "McDonald's"}]
        categories = [{"category_id": "CAT_BURGERS_VEG", "display_name": "Vegetarian Burgers"}]
        menu_items = [{
            "item_id": 101,
            "restaurant_id": 1,
            "item_code": "MCD_BURGER_001",
            "name": "McAloo Tikki",
            "category_intelligence": {"category_id": "CAT_BURGERS_VEG"},
            "search_aliases": ["mcaloo", "aloo tikki"]
        }]
        combos = [{"combo_id": 2001, "combo_code": "KFC_COMBO_001", "combo_name": "Zinger Box"}]

        indexes.build_indexes(restaurants, menu_items, combos, categories)

        self.assertEqual(indexes.restaurant_by_id.get(1)["name"], "McDonald's")
        self.assertEqual(indexes.item_by_id.get(101)["name"], "McAloo Tikki")
        self.assertEqual(len(indexes.alias_index.get("mcaloo")), 1)


class TestKnowledgeBaseService(unittest.TestCase):
    def test_service_initialization_and_queries(self):
        service = KnowledgeBaseService()
        stats = service.get_statistics()
        self.assertTrue(stats["is_loaded"])
        self.assertGreaterEqual(stats["total_restaurants"], 6)
        self.assertGreaterEqual(stats["total_menu_items"], 35)

        mcd = service.get_restaurant(1)
        self.assertIsNotNone(mcd)
        self.assertEqual(mcd["name"], "McDonald's")

        item_101 = service.get_item(101)
        self.assertIsNotNone(item_101)

        fries_matches = service.search_alias("fries")
        self.assertGreaterEqual(len(fries_matches), 1)


# STAGE 1B TEST SUITES
class TestCatalogAdapter(unittest.TestCase):
    def test_to_legacy_item_mapping(self):
        kb_item = {
            "item_id": 101,
            "name": "McAloo Tikki Burger",
            "description": "Golden fried potato patty",
            "meal_type": "LUNCH",
            "available": True,
            "dietary_safety": {"is_veg": True, "is_vegan": False, "is_gluten_free": False},
            "health_scores": {"overall_health_score": 7.5},
            "nutrition": {"macronutrients": {"protein_g": 8.5, "calories_kcal": 339.5}},
            "mood_sensory": {"spicy": False},
            "commerce_intelligence": {"price": 65},
            "restaurant_id": 1,
        }
        restaurant = {"restaurant_id": 1, "name": "McDonald's", "primary_cuisine": "Fast Food"}

        legacy_item = CatalogAdapter.to_legacy_item(kb_item, restaurant)
        self.assertEqual(legacy_item["item_id"], 101)
        self.assertEqual(legacy_item["name"], "McAloo Tikki Burger")
        self.assertEqual(legacy_item["price"], 65)
        self.assertEqual(legacy_item["category"], "veg")
        self.assertEqual(legacy_item["restaurant_name"], "McDonald's")

    def test_to_legacy_restaurant_mapping(self):
        kb_restaurant = {"restaurant_id": 1, "name": "McDonald's", "primary_cuisine": "Fast Food", "rating": 4.5, "delivery_time_mins": 25}
        legacy_rest = CatalogAdapter.to_legacy_restaurant(kb_restaurant, [])
        self.assertEqual(legacy_rest["delivery_time"], 25)


class TestCatalogServiceMigrated(unittest.TestCase):
    def setUp(self):
        self.service = CatalogService()

    def test_get_all_restaurants(self):
        restaurants = self.service.get_all_restaurants()
        self.assertGreaterEqual(len(restaurants), 6)

    def test_get_available_items(self):
        items = self.service.get_available_items()
        self.assertGreaterEqual(len(items), 35)

    def test_get_item_by_id(self):
        item = self.service.get_item_by_id(101)
        self.assertEqual(item["name"], "McAloo Tikki Burger")

    def test_search_items(self):
        results = self.service.search_items("burger")
        self.assertGreaterEqual(len(results), 1)


class TestBackwardCompatibilityIntegration(unittest.TestCase):
    def setUp(self):
        self.catalog_service = CatalogService()
        self.context_engine = ContextEngine(self.catalog_service)
        self.meal_planner = MealPlanner(self.catalog_service)
        self.cart_service = CartService(self.catalog_service)
        self.order_service = OrderService(self.catalog_service)

    def test_context_engine_recommendations(self):
        res = self.context_engine.recommend_food({"preference": "veg", "max_budget": 300})
        self.assertGreater(len(res["recommendations"]), 0)

    def test_cart_service_add_and_totals(self):
        item = self.catalog_service.get_item_by_id(101)
        cart = self.cart_service.add_to_cart("session_1b", item, quantity=2)
        self.assertGreater(cart["total"], 0)

    def test_order_service_place_order(self):
        order = self.order_service.place_order([101, 201])
        self.assertEqual(len(order["items"]), 2)
        self.assertGreater(order["estimated_delivery_time"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
