import json
import re
from typing import Any, Dict, Optional

try:
    from app.services.catalog_service import CatalogService
    from app.services.context_engine import ContextEngine
    from app.services.history_analyzer import analyze_history
    from app.services.llm_service import GroqService
    from app.services.order_service import OrderService
    from app.services.planner import MealPlanner
except ImportError:
    from .catalog_service import CatalogService
    from .context_engine import ContextEngine
    from .history_analyzer import analyze_history
    from .llm_service import GroqService
    from .order_service import OrderService
    from .planner import MealPlanner


class ChatOrchestrator:
    """Central conversational orchestration layer for AI commerce assistant."""

    INTENT_KEYWORDS = {
        "order_status": ["status", "track", "where is my order", "order status", "track order"],
        "place_order": ["order", "buy", "get me", "place", "want", "would like", "can you get me", "i need", "bring me", "send me", "one", "two", "three", "four", "five", "extra", "double"],
        "meal_planning": ["plan", "weekly", "meal plan", "schedule"],
        "food_recommendation": ["recommend", "suggest", "cheap", "expensive", "dinner", "lunch", "breakfast", "snacks", "comfort", "healthy"],
        "healthy_suggestions": ["healthy", "health", "diet", "nutrition"],
    }

    def __init__(self) -> None:
        self.catalog_service = CatalogService()
        self.context_engine = ContextEngine()
        self.order_service = OrderService()
        self.meal_planner = MealPlanner()
        self.llm_service = GroqService()

    def detect_intent(self, message: str) -> str:
        """Detect user intent from message using keyword matching."""
        message_lower = message.lower()

        explicit_order_triggers = [
            "place order",
            "checkout",
            "buy",
            "order",
            "get me",
            "send me",
            "bring me",
            "place",
        ]
        order_intent_words = [
            "order",
            "place",
            "buy",
            "get",
            "need",
            "want",
            "would like",
            "can you get me",
            "send me",
            "bring me",
        ]
        quantity_words = ["one", "two", "three", "four", "five", "extra", "double"]
        food_entities = [
            "burger",
            "fries",
            "dosa",
            "noodles",
            "momos",
            "pizza",
            "sandwich",
            "chicken",
            "biryani",
            "pasta",
            "rice",
            "curry",
            "bread",
            "naan",
            "tacos",
            "nachos",
            "coffee",
            "tea",
            "pastry",
        ]

        if any(trigger in message_lower for trigger in explicit_order_triggers):
            return "place_order"

        has_food_entity = any(
            re.search(rf"\b{re.escape(entity)}s?\b", message_lower)
            for entity in food_entities
        )
        has_order_intent = any(
            phrase in message_lower for phrase in order_intent_words
        )
        has_quantity = any(
            re.search(rf"\b{re.escape(quantity)}\b", message_lower)
            for quantity in quantity_words
        )

        if has_food_entity and (has_order_intent or has_quantity):
            return "place_order"

        # Standard keyword matching for non-order intents only
        for intent, keywords in self.INTENT_KEYWORDS.items():
            if intent == "place_order":
                continue
            if any(keyword in message_lower for keyword in keywords):
                return intent
        return "fallback_chat"

    def handle_message(self, message: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Main orchestration method that routes to appropriate handlers."""
        intent = self.detect_intent(message)
        if intent == "food_recommendation":
            return self.handle_food_recommendation(message, user_context)
        elif intent == "meal_planning":
            return self.handle_meal_planning(message, user_context)
        elif intent == "place_order":
            return self.handle_order_request(message, user_context)
        elif intent == "order_status":
            return self.handle_order_status(message, user_context)
        elif intent == "healthy_suggestions":
            return self.handle_healthy_suggestions(message, user_context)
        else:
            return self.fallback_response(message)

    def handle_food_recommendation(self, message: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle food recommendation requests."""
        context = self._extract_recommendation_context(message, user_context)
        result = self.context_engine.recommend_food(context)
        response = self.generate_chat_response("food_recommendation", result)
        return {
            "intent": "food_recommendation",
            "response": response,
            "recommendations": result.get("recommendations", []),
        }

    def handle_meal_planning(self, message: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle meal planning requests."""
        plan_input = self._extract_planning_context(message, user_context)
        plan = self.meal_planner.generate_meal_plan(plan_input)
        response = self.generate_chat_response("meal_planning", plan)
        return {
            "intent": "meal_planning",
            "response": response,
            "meal_plan": plan,
        }

    def handle_order_request(self, message: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle order placement requests."""
        item_ids = self._extract_order_items(message)
        if not item_ids:
            return {
                "intent": "place_order",
                "response": "I couldn't identify any available food items in your request. Please specify items from our menu.",
                "order": None,
            }

        # Check availability
        available_items = []
        unavailable_items = []
        for item_id in item_ids:
            try:
                item = self.catalog_service.get_item_by_id(item_id)
                if item.get("available"):
                    available_items.append(item)
                else:
                    unavailable_items.append(item["name"])
            except ValueError:
                unavailable_items.append(f"item {item_id}")

        if not available_items:
            unavailable_str = ", ".join(unavailable_items)
            return {
                "intent": "place_order",
                "response": f"Sorry, none of the requested items are currently available: {unavailable_str}.",
                "order": None,
            }

        # Place order with available items
        try:
            order = self.order_service.place_order([item["item_id"] for item in available_items])
            response = self.generate_chat_response("place_order", order)

            if unavailable_items:
                unavailable_str = ", ".join(unavailable_items)
                response += f" Note: {unavailable_str} are currently unavailable."

            return {
                "intent": "place_order",
                "response": response,
                "order": order,
            }
        except ValueError as exc:
            return {
                "intent": "place_order",
                "response": f"Sorry, I couldn't place your order: {str(exc)}",
                "order": None,
            }

    def handle_order_status(self, message: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle order status requests."""
        order_id = self._extract_order_id(message)
        if not order_id:
            return {
                "intent": "order_status",
                "response": "Please provide your order ID to check status.",
                "status": None,
            }
        try:
            status = self.order_service.get_order_status(order_id)
            response = self.generate_chat_response("order_status", {"order_id": order_id, "status": status})
            return {
                "intent": "order_status",
                "response": response,
                "status": status,
            }
        except ValueError:
            return {
                "intent": "order_status",
                "response": f"I couldn't find an order with ID {order_id}.",
                "status": None,
            }

    def handle_healthy_suggestions(self, message: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle healthy food suggestions."""
        context = self._extract_recommendation_context(message, user_context)
        context["health_goal"] = True
        result = self.context_engine.recommend_food(context)
        response = self.generate_chat_response("healthy_suggestions", result)
        return {
            "intent": "healthy_suggestions",
            "response": response,
            "recommendations": result.get("recommendations", []),
        }

    def generate_chat_response(self, intent: str, data: Dict[str, Any]) -> str:
        """Generate conversational human-readable response."""
        if intent == "food_recommendation":
            recs = data.get("recommendations", [])
            if not recs:
                return "I couldn't find any recommendations matching your preferences. Try adjusting your budget or preferences."
            return f"Here are some great options for you: {', '.join([rec['item_name'] for rec in recs[:3]])}."
        elif intent == "meal_planning":
            return "I've created a personalized meal plan for you based on your goals and preferences."
        elif intent == "place_order":
            order = data
            items = order.get("items", [])
            item_names = [item["name"] for item in items]
            order_id = order.get("order_id", "unknown")
            if item_names:
                items_str = ", ".join(item_names)
                return f"Your order for {items_str} has been placed successfully! Order ID: {order_id}."
            return f"Your order has been placed successfully! Order ID: {order_id}."
        elif intent == "order_status":
            status = data.get("status", "unknown")
            order_id = data.get("order_id", "unknown")
            return f"Your order {order_id} status is: {status}."
        elif intent == "healthy_suggestions":
            recs = data.get("recommendations", [])
            if not recs:
                return "I couldn't find healthy options right now. Check back later!"
            return f"Here are some healthy choices: {', '.join([rec['item_name'] for rec in recs[:3]])}."
        return "I'm here to help with your food ordering needs!"

    def fallback_response(self, message: str) -> Dict[str, Any]:
        """Handle unclear or unsupported requests."""
        return {
            "intent": "fallback_chat",
            "response": "I'm not sure how to help with that. Try asking about food recommendations, meal planning, or ordering!",
        }

    def _extract_recommendation_context(self, message: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract context for recommendations from message and user_context."""
        context = dict(user_context)
        message_lower = message.lower()

        # Extract mood
        if "comfort" in message_lower:
            context["mood"] = "comfort food"
        elif "healthy" in message_lower or "health" in message_lower:
            context["mood"] = "healthy"
        elif "late" in message_lower or "night" in message_lower:
            context["mood"] = "late night"

        # Extract meal_type
        if "dinner" in message_lower:
            context["meal_type"] = "dinner"
        elif "lunch" in message_lower:
            context["meal_type"] = "lunch"
        elif "breakfast" in message_lower:
            context["meal_type"] = "breakfast"
        elif "snacks" in message_lower:
            context["meal_type"] = "snacks"

        # Extract preference if not in user_context
        if "veg" in message_lower and not context.get("preference"):
            context["preference"] = "veg"
        elif "non-veg" in message_lower and not context.get("preference"):
            context["preference"] = "non-veg"

        # Set health_goal
        context["health_goal"] = "healthy" in message_lower or context.get("health_goal", False)

        return context

    def _extract_planning_context(self, message: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract context for meal planning."""
        goal = "General health and wellness"
        if "weight" in message.lower():
            goal = "Weight management"
        elif "muscle" in message.lower():
            goal = "Muscle building"

        budget = user_context.get("budget_left", 2000)
        preferences = user_context.get("preference", "veg")

        return {
            "goal": goal,
            "budget": budget,
            "preferences": preferences,
        }

    def _extract_order_items(self, message: str) -> list[int]:
        """Extract item IDs from order message using smart keyword extraction."""
        keywords = self.extract_order_keywords(message)
        item_ids = []
        for keyword in keywords:
            item = self.resolve_catalog_item(keyword)
            if item and item["item_id"] not in item_ids:
                item_ids.append(item["item_id"])
        return item_ids[:5]

    def extract_order_keywords(self, message: str) -> list[str]:
        """Extract food keywords from order message."""
        message_lower = message.lower().strip()

        connectors_pattern = r"\s*(?:and|with|plus|,|&)\s*"
        raw_tokens = [token.strip() for token in re.split(connectors_pattern, message_lower) if token.strip()]

        filler_words = {
            "order",
            "get",
            "buy",
            "want",
            "me",
            "some",
            "a",
            "the",
            "please",
            "would",
            "like",
            "can",
            "you",
            "send",
            "bring",
            "extra",
            "double",
            "one",
            "two",
            "three",
            "four",
            "five",
        }

        keywords = []
        for raw in raw_tokens:
            tokens = [token for token in re.split(r"\s+", raw) if token and token not in filler_words]
            normalized = " ".join(tokens).strip()
            if normalized and len(normalized) >= 2:
                keywords.append(normalized)

        return keywords[:10]

    def resolve_catalog_item(self, keyword: str) -> Optional[Dict[str, Any]]:
        """Resolve a keyword to the best matching catalog item."""
        available_items = self.catalog_service.get_available_items()
        keyword_lower = keyword.lower()

        # Normalize simple plural forms
        if keyword_lower.endswith("s"):
            keyword_lower = keyword_lower[:-1]

        # Exact name match
        for item in available_items:
            if item["name"].lower() == keyword_lower:
                return item

        # Partial name match (keyword in name)
        partial_matches = []
        for item in available_items:
            if keyword_lower in item["name"].lower():
                partial_matches.append(item)

        if partial_matches:
            # Prefer shortest name (more specific match)
            partial_matches.sort(key=lambda x: len(x["name"]))
            return partial_matches[0]

        # Token-based matching (split keyword and check overlap)
        keyword_tokens = set(keyword_lower.split())
        best_match = None
        best_score = 0

        for item in available_items:
            item_tokens = set(item["name"].lower().split())
            overlap = len(keyword_tokens & item_tokens)
            if overlap > best_score:
                best_score = overlap
                best_match = item

        if best_score > 0:
            return best_match

        return None

    def _extract_order_id(self, message: str) -> Optional[str]:
        """Extract order ID from message."""
        import re
        match = re.search(r"ORD-\d+", message.upper())
        return match.group(0) if match else None


def _print_json(title: str, payload: Dict[str, Any]) -> None:
    print(f"\n=== {title} ===")
    print(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    orchestrator = ChatOrchestrator()

    test_cases = [
    ("Order burger and fries", {"budget_left": 300}),
    ("Order dosa, noodles, and momos", {"budget_left": 400}),
    ("I want pizza and garlic bread", {"budget_left": 500}),
    ("Please order chowmein, spring rolls, and cold coffee", {"budget_left": 450}),
    ("Get me paneer tikka and butter naan", {"budget_left": 350}),
    ("Order chicken burger, fries, and coke", {"budget_left": 450}),
    ("Can you order pasta and white sauce momos", {"budget_left": 400}),
    ("I would like sandwiches, fries, and a chocolate shake", {"budget_left": 500}),
    ("Order idli, dosa and vada", {"budget_left": 300}),
    ("Get me biryani, raita, and gulab jamun", {"budget_left": 550}),
    ("Please order tacos, nachos, and pepsi", {"budget_left": 450}),
    ("I want momos, noodles, pasta, and fries", {"budget_left": 600}),
    ("Order pav bhaji and extra butter pav", {"budget_left": 300}),
    ("Can you get me sushi, ramen, and iced tea", {"budget_left": 700}),
    ("Order chocolate pastry, donuts, and coffee", {"budget_left": 350}),
    ("Get me dal makhani, jeera rice, and naan", {"budget_left": 500}),
    ("I want two burgers and one fries", {"budget_left": 400}),
    ("Order veg pizza, garlic bread, coke, and brownies", {"budget_left": 700}),
    ("Please get me samosa, kachori, and jalebi", {"budget_left": 250}),
    ("Order noodles with momos and manchurian", {"budget_left": 450}),
]

    for message, user_context in test_cases:
        result = orchestrator.handle_message(message, user_context)
        _print_json(f"Query: {message}", result)
