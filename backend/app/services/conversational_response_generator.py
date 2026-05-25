"""
Conversational Response Generator

Generates natural, varied responses based on intent, context, and tone.
Replaces template-based hardcoded responses with LLM-powered natural language generation.
"""

from typing import Any, Dict, List, Optional

try:
    from app.services.llm_service import GroqService
except ImportError:
    from .llm_service import GroqService


class ConversationalResponseGenerator:
    """
    Generates natural conversational responses for different intents and contexts.
    
    Maintains tone variation and personalizes responses based on:
    - Intent type
    - Previous context
    - User tone
    - Business data (recommendations, cart, etc.)
    """

    def __init__(self) -> None:
        """Initialize response generator with LLM service."""
        self.llm_service = GroqService()

    def generate_response(
        self,
        intent: str,
        data: Dict[str, Any],
        tone: str = "casual",
        session_context: Optional[Dict[str, Any]] = None,
        add_followup: bool = True,
        original_response: Optional[str] = None,
    ) -> str:
        """
        Generate a natural response for the given intent and data.

        Args:
            intent: The classified intent
            data: Business data (recommendations, cart, order, etc.)
            tone: User's tone (casual, formal, excited, neutral)
            session_context: Previous conversation context
            add_followup: Whether to include follow-up suggestions
            original_response: The deterministic business logic response to preserve

        Returns:
            Natural conversational response string
        """
        # ISSUE 4 FIX: Ensure conversational formatting NEVER removes business logic actions
        transactional_intents = ["add_to_cart", "remove_from_cart", "checkout_cart", "cart_action", "multi_action", "place_order", "reorder_action"]
        if original_response and intent in transactional_intents:
            return original_response

        try:
            # Try LLM-powered response generation
            response = self._generate_with_llm(
                intent,
                data,
                tone,
                session_context,
                add_followup,
                original_response
            )
            return response

        except Exception as e:
            # Fallback to template-based generation
            return self._generate_template_response(intent, data, tone, original_response)

    def _generate_with_llm(
        self,
        intent: str,
        data: Dict[str, Any],
        tone: str,
        session_context: Optional[Dict[str, Any]] = None,
        add_followup: bool = True,
        original_response: Optional[str] = None,
    ) -> str:
        """Generate response using LLM."""
        
        context_info = ""
        if session_context:
            context_info = f"""
Previous intent: {session_context.get('last_intent', 'unknown')}
Recent messages: {', '.join(session_context.get('recent_messages', [])[:2])}
"""

        followup_instruction = ""
        if add_followup:
            followup_instruction = "\nInclude a natural follow-up suggestion at the end (not as a separate line)."

        system_action_info = ""
        if original_response:
            system_action_info = f"\nSystem Action Taken: \"{original_response}\"\n(CRITICAL: You MUST preserve the exact facts, item names, prices, and quantities from this system action in your response. Do not overwrite business facts with generic text.)"

        data_str = self._format_data_for_prompt(intent, data)

        response_prompt = f"""Generate a natural, conversational response for a Swiggy food ordering AI assistant.

User tone: {tone}
Intent: {intent}{context_info}{system_action_info}

Business data:
{data_str}

Generate a friendly, natural response. Keep it concise (1-2 sentences max).{followup_instruction}

Do NOT include:
- Formal or robotic language
- Templates or generic phrases
- Multiple options separated by OR
- Explanations about the system

Just respond naturally as a helpful food ordering assistant would."""

        response = self.llm_service.generate_response(response_prompt)
        return response.strip()

    def _format_data_for_prompt(self, intent: str, data: Dict[str, Any]) -> str:
        """Format business data for LLM prompt."""
        if intent == "food_recommendation" or intent == "healthy_suggestions":
            recs = data.get("recommendations", [])
            if not recs:
                return "No recommendations found matching criteria."
            items = [f"• {r.get('item_name', '')} (₹{r.get('price', 0)})" for r in recs[:3]]
            return "\n".join(items)

        elif intent == "add_to_cart":
            cart = data.get("cart", {})
            items = [f"• {i['name']} x{i['quantity']}" for i in cart.get("items", [])]
            total = cart.get("total", 0)
            return f"Cart items:\n" + "\n".join(items) + f"\nTotal: ₹{total}"

        elif intent == "view_cart":
            cart = data.get("cart", {})
            if not cart.get("items"):
                return "Empty cart"
            items = [f"• {i['name']} x{i['quantity']} (₹{i.get('price', 0) * i['quantity']})" 
                     for i in cart.get("items", [])]
            total = cart.get("total", 0)
            return f"Cart contains:\n" + "\n".join(items) + f"\nTotal: ₹{total}"

        elif intent == "checkout_cart":
            order = data.get("order", {})
            items = [item.get("name", "") for item in order.get("items", [])]
            order_id = order.get("order_id", "")
            return f"Order ID: {order_id}\nItems: {', '.join(items)}"

        elif intent == "order_status":
            status = data.get("status", "unknown")
            order_id = data.get("order_id", "")
            return f"Order ID: {order_id}\nStatus: {status}"

        elif intent == "meal_planning" or intent == "modify_meal_plan" or intent == "show_meal_plan":
            plan = data.get("meal_plan", {})
            if not plan:
                return "No meal plan found."
            days = list(plan.keys())[:3]
            if intent == "modify_meal_plan":
                action = "updated"
            elif intent == "show_meal_plan":
                action = "retrieved"
            else:
                action = "created"
            return f"7-day meal plan {action} with {len(plan)} days planned."

        elif intent in ["greeting", "gratitude", "affirmation", "rejection"]:
            return ""

        else:
            return str(data)

    def _generate_template_response(
        self, 
        intent: str, 
        data: Dict[str, Any], 
        tone: str = "casual", 
        original_response: Optional[str] = None
    ) -> str:
        """Fallback template-based response generation."""
        
        if original_response:
            return original_response  # Preserve exact business logic facts on LLM failure

        if intent == "greeting":
            return self._template_greeting(tone)

        elif intent == "gratitude":
            return self._template_gratitude(tone)

        elif intent == "affirmation":
            return self._template_affirmation(tone)

        elif intent == "rejection":
            return self._template_rejection(tone)

        elif intent == "casual_chat":
            return self._template_casual_chat(tone)

        elif intent == "food_recommendation":
            return self._template_recommendation(data, tone)

        elif intent == "add_to_cart":
            return self._template_add_to_cart(data, tone)

        elif intent == "remove_from_cart":
            return self._template_remove_from_cart(data, tone)

        elif intent == "view_cart":
            return self._template_view_cart(data, tone)

        elif intent == "checkout_cart":
            return self._template_checkout(data, tone)

        elif intent == "order_status":
            return self._template_order_status(data, tone)

        elif intent == "meal_planning":
            return self._template_meal_plan(data, tone)
            
        elif intent == "modify_meal_plan":
            return "I've successfully updated your meal plan based on your request!"
            
        elif intent == "show_meal_plan":
            return "Here is your current meal plan!"

        else:
            return "How can I help you with your order?"

    # Greeting responses
    def _template_greeting(self, tone: str) -> str:
        """Generate greeting response."""
        if tone == "excited":
            return "Hey there! Great to see you! 👋 What can I get you today?"
        elif tone == "formal":
            return "Hello! Welcome. How may I assist you with your order today?"
        else:
            return "Hi! Ready to order something delicious? 😊"

    # Gratitude responses
    def _template_gratitude(self, tone: str) -> str:
        """Generate gratitude response."""
        responses = [
            "You're welcome! Anything else I can help with?",
            "Happy to help! Need anything else?",
            "My pleasure! Want to add anything to your order?",
            "Glad I could help! Want a dessert to go with that?",
        ]
        idx = hash(tone) % len(responses)
        return responses[idx]

    # Affirmation responses
    def _template_affirmation(self, tone: str) -> str:
        """Generate affirmation response."""
        responses = [
            "Awesome! Let's proceed.",
            "Perfect! What's next?",
            "Great choice! Anything else?",
            "Sounds good! Want to add more?",
        ]
        idx = hash(tone) % len(responses)
        return responses[idx]

    # Rejection responses
    def _template_rejection(self, tone: str) -> str:
        """Generate rejection response."""
        responses = [
            "No problem! What would you prefer instead?",
            "Gotcha! Let me suggest something different.",
            "All good! Want to explore other options?",
            "Sure thing! What else can I help with?",
        ]
        idx = hash(tone) % len(responses)
        return responses[idx]

    # Casual chat responses
    def _template_casual_chat(self, tone: str) -> str:
        """Generate casual chat response."""
        return "I'm here to help you order! 😊 What can I get you?"

    # Recommendation responses
    def _template_recommendation(self, data: Dict[str, Any], tone: str) -> str:
        """Generate recommendation response."""
        recs = data.get("recommendations", [])
        if not recs:
            return "Couldn't find matches for those filters. Try adjusting your preferences!"

        names = [r.get("item_name", "") for r in recs[:3]]
        items_str = ", ".join(names)

        responses = [
            f"Check these out: {items_str}. Want to add any?",
            f"How about: {items_str}? Any of these sound good?",
            f"I'd recommend: {items_str}. Interested?",
            f"Try these: {items_str}. Like any of them?",
        ]
        idx = hash(tone) % len(responses)
        return responses[idx]

    # Cart action responses
    def _template_add_to_cart(self, data: Dict[str, Any], tone: str) -> str:
        """Generate add to cart response."""
        cart = data.get("cart", {})
        total = cart.get("total", 0)
        
        responses = [
            f"Done! Your cart total is now ₹{total}.",
            f"Added to cart. Cart total: ₹{total}.",
            f"Got it! That's ₹{total} total.",
            f"Perfect! Your cart is ₹{total} now.",
        ]
        idx = hash(str(total)) % len(responses)
        return responses[idx]

    def _template_remove_from_cart(self, data: Dict[str, Any], tone: str) -> str:
        """Generate remove from cart response."""
        cart = data.get("cart", {})
        total = cart.get("total", 0)
        
        responses = [
            f"Removed! Cart total is now ₹{total}.",
            f"Done! New total: ₹{total}.",
            f"Updated. Cart is now ₹{total}.",
            f"Got it! That's ₹{total} total.",
        ]
        idx = hash(str(total)) % len(responses)
        return responses[idx]

    def _template_view_cart(self, data: Dict[str, Any], tone: str) -> str:
        """Generate view cart response."""
        cart = data.get("cart", {})
        items = cart.get("items", [])

        if not items:
            return "Your cart is empty. What would you like to add?"

        item_list = ", ".join([f"{i['name']} x{i['quantity']}" for i in items])
        total = cart.get("total", 0)

        return f"Your cart has: {item_list}. Total: ₹{total}. Ready to checkout?"

    def _template_checkout(self, data: Dict[str, Any], tone: str) -> str:
        """Generate checkout response."""
        order = data.get("order", {})
        order_id = order.get("order_id", "")
        items = order.get("items", [])

        item_names = [item.get("name", "") for item in items]
        items_str = ", ".join(item_names)

        responses = [
            f"Order placed! 🎉 Order ID: {order_id}. {items_str} is on its way!",
            f"All set! Your order {order_id} is confirmed.",
            f"Got it! {items_str} will be delivered soon. Order ID: {order_id}.",
            f"Perfect! Order {order_id} confirmed. Your food is being prepared.",
        ]
        idx = hash(order_id) % len(responses)
        return responses[idx]

    def _template_order_status(self, data: Dict[str, Any], tone: str) -> str:
        """Generate order status response."""
        status = data.get("status", "unknown").upper()
        order_id = data.get("order_id", "")

        status_messages = {
            "PENDING": f"Your order {order_id} is being prepared. Coming soon!",
            "CONFIRMED": f"Order {order_id} confirmed! Chef is working on it.",
            "PREPARING": f"Your food is being prepared. Stay tuned!",
            "ON_THE_WAY": f"Your order {order_id} is out for delivery! 🚴",
            "DELIVERED": f"Order {order_id} delivered! Hope you enjoyed! 😊",
            "CANCELLED": f"Order {order_id} was cancelled.",
        }

        return status_messages.get(status, f"Order {order_id} status: {status}")

    def _template_meal_plan(self, data: Dict[str, Any], tone: str) -> str:
        """Generate meal plan response."""
        responses = [
            "Your personalized meal plan is ready! Check out the details.",
            "All set! I've created a custom 7-day meal plan for you.",
            "Done! Your meal plan is tailored to your preferences.",
            "Perfect! Your weekly meal plan is ready to go.",
        ]
        idx = hash(str(len(data))) % len(responses)
        return responses[idx]

    # New conversational features
    def generate_greeting_with_context(self, returning_user: bool = False) -> str:
        """Generate context-aware greeting."""
        if returning_user:
            return "Welcome back! 👋 What can I get for you today?"
        return "Hi there! 😊 Looking for something delicious?"

    def generate_followup_suggestion(self, intent: str, data: Dict[str, Any]) -> str:
        """Generate natural follow-up suggestion."""
        suggestions = {
            "food_recommendation": "Want to add one of these to your cart?",
            "add_to_cart": "Need anything else?",
            "view_cart": "Ready to checkout?",
            "meal_planning": "Want me to optimize the grocery list?",
            "order_status": "Anything else you'd like to order?",
        }
        return suggestions.get(intent, "Anything else I can help with?")

    def generate_error_response(self, error_type: str) -> str:
        """Generate natural error responses."""
        errors = {
            "empty_cart": "Your cart is empty. Let me help you find something tasty!",
            "item_not_found": "Couldn't find that item. Want me to suggest something similar?",
            "budget_exceeded": "That's a bit over budget. Let me find something cheaper?",
            "not_available": "That item is out of stock right now. Try something else?",
            "generic": "Oops! Something went wrong. Let's try again!",
        }
        return errors.get(error_type, errors["generic"])
