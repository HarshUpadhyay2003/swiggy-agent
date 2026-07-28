"""Unit tests for migrated CatalogService API."""

import unittest
from app.services.catalog_service import CatalogService


class TestCatalogService(unittest.TestCase):
    def setUp(self):
        self.service = CatalogService()

    def test_get_all_restaurants(self):
        restaurants = self.service.get_all_restaurants()
        self.assertIsInstance(restaurants, list)
        self.assertGreaterEqual(len(restaurants), 6)

        first_rest = restaurants[0]
        self.assertIn("restaurant_id", first_rest)
        self.assertIn("name", first_rest)
        self.assertIn("cuisine", first_rest)
        self.assertIn("delivery_time", first_rest)
        self.assertIn("menu", first_rest)

    def test_get_available_items(self):
        items = self.service.get_available_items()
        self.assertIsInstance(items, list)
        self.assertGreaterEqual(len(items), 35)

    def test_get_item_by_id(self):
        item_101 = self.service.get_item_by_id(101)
        self.assertEqual(item_101["item_id"], 101)
        self.assertEqual(item_101["name"], "McAloo Tikki Burger")
        self.assertEqual(item_101["restaurant_name"], "McDonald's")

    def test_invalid_item_id_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.service.get_item_by_id(999999)

    def test_search_items_and_alias(self):
        results = self.service.search_items("burger")
        self.assertGreaterEqual(len(results), 1)

        alias_results = self.service.search_items("mcaloo")
        self.assertGreaterEqual(len(alias_results), 1)

    def test_get_budget_meals(self):
        budget_meals = self.service.get_budget_meals(max_price=100)
        self.assertTrue(all(item["price"] <= 100 for item in budget_meals))

    def test_get_items_by_preference(self):
        veg_items = self.service.get_items_by_preference("veg")
        self.assertTrue(all(item["category"] == "veg" for item in veg_items))

        non_veg_items = self.service.get_items_by_preference("non-veg")
        self.assertTrue(all(item["category"] == "non-veg" for item in non_veg_items))

    def test_invalid_preference_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.service.get_items_by_preference("invalid_preference")


if __name__ == "__main__":
    unittest.main(verbosity=2)
