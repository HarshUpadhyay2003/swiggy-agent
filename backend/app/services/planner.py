from typing import Dict, Any
from .llm_service import GroqService


class MealPlanner:
    """
    MealPlanner class for generating structured 7-day meal plans using Groq LLM.

    This class handles user goals, budget constraints, and dietary preferences
    to create realistic Indian meal plans. It includes fallback logic for robustness.
    """

    def __init__(self):
        """Initialize the MealPlanner with GroqService."""
        self.llm_service = GroqService()

    def generate_meal_plan(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a 7-day meal plan based on user input.

        Args:
            user_input (dict): Contains 'goal', 'budget', 'preferences'

        Returns:
            dict: Structured meal plan with day_1 to day_7
        """
        prompt = self.build_prompt(user_input)

        try:
            plan = self.llm_service.generate_json_response(prompt)
            if self.validate_plan_structure(plan):
                return plan
            else:
                return self.generate_fallback_plan(user_input)
        except Exception as e:
            # Log error if needed, but for now just fallback
            return self.generate_fallback_plan(user_input)

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

    def generate_fallback_plan(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a static fallback meal plan if LLM fails.

        Args:
            user_input (dict): User preferences for fallback customization

        Returns:
            dict: Basic meal plan
        """
        preferences = user_input.get('preferences', 'veg')
        budget = user_input.get('budget', 2000)
        daily_budget = budget // 7

        plan = {}

        for i in range(1, 8):
            if preferences == 'veg':
                breakfast = "Poha"
                lunch = "Dal Rice"
                dinner = "Veg Wrap"
            else:
                breakfast = "Egg Paratha"
                lunch = "Chicken Biryani"
                dinner = "Fish Curry"

            plan[f"day_{i}"] = {
                "breakfast": breakfast,
                "lunch": lunch,
                "dinner": dinner,
                "estimated_cost": daily_budget
            }

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