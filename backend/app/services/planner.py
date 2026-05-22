from typing import Dict, Any, List, Optional
from .llm_service import GroqService

try:
    from .catalog_service import CatalogService
except ImportError:
    from app.services.catalog_service import CatalogService


class MealPlanner:
    """
    MealPlanner class for generating structured 7-day meal plans using Groq LLM.

    This class handles user goals, budget constraints, and dietary preferences
    to create realistic Indian meal plans. It includes fallback logic for robustness.
    """

    def __init__(self, catalog_service: Optional[CatalogService] = None):
        """Initialize the MealPlanner with GroqService and CatalogService."""
        self.llm_service = GroqService()
        self.catalog_service = catalog_service or CatalogService()

    def _parse_budget(self, budget: Any, default: int = 2000) -> int:
        try:
            return int(budget)
        except (TypeError, ValueError):
            return default

    def _normalize_preference(self, preference: Optional[str]) -> Optional[str]:
        if not preference:
            return None
        normalized = preference.strip().lower()
        if normalized in {"nonveg", "non veg"}:
            return "non-veg"
        if normalized in {"veg", "non-veg"}:
            return normalized
        return normalized

    def _catalog_items(
        self,
        preference: Optional[str] = None,
        meal_type: Optional[str] = None,
        max_price: Optional[int] = None,
        healthy_only: bool = False,
        exclude_ids: Optional[set[int]] = None,
    ) -> List[Dict[str, Any]]:
        items = self.catalog_service.get_available_items()

        if preference:
            normalized_preference = self._normalize_preference(preference)
            if normalized_preference in {"veg", "non-veg"}:
                items = [
                    item
                    for item in items
                    if item.get("category", "").lower() == normalized_preference
                ]

        if meal_type:
            items = [
                item
                for item in items
                if item.get("meal_type", "").lower() == meal_type.lower()
            ]

        if max_price is not None:
            items = [
                item
                for item in items
                if isinstance(item.get("price"), (int, float)) and item["price"] <= max_price
            ]

        if healthy_only:
            items = [item for item in items if item.get("healthy")]

        if exclude_ids:
            items = [item for item in items if item.get("item_id") not in exclude_ids]

        return items

    def _select_varied_item(
        self,
        preference: Optional[str],
        meal_type: str,
        max_price: Optional[int],
        used_item_ids: Optional[set] = None,
        cuisine_freq: Optional[dict] = None,
        rest_freq: Optional[dict] = None,
    ) -> Optional[Dict[str, Any]]:
        candidates = self._catalog_items(
            preference=preference,
            meal_type=meal_type,
            max_price=max_price,
        )
        if not candidates:
            return None
            
        used_item_ids = used_item_ids or set()
        cuisine_freq = cuisine_freq or {}
        rest_freq = rest_freq or {}
        
        def score(item):
            penalty = 0
            if item.get("item_id") in used_item_ids:
                penalty += 1000
                
            cuisine = item.get("cuisine", "")
            if cuisine:
                penalty += cuisine_freq.get(cuisine, 0) * 50
                
            rest = item.get("restaurant_name", "")
            if rest:
                penalty += rest_freq.get(rest, 0) * 50
                
            price = item.get("price", 0)
            if meal_type == "breakfast" and price > 150:
                penalty += 100
            elif meal_type == "lunch" and price < 100:
                penalty += 50
            elif meal_type == "dinner" and price > 300:
                penalty += 50
                
            return (penalty, price, item.get("restaurant_id", 0), item.get("item_id", 0))
            
        candidates = sorted(candidates, key=score)
        return candidates[0]

    def _structure_plan_items(
        self,
        plan: Dict[str, Any],
        preferences: Optional[str] = None,
        daily_budget: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Convert text meal names in plan to structured items from catalog."""
        structured_plan = {}
        used_item_ids = set()
        cuisine_freq = {}
        rest_freq = {}
        
        for day_key, day_data in plan.items():
            structured_day: Dict[str, Any] = {}
            for meal_type in ["breakfast", "lunch", "dinner"]:
                meal = day_data.get(meal_type)
                if isinstance(meal, str):
                    meal_name = meal
                elif isinstance(meal, dict):
                    meal_name = meal.get("name", "")
                else:
                    meal_name = "Mixed Meal"
                    
                structured_item = self._structure_meal_item(
                    meal_name,
                    max_price=daily_budget,
                    preference=preferences,
                    meal_type=meal_type,
                    used_item_ids=used_item_ids,
                    cuisine_freq=cuisine_freq,
                    rest_freq=rest_freq,
                )
                
                if structured_item.get("item_id"):
                    used_item_ids.add(structured_item["item_id"])
                c = structured_item.get("cuisine")
                if c: cuisine_freq[c] = cuisine_freq.get(c, 0) + 1
                r = structured_item.get("restaurant_name")
                if r: rest_freq[r] = rest_freq.get(r, 0) + 1
                
                structured_day[meal_type] = structured_item

            total_cost = sum(
                item.get("price", 0)
                for item in (
                    structured_day[meal]
                    for meal in ["breakfast", "lunch", "dinner"]
                    if isinstance(structured_day.get(meal), dict)
                )
                if isinstance(item.get("price", 0), (int, float))
            )
            structured_day["estimated_cost"] = total_cost
            structured_plan[day_key] = structured_day
        return structured_plan

    def generate_meal_plan(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a 7-day meal plan based on user input.

        Args:
            user_input (dict): Contains 'goal', 'budget', 'preferences'

        Returns:
            dict: Structured meal plan with day_1 to day_7
        """
        prompt = self.build_prompt(user_input)
        budget = self._parse_budget(user_input.get("budget", 2000))
        daily_budget = budget // 7 if budget else None

        try:
            plan = self.llm_service.generate_json_response(prompt)
            if self.validate_plan_structure(plan):
                return self._structure_plan_items(
                    plan,
                    preferences=user_input.get("preferences"),
                    daily_budget=daily_budget,
                )
            else:
                return self.generate_fallback_plan(user_input, daily_budget=daily_budget)
        except Exception:
            return self.generate_fallback_plan(user_input, daily_budget=daily_budget)

    def build_prompt(self, user_input: Dict[str, Any]) -> str:
        """
        Build the LLM prompt based on user input.

        Args:
            user_input (dict): User preferences

        Returns:
            str: Formatted prompt for LLM
        """
        goal = user_input.get('goal', 'General')
        budget = user_input.get('budget', 2000)
        preferences = user_input.get('preferences', 'veg')

        prompt = f"""
You must return ONLY valid JSON. Do not include explanations, markdown, comments, or extra text.

Generate a 7-day meal plan for a user with the following details:

Goal: {goal}
Budget: {budget} INR per week
Preferences: {preferences}

The plan should be a JSON object with keys day_1 to day_7.

Each day should have:
- breakfast: string (meal name)
- lunch: string (meal name)
- dinner: string (meal name)
- estimated_cost: number (daily cost in INR)

Requirements:
- Total weekly cost should be close to {budget} INR
- Meals should be realistic Indian meals
- Consider the goal: if "Reduce Spending", use cheaper ingredients; if "Improve Eating Habits", focus on healthier options
- Respect preferences: if "veg", avoid non-veg items; if "non-veg", include meat/fish
- Avoid luxury or expensive foods
- Keep meals varied but practical
- Do NOT repeat the same meal across different days.
- Breakfast should be lighter/cheaper, Lunch should be filling, Dinner should be balanced.
- Ensure variety in cuisines and meal types across the week.

Return only the JSON object.
"""
        return prompt

    def validate_plan_structure(self, plan: Dict[str, Any]) -> bool:
        """
        Validate the structure of the generated meal plan.

        Args:
            plan (dict): The meal plan to validate

        Returns:
            bool: True if valid, False otherwise
        """
        if not isinstance(plan, dict):
            return False

        for i in range(1, 8):
            day_key = f"day_{i}"
            if day_key not in plan:
                return False

            day = plan[day_key]
            if not isinstance(day, dict):
                return False

            required_keys = ['breakfast', 'lunch', 'dinner', 'estimated_cost']
            if not all(key in day for key in required_keys):
                return False

            if not isinstance(day['estimated_cost'], (int, float)):
                return False

            # Ensure meal names are strings
            for meal in ['breakfast', 'lunch', 'dinner']:
                if not isinstance(day[meal], str):
                    return False

        return True

    def _find_item_by_name(
        self,
        name: str,
        max_price: Optional[int] = None,
        preference: Optional[str] = None,
        meal_type: Optional[str] = None,
        used_item_ids: Optional[set] = None,
        cuisine_freq: Optional[dict] = None,
        rest_freq: Optional[dict] = None,
    ) -> Optional[Dict[str, Any]]:
        """Find a catalog item by name (fuzzy match) while respecting constraints."""
        items = self._catalog_items(
            preference=preference,
            meal_type=meal_type,
            max_price=max_price,
        )
        if not items:
            return None
            
        name_lower = name.lower().strip()
        matches = [item for item in items if name_lower in item.get("name", "").lower()]
        if not matches:
            matches = items
            
        used_item_ids = used_item_ids or set()
        cuisine_freq = cuisine_freq or {}
        rest_freq = rest_freq or {}
        
        def score(item):
            penalty = 0
            if item.get("item_id") in used_item_ids:
                penalty += 1000
            penalty += cuisine_freq.get(item.get("cuisine"), 0) * 50
            penalty += rest_freq.get(item.get("restaurant_name"), 0) * 50
            
            exact_match_bonus = -10 if item.get("name", "").lower() == name_lower else 0
            return (penalty + exact_match_bonus, item.get("price", 0), item.get("item_id", 0))
            
        matches.sort(key=score)
        return matches[0]

    def _structure_meal_item(
        self,
        meal_name: str,
        max_price: Optional[int] = None,
        preference: Optional[str] = None,
        meal_type: Optional[str] = None,
        used_item_ids: Optional[set] = None,
        cuisine_freq: Optional[dict] = None,
        rest_freq: Optional[dict] = None,
    ) -> Dict[str, Any]:
        """Convert meal name to structured item from catalog."""
        item = self._find_item_by_name(
            meal_name,
            max_price=max_price,
            preference=preference,
            meal_type=meal_type,
            used_item_ids=used_item_ids,
            cuisine_freq=cuisine_freq,
            rest_freq=rest_freq,
        )

        if not item and meal_type:
            item = self._select_varied_item(
                preference,
                meal_type,
                max_price=max_price,
                used_item_ids=used_item_ids,
                cuisine_freq=cuisine_freq,
                rest_freq=rest_freq,
            )

        if not item and max_price is None:
            item = self._find_item_by_name(
                meal_name,
                preference=preference,
                meal_type=meal_type,
                used_item_ids=used_item_ids,
                cuisine_freq=cuisine_freq,
                rest_freq=rest_freq,
            )

        if item:
            return {
                "item_id": item.get("item_id", 0),
                "name": item.get("name", meal_name),
                "price": item.get("price", max_price if max_price is not None else 150),
                "restaurant_name": item.get("restaurant_name", "Restaurant"),
                "cuisine": item.get("cuisine", "Indian"),
                "healthy": item.get("healthy", False),
                "vegetarian": item.get("vegetarian", True),
            }

        return {
            "item_id": 0,
            "name": meal_name,
            "price": max_price if max_price is not None else 150,
            "restaurant_name": "Default",
            "cuisine": "Indian",
            "healthy": False,
            "vegetarian": True,
        }

    def generate_fallback_plan(
        self,
        user_input: Dict[str, Any],
        daily_budget: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Generate a fallback meal plan if LLM fails.

        Args:
            user_input (dict): User preferences for fallback customization
            daily_budget (int | None): Daily budget for each day in INR

        Returns:
            dict: Basic meal plan with structured items
        """
        preferences = self._normalize_preference(user_input.get("preferences", "veg"))
        budget = self._parse_budget(user_input.get("budget", 2000))
        if daily_budget is None:
            daily_budget = budget // 7 if budget else None

        plan: Dict[str, Any] = {}
        used_item_ids = set()
        cuisine_freq = {}
        rest_freq = {}

        for i in range(1, 8):
            day_items: Dict[str, Any] = {}
            for meal_type in ["breakfast", "lunch", "dinner"]:
                item = self._select_varied_item(
                    preferences,
                    meal_type,
                    max_price=daily_budget,
                    used_item_ids=used_item_ids,
                    cuisine_freq=cuisine_freq,
                    rest_freq=rest_freq,
                )
                if not item and daily_budget is not None:
                    item = self._select_varied_item(
                        preferences,
                        meal_type,
                        max_price=daily_budget,
                    )
                if not item and daily_budget is None:
                    item = self._select_varied_item(
                        preferences,
                        meal_type,
                        max_price=None,
                        used_item_ids=used_item_ids,
                    )
                if not item:
                    item = self._find_item_by_name(
                        f"{meal_type.title()} Meal",
                        max_price=daily_budget,
                        preference=preferences,
                        meal_type=meal_type,
                    )

                meal_name = item["name"] if item else f"{meal_type.title()} Meal"
                
                structured_item = self._structure_meal_item(
                    meal_name,
                    max_price=daily_budget,
                    preference=preferences,
                    meal_type=meal_type,
                    used_item_ids=used_item_ids,
                    cuisine_freq=cuisine_freq,
                    rest_freq=rest_freq,
                )

                if structured_item.get("item_id"):
                    used_item_ids.add(structured_item["item_id"])
                c = structured_item.get("cuisine")
                if c: cuisine_freq[c] = cuisine_freq.get(c, 0) + 1
                r = structured_item.get("restaurant_name")
                if r: rest_freq[r] = rest_freq.get(r, 0) + 1
                    
                day_items[meal_type] = structured_item

            total_cost = sum(
                item.get("price", 0)
                for item in (
                    day_items[meal]
                    for meal in ["breakfast", "lunch", "dinner"]
                )
                if isinstance(item.get("price", 0), (int, float))
            )
            day_items["estimated_cost"] = total_cost
            plan[f"day_{i}"] = day_items

        return plan


if __name__ == "__main__":
    import json

    planner = MealPlanner()

    # Test 1: Reduce Spending + veg
    input1 = {"goal": "Reduce Spending", "budget": 2000, "preferences": "veg"}
    plan1 = planner.generate_meal_plan(input1)
    print("Test 1 - Reduce Spending + Veg:")
    print(json.dumps(plan1, indent=2))

    # Test 2: Improve Eating Habits + non-veg
    input2 = {"goal": "Improve Eating Habits", "budget": 2500, "preferences": "non-veg"}
    plan2 = planner.generate_meal_plan(input2)
    print("\nTest 2 - Improve Eating Habits + Non-Veg:")
    print(json.dumps(plan2, indent=2))