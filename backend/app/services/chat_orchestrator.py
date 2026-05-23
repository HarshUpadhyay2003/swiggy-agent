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


class ChatOrchestrator:
    """Central conversational orchestration layer for AI commerce assistant."""

    INTENT_KEYWORDS = {
        "order_status": ["status", "track", "where is my order", "order status", "track order"],
        "view_cart": ["show my cart", "view cart", "my cart", "show cart", "what's in my cart"],
        "remove_from_cart": ["remove", "delete", "drop", "cancel", "take out"],
        "checkout_cart": ["checkout", "place order", "complete order", "order now", "pay now", "finish order"],
        "meal_planning": ["plan", "weekly", "meal plan", "schedule"],
        "food_recommendation": ["recommend", "suggest", "cheap", "expensive", "dinner", "lunch", "breakfast", "snacks", "comfort", "healthy"],
        "healthy_suggestions": ["healthy", "health", "diet", "nutrition"],
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
        action_summary = ", ".join(actions_executed)

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

        print(f"[DEBUG] Follow-up resolution | Domain: {active_domain} | Intent: {current_intent}")

        # Planner Continuity Override
        if active_domain == "planner":
            if current_intent in ["remove_from_cart", "modify_previous_request", "casual_chat"]:
                classification["intent"] = "modify_meal_plan"
                return self.handle_modify_meal_plan(message, user_context, session_context, classification, session_state)
            elif current_intent == "meal_planning":
                return self.handle_meal_planning(message, user_context, classification, session_state)

        # Cart Continuity Override
        if active_domain == "cart":
            if current_intent in ["modify_meal_plan", "modify_previous_request"]:
                classification["intent"] = "remove_from_cart"
                return self.handle_remove_from_cart(message, user_context, classification)
        
        # If user previously got recommendations and asks for cheaper/healthier version
        if last_intent in ["food_recommendation", "healthy_suggestions"] or active_domain == "recommendations":
            # Merge contexts - keep last recommendation context, update with new filters
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
        
        # If user previously got a meal plan and asks for modifications
        if last_intent == "meal_planning":
            merged_context = dict(user_context)
            merged_context.update(last_entities)
            merged_context.update(entities)
            return self.handle_meal_planning(message, merged_context)
        
        # Default: handle as regular core intent
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
        if intent == "food_recommendation":
            result = self.handle_food_recommendation(message, user_context)
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
            result = self.handle_order_status(message, user_context)
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
                )
                if improved_response:
                    result["response"] = improved_response
            except Exception:
                # Keep original response if generation fails
                pass
        
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
        
        intent = classification.get("intent", "casual_chat")
        msg_lower = message.lower()
        
        # Planner Override Logic: Ensure explicit planner prompts don't get lost in conversational flows
        if any(w in msg_lower for w in ["show my planner", "my weekly planner", "display meal plan", "show meal plan"]):
            classification["intent"] = "show_meal_plan"
            
        planner_keywords = ["plan", "planner", "weekly meal", "meal prep"]
        if any(w in msg_lower for w in planner_keywords) and self._is_conversational_intent(intent):
            classification["intent"] = "meal_planning"

        intent = classification.get("intent")

        # Route to appropriate handler
        if intent in ["meal_planning", "modify_meal_plan", "show_meal_plan"]:
            # Always prioritize planner core execution
            result = self._handle_core_intent(message, classification, user_context, session_context, session_state)
        elif self._is_conversational_intent(intent):
            result = self._handle_conversational_intent(
                message, classification, user_context
            )
        # Handle multi-action intents (actions array > 0)
        elif classification.get("actions"):
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

    def handle_food_recommendation(self, message: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle food recommendation requests."""
        context = self._extract_recommendation_context(message, user_context)
        result = self.context_engine.recommend_food(context)
        if not result.get("recommendations"):
            if context.get("min_budget") is not None or context.get("max_budget") is not None:
                response = self._build_price_range_response(context)
            else:
                response = "I couldn't find any recommendations matching your preferences. Try adjusting your budget or preferences."
        else:
            response = self._generate_recommendation_response(result, context)
        return {
            "intent": "food_recommendation",
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
            }
        except ValueError:
            return {
                "intent": "order_status",
                "response": f"I couldn't find an order with ID {order_id}.",
                "status": None,
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
                "active_cart": self.cart_service.get_cart(service.get_cart(session_id)),
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

    def _extract_recommendation_context(self, message: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract context for recommendations - now enhanced with LLM-based entity extraction."""
        context = dict(user_context)
        message_lower = message.lower()
        try:
            classification = self.classifier.classify_user_message(message)
            classified_entities = classification.get("entities", {})
            
            # Merge classified entities into context
            if "meal_type" in classified_entities:
                context["meal_type"] = classified_entities["meal_type"]
            if "budget_min" in classified_entities:
                context["min_budget"] = classified_entities["budget_min"]
            if "budget_max" in classified_entities:
                context["max_budget"] = classified_entities["budget_max"]
            if "preference" in classified_entities:
                context["preference"] = classified_entities["preference"]
            if "health_goal" in classified_entities:
                context["health_goal"] = classified_entities["health_goal"]
            if "mood" in classified_entities:
                context["mood"] = classified_entities["mood"]
            if "spicy" in classified_entities and classified_entities["spicy"] is not None:
                context["spicy"] = classified_entities["spicy"]
            if "protein_rich" in classified_entities and classified_entities["protein_rich"]:
                context["protein_rich"] = True
            if "vegan" in classified_entities and classified_entities["vegan"]:
                context["vegan"] = True
            if "low_calorie" in classified_entities and classified_entities["low_calorie"]:
                context["low_calorie"] = True
                
        except Exception:
            # Fallback to regex-based extraction if classifier fails
            pass

        # Fallback regex extraction for new tags
        if "vegan" in message_lower:
            context["vegan"] = True
        if "gluten free" in message_lower or "gluten-free" in message_lower:
            context["gluten_free"] = True
        if "diet" in message_lower or "low calorie" in message_lower:
            context["low_calorie"] = True

        # Fallback regex extraction for items not caught by classifier
        # Extract mood
        if "mood" not in context:
            if "comfort" in message_lower:
                context["mood"] = "comfort food"
            elif "healthy" in message_lower or "health" in message_lower:
                context["mood"] = "healthy"
            elif "late" in message_lower or "night" in message_lower:
                context["mood"] = "late night"

        # Extract budget constraints if not already set
        if "min_budget" not in context and "max_budget" not in context:
            between_match = re.search(
                r"\bbetween\s*₹?\s*(\d{2,4})\s*(?:and|to)\s*₹?\s*(\d{2,4})\b",
                message_lower,
            )
            if between_match:
                try:
                    low = int(between_match.group(1))
                    high = int(between_match.group(2))
                    context["min_budget"] = min(low, high)
                    context["max_budget"] = max(low, high)
                except ValueError:
                    pass
            else:
                min_match = re.search(
                    r"\b(?:above|over|more than|greater than|minimum|min)\s*₹?\s*(\d{2,4})\b",
                    message_lower,
                )
                max_match = re.search(
                    r"\b(?:under|below|less than|maximum|max)\s*₹?\s*(\d{2,4})\b",
                    message_lower,
                )
                if min_match and "min_budget" not in context:
                    try:
                        context["min_budget"] = int(min_match.group(1))
                    except ValueError:
                        pass
                if max_match and "max_budget" not in context:
                    try:
                        context["max_budget"] = int(max_match.group(1))
                    except ValueError:
                        pass
                if ("cheap" in message_lower or "budget meal" in message_lower) and "max_budget" not in context:
                    context["max_budget"] = 200

        # Extract meal_type if not set
        if "meal_type" not in context:
            if "dinner" in message_lower:
                context["meal_type"] = "dinner"
            elif "lunch" in message_lower:
                context["meal_type"] = "lunch"
            elif "breakfast" in message_lower:
                context["meal_type"] = "breakfast"
            elif "snacks" in message_lower:
                context["meal_type"] = "snacks"

        # Extract preference if not in user_context
        if "preference" not in context or not context.get("preference"):
            if "veg" in message_lower and "non" not in message_lower:
                context["preference"] = "veg"
            elif "non-veg" in message_lower or "non veg" in message_lower:
                context["preference"] = "non-veg"

        # Set health_goal if not already set
        if "health_goal" not in context:
            context["health_goal"] = "healthy" in message_lower or context.get("health_goal", False)

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
        
        if classification and "entities" in classification:
            item_names = classification["entities"].get("item_names", [])
            for name in item_names:
                item = self.resolve_catalog_item(name)
                if item and item["item_id"] not in item_ids:
                    item_ids.append(item["item_id"])
                    
        if not item_ids:
            keywords = self.extract_order_keywords(message)
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
