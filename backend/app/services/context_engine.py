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

    def filter_by_budget(self, items: List[Dict[str, Any]], budget: Optional[int]) -> List[Dict[str, Any]]:
        """Only include items whose price is less than or equal to the given budget."""
        if budget is None:
            return items
        return [item for item in items if isinstance(item.get("price"), (int, float)) and item["price"] <= budget]

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

        if context.get("budget_left") is not None and isinstance(item.get("price"), (int, float)):
            budget_left = context["budget_left"]
            if item["price"] <= budget_left:
                score += 10
                score += max(0, 5 - int((item["price"] / (budget_left + 1)) * 5))

        return score

    def generate_reason(self, item: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Create a human-readable recommendation reason."""
        budget_left = context.get("budget_left")
        preference = context.get("preference")
        meal_type = context.get("meal_type")
        mood = context.get("mood")
        health_goal = context.get("health_goal")

        parts = []

        if preference and self._normalize_str(item.get("category", "")) == self._normalize_str(preference):
            parts.append("matches your preference")

        if meal_type and self._normalize_str(item.get("meal_type", "")) == self._normalize_str(meal_type):
            parts.append(f"perfect for {meal_type}")

        if budget_left is not None and isinstance(item.get("price"), (int, float)) and item["price"] <= budget_left:
            parts.append("affordable")

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

        budget_left = context.get("budget_left")
        preference = context.get("preference")
        meal_type = context.get("meal_type")
        mood = context.get("mood")
        health_goal = context.get("health_goal")

        # Initial filtering
        recommendations = available_items
        recommendations = self.filter_by_preference(recommendations, preference)
        recommendations = self.filter_by_meal_type(recommendations, meal_type)
        recommendations = self.filter_by_budget(recommendations, budget_left)

        if health_goal:
            healthy_items = [item for item in recommendations if item.get("healthy")]
            recommendations = healthy_items

        recommendations = self.apply_mood_logic(recommendations, mood)

        # Only prioritize healthy if health goal or healthy mood
        if health_goal or (mood and "healthy" in self._normalize_str(mood)):
            recommendations = self.prioritize_healthy(recommendations)

        # Fallback logic if no recommendations
        fallback_used = False
        fallback_reason = ""

        if not recommendations:
            fallback_used = True
            # Step 1: Relax meal_type
            recommendations = available_items
            recommendations = self.filter_by_preference(recommendations, preference)
            recommendations = self.filter_by_budget(recommendations, budget_left)
            if health_goal:
                recommendations = [item for item in recommendations if item.get("healthy")]
            recommendations = self.apply_mood_logic(recommendations, mood)
            if health_goal or (mood and "healthy" in self._normalize_str(mood)):
                recommendations = self.prioritize_healthy(recommendations)

            if not recommendations:
                # Step 2: Relax preference
                recommendations = available_items
                recommendations = self.filter_by_budget(recommendations, budget_left)
                if health_goal:
                    recommendations = [item for item in recommendations if item.get("healthy")]
                recommendations = self.apply_mood_logic(recommendations, mood)
                if health_goal or (mood and "healthy" in self._normalize_str(mood)):
                    recommendations = self.prioritize_healthy(recommendations)

                if not recommendations:
                    # Step 3: Closest healthy available
                    recommendations = [item for item in available_items if item.get("healthy")]
                    recommendations = self.apply_mood_logic(recommendations, mood)
                    recommendations = self.prioritize_healthy(recommendations)

            fallback_reason = "No exact matches found. Showing closest alternatives."

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
                "item_name": item["name"],
                "restaurant": item["restaurant_name"],
                "price": item["price"],
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
            "budget_left": 150,
            "meal_type": "dinner",
            "preference": "veg",
            "health_goal": False,
        },
        {
            "mood": "healthy",
            "budget_left": 400,
            "meal_type": "lunch",
            "preference": "non-veg",
            "health_goal": True,
        },
        {
            "mood": "late night",
            "budget_left": 250,
            "meal_type": "snacks",
            "preference": None,
            "health_goal": False,
        },
        # New test: healthy + non-veg + lunch (should fallback)
        {
            "mood": "healthy",
            "budget_left": 500,
            "meal_type": "lunch",
            "preference": "non-veg",
            "health_goal": True,
        },
        # New test: late night snacks (should not prioritize salads)
        {
            "mood": "late night",
            "budget_left": 200,
            "meal_type": "snacks",
            "preference": "veg",
            "health_goal": False,
        },
        # New test: comfort food (prioritize burgers/noodles/dosa)
        {
            "mood": "comfort food",
            "budget_left": 300,
            "meal_type": "dinner",
            "preference": "non-veg",
            "health_goal": False,
        },
    ]

    for case in test_cases:
        _print_json(f"Context: {case['mood']}", engine.recommend_food(case))
