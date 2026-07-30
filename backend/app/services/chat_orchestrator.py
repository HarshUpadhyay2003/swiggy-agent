import json
import re
import logging
from datetime import datetime
from typing import Any, Dict, Optional

try:
    from app.services.catalog_service import CatalogService
    from app.services.context_engine import ContextEngine
    from app.services.history_analyzer import analyze_history
    from app.services.llm_service import GroqService
    from app.services.order_service import OrderService
    from app.services.planner import MealPlanner
    from app.services.session_manager import SessionManager
    from app.services.cart_service import CartService
    from app.services.conversational_classifier import ConversationalClassifier, ConversationMemory
    from app.services.conversational_response_generator import ConversationalResponseGenerator
    from app.services.action_executor import ActionExecutor
except ImportError:
    from .catalog_service import CatalogService
    from .context_engine import ContextEngine
    from .history_analyzer import analyze_history
    from .llm_service import GroqService
    from .order_service import OrderService
    from .planner import MealPlanner
    from .session_manager import SessionManager
    from .cart_service import CartService
    from .conversational_classifier import ConversationalClassifier, ConversationMemory
    from .conversational_response_generator import ConversationalResponseGenerator
    from .action_executor import ActionExecutor

logger = logging.getLogger(__name__)


class ChatOrchestrator:
    """Central conversational orchestration layer for AI commerce assistant."""

    INTENT_KEYWORDS = {
        "order_status": ["status", "track", "where is my order", "order status", "track order"],
        "view_cart": ["show my cart", "view cart", "my cart", "show cart", "what's in my cart"],
        "remove_from_cart": ["remove", "delete", "drop", "cancel", "take out"],
        "checkout_cart": ["checkout", "place order", "complete order", "order now", "pay now", "finish order"],
        "meal_planning": ["plan", "weekly", "meal plan", "schedule"],
        "food_recommendation": [
            "recommend", "suggest", "cheap", "budget", "under", "below", "less than", "affordable", "expensive",
            "dinner", "lunch", "breakfast", "snacks", "comfort", "healthy", "meal", "meals", "food", "dish", "dishes",
            "burger", "burgers", "pizza", "pizzas", "wrap", "wraps", "rice", "bowl", "bowls", "pasta", "pastas",
            "noodles", "noodle", "fries", "fry", "chicken", "paneer", "veg", "non veg", "non-veg", "late night",
            "dessert", "desserts", "sweet", "sweets", "ice cream", "icecream", "coffee", "tea", "shake", "shakes",
            "smoothie", "smoothies", "juice", "juices", "cold drink", "drink", "drinks", "beverage", "beverages",
            "combo", "combos", "family meal", "kids meal", "best", "top", "popular", "trending", "famous"
        ],
        "healthy_suggestions": [
            "healthy", "health", "diet", "nutrition", "high protein", "protein rich", "gym meals",
            "healthy food", "diet food", "low calorie", "high fibre", "high fiber", "fitness", "light"
        ],
    }

    def __init__(self) -> None:
        self.catalog_service = CatalogService()
        self.context_engine = ContextEngine()
        self.order_service = OrderService()
        self.meal_planner = MealPlanner(self.catalog_service)
        self.llm_service = GroqService()
        self.session_manager = SessionManager()
        self.cart_service = CartService(self.catalog_service, self.order_service)
        
        # NEW: Conversational intelligence components
        self.classifier = ConversationalClassifier()
        self.response_generator = ConversationalResponseGenerator()
        self.action_executor = ActionExecutor(self.cart_service, self.catalog_service, self.meal_planner)
        
        # Per-session conversation memory for context tracking
        self.conversation_memories: Dict[str, ConversationMemory] = {}
        
        # Dataset-aware search terms from Catalog/Knowledge Base
        self._dataset_terms = self._load_dataset_terms()

    def _is_conversational_intent(self, intent: str) -> bool:
        """Check if this is a conversational intent (not requiring business logic)."""
        conversational_intents = [
            "greeting",
            "gratitude",
            "affirmation",
            "rejection",
            "clarification",
            "casual_chat",
        ]
        return intent in conversational_intents

    def _handle_conversational_intent(
        self,
        message: str,
        classification: Dict[str, Any],
        user_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Handle pure conversational intents."""
        intent = classification.get("intent")
        tone = classification.get("tone", "casual")
        
        response = self.response_generator.generate_response(
            intent, {}, tone=tone
        )
        
        return {
            "intent": intent,
            "response": response,
            "data": {},
        }

    def _handle_action_graph(
        self,
        message: str,
        classification: Dict[str, Any],
        user_context: Dict[str, Any],
        session_context: Dict[str, Any],
        session_state: Any = None,
    ) -> Dict[str, Any]:
        """Handle action graph execution for multiple operations."""
        primary_intent = classification.get("intent")
        actions = classification.get("actions", [])
        
        session_id = user_context.get("session_id")
        user_prefs = session_state.user_preferences if session_state else {}

        # Execute all actions transactionally
        exec_results = self.action_executor.execute_batch(
            session_id=session_id,
            session_state=session_state,
            actions=actions,
            message=message,
            user_preferences=user_prefs
        )

        actions_executed = exec_results.get("actions_executed", [])
        combined_data = {
            "actions_executed": actions_executed,
            "cart": exec_results.get("cart"),
            "meal_plan": exec_results.get("meal_plan"),
        }
        
        if session_state and exec_results.get("meal_plan"):
            session_state.planner_state.active_plan = exec_results["meal_plan"]
            session_state.switch_domain("planner")
        elif session_state and exec_results.get("cart"):
            session_state.active_cart = exec_results["cart"]
            session_state.switch_domain("cart")

        tone = classification.get("tone", "casual")
        # PHASE 7 & 12: Ensure action summary is robust and safely defaults
        action_summary = ", ".join(actions_executed) if actions_executed else "I encountered an issue executing those actions."

        combined_response = self.response_generator.generate_response(
            primary_intent or "multi_action",
            combined_data,
            tone=tone,
            original_response=action_summary
        )
        
        return {
            "intent": primary_intent or "multi_action",
            "actions_executed": actions_executed,
            "response": combined_response,
            "data": combined_data,
            "active_domain": session_state.active_domain if session_state else "general",
            "cart": exec_results.get("cart"),
            "meal_plan": exec_results.get("meal_plan")
        }

    def _handle_context_aware_followup(
        self,
        message: str,
        classification: Dict[str, Any],
        user_context: Dict[str, Any],
        session_context: Dict[str, Any],
        session_state: Any = None,
    ) -> Dict[str, Any]:
        """Handle follow-ups intelligently using conversation context."""
        current_intent = classification.get("intent")
        entities = classification.get("entities", {})
        last_intent = session_context.get("last_intent")
        last_entities = session_context.get("last_entities", {})
        active_domain = session_state.active_domain if session_state else "general"

        # PHASE 3: FIX FOLLOW-UP RESOLUTION & SCOPING
        
        logger.info(f"[FOLLOWUP] Evaluating followup. Last intent: {last_intent}, Current intent: {current_intent}, Domain: {active_domain}")

        # 1. Planner Scoping
        if active_domain == "planner" or last_intent == "meal_planning":
            if self._is_planner_followup(message.lower()) or current_intent == "modify_previous_request":
                logger.info("[DOMAIN] Planner followup accepted")
                classification["intent"] = "modify_meal_plan"
                return self.handle_modify_meal_plan(message, user_context, session_context, classification, session_state)
            logger.info("[DOMAIN] Planner override bypassed")
        
        # 2. Cart Continuity Override
        if active_domain == "cart" or last_intent in ["add_to_cart", "remove_from_cart"]:
            if self._is_cart_followup(message.lower()) or (current_intent == "modify_previous_request" and "remove" in message.lower()):
                logger.info("[DOMAIN] Cart followup accepted")
                classification["intent"] = "remove_from_cart"
                return self.handle_remove_from_cart(message, user_context, classification)
        
        # 3. Recommendation Scoping
        if active_domain == "recommendations" or last_intent in ["food_recommendation", "healthy_suggestions"]:
            is_rec_followup = bool(re.search(r'\b(cheaper|healthier|spicy|more|another|instead)\b', message.lower()))
            if is_rec_followup or current_intent in ["modify_previous_request", "food_recommendation"]:
                logger.info("[DOMAIN] Recommendation followup accepted")
                merged_context = dict(user_context)
                merged_context.update(last_entities)
                merged_context.update(entities)
                
                # Apply modifications
                if "budget_max" in entities and "budget_max" in last_entities:
                    if entities["budget_max"] < last_entities["budget_max"]:
                        merged_context["budget_max"] = entities["budget_max"]
                
                if "health_goal" in entities:
                    merged_context["health_goal"] = entities["health_goal"]
                
                if "preference" in entities:
                    merged_context["preference"] = entities["preference"]
                
                return self.handle_food_recommendation(message, merged_context)

        # Default fallback
        logger.info("[FOLLOWUP] No specific domain followup matched. Falling back to core intent.")
        return self._handle_core_intent(message, classification, user_context, session_context, session_state)

    def _handle_core_intent(
        self,
        message: str,
        classification: Dict[str, Any],
        user_context: Dict[str, Any],
        session_context: Optional[Dict[str, Any]] = None,
        session_state: Any = None,
    ) -> Dict[str, Any]:
        """Handle main business intents (orders, recommendations, cart, etc.)."""
        intent = classification.get("intent", "casual_chat")
        
        # Route to appropriate handler based on intent
        if intent in ["food_recommendation", "healthy_suggestions"]:
            result = self.handle_food_recommendation(message, user_context, intent=intent, session_state=session_state)
        elif intent == "meal_planning":
            result = self.handle_meal_planning(message, user_context, classification, session_state)
        elif intent == "modify_meal_plan":
            result = self.handle_modify_meal_plan(message, user_context, session_context, classification, session_state)
        elif intent == "show_meal_plan":
            result = self.handle_show_meal_plan(message, user_context, session_context, session_state)
        elif intent == "add_to_cart":
            result = self.handle_add_to_cart(message, user_context, classification)
        elif intent == "cart_action":
            result = self._handle_action_graph(message, classification, user_context, session_context, session_state)
        elif intent == "remove_from_cart":
            result = self.handle_remove_from_cart(message, user_context, classification)
        elif intent == "view_cart":
            result = self.handle_view_cart(message, user_context)
        elif intent == "checkout_cart":
            result = self.handle_checkout_cart(message, user_context)
        elif intent == "order_status":
            session_order_id = None
            if session_state and session_state.last_order:
                session_order_id = session_state.last_order.get("order_id")
            elif session_context and session_context.get("last_order"):
                session_order_id = session_context.get("last_order", {}).get("order_id")
                
            result = self.handle_order_status(message, user_context, session_order_id=session_order_id)
        elif intent == "reorder_action":
            result = self.handle_reorder_action(message, user_context, session_context, session_state)
        else:
            result = self.fallback_response(message)
        
        # Try to improve response with new generator
        if "response" in result:
            tone = classification.get("tone", "casual")
            try:
                improved_response = self.response_generator.generate_response(
                    intent,
                    result.get("data", {}),
                    tone=tone,
                    original_response=result.get("response")
                )
                if improved_response:
                    result["response"] = improved_response
            except Exception:
                # Keep original response if generation fails
                pass
        
        # ISSUE 5 FIX: Debugging executed actions and final cart state
        logger.info(f"[Orchestrator] Executed Action: {result.get('intent')} | Final Cart State: {result.get('cart')}")
        
        return result

    def detect_intent(self, message: str) -> str:
        """Detect user intent from message using keyword matching."""
        message_lower = message.lower()

        checkout_phrases = [
            "checkout",
            "place order",
            "complete order",
            "order now",
            "pay now",
            "finish order",
        ]
        remove_phrases = ["remove", "delete", "drop", "cancel", "take out"]
        view_phrases = ["show my cart", "view cart", "my cart", "show cart", "what's in my cart"]
        order_intent_words = ["can you get me", "send me", "bring me", "add", "also", "too", "more"]
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

        if any(phrase in message_lower for phrase in checkout_phrases):
            return "checkout_cart"

        if any(phrase in message_lower for phrase in remove_phrases):
            return "remove_from_cart"

        if any(phrase in message_lower for phrase in view_phrases):
            return "view_cart"

        if any(keyword in message_lower for keyword in self.INTENT_KEYWORDS["order_status"]):
            return "order_status"

        has_food_entity = any(
            re.search(rf"\b{re.escape(entity)}s?\b", message_lower)
            for entity in food_entities
        )
        has_order_intent = any(phrase in message_lower for phrase in order_intent_words)
        has_quantity = any(
            re.search(rf"\b{re.escape(quantity)}\b", message_lower)
            for quantity in quantity_words
        )

        if has_food_entity and (has_order_intent or has_quantity):
            return "add_to_cart"

        for intent, keywords in self.INTENT_KEYWORDS.items():
            if any(keyword in message_lower for keyword in keywords):
                return intent

        return "fallback_chat"

    def _load_dataset_terms(self) -> set:
        """Load entity names, categories, search aliases, combos, and cuisines from Catalog & Knowledge Base."""
        terms = set()
        try:
            kb = self.catalog_service.kb_service
            for r in kb.get_all_restaurants():
                if r.get("name"):
                    terms.add(r["name"].lower().strip())
                if r.get("restaurant_code"):
                    terms.add(r["restaurant_code"].lower().strip())
                if r.get("cuisine"):
                    terms.add(r["cuisine"].lower().strip())
            for c in kb.get_all_categories():
                if c.get("name"):
                    terms.add(c["name"].lower().strip())
                if c.get("category_id"):
                    terms.add(c["category_id"].lower().strip())
            for cb in kb.get_all_combos():
                if cb.get("name"):
                    terms.add(cb["name"].lower().strip())
            for item in kb.get_all_menu_items():
                if item.get("name"):
                    terms.add(item["name"].lower().strip())
                for alias in item.get("search_aliases", []):
                    if alias:
                        terms.add(str(alias).lower().strip())
                if item.get("cuisine"):
                    terms.add(item["cuisine"].lower().strip())
                if item.get("category"):
                    terms.add(item["category"].lower().strip())
        except Exception as e:
            logger.warning(f"Error loading dataset terms for routing: {e}")
        return terms

    def _is_dataset_food_query(self, message: str) -> bool:
        """Check if user message matches any entity, category, combo, or alias in backend dataset."""
        msg_clean = message.lower().strip()
        words = set(re.findall(r'\b\w+\b', msg_clean))

        for term in self._dataset_terms:
            if not term or len(term) <= 2:
                continue
            if " " in term:
                if term in msg_clean:
                    return True
            else:
                if term in words:
                    return True
        return False

    def _is_checkout_action(self, message: str) -> bool:
        return bool(re.search(r'\b(checkout|place order|pay now|finish order|buy now)\b', message.lower()))

    def _is_reorder_action(self, message: str) -> bool:
        return bool(re.search(r'\b(repeat last order|same as before|order previous|reorder|same as last time|add my usual|previous order|last order|repeat my last order|add previous items again|what did i order before|add previous cart again)\b', message.lower()))

    def _is_healthy_request(self, message: str) -> bool:
        return bool(re.search(r'\b(healthy|protein|high protein|protein rich|gym meals|healthy food|diet food|low calorie|high fibre|high fiber|fitness|diet|light)\b', message.lower()))

    def _is_recommendation_request(self, message: str) -> bool:
        msg_lower = message.lower()
        if re.search(r'\b(suggest|recommend|recommendation|suggestions|options|ideas)\b', msg_lower):
            return True

        cuisine_pattern = r'\b(indian|chinese|italian|american|mexican|asian|mediterranean|continental|parsi|greek|fast food|cafe)\b'
        if re.search(cuisine_pattern, msg_lower):
            return True

        taste_pattern = r'\b(spicy|sweet|tangy|smoky|cheesy|crunchy|creamy|salty|savory)\b'
        if re.search(taste_pattern, msg_lower):
            return True

        food_pattern = r'\b(meals?|food|dish|dishes|burgers?|pizzas?|wraps?|rice|bowls?|pastas?|noodles?|fries|fry|chicken|paneer|veg|non-?veg|breakfast|lunch|dinner|snacks?|late night|desserts?|sweets?|ice cream|icecream|coffee|tea|shakes?|smoothies?|juices?|cold drink|drinks?|beverages?|combos?|family meal|kids meal)\b'
        if re.search(food_pattern, msg_lower):
            return True

        budget_pattern = r'\b(cheap|budget|under|below|less than|affordable)\b'
        if re.search(budget_pattern, msg_lower):
            return True

        health_pattern = r'\b(healthy|protein|high protein|protein rich|gym meals|healthy food|diet food|low calorie|high fibre|high fiber|fitness|diet|light)\b'
        if re.search(health_pattern, msg_lower):
            return True

        pop_pattern = r'\b(best|top|popular|trending|famous)\b'
        if re.search(pop_pattern, msg_lower):
            return True

        if self._is_dataset_food_query(message):
            return True

        return False

    def _is_explicit_meal_plan_request(self, message: str) -> bool:
        return bool(re.search(r'\b(meal plan|weekly plan|diet plan|7 day plan|full plan)\b', message.lower()))

    def _is_planner_followup(self, message: str) -> bool:
        return bool(re.search(r'\b(replace|change|swap|instead|remove|day|make it)\b', message.lower()))

    def _is_cart_followup(self, message: str) -> bool:
        return bool(re.search(r'\b(remove|delete|change|update|quantity)\b', message.lower()))

    def handle_message(self, message: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Main orchestration method that routes to appropriate handlers."""
        session_id = user_context.get("session_id")
        
        session_state = self.session_manager.create_session(session_id) if session_id else None

        # Initialize or get session conversation memory
        if session_id and session_id not in self.conversation_memories:
            self.conversation_memories[session_id] = ConversationMemory()
        
        conversation_memory = self.conversation_memories.get(session_id)
        session_context = conversation_memory.get_session_context() if conversation_memory else {}
        
        # Sync active domain state down into the AI classifier context
        if session_state:
            session_context["active_domain"] = session_state.active_domain
            session_context["planner_state"] = session_state.planner_state.model_dump() if session_state.planner_state else {}
            print(f"[DEBUG] Active Domain: {session_state.active_domain} | Message: {message}")

        # NEW: Use conversational classifier for intelligent understanding
        classification = self.classifier.classify_user_message(message, session_context)
        llm_intent = classification.get("intent", "casual_chat")
        
        logger.info(f"[Orchestrator] Initial LLM Classification: {llm_intent} | Entities: {classification.get('entities')}")

        msg_lower = message.lower()

        # Check for Reset Preferences command
        if bool(re.search(r'\b(reset preferences|clear preferences|reset recommendation|start over recommendation|reset my preferences)\b', msg_lower)):
            if session_state and hasattr(session_state, "recommendation_memory"):
                session_state.recommendation_memory.clear()
            print("\n========================================")
            print("[RECOMMENDATION ENGINE]")
            print("Recommendation memory cleared.")
            print("========================================\n")
            return {
                "intent": "food_recommendation",
                "response": "I've reset your recommendation preferences! What would you like to order or explore now?",
                "recommendations": [],
                "data": {"recommendations": []}
            }
        
        # PHASE 1 & 6: STRICT DETERMINISTIC ROUTING (Regex word boundaries to prevent overlap)
        is_checkout = self._is_checkout_action(msg_lower)
        is_reorder = self._is_reorder_action(msg_lower)
        is_add = bool(re.search(r'\b(add|put|include|get me|bring me)\b', msg_lower))
        is_remove = bool(re.search(r'\b(remove|delete|discard|take out)\b', msg_lower))
        is_replace = bool(re.search(r'\b(replace|swap)\b', msg_lower))
        is_view_cart = bool(re.search(r'\b(show cart|view cart|my cart|what\'s in my cart)\b', msg_lower))
        is_order_status = bool(re.search(r'\b(track|status|where is my order|track order)\b', msg_lower))
        
        # STRICT Planner definition
        is_planner = self._is_explicit_meal_plan_request(msg_lower)
        
        # STRICT Healthy suggestions definition
        is_healthy = self._is_healthy_request(msg_lower)

        # STRICT Recommendation definition
        is_recommendation = self._is_recommendation_request(msg_lower)

        # STRICT Planner modification definition (requires explicit day or planner target to distinguish from standalone cart ops)
        is_planner_mod = (session_state and session_state.active_domain == "planner" and self._is_planner_followup(msg_lower) and bool(re.search(r'\b(day \d|day_\d|breakfast|lunch|dinner|meal plan|planner)\b', msg_lower))) or bool(re.search(r'\b(day \d|day_\d)\b', msg_lower))

        deterministic_intent = None
        reason = ""
        actions = []

        # Priority 1: Checkout
        if is_checkout:
            deterministic_intent = "checkout_cart"
            reason = "Matched checkout action keyword"
        # Priority 1.5: Reorder
        elif is_reorder:
            deterministic_intent = "reorder_action"
            reason = "Matched reorder action keyword"
        # Priority 1.8: Meal Planner Modification (must take precedence over cart swap if in planner domain or mentioning day N)
        elif is_planner_mod:
            deterministic_intent = "modify_meal_plan"
            reason = "Matched meal planner modification keyword"
        # Priority 2: Cart Actions (Batch/Multi)
        elif is_replace or (is_add and is_remove):
            deterministic_intent = "cart_action"
            actions = [{"type": "cart_remove"}, {"type": "cart_add"}]
            reason = "Matched multi-cart replace/swap action"
        elif is_remove:
            deterministic_intent = "remove_from_cart"
            reason = "Matched remove from cart keyword"
        elif is_add:
            deterministic_intent = "add_to_cart"
            reason = "Matched add to cart keyword"
        # Priority 3: View Cart
        elif is_view_cart:
            deterministic_intent = "view_cart"
            reason = "Matched view cart keyword"
        # Priority 3.5: Order Status
        elif is_order_status:
            deterministic_intent = "order_status"
            reason = "Matched order status keyword"
        # Priority 4: Explicit Meal Planning
        elif is_planner:
            deterministic_intent = "meal_planning"
            reason = "Matched explicit meal planning keyword"
        # Priority 4.5: Healthy Suggestions
        elif is_healthy and llm_intent != "add_to_cart":
            deterministic_intent = "healthy_suggestions"
            reason = "Matched healthy suggestion keyword"
        # Priority 5: Recommendation / Concise Food Query / Dataset Match
        elif is_recommendation and llm_intent != "add_to_cart":
            deterministic_intent = "food_recommendation"
            reason = "Matched recommendation keyword or dataset food query"
            
        if deterministic_intent:
            classification["intent"] = deterministic_intent
            classification["is_followup"] = False  # CRITICAL: Prevent active_domain hijacking
            if actions:
                classification["actions"] = actions
            else:
                classification["actions"] = []
            final_intent = deterministic_intent
        else:
            final_intent = llm_intent
            reason = "Accepted LLM classification"

        # TASK 6 LOGGING: Improved structured request log
        print("\n" + "=" * 40)
        print("[ROUTER]")
        print(f"Message:\n\"{message}\"\n")
        print(f"LLM:\n{llm_intent}\n")
        print(f"Deterministic:\n{deterministic_intent or 'None'}\n")
        print(f"Final:\n{final_intent}\n")
        print(f"Reason:\n{reason}")
        print("=" * 40 + "\n")

        logger.info(f"[ROUTER] Message: '{message}' | LLM: {llm_intent} | Deterministic: {deterministic_intent} | Final: {final_intent} | Reason: {reason}")

        intent = classification.get("intent", "casual_chat")
        
        # PHASE 2 & 8: FIX ACTIVE DOMAIN HIJACKING & DOMAIN STICKINESS
        if session_state:
            active_domain = session_state.active_domain
            logger.info(f"[DOMAIN] Current Active Domain: {active_domain}")
            
            if active_domain == "planner":
                # Only keep planner if explicitly modifying
                planner_followup = bool(re.search(r'\b(replace|change|swap|instead|remove|day|make it)\b', msg_lower))
                if not planner_followup and intent not in ["meal_planning", "modify_meal_plan", "show_meal_plan", "casual_chat"]:
                    logger.info("[DOMAIN] Resetting Planner -> General due to unrelated intent")
                    session_state.switch_domain("general")
            
            elif active_domain == "recommendations":
                rec_followup = bool(re.search(r'\b(cheaper|healthier|spicy|more|another|instead)\b', msg_lower))
                if not rec_followup and intent not in ["food_recommendation", "add_to_cart"]:
                    logger.info("[DOMAIN] Resetting Recommendations -> General")
                    session_state.switch_domain("general")

        logger.info(f"[ROUTER] Final Routed Intent: {intent}")

        intent = classification.get("intent")

        # Route to appropriate handler
        if intent in ["meal_planning", "modify_meal_plan", "show_meal_plan"]:
            # Always prioritize planner core execution
            result = self._handle_core_intent(message, classification, user_context, session_context, session_state)
        elif self._is_conversational_intent(intent):
            result = self._handle_conversational_intent(
                message, classification, user_context
            )
        # Handle multi-action intents safely (actions array > 0 AND intent is cart-related)
        elif classification.get("actions") and intent in ["cart_action", "add_to_cart", "remove_from_cart", "multi_action"]:
            result = self._handle_action_graph(
                message, classification, user_context, session_context, session_state
            )
        # Handle follow-ups with context awareness
        elif classification.get("is_followup") and session_context:
            result = self._handle_context_aware_followup(
                message, classification, user_context, session_context, session_state
            )
        # Handle core intents (orders, recommendations, etc.)
        else:
            result = self._handle_core_intent(message, classification, user_context, session_context, session_state)
        
        # Update conversation memory with this interaction
        if conversation_memory:
            response_text = result.get("response", "")
            conversation_memory.add_interaction(
                message, classification, response_text, result.get("data", {})
            )

        # OLD: Session tracking (kept for backward compatibility)
        if session_id:
            self.session_manager.add_interaction(
                session_id,
                message,
                result.get("response", ""),
                result.get("intent", "fallback_chat"),
                result,
            )
            # Post-execution logs
            print(f"[DEBUG] Post-Execution Domain: {self.session_manager.get_session_context(session_id).active_domain}")

        return self.format_response(result)

    def handle_food_recommendation(self, message: str, user_context: Dict[str, Any], intent: str = "food_recommendation", session_state: Any = None) -> Dict[str, Any]:
        """Handle food recommendation requests with Progressive Recommendation Memory V2."""
        context = self._extract_recommendation_context(message, user_context, session_state)
        result = self.context_engine.recommend_food(context)

        if session_state and hasattr(session_state, "switch_domain"):
            session_state.switch_domain("recommendations")
            session_state.last_recommendations = result.get("recommendations", [])

        if not result.get("recommendations"):
            if context.get("min_budget") is not None or context.get("max_budget") is not None:
                response = self._build_price_range_response(context)
            else:
                response = "I couldn't find any recommendations matching your exact preferences. Try adjusting your budget, cuisine, or category."
        else:
            response = self._generate_recommendation_response(result, context)
        return {
            "intent": intent,
            "response": response,
            "recommendations": result.get("recommendations", []),
            "data": {"recommendations": result.get("recommendations", [])},
        }

    def handle_meal_planning(self, message: str, user_context: Dict[str, Any], classification: Optional[Dict[str, Any]] = None, session_state: Any = None) -> Dict[str, Any]:
        """Handle meal planning requests."""
        plan_input = self._extract_planning_context(message, user_context, classification)
        
        # Merge with persistent session preferences
        if session_state:
            if not plan_input.get("budget") and session_state.user_preferences.get("budget"):
                plan_input["budget"] = session_state.user_preferences["budget"]
            if not plan_input.get("preferences") and session_state.user_preferences.get("preference"):
                plan_input["preferences"] = session_state.user_preferences["preference"]
                
        # Incomplete Constraint detection (Stop asking unnecessary questions unless really generic)
        has_budget = bool(classification and classification.get("entities", {}).get("budget_max"))
        has_pref = bool(classification and classification.get("entities", {}).get("preference"))
        message_words = len(message.split())
        
        if not has_budget and not has_pref and message_words < 4:
            return {
                "intent": "meal_planning",
                "response": "I'd love to plan your weekly meals! What cuisine or budget would you prefer?",
                "meal_plan": None,
                "data": {}
            }

        # Persist extracted constraints
        if session_state and classification and "entities" in classification:
            entities = classification["entities"]
            if entities.get("budget_max"):
                session_state.user_preferences["budget"] = entities["budget_max"]
            if entities.get("preference"):
                session_state.user_preferences["preference"] = entities["preference"]

        print(f"[DEBUG] Generating planner | Detected Constraints: {plan_input}")
        
        plan = self.meal_planner.generate_meal_plan(plan_input)
        response = self.generate_chat_response("meal_planning", plan)
        
        if session_state:
            session_state.planner_state.active_plan = plan
            session_state.last_meal_plan = plan
            session_state.switch_domain("planner")
            print(f"[DEBUG] Planner Persistence Status: Saved to SessionState")
            
        return {
            "intent": "meal_planning",
            "response": response,
            "meal_plan": plan,
            "data": {"meal_plan": plan},
        }

    def handle_modify_meal_plan(self, message: str, user_context: Dict[str, Any], session_context: Optional[Dict[str, Any]], classification: Dict[str, Any], session_state: Any = None) -> Dict[str, Any]:
        """Handle surgical conversational modifications to the active meal plan."""
        existing_plan = session_state.planner_state.active_plan if (session_state and session_state.planner_state.active_plan) else (session_context.get("last_meal_plan") if session_context else None)
        
        if not existing_plan:
            # Treat as a new plan if no prior plan exists
            return self.handle_meal_planning(message, user_context, classification, session_state)
            
        entities = classification.get("entities", {})
        print(f"[DEBUG] Modifying planner | Extracted Entities: {entities}")
        
        user_preferences = session_state.user_preferences if session_state else {}
        modified_plan = self.meal_planner.modify_existing_plan(existing_plan, entities, message, user_preferences)
        response = self.response_generator.generate_response("modify_meal_plan", {"meal_plan": modified_plan}, tone=classification.get("tone", "casual"))
        
        if session_state:
            session_state.planner_state.active_plan = modified_plan
            session_state.last_meal_plan = modified_plan
            session_state.switch_domain("planner")
            
        return {
            "intent": "meal_planning",
            "response": response,
            "meal_plan": modified_plan,
            "data": {"meal_plan": modified_plan},
        }

    def handle_show_meal_plan(self, message: str, user_context: Dict[str, Any], session_context: Optional[Dict[str, Any]], session_state: Any = None) -> Dict[str, Any]:
        """Handle viewing the existing meal plan."""
        existing_plan = session_state.planner_state.active_plan if (session_state and session_state.planner_state.active_plan) else (session_context.get("last_meal_plan") if session_context else None)
        if not existing_plan:
            return {
                "intent": "show_meal_plan",
                "response": "You don't have an active meal plan yet. Shall I create a weekly meal plan for you?",
                "meal_plan": None,
                "data": {}
            }
        
        if session_state:
            session_state.switch_domain("planner")
            
        response = self.response_generator.generate_response("show_meal_plan", {"meal_plan": existing_plan}, tone="casual")
        return {
            "intent": "show_meal_plan",
            "response": response,
            "meal_plan": existing_plan,
            "data": {"meal_plan": existing_plan}
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

    def handle_order_status(self, message: str, user_context: Dict[str, Any], session_order_id: Optional[str] = None) -> Dict[str, Any]:
        """Handle order status requests."""
        order_id = self._extract_order_id(message) or session_order_id
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
                "order": {"order_id": order_id, "status": status}
            }
        except ValueError:
            return {
                "intent": "order_status",
                "response": f"I couldn't find an order with ID {order_id}.",
                "status": None,
            }

    def handle_reorder_action(self, message: str, user_context: Dict[str, Any], session_context: Dict[str, Any], session_state: Any = None) -> Dict[str, Any]:
        """Handle conversational reorder requests by restoring previous order to cart."""
        session_id = user_context.get("session_id")
        last_order = session_state.last_order if session_state else session_context.get("last_order")

        if not last_order or not last_order.get("items"):
            response = "I couldn't find a previous order yet. Try adding a few items to your cart first."
            return {
                "intent": "reorder_action",
                "response": response,
                "cart": self.cart_service.get_cart(session_id) if session_id else None,
                "data": {}
            }

        # Add items back to cart
        added_names = []
        for item in last_order["items"]:
            try:
                catalog_item = self.catalog_service.get_item_by_id(item["item_id"])
                if catalog_item and catalog_item.get("available"):
                    qty = item.get("quantity", 1)
                    self.cart_service.add_to_cart(session_id, catalog_item, qty)
                    added_names.append(catalog_item["name"])
            except ValueError:
                pass

        if not added_names:
            return {
                "intent": "reorder_action",
                "response": "Your previous order items are no longer available.",
                "cart": self.cart_service.get_cart(session_id) if session_id else None,
                "data": {}
            }

        items_bulleted = "\n".join([f"• {name}" for name in added_names])
        response = f"I've added your previous order items back into the cart:\n{items_bulleted}"
        cart = self.cart_service.get_cart(session_id)
        
        return {
            "intent": "reorder_action",
            "response": response,
            "cart": cart,
            "active_cart": cart,
            "data": {"cart": cart, "reordered_items": added_names}
        }

    def handle_add_to_cart(self, message: str, user_context: Dict[str, Any], classification: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Handle adding items into the user's cart."""
        session_id = user_context.get("session_id")
        if not session_id:
            return {
                "intent": "add_to_cart",
                "response": "Please provide a session_id to keep your cart persistent.",
                "cart": None,
            }

        item_ids = self._extract_order_items(message, classification)
        if not item_ids:
            return {
                "intent": "add_to_cart",
                "response": "I couldn't identify any menu items to add. Please tell me what you'd like in your cart.",
                "cart": self.cart_service.get_cart(session_id),
                "active_cart": self.cart_service.get_cart(session_id),
                "last_cart_action": "add",
            }

        added_names = []
        for item_id in item_ids:
            item = self.catalog_service.get_item_by_id(item_id)
            if not item.get("available"):
                continue
            self.cart_service.add_to_cart(session_id, item)
            added_names.append(item["name"])

        if not added_names:
            return {
                "intent": "add_to_cart",
                "response": "None of those items are available right now. Try adding something else.",
                "cart": self.cart_service.get_cart(session_id),
                "active_cart": self.cart_service.get_cart(session_id),
                "last_cart_action": "add",
            }

        cart = self.cart_service.get_cart(session_id)
        response = f"Added {', '.join(added_names)} to your cart."
        return {
            "intent": "add_to_cart",
            "response": response,
            "cart": cart,
            "active_cart": cart,
            "last_cart_action": "add",
        }

    def handle_remove_from_cart(self, message: str, user_context: Dict[str, Any], classification: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Handle cart item removal."""
        session_id = user_context.get("session_id")
        if not session_id:
            return {
                "intent": "remove_from_cart",
                "response": "Please provide a session_id to manage your cart.",
                "cart": None,
            }

        item_ids = self._extract_order_items(message, classification)
        if not item_ids:
            return {
                "intent": "remove_from_cart",
                "response": "Please tell me which cart item to remove.",
                "cart": self.cart_service.get_cart(session_id),
                "active_cart": self.cart_service.get_cart(session_id),
                "last_cart_action": "remove",
            }

        removed_names = []
        for item_id in item_ids:
            try:
                self.cart_service.remove_from_cart(session_id, item_id)
                item = self.catalog_service.get_item_by_id(item_id)
                removed_names.append(item["name"])
            except ValueError:
                continue

        cart = self.cart_service.get_cart(session_id)
        if not removed_names:
            return {
                "intent": "remove_from_cart",
                "response": "I couldn't find those items in your cart.",
                "cart": cart,
                "active_cart": cart,
                "last_cart_action": "remove",
            }

        response = f"Removed {', '.join(removed_names)} from your cart."
        return {
            "intent": "remove_from_cart",
            "response": response,
            "cart": cart,
            "active_cart": cart,
            "last_cart_action": "remove",
        }

    def handle_view_cart(self, message: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle cart viewing requests."""
        session_id = user_context.get("session_id")
        if not session_id:
            return {
                "intent": "view_cart",
                "response": "Please provide a session_id to view your cart.",
                "cart": None,
            }

        cart = self.cart_service.get_cart(session_id)
        if not cart["items"]:
            return {
                "intent": "view_cart",
                "response": "Your cart is currently empty.",
                "cart": cart,
                "active_cart": cart,
                "last_cart_action": "view",
            }

        item_names = [f"{entry['quantity']}× {entry['name']}" for entry in cart["items"]]
        response = f"Your cart contains {', '.join(item_names)}. Total is ₹{cart['total']}."
        return {
            "intent": "view_cart",
            "response": response,
            "cart": cart,
            "active_cart": cart,
            "last_cart_action": "view",
        }

    def handle_checkout_cart(self, message: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle checkout requests by converting cart into an order."""
        session_id = user_context.get("session_id")
        if not session_id:
            return {
                "intent": "checkout_cart",
                "response": "Please provide a session_id to checkout your cart.",
                "order": None,
            }

        cart = self.cart_service.get_cart(session_id)
        if not cart["items"]:
            return {
                "intent": "checkout_cart",
                "response": "Your cart is empty. Add an item before checking out.",
                "cart": cart,
                "active_cart": cart,
                "last_cart_action": "checkout",
            }

        item_ids = self.cart_service.get_cart_item_ids(session_id)
        try:
            order = self.order_service.place_order(item_ids)
            self.cart_service.clear_cart(session_id)
            response = f"Your order {order['order_id']} has been placed successfully."
            return {
                "intent": "checkout_cart",
                "response": response,
                "order": order,
                "cart": self.cart_service.get_cart(session_id),
                "active_cart": self.cart_service.get_cart(session_id),
                "last_cart_action": "checkout",
            }
        except ValueError as exc:
            return {
                "intent": "checkout_cart",
                "response": f"I couldn't checkout your cart: {str(exc)}",
                "order": None,
                "cart": cart,
                "active_cart": cart,
                "last_cart_action": "checkout",
            }

    def handle_healthy_suggestions(self, message: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle healthy food suggestions."""
        context = self._extract_recommendation_context(message, user_context)
        context["health_goal"] = True
        result = self.context_engine.recommend_food(context)
        if not result.get("recommendations"):
            if context.get("min_budget") is not None or context.get("max_budget") is not None:
                response = self._build_price_range_response(context)
            else:
                response = "I couldn't find healthy options right now. Check back later!"
        else:
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

    def format_response(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Standardize orchestrator responses for frontend consumption."""
        data: Dict[str, Any] = {}
        if "cart" in result and result["cart"] is not None:
            data["cart"] = result["cart"]
        if "order" in result and result["order"] is not None:
            data["order"] = result["order"]
        if "recommendations" in result and result["recommendations"]:
            data["recommendations"] = result["recommendations"]
        if "meal_plan" in result and result["meal_plan"]:
            data["meal_plan"] = result["meal_plan"]
        if "status" in result and result["status"]:
            data["status"] = result["status"]
        if "actions_executed" in result:
            data["actions_executed"] = result["actions_executed"]

        logger.info(f"[PAYLOAD] Returning {result.get('intent')} response to frontend.")

        return {
            "status": "success",
            "intent": result.get("intent", "unknown"),
            "response": result.get("response", ""),
            "data": data,
            "active_domain": result.get("active_domain", "general"),
            "timestamp": self._current_timestamp(),
        }

    def _current_timestamp(self) -> str:
        from datetime import datetime

        return datetime.utcnow().isoformat() + "Z"

    def fallback_response(self, message: str) -> Dict[str, Any]:
        """Handle unclear or unsupported requests."""
        return {
            "intent": "fallback_chat",
            "response": "I'm not sure how to help with that. Try asking about food recommendations, meal planning, or ordering!",
        }

    def _build_price_range_response(self, context: Dict[str, Any]) -> str:
        min_budget = context.get("min_budget")
        max_budget = context.get("max_budget")
        if min_budget is not None and max_budget is not None:
            return f"No meals found between ₹{min_budget} and ₹{max_budget}."
        if min_budget is not None:
            return f"No meals found above ₹{min_budget}."
        return f"No meals found under ₹{max_budget}."

    def is_followup_message(self, message: str) -> bool:
        """Detect follow-up requests that rely on prior session context."""
        lowered = message.lower()
        followup_signals = [
            r"\b(add|also|too|again|same|more|still)\b",
            r"\b(cheaper|healthier|lighter|spicier|less spicy|more spicy|better)\b",
            r"\b(track|status|that order|that)\b",
            r"\b(checkout|cart|show cart|view cart|remove)\b",
        ]
        return any(re.search(pattern, lowered) for pattern in followup_signals)

    def handle_followup(
        self,
        message: str,
        user_context: Dict[str, Any],
        session_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Route a follow-up message using previous session state."""
        lowered = message.lower()
        last_order = session_context.get("last_order")

        intent = self.detect_intent(message)
        if intent == "add_to_cart":
            return self.handle_add_to_cart(message, user_context, None)
        if intent == "remove_from_cart":
            return self.handle_remove_from_cart(message, user_context, None)
        if intent == "view_cart":
            return self.handle_view_cart(message, user_context)
        if intent == "checkout_cart":
            return self.handle_checkout_cart(message, user_context)
        if intent == "order_status":
            if last_order and last_order.get("order_id"):
                return self.handle_order_status(message, user_context, session_order_id=last_order["order_id"])
            return {
                "intent": "order_status",
                "response": "I couldn't find your last order to track. Please provide an order ID.",
                "status": None,
            }

        last_intent = session_context.get("last_intent")
        if last_intent in ("food_recommendation", "healthy_suggestions"):
            if "cheaper" in lowered or "healthier" in lowered or "lighter" in lowered:
                enhanced_context = dict(user_context)
                enhanced_context["health_goal"] = "healthier" in lowered or "lighter" in lowered
                return self.handle_food_recommendation(message, enhanced_context)
            return self.handle_food_recommendation(message, user_context)
        if last_intent == "meal_planning":
            if "healthier" in lowered or "lighter" in lowered:
                enhanced_context = dict(user_context)
                enhanced_context["health_goal"] = True
                return self.handle_meal_planning(message, enhanced_context)
            return self.handle_meal_planning(message, user_context)

        return self.fallback_response(message)

    def handle_place_order_followup(
        self,
        message: str,
        user_context: Dict[str, Any],
        session_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Handle follow-up order updates using the last order as context."""
        additional_item_ids = self._extract_order_items(message)
        last_order = session_context.get("last_order")
        if not last_order:
            return self.handle_order_request(message, user_context)

        if re.search(r"\b(same order|repeat order|again|same)\b", message.lower()):
            previous_item_ids = [item.get("item_id") for item in last_order.get("items", []) if item.get("item_id")]
            if previous_item_ids:
                try:
                    order = self.order_service.place_order(previous_item_ids)
                    response = self.generate_chat_response("place_order", order)
                    return {"intent": "place_order", "response": response, "order": order}
                except ValueError as exc:
                    return {"intent": "place_order", "response": f"I couldn't repeat the order: {str(exc)}", "order": None}

        if additional_item_ids:
            previous_item_ids = [item.get("item_id") for item in last_order.get("items", []) if item.get("item_id")]
            combined_item_ids = list(dict.fromkeys(previous_item_ids + additional_item_ids))[:5]
            try:
                order = self.order_service.place_order(combined_item_ids)
                response = self.generate_chat_response("place_order", order)
                return {"intent": "place_order", "response": response, "order": order}
            except ValueError as exc:
                return {"intent": "place_order", "response": f"I couldn't update your order: {str(exc)}", "order": None}

        return {
            "intent": "place_order",
            "response": "I couldn't find any new items to add to your previous order. Please tell me what you'd like to add.",
            "order": last_order,
        }

    def _get_adaptive_default_meal_type(self) -> str:
        """Infer meal type from system current local time."""
        current_hour = datetime.now().hour
        if 6 <= current_hour < 11:
            return "breakfast"
        elif 11 <= current_hour < 16:
            return "lunch"
        elif 16 <= current_hour < 19:
            return "snacks"
        elif 19 <= current_hour < 23:
            return "dinner"
        else:
            return "late night"

    def _extract_recommendation_context(
        self, message: str, user_context: Dict[str, Any], session_state: Any = None
    ) -> Dict[str, Any]:
        """Progressive constraint extraction and memory refinement for Recommendation Intelligence V2."""
        message_lower = message.lower()
        context = dict(user_context)

        session_id = user_context.get("session_id")
        if not session_state and session_id:
            session_state = self.session_manager.get_session_context(session_id)

        rec_mem = session_state.recommendation_memory if session_state and hasattr(session_state, "recommendation_memory") else None
        prev_memory_dict = rec_mem.to_dict() if rec_mem else {}

        # 1. Cuisine Extraction & Replacement
        cuisines_map = {
            "indian": "Indian",
            "chinese": "Chinese",
            "italian": "Italian",
            "american": "American",
            "mexican": "Mexican",
            "asian": "Asian",
            "mediterranean": "Mediterranean",
            "continental": "Continental",
            "parsi": "Parsi",
            "greek": "Greek",
            "fast food": "Fast Food",
            "cafe": "Cafe",
        }
        for k, v in cuisines_map.items():
            if k in message_lower:
                if rec_mem:
                    rec_mem.cuisine_type = v
                context["cuisine_type"] = v
                break

        # 2. Taste Preference Extraction & Replacement
        tastes = ["spicy", "sweet", "tangy", "smoky", "cheesy", "crunchy", "creamy", "salty", "savory"]
        for t in tastes:
            if t in message_lower:
                if rec_mem:
                    rec_mem.taste_preference = t
                context["taste_preference"] = t
                break

        # 3. Diet Extraction & Replacement
        if "non-veg" in message_lower or "non veg" in message_lower or "nonveg" in message_lower:
            if rec_mem:
                rec_mem.diet = "non-veg"
            context["diet"] = "non-veg"
            context["preference"] = "non-veg"
        elif "veg" in message_lower or "vegetarian" in message_lower:
            if rec_mem:
                rec_mem.diet = "veg"
            context["diet"] = "veg"
            context["preference"] = "veg"

        # 4. Item Category Extraction & Replacement
        categories_list = [
            ("beverages", ["beverage", "beverages", "drink", "drinks", "coffee", "tea", "juice", "smoothie", "shake", "cold drink"]),
            ("desserts", ["dessert", "desserts", "sweet", "sweets", "ice cream", "icecream", "brownie", "cake"]),
            ("combos", ["combo", "combos", "meal deal", "family combo", "kids combo"]),
            ("burgers", ["burger", "burgers"]),
            ("pizzas", ["pizza", "pizzas"]),
            ("rice", ["rice", "biryani", "bowl"]),
            ("wraps", ["wrap", "wraps", "roll"]),
        ]
        for cat_name, keywords in categories_list:
            if any(k in message_lower for k in keywords):
                if rec_mem:
                    rec_mem.category = cat_name
                context["category"] = cat_name
                break

        # 5. Health Goal Extraction & Replacement
        if "high protein" in message_lower or "protein rich" in message_lower or "protein" in message_lower:
            if rec_mem:
                rec_mem.health_goal = "high_protein"
            context["health_goal"] = "high_protein"
        elif "low calorie" in message_lower or "diet food" in message_lower or "light" in message_lower:
            if rec_mem:
                rec_mem.health_goal = "low_calorie"
            context["health_goal"] = "low_calorie"
        elif "healthy" in message_lower or "gym meals" in message_lower or "fitness" in message_lower:
            if rec_mem:
                rec_mem.health_goal = "healthy"
            context["health_goal"] = "healthy"

        # 6. Serving Extraction & Replacement
        if "family" in message_lower or "party" in message_lower:
            if rec_mem:
                rec_mem.serving = "family"
            context["serving"] = "family"
        elif "kids" in message_lower or "kid" in message_lower:
            if rec_mem:
                rec_mem.serving = "kids"
            context["serving"] = "kids"

        # 7. Budget Extraction & Replacement
        between_match = re.search(r"\bbetween\s*₹?\s*(\d{2,4})\s*(?:and|to)\s*₹?\s*(\d{2,4})\b", message_lower)
        if between_match:
            high = max(int(between_match.group(1)), int(between_match.group(2)))
            if rec_mem:
                rec_mem.budget = float(high)
            context["max_budget"] = float(high)
            context["budget"] = float(high)
        else:
            budget_match = re.search(r"\b(?:under|below|less than|around|<=|at|max|budget)\s*₹?\s*(\d{2,4})\b", message_lower)
            if budget_match:
                b_val = float(budget_match.group(1))
                if rec_mem:
                    rec_mem.budget = b_val
                context["max_budget"] = b_val
                context["budget"] = b_val
            elif "cheap" in message_lower or "affordable" in message_lower:
                if rec_mem:
                    rec_mem.budget = 200.0
                context["max_budget"] = 200.0
                context["budget"] = 200.0

        # 8. Meal Type Extraction & Replacement
        meal_types = ["breakfast", "lunch", "dinner", "snack", "snacks", "late night"]
        for m in meal_types:
            if m in message_lower:
                norm_m = "snacks" if m == "snack" else m
                if rec_mem:
                    rec_mem.meal_type = norm_m
                context["meal_type"] = norm_m
                break

        # Adaptive Default: If meal_type is still missing and no category/cuisine specified, infer from current time
        if rec_mem and not rec_mem.meal_type and "meal_type" not in context:
            adaptive_meal = self._get_adaptive_default_meal_type()
            rec_mem.meal_type = adaptive_meal
            context["meal_type"] = adaptive_meal

        # 9. Merge Memory into Context
        if rec_mem:
            updated_dict = rec_mem.to_dict()
            for key, val in updated_dict.items():
                if val is not None and key not in context:
                    context[key] = val
                    if key == "budget":
                        context["max_budget"] = val
                    if key == "diet":
                        context["preference"] = val

            print("\n========================================")
            print("[RECOMMENDATION ENGINE]")
            print(f"Message: \"{message}\"")
            print(f"Previous Memory: {prev_memory_dict}")
            print(f"Updated Memory:  {updated_dict}")
            print("========================================\n")

        return context

    def _extract_planning_context(self, message: str, user_context: Dict[str, Any], classification: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Extract context for meal planning."""
        goal = "General health and wellness"
        budget = user_context.get("budget_left", 2000)
        preferences = user_context.get("preference", "veg")
        
        # Override from classification if available
        if classification and "entities" in classification:
            entities = classification["entities"]
            if entities.get("budget_max"):
                budget = entities["budget_max"]
            if entities.get("preference"):
                preferences = entities["preference"]
            
            if entities.get("health_goal"):
                goal = "Healthy and nutritious"
            elif entities.get("protein_rich"):
                goal = "High protein and muscle building"
            elif "weight" in message.lower():
                goal = "Weight management"
        
        # Build constraints
        constraints = [message] # raw message has natural language
        if classification and "entities" in classification:
            entities = classification["entities"]
            if entities.get("cuisine"):
                constraints.append(f"Cuisine: {entities.get('cuisine')}")
            if entities.get("excluded_items"):
                constraints.append(f"Exclude: {', '.join(entities.get('excluded_items'))}")
            if entities.get("included_items"):
                constraints.append(f"Include: {', '.join(entities.get('included_items'))}")
                
        return {
            "goal": goal,
            "budget": budget,
            "preferences": preferences,
            "constraints": " | ".join(constraints),
        }

    def _extract_order_items(self, message: str, classification: Optional[Dict[str, Any]] = None) -> list[int]:
        """Extract item IDs from order message using smart keyword extraction."""
        item_ids = []
        
        # 1. High-priority LLM entity extraction (Context-aware)
        if classification and "entities" in classification:
            item_names = classification["entities"].get("item_names", [])
            for name in item_names:
                item = self.resolve_catalog_item(name)
                if item and item["item_id"] not in item_ids:
                    item_ids.append(item["item_id"])
                    
        # 2. Strict Deterministic Fallback if LLM missed items
        if not item_ids:
            message_lower = message.lower()
            parts = re.split(r",|\s+and\s+|\s+with\s+", message_lower)
            
            for part in parts:
                part = part.strip()
                if not part:
                    continue
                keywords = self.extract_order_keywords(part)
                for keyword in keywords:
                    item = self.resolve_catalog_item(keyword)
                    if item and item["item_id"] not in item_ids:
                        item_ids.append(item["item_id"])
                        
        return item_ids[:5]

    def _generate_recommendation_response(self, result: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Generate natural recommendation response using the new generator."""
        try:
            # Use new response generator
            return self.response_generator.generate_response(
                "food_recommendation",
                result,
                tone="casual"
            )
        except Exception:
            # Fallback to old method if new generator fails
            return self.generate_chat_response("food_recommendation", result)

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

    session_id = "demo-session"

    conversation = [
    ("Order burger", {"session_id": session_id}),
    ("Add fries too", {"session_id": session_id}),
    ("Show my cart", {"session_id": session_id}),
    ("Add another burger", {"session_id": session_id}),
    ("Show my cart", {"session_id": session_id}),
    ("Remove fries", {"session_id": session_id}),
    ("Show my cart", {"session_id": session_id}),
    ("Checkout", {"session_id": session_id}),
    ("Track that order", {"session_id": session_id}),
    ("Suggest healthy lunch", {"session_id": session_id}),
    ("Make it cheaper", {"session_id": session_id}),
    ("Make me a weekly meal plan", {"session_id": session_id}),
    ("Non-veg version instead", {"session_id": session_id}),
]

    for message, user_context in conversation:
        print(f"\nUSER: {message}")
        result = orchestrator.handle_message(message, user_context)
        print(json.dumps(result, indent=2))
