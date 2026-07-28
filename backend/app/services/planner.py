import copy
import json
from typing import Any, Dict, List, Optional, Set, Tuple

from .llm_service import GroqService

try:
    from .catalog_service import CatalogService
    from .recommendation_engine import (
        Constraint,
        RecommendationEngine,
        RecommendationRequest,
    )
except ImportError:
    from app.services.catalog_service import CatalogService
    from app.services.recommendation_engine import (
        Constraint,
        RecommendationEngine,
        RecommendationRequest,
    )


class MealPlanner:
    """
    MealPlanner class for generating structured 7-day meal plans using Groq LLM and RecommendationEngine.

    This class owns planning-specific logic:
    - Meal sequencing & daily scheduling (breakfast, lunch, dinner)
    - Variety scoring across days (cuisine rotation, restaurant rotation, duplicate prevention)
    - Surgical plan modification workflows (cheaper, healthier, replacement, removal)
    - Assembling the final 7-day meal plan

    All candidate retrieval, recommendation filtering, and recommendation scoring
    are delegated to RecommendationEngine.
    """

    def __init__(
        self,
        catalog_service: Optional[CatalogService] = None,
        recommendation_engine: Optional[RecommendationEngine] = None,
    ) -> None:
        """Initialize MealPlanner with GroqService, CatalogService, and RecommendationEngine."""
        self.llm_service = GroqService()
        self.catalog_service = catalog_service or CatalogService()
        self.recommendation_engine = recommendation_engine or RecommendationEngine(self.catalog_service)

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
        exclude_ids: Optional[Set[int]] = None,
    ) -> List[Dict[str, Any]]:
        """Delegate candidate retrieval and filtering to RecommendationEngine."""
        constraints: List[Constraint] = []

        if preference:
            norm_pref = self._normalize_preference(preference)
            if norm_pref:
                constraints.append(Constraint(type="preference", value=norm_pref))

        if meal_type:
            constraints.append(Constraint(type="meal_type", value=meal_type))

        if max_price is not None:
            constraints.append(Constraint(type="max_budget", value=max_price))

        if healthy_only:
            constraints.append(Constraint(type="healthy_only", value=True))

        req = RecommendationRequest(constraints=constraints, top_k=100)
        results = self.recommendation_engine.generate_recommendations(req)

        items: List[Dict[str, Any]] = []
        for res in results:
            cand = res.candidate
            if exclude_ids and cand.item_id in exclude_ids:
                continue

            items.append({
                "item_id": cand.item_id,
                "name": cand.name,
                "description": cand.description,
                "price": cand.price,
                "available": cand.available,
                "category": cand.category,
                "meal_type": cand.meal_type,
                "healthy": cand.healthy,
                "vegetarian": cand.vegetarian,
                "high_protein": cand.high_protein,
                "spicy": cand.spicy,
                "vegan": cand.vegan,
                "low_calorie": cand.low_calorie,
                "gluten_free": cand.gluten_free,
                "restaurant_id": cand.restaurant_id,
                "restaurant_name": cand.restaurant_name,
                "cuisine": cand.cuisine,
                "recommendation_score": res.score.total_score,
                "recommendation_reasons": res.reason.reasons,
            })

        return items

    def _select_varied_item(
        self,
        preference: Optional[str],
        meal_type: str,
        max_price: Optional[int],
        used_item_ids: Optional[Set[int]] = None,
        cuisine_freq: Optional[Dict[str, int]] = None,
        rest_freq: Optional[Dict[str, int]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Select item for meal_type using RecommendationEngine candidates and planner variety scoring."""
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

        def planner_score(item: Dict[str, Any]) -> Tuple[float, int, int, int]:
            penalty = 0.0
            if item.get("item_id") in used_item_ids:
                penalty += 1000.0

            cuisine = item.get("cuisine", "")
            if cuisine:
                penalty += cuisine_freq.get(cuisine, 0) * 50.0

            rest = item.get("restaurant_name", "")
            if rest:
                penalty += rest_freq.get(rest, 0) * 50.0

            price = item.get("price", 0)
            if meal_type == "breakfast" and price > 150:
                penalty += 100.0
            elif meal_type == "lunch" and price < 100:
                penalty += 50.0
            elif meal_type == "dinner" and price > 300:
                penalty += 50.0

            rec_score = item.get("recommendation_score", 0.0)
            final_penalty = penalty - (rec_score * 0.1)

            return (final_penalty, price, item.get("restaurant_id", 0), item.get("item_id", 0))

        candidates.sort(key=planner_score)
        return candidates[0]

    def _find_item_by_name(
        self,
        name: str,
        max_price: Optional[int] = None,
        preference: Optional[str] = None,
        meal_type: Optional[str] = None,
        used_item_ids: Optional[Set[int]] = None,
        cuisine_freq: Optional[Dict[str, int]] = None,
        rest_freq: Optional[Dict[str, int]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Find catalog item by fuzzy name match using RecommendationEngine candidates and planner variety scoring."""
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

        def planner_score(item: Dict[str, Any]) -> Tuple[float, int, int]:
            penalty = 0.0
            if item.get("item_id") in used_item_ids:
                penalty += 1000.0
            penalty += cuisine_freq.get(item.get("cuisine", ""), 0) * 50.0
            penalty += rest_freq.get(item.get("restaurant_name", ""), 0) * 50.0

            exact_match_bonus = -10.0 if item.get("name", "").lower() == name_lower else 0.0
            rec_score = item.get("recommendation_score", 0.0)

            return (penalty + exact_match_bonus - (rec_score * 0.1), item.get("price", 0), item.get("item_id", 0))

        matches.sort(key=planner_score)
        return matches[0]

    def _structure_meal_item(
        self,
        meal_name: str,
        max_price: Optional[int] = None,
        preference: Optional[str] = None,
        meal_type: Optional[str] = None,
        used_item_ids: Optional[Set[int]] = None,
        cuisine_freq: Optional[Dict[str, int]] = None,
        rest_freq: Optional[Dict[str, int]] = None,
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
                "high_protein": item.get("high_protein", False),
                "vegan": item.get("vegan", False),
                "spicy": item.get("spicy", False),
                "low_calorie": item.get("low_calorie", False),
                "gluten_free": item.get("gluten_free", False),
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

    def _structure_plan_items(
        self,
        plan: Dict[str, Any],
        preferences: Optional[str] = None,
        daily_budget: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Convert text meal names in plan to structured items from RecommendationEngine."""
        structured_plan = {}
        used_item_ids: Set[int] = set()
        cuisine_freq: Dict[str, int] = {}
        rest_freq: Dict[str, int] = {}

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
                if c:
                    cuisine_freq[c] = cuisine_freq.get(c, 0) + 1
                r = structured_item.get("restaurant_name")
                if r:
                    rest_freq[r] = rest_freq.get(r, 0) + 1

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
        """Generate a 7-day meal plan based on user input."""
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
        """Build the LLM prompt based on user input."""
        goal = user_input.get('goal', 'General')
        budget = user_input.get('budget', 2000)
        preferences = user_input.get('preferences', 'veg')
        constraints = user_input.get('constraints', '')

        constraints_text = f"\nSpecific Constraints to Follow: {constraints}\n" if constraints else ""

        prompt = f"""
You must return ONLY valid JSON. Do not include explanations, markdown, comments, or extra text.

Generate a 7-day meal plan for a user with the following details:

Goal: {goal}
Budget: {budget} INR per week
Preferences: {preferences}{constraints_text}

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
- Do NOT repeat the same meal or cuisine consecutively across different days.
- Breakfast should be lighter/cheaper, Lunch should be filling, Dinner should be balanced.
- Ensure huge variety in cuisines across the week (use Italian, Mexican, Continental, Street Food, etc.).
- Feel free to use complete meal Combos/Boxes for lunch/dinner when appropriate.
- Optionally include healthy beverages or protein shakes as snacks.

Return only the JSON object.
"""
        return prompt

    def validate_plan_structure(self, plan: Dict[str, Any]) -> bool:
        """Validate the structure of the generated meal plan."""
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

            for meal in ['breakfast', 'lunch', 'dinner']:
                if not isinstance(day[meal], (str, dict)):
                    return False

        return True

    def modify_existing_plan(
        self,
        existing_plan: Dict[str, Any],
        entities: Dict[str, Any],
        raw_message: str = "",
        user_preferences: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Conversational planner editing. Surgically alters specific days or meals using RecommendationEngine."""
        new_plan = copy.deepcopy(existing_plan)
        user_preferences = user_preferences or {}

        target_day = entities.get("target_day")
        target_meal = entities.get("target_meal")
        replacement = entities.get("replacement_request") or (
            entities.get("item_names", [None])[0] if entities.get("item_names") else None
        )

        preference = entities.get("preference") or user_preferences.get("preference")
        cuisine = entities.get("cuisine")

        budget = entities.get("budget_max") or user_preferences.get("budget")
        daily_budget = (int(budget) // 7) if budget else None

        days_to_modify = [target_day] if target_day and target_day in new_plan else [f"day_{i}" for i in range(1, 8)]

        if target_meal and not target_day:
            meals_to_modify = [target_meal]
        elif target_day and not target_meal:
            meals_to_modify = ["breakfast", "lunch", "dinner"]
        else:
            meals_to_modify = [target_meal] if target_meal else (["dinner"] if replacement else ["breakfast", "lunch", "dinner"])

        is_remove = "remove" in raw_message.lower() or "delete" in raw_message.lower()
        is_cheaper = "cheap" in raw_message.lower() or "less" in raw_message.lower()
        is_healthier = "health" in raw_message.lower() or "light" in raw_message.lower()

        used_item_ids: Set[int] = set()
        cuisine_freq: Dict[str, int] = {}
        for d_key, d_data in new_plan.items():
            for m_key in ["breakfast", "lunch", "dinner"]:
                item = d_data.get(m_key, {})
                if isinstance(item, dict) and item.get("item_id"):
                    used_item_ids.add(item["item_id"])
                    c = item.get("cuisine")
                    if c:
                        cuisine_freq[c] = cuisine_freq.get(c, 0) + 1

        for day in days_to_modify:
            if day not in new_plan:
                continue
            for meal in meals_to_modify:
                if meal not in new_plan[day]:
                    continue
                current_item = new_plan[day][meal]

                should_remove = False
                if is_remove:
                    if target_meal == meal or target_day == day:
                        should_remove = True
                    elif replacement and replacement.lower() in current_item.get("name", "").lower():
                        should_remove = True

                if should_remove:
                    new_plan[day][meal] = {
                        "item_id": 0,
                        "name": "Skipped",
                        "price": 0,
                        "restaurant_name": "-",
                        "cuisine": "-",
                        "healthy": False,
                        "vegetarian": True,
                    }
                    continue

                meal_max_price = daily_budget
                if is_cheaper and isinstance(current_item.get("price"), (int, float)) and current_item["price"] > 0:
                    meal_max_price = int(current_item["price"] * 0.8)

                prefix = []
                if cuisine:
                    prefix.append(cuisine.title())
                if preference:
                    prefix.append(preference.title())

                meal_name = (
                    replacement
                    if replacement
                    else f"{' '.join(prefix) if prefix else 'Healthy' if is_healthier else 'Delicious'} {meal.title()} Meal"
                )

                candidates = self._catalog_items(
                    preference=preference,
                    meal_type=meal,
                    max_price=meal_max_price,
                    healthy_only=is_healthier,
                )

                new_item = None
                if candidates:
                    def planner_score(it: Dict[str, Any]) -> float:
                        pen = 0.0
                        if it.get("item_id") in used_item_ids:
                            pen += 1000.0
                        pen += cuisine_freq.get(it.get("cuisine", ""), 0) * 50.0
                        rec_score = it.get("recommendation_score", 0.0)
                        return pen + it.get("price", 0) - (rec_score * 0.1)

                    candidates.sort(key=planner_score)

                    if replacement:
                        repl_matches = [c for c in candidates if replacement.lower() in c.get("name", "").lower()]
                        if repl_matches:
                            new_item = repl_matches[0]

                    if not new_item:
                        new_item = candidates[0]

                if new_item:
                    struct_item = {
                        "item_id": new_item.get("item_id", 0),
                        "name": new_item.get("name", meal_name),
                        "price": new_item.get("price", meal_max_price or 150),
                        "restaurant_name": new_item.get("restaurant_name", "Restaurant"),
                        "cuisine": new_item.get("cuisine", "Indian"),
                        "healthy": new_item.get("healthy", False),
                        "vegetarian": new_item.get("vegetarian", True),
                    }
                    new_plan[day][meal] = struct_item
                    used_item_ids.add(struct_item["item_id"])
                    c = struct_item.get("cuisine")
                    if c:
                        cuisine_freq[c] = cuisine_freq.get(c, 0) + 1
                else:
                    new_plan[day][meal] = self._structure_meal_item(
                        meal_name=meal_name.strip(),
                        preference=preference,
                        meal_type=meal,
                        max_price=meal_max_price,
                    )

            total_cost = sum(
                item.get("price", 0)
                for item in (new_plan[day].get(m) for m in ["breakfast", "lunch", "dinner"])
                if isinstance(item, dict) and isinstance(item.get("price", 0), (int, float))
            )
            new_plan[day]["estimated_cost"] = total_cost

        return new_plan

    def generate_fallback_plan(
        self,
        user_input: Dict[str, Any],
        daily_budget: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Generate a fallback 7-day meal plan using RecommendationEngine candidates and planner variety scoring."""
        preferences = self._normalize_preference(user_input.get("preferences", "veg"))
        budget = self._parse_budget(user_input.get("budget", 2000))
        if daily_budget is None:
            daily_budget = budget // 7 if budget else None

        plan: Dict[str, Any] = {}
        used_item_ids: Set[int] = set()
        cuisine_freq: Dict[str, int] = {}
        rest_freq: Dict[str, int] = {}

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
                if c:
                    cuisine_freq[c] = cuisine_freq.get(c, 0) + 1
                r = structured_item.get("restaurant_name")
                if r:
                    rest_freq[r] = rest_freq.get(r, 0) + 1

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