"""
Conversational Classifier Module

Transforms rigid keyword/regex detection into LLM-powered natural language understanding.
Classifies user messages into intents, extracts entities, and understands conversational nuances.
"""

import json
from typing import Any, Dict, List, Optional

try:
    from app.services.llm_service import GroqService
except ImportError:
    from .llm_service import GroqService


class ConversationalClassifier:
    """
    LLM-powered classifier for natural conversational understanding.
    
    Transforms messages into structured classification with:
    - Primary intent
    - Sub-intents (for mixed actions)
    - Conversational entities
    - Tone detection
    - Follow-up detection
    - Context needs
    """

    # Supported intents
    CORE_INTENTS = [
        "food_recommendation",
        "add_to_cart",
        "remove_from_cart",
        "view_cart",
        "checkout_cart",
        "meal_planning",
        "order_status",
    ]

    CONVERSATIONAL_INTENTS = [
        "greeting",
        "gratitude",
        "affirmation",
        "rejection",
        "clarification",
        "casual_chat",
        "modify_previous_request",
        "preference_update",
    ]

    def __init__(self) -> None:
        """Initialize the classifier with LLM service."""
        self.llm_service = GroqService()

    def classify_user_message(
        self,
        message: str,
        session_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Classify a user message into structured intent and entities.

        Args:
            message: User input message
            session_context: Previous conversation context for follow-ups

        Returns:
            Classification result with intent, entities, tone, etc.
            
        Classification structure:
        {
            "intent": "primary intent",
            "sub_intents": ["additional intents if multi-action"],
            "confidence": 0.0-1.0,
            "entities": {
                "meal_type": "dinner",
                "budget_max": 200,
                "preference": "non-veg",
                ...
            },
            "tone": "casual|formal|excited|neutral",
            "is_followup": bool,
            "needs_context": bool,
            "raw_classification": {...},  # Full LLM response
        }
        """
        try:
            # Use LLM to classify the message
            classification = self._llm_classify(message, session_context)

            # Validate and enhance classification
            validated = self._validate_classification(classification)

            # Extract and normalize entities
            entities = self._extract_entities(message, validated)

            # Detect tone
            tone = self._detect_tone(message)

            # Determine if this is a follow-up
            is_followup = self._is_followup_message(message, session_context)

            # Check if needs context from session
            needs_context = self._needs_context(validated)

            return {
                "intent": validated.get("intent", "casual_chat"),
                "sub_intents": validated.get("sub_intents", []),
                "confidence": validated.get("confidence", 0.7),
                "entities": entities,
                "tone": tone,
                "is_followup": is_followup,
                "needs_context": needs_context,
                "raw_classification": classification,
            }

        except Exception as e:
            # Fallback to keyword-based classification on LLM failure
            return self._fallback_classify(message, session_context, str(e))

    def _llm_classify(
        self,
        message: str,
        session_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Use LLM to classify message into structured intent."""
        
        session_info = ""
        if session_context:
            last_intent = session_context.get("last_intent", "unknown")
            session_info = f"\n\nPrevious intent in this conversation: {last_intent}"

        classification_prompt = f"""Analyze this user message and classify it into a structured intent classification.

User message: "{message}"{session_info}

Respond with ONLY valid JSON (no markdown, no code blocks, no extra text):

{{
  "intent": "primary intent (one of: food_recommendation, add_to_cart, remove_from_cart, view_cart, checkout_cart, meal_planning, order_status, greeting, gratitude, affirmation, rejection, clarification, casual_chat, modify_previous_request, preference_update)",
  "sub_intents": ["list of secondary intents if this is a multi-action request, empty array if single"],
  "confidence": confidence score from 0 to 1,
  "reasoning": "brief reason for this classification"
}}

Classification rules:
- If user says "thanks", "thank you", "awesome" → gratitude
- If user says "yes", "ok", "sure", "cool" → affirmation
- If user says "no", "nope", "don't want" → rejection
- If user says "hi", "hello", "hey" → greeting
- If user mentions food items to add → add_to_cart
- If user wants to remove items → remove_from_cart
- If user asks about cart contents → view_cart
- If user wants to pay/complete → checkout_cart
- If user mentions dietary preferences, budget, or wants suggestions → food_recommendation
- If user wants a meal plan → meal_planning
- If user asks about their order status → order_status
- If user modifies previous request → modify_previous_request
- If user updates preferences → preference_update
- If "something cheaper" after recommendations → modify_previous_request with food_recommendation sub_intent
- If "remove fries and add burger" → remove_from_cart + add_to_cart sub_intents
"""

        response = self.llm_service.generate_json_response(classification_prompt)
        return response

    def _validate_classification(self, classification: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and normalize the LLM classification."""
        intent = classification.get("intent", "casual_chat").lower()
        
        # Normalize intent names
        all_intents = self.CORE_INTENTS + self.CONVERSATIONAL_INTENTS
        if intent not in all_intents:
            intent = "casual_chat"

        sub_intents = classification.get("sub_intents", [])
        sub_intents = [s.lower() for s in sub_intents if isinstance(s, str)]
        sub_intents = [s for s in sub_intents if s in all_intents]

        confidence = float(classification.get("confidence", 0.7))
        confidence = max(0.0, min(1.0, confidence))

        return {
            "intent": intent,
            "sub_intents": sub_intents,
            "confidence": confidence,
            "reasoning": classification.get("reasoning", ""),
        }

    def _extract_entities(
        self,
        message: str,
        classification: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Extract conversational entities from message.
        
        Returns entities like:
        {
            "meal_type": "dinner",
            "budget_max": 200,
            "preference": "non-veg",
            "health_goal": True,
            "spicy": True,
            "protein_rich": True,
            "mood": "comfort",
            "excluded_items": ["fries"],
            "included_items": ["wrap"]
        }
        """
        try:
            entity_prompt = f"""Extract conversational entities from this message.

Message: "{message}"

Respond with ONLY valid JSON:

{{
  "meal_type": "breakfast|lunch|dinner|snacks|null",
  "budget_min": null or number,
  "budget_max": null or number,
  "preference": "veg|non-veg|null",
  "health_goal": true or false,
  "spicy": true or false or null (null = no spice preference mentioned),
  "protein_rich": true or false,
  "mood": "comfort|light|healthy|expensive|budget|late_night|null",
  "excluded_items": ["list of items to exclude"],
  "included_items": ["list of items to include"],
  "quantity": null or number,
  "item_names": ["specific food items mentioned"]
}}

Rules:
- Extract budget as numeric value only
- null means not mentioned in message
- Look for keywords like "lighter", "protein", "spicy", "cheap", "expensive"
- Extract specific item names mentioned
- "non veg" should be "non-veg"
"""
            entities_response = self.llm_service.generate_json_response(entity_prompt)
            
            # Clean up entities
            entities = {}
            for key, value in entities_response.items():
                if value is not None and value != "null":
                    entities[key] = value
            
            return entities

        except Exception as e:
            # Fallback to empty entities on extraction failure
            return {}

    def _detect_tone(self, message: str) -> str:
        """Detect tone of the message."""
        message_lower = message.lower()

        if any(marker in message_lower for marker in ["!", "omg", "wow", "amazing", "love", "awesome"]):
            return "excited"

        if any(marker in message_lower for marker in ["?", "please", "could", "would", "could you"]):
            return "formal"

        if any(marker in message_lower for marker in ["lol", "haha", "cool", "nice", "yeah", "yep"]):
            return "casual"

        return "neutral"

    def _is_followup_message(
        self,
        message: str,
        session_context: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Detect if this is a follow-up to previous message."""
        if not session_context:
            return False

        message_lower = message.lower()

        # Explicit follow-up markers
        followup_markers = [
            "cheaper", "more expensive",
            "healthier", "less healthy",
            "lighter", "heavier",
            "spicier", "less spicy",
            "something", "anything",
            "more", "less",
            "instead", "also", "too",
            "instead of",
            "remove that", "change that",
            "modify",
        ]

        if any(marker in message_lower for marker in followup_markers):
            return True

        # Context-based detection
        if session_context.get("last_intent"):
            if session_context["last_intent"] in [
                "food_recommendation",
                "meal_planning",
                "add_to_cart",
            ]:
                # Short messages might be follow-ups
                if len(message.split()) <= 5:
                    return True

        return False

    def _needs_context(self, classification: Dict[str, Any]) -> bool:
        """Determine if message needs context from session."""
        followup_intents = [
            "modify_previous_request",
            "preference_update",
        ]

        return classification.get("intent") in followup_intents

    def _fallback_classify(
        self,
        message: str,
        session_context: Optional[Dict[str, Any]] = None,
        error: str = "",
    ) -> Dict[str, Any]:
        """
        Fallback classification when LLM fails.
        Uses simple heuristics to maintain service availability.
        """
        message_lower = message.lower()

        intent = "casual_chat"
        sub_intents = []

        # Simple intent detection
        if any(word in message_lower for word in ["hello", "hi", "hey", "greet"]):
            intent = "greeting"
        elif any(word in message_lower for word in ["thanks", "thank", "thankyou", "appreciated"]):
            intent = "gratitude"
        elif any(word in message_lower for word in ["yes", "yeah", "yep", "ok", "okay", "sure", "cool"]):
            intent = "affirmation"
        elif any(word in message_lower for word in ["no", "nope", "don't", "dont", "not"]):
            intent = "rejection"
        elif any(word in message_lower for word in ["add", "order", "get", "want", "send"]):
            intent = "add_to_cart"
        elif any(word in message_lower for word in ["remove", "delete", "drop", "cancel"]):
            intent = "remove_from_cart"
        elif any(word in message_lower for word in ["cart", "show", "view"]):
            intent = "view_cart"
        elif any(word in message_lower for word in ["checkout", "pay", "complete", "place order"]):
            intent = "checkout_cart"
        elif any(word in message_lower for word in ["plan", "weekly", "schedule"]):
            intent = "meal_planning"
        elif any(word in message_lower for word in ["recommend", "suggest", "cheap", "healthy"]):
            intent = "food_recommendation"
        elif any(word in message_lower for word in ["status", "track", "where"]):
            intent = "order_status"

        # Detect multi-action
        if "and" in message_lower or "also" in message_lower:
            if "remove" in message_lower and "add" in message_lower:
                sub_intents = ["remove_from_cart", "add_to_cart"]

        return {
            "intent": intent,
            "sub_intents": sub_intents,
            "confidence": 0.5,
            "entities": {},
            "tone": "neutral",
            "is_followup": len(message.split()) <= 5,
            "needs_context": intent in ["modify_previous_request", "preference_update"],
            "raw_classification": {"error": error, "fallback": True},
        }


class ConversationMemory:
    """
    Maintains conversation history and context for better follow-up understanding.
    Tracks intents, entities, and recommendations across messages.
    """

    def __init__(self, max_history: int = 10) -> None:
        """Initialize conversation memory."""
        self.max_history = max_history
        self.messages: List[Dict[str, Any]] = []
        self.last_intent: Optional[str] = None
        self.last_entities: Dict[str, Any] = {}
        self.last_recommendation_context: Dict[str, Any] = {}

    def add_interaction(
        self,
        user_message: str,
        classification: Dict[str, Any],
        response: str = "",
        data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add a new user-assistant interaction to memory."""
        interaction = {
            "user_message": user_message,
            "classification": classification,
            "response": response,
            "data": data or {},
        }

        self.messages.append(interaction)

        # Keep only recent history
        if len(self.messages) > self.max_history:
            self.messages = self.messages[-self.max_history :]

        # Update tracking
        self.last_intent = classification.get("intent")
        self.last_entities = classification.get("entities", {})

        if classification.get("intent") == "food_recommendation":
            self.last_recommendation_context = self.last_entities.copy()

    def get_session_context(self) -> Dict[str, Any]:
        """Get current session context for follow-up processing."""
        return {
            "last_intent": self.last_intent,
            "last_entities": self.last_entities,
            "last_recommendation_context": self.last_recommendation_context,
            "history_length": len(self.messages),
            "recent_messages": [m.get("user_message") for m in self.messages[-3:]],
        }

    def get_interaction_history(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent interaction history."""
        return self.messages[-limit:]
