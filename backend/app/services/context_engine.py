import json
from typing import Any, Dict, List, Optional

try:
    from app.services.catalog_service import CatalogService
    from app.services.history_analyzer import analyze_history
except ImportError:
    from .catalog_service import CatalogService
    from .history_analyzer import analyze_history


class ContextEngine:
    """Context-aware recommendation engine for food ordering."""

    MOOD_KEYWORDS = {
        "comfort": ["biryani", "burger", "dosa", "noodle", "fried rice", "manchurian", "masala"],
        "healthy": ["salad", "grilled", "smoothie", "bowl", "protein", "quinoa", "avocado"],
        "late night": ["snacks", "wrap", "momos", "roll", "fries", "burger", "quick"],
    }

    MOOD_PENALTIES = {
        "comfort": ["salad", "smoothie", "protein", "quinoa", "avocado"],
        "healthy": ["fried", "biryani", "burger", "manchurian", "masala"],
        "late night": ["salad", "smoothie", "protein", "quinoa", "avocado", "heavy", "lunch", "bowl"],
    }

    def __init__(self, catalog_service: Optional[CatalogService] = None) -> None:
        self.catalog_service = catalog_service or CatalogService()

    def _normalize_str(self, value: str) -> str:
        return value.strip().lower()

    def filter_by_budget(
        self,
        items: List[Dict[str, Any]],
        min_budget: Optional[int] = None,
        max_budget: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Only include items whose price falls within the given budget range."""
        if min_budget is None and max_budget is None:
            return items
        def price_ok(item: Dict[str, Any]) -> bool:
            price = item.get("price")
            if not isinstance(price, (int, float)):
                return False
            if min_budget is not None and price < min_budget:
                return False
            if max_budget is not None and price > max_budget:
                return False
            return True
        return [item for item in items if price_ok(item)]

    def filter_by_preference(self, items: List[Dict[str, Any]], preference: Optional[str]) -> List[Dict[str, Any]]:
        """Filter items by dietary preference: veg or non-veg."""
        if not preference:
            return items

        normalized = self._normalize_str(preference)
        if normalized in {"nonveg", "non veg"}:
            normalized = "non-veg"

        if normalized not in {"veg", "non-veg"}:
            raise ValueError("preference must be 'veg' or 'non-veg'")

        return [item for item in items if self._normalize_str(item.get("category", "")) == normalized]

    def filter_by_meal_type(self, items: List[Dict[str, Any]], meal_type: Optional[str]) -> List[Dict[str, Any]]:
        """Filter items by meal type."""
        if not meal_type:
            return items

        normalized = self._normalize_str(meal_type)
        supported = {"breakfast", "lunch", "dinner", "snacks"}
        if normalized not in supported:
            raise ValueError(f"meal_type must be one of {sorted(supported)}")

        return [item for item in items if self._normalize_str(item.get("meal_type", "")) == normalized]

    def filter_by_healthy(self, items: List[Dict[str, Any]], healthy: bool) -> List[Dict[str, Any]]:
        """Filter items by healthy flag."""
        if healthy is None:
            return items
        return [item for item in items if bool(item.get("healthy")) is True]

    def prioritize_healthy(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Place healthy items higher in the recommendation list."""
        return sorted(items, key=lambda item: (0 if item.get("healthy") else 1, item.get("price", 0)))

    def apply_mood_logic(self, items: List[Dict[str, Any]], mood: Optional[str]) -> List[Dict[str, Any]]:
        """Score and prioritize items based on mood-related keywords."""
        if not mood:
            return items

        normalized_mood = self._normalize_str(mood)
        ranked: List[Dict[str, Any]] = []

        for item in items:
            score = self.score_item(item, mood=normalized_mood)
            ranked.append({**item, "_mood_score": score})

        ranked.sort(key=lambda item: item["_mood_score"], reverse=True)
        return [{k: v for k, v in item.items() if k != "_mood_score"} for item in ranked]

    def score_item(self, item: Dict[str, Any], mood: Optional[str] = None, context: Optional[Dict[str, Any]] = None) -> int:
        """Score an item for recommendation ranking."""
        score = 0
        context = context or {}

        if item.get("healthy"):
            score += 20

        category = self._normalize_str(item.get("category", ""))
        if context.get("preference") and category == self._normalize_str(context["preference"]):
            score += 15

        if context.get("meal_type") and self._normalize_str(item.get("meal_type", "")) == self._normalize_str(context["meal_type"]):
            score += 10

        if mood:
            mood_terms = []
            penalty_terms = []
            if "healthy" in mood:
                mood_terms = self.MOOD_KEYWORDS["healthy"]
                penalty_terms = self.MOOD_PENALTIES["healthy"]
            elif "late" in mood or "night" in mood:
                mood_terms = self.MOOD_KEYWORDS["late night"]
                penalty_terms = self.MOOD_PENALTIES["late night"]
            else:
                mood_terms = self.MOOD_KEYWORDS["comfort"]
                penalty_terms = self.MOOD_PENALTIES["comfort"]

            text = f"{item.get('name', '')} {item.get('category', '')} {item.get('meal_type', '')}"
            normalized_text = self._normalize_str(text)
            if any(term in normalized_text for term in mood_terms):
                score += 20
            if any(term in normalized_text for term in penalty_terms):
                score -= 15

        min_budget = context.get("min_budget")
        max_budget = context.get("max_budget")
        if max_budget is None and context.get("budget_left") is not None:
            try:
                max_budget = int(context["budget_left"])
            except (TypeError, ValueError):
                max_budget = None

        if isinstance(item.get("price"), (int, float)):
            price = item["price"]
            if max_budget is not None and price <= max_budget:
                score += 10
                score += max(0, 5 - int((price / (max_budget + 1)) * 5))
            if min_budget is not None and price >= min_budget:
                score += 5

        return score

    def generate_reason(self, item: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Create a human-readable recommendation reason."""
        min_budget = context.get("min_budget")
        max_budget = context.get("max_budget")
        if max_budget is None and context.get("budget_left") is not None:
            try:
                max_budget = int(context["budget_left"])
            except (TypeError, ValueError):
                max_budget = None

        preference = context.get("preference")
        meal_type = context.get("meal_type")
        mood = context.get("mood")
        health_goal = context.get("health_goal")

        parts = []

        if preference and self._normalize_str(item.get("category", "")) == self._normalize_str(preference):
            parts.append("matches your preference")

        if meal_type and self._normalize_str(item.get("meal_type", "")) == self._normalize_str(meal_type):
            parts.append(f"perfect for {meal_type}")

        if isinstance(item.get("price"), (int, float)):
            price = item["price"]
            if max_budget is not None and price <= max_budget:
                parts.append("affordable")
            elif min_budget is not None and price >= min_budget:
                parts.append("luxury choice")

        if health_goal and item.get("healthy"):
            parts.append("healthy choice")
        elif health_goal and not item.get("healthy"):
            parts.append("a tasty treat")

        if mood:
            normalized_mood = self._normalize_str(mood)
            if "comfort" in normalized_mood:
                parts.append("comforting")
            elif "late" in normalized_mood or "night" in normalized_mood:
                parts.append("great for cravings")
            elif "healthy" in normalized_mood:
                parts.append("nourishing")

        if not parts:
            return "A good choice for you."

        # Combine into a natural sentence
        if len(parts) == 1:
            return parts[0].capitalize() + "."
        elif len(parts) == 2:
            return f"{parts[0].capitalize()} and {parts[1]}."
        else:
            return f"{parts[0].capitalize()}, {', '.join(parts[1:-1])}, and {parts[-1]}."

    def recommend_food(self, context: Dict[str, Any], include_scores: bool = False) -> Dict[str, Any]:
        """Generate context-aware food recommendations."""
        available_items = self.catalog_service.get_available_items()

        if not available_items:
            return {"fallback_used": False, "recommendations": []}

        min_budget = context.get("min_budget")
        max_budget = context.get("max_budget")
        if max_budget is None and context.get("budget_left") is not None:
            try:
                max_budget = int(context["budget_left"])
            except (TypeError, ValueError):
                max_budget = None

        preference = context.get("preference")
        meal_type = context.get("meal_type")
        mood = context.get("mood")
        health_goal = bool(context.get("health_goal"))

        def apply_strict_filters(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
            filtered = self.filter_by_preference(items, preference)
            filtered = self.filter_by_meal_type(filtered, meal_type)
            filtered = self.filter_by_budget(filtered, min_budget, max_budget)
            if health_goal:
                filtered = self.filter_by_healthy(filtered, True)
            return filtered

        print("USER MIN BUDGET:", min_budget, "USER MAX BUDGET:", max_budget)

        recommendations = apply_strict_filters(available_items)
        print("FILTERED ITEMS (strict):", len(recommendations), [item["name"] for item in recommendations[:10]])

        fallback_used = False
        fallback_reason = ""

        if not recommendations:
            fallback_used = True
            suggestions = self.filter_by_preference(available_items, preference)
            suggestions = self.filter_by_budget(suggestions, min_budget, max_budget)
            if health_goal:
                suggestions = self.filter_by_healthy(suggestions, True)
            recommendations = suggestions
            print("FILTERED ITEMS (without meal_type):", len(recommendations), [item["name"] for item in recommendations[:10]])

        if not recommendations:
            fallback_used = True
            suggestions = self.filter_by_budget(available_items, min_budget, max_budget)
            if health_goal:
                suggestions = self.filter_by_healthy(suggestions, True)
            recommendations = suggestions
            print("FILTERED ITEMS (without preference):", len(recommendations), [item["name"] for item in recommendations[:10]])

        if not recommendations:
            fallback_used = True
            if min_budget is not None or max_budget is not None:
                if min_budget is not None and max_budget is not None:
                    fallback_reason = f"No meals found between ₹{min_budget} and ₹{max_budget}."
                elif min_budget is not None:
                    fallback_reason = f"No meals found above ₹{min_budget}."
                else:
                    fallback_reason = f"No meals found under ₹{max_budget}."
                return {
                    "fallback_used": fallback_used,
                    "recommendations": [],
                    "fallback_reason": fallback_reason,
                }
            fallback_reason = "No meals found matching your constraints. Please adjust your preferences."
            return {
                "fallback_used": fallback_used,
                "recommendations": [],
                "fallback_reason": fallback_reason,
            }

        recommendations = self.apply_mood_logic(recommendations, mood)

        if health_goal or (mood and "healthy" in self._normalize_str(mood)):
            recommendations = self.prioritize_healthy(recommendations)

        scored = [
            {
                **item,
                "score": self.score_item(item, mood=mood, context=context),
            }
            for item in recommendations
        ]

        scored.sort(key=lambda item: item["score"], reverse=True)
        scored = scored[:5]

        output = []
        for item in scored:
            rec = {
                "item_id": item["item_id"],
                "item_name": item["name"],
                "restaurant": item["restaurant_name"],
                "price": item["price"],
                "cuisine": item.get("cuisine"),
                "healthy": item.get("healthy", False),
                "reason": self.generate_reason(item, context),
            }
            if include_scores:
                rec["score"] = item["score"]
            output.append(rec)

        return {
            "fallback_used": fallback_used,
            "fallback_reason": fallback_reason if fallback_used else "",
            "recommendations": output,
        }


def _print_json(title: str, payload: Dict[str, Any]) -> None:
    print(f"\n=== {title} ===")
    print(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    engine = ContextEngine()

    test_cases = [
        {
            "mood": "comfort food",
            "max_budget": 150,
            "meal_type": "dinner",
            "preference": "veg",
            "health_goal": False,
        },
        {
            "mood": "healthy",
            "max_budget": 400,
            "meal_type": "lunch",
            "preference": "non-veg",
            "health_goal": True,
        },
        {
            "mood": "late night",
            "max_budget": 250,
            "meal_type": "snacks",
            "preference": None,
            "health_goal": False,
        },
        # New test: healthy + non-veg + lunch (should fallback)
        {
            "mood": "healthy",
            "max_budget": 500,
            "meal_type": "lunch",
            "preference": "non-veg",
            "health_goal": True,
        },
        # New test: late night snacks (should not prioritize salads)
        {
            "mood": "late night",
            "max_budget": 200,
            "meal_type": "snacks",
            "preference": "veg",
            "health_goal": False,
        },
        # New test: comfort food (prioritize burgers/noodles/dosa)
        {
            "mood": "comfort food",
            "max_budget": 300,
            "meal_type": "dinner",
            "preference": "non-veg",
            "health_goal": False,
        },
    ]

    for case in test_cases:
        _print_json(f"Context: {case['mood']}", engine.recommend_food(case))
