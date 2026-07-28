"""Unit tests for CatalogAdapter."""

import unittest
from app.services.catalog.catalog_adapter import CatalogAdapter


class TestCatalogAdapter(unittest.TestCase):
    def test_to_legacy_item_mapping(self):
        kb_item = {
            "item_id": 101,
            "name": "McAloo Tikki Burger",
            "description": "Golden fried potato patty",
            "meal_type": "LUNCH",
            "available": True,
            "dietary_safety": {
                "is_veg": True,
                "is_vegan": False,
                "is_gluten_free": False,
            },
            "health_scores": {
                "overall_health_score": 7.5,
            },
            "nutrition": {
                "macronutrients": {
                    "protein_g": 8.5,
                    "calories_kcal": 339.5,
                }
            },
            "mood_sensory": {
                "spicy": False,
            },
            "commerce_intelligence": {
                "price": 65
            },
            "restaurant_id": 1,
        }

        restaurant = {
            "restaurant_id": 1,
            "name": "McDonald's",
            "primary_cuisine": "Fast Food"
        }

        legacy_item = CatalogAdapter.to_legacy_item(kb_item, restaurant)

        self.assertEqual(legacy_item["item_id"], 101)
        self.assertEqual(legacy_item["name"], "McAloo Tikki Burger")
        self.assertEqual(legacy_item["price"], 65)
        self.assertEqual(legacy_item["category"], "veg")
        self.assertEqual(legacy_item["meal_type"], "lunch")
        self.assertTrue(legacy_item["healthy"])
        self.assertTrue(legacy_item["vegetarian"])
        self.assertFalse(legacy_item["high_protein"])
        self.assertTrue(legacy_item["low_calorie"])
        self.assertEqual(legacy_item["restaurant_name"], "McDonald's")
        self.assertEqual(legacy_item["cuisine"], "Fast Food")

    def test_to_legacy_restaurant_mapping(self):
        kb_restaurant = {
            "restaurant_id": 1,
            "name": "McDonald's",
            "primary_cuisine": "Fast Food",
            "rating": 4.5,
            "delivery_time_mins": 25,
        }

        legacy_rest = CatalogAdapter.to_legacy_restaurant(kb_restaurant, [])

        self.assertEqual(legacy_rest["restaurant_id"], 1)
        self.assertEqual(legacy_rest["name"], "McDonald's")
        self.assertEqual(legacy_rest["cuisine"], "Fast Food")
        self.assertEqual(legacy_rest["rating"], 4.5)
        self.assertEqual(legacy_rest["delivery_time"], 25)
        self.assertEqual(legacy_rest["menu"], [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
