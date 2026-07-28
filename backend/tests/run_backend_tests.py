"""Standard unittest test runner for backend tests."""

import sys
import unittest
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parents[1]
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.services.knowledge_base.json_loader import KnowledgeBaseJSONLoader, KnowledgeBaseLoadError
from app.services.knowledge_base.validators import KnowledgeBaseValidator, KnowledgeBaseValidationError
from app.services.knowledge_base.indexes import KnowledgeBaseIndexes
from app.services.knowledge_base.knowledge_base_service import KnowledgeBaseService


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


if __name__ == "__main__":
    unittest.main(verbosity=2)
