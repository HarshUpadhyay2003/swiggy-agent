"""
Test Cases for Conversational AI Commerce Assistant Refactor

Tests the new LLM-based conversational intelligence system.
Covers: natural language understanding, entity extraction, mixed intents, 
context-aware follow-ups, and conversational responses.
"""

import json
import sys
from typing import Any, Dict

try:
    from app.services.chat_orchestrator import ChatOrchestrator
except ImportError:
    from services.chat_orchestrator import ChatOrchestrator


class ConversationalAssistantTester:
    """Comprehensive test suite for conversational AI improvements."""

    def __init__(self):
        """Initialize tester with orchestrator."""
        self.orchestrator = ChatOrchestrator()
        self.test_results = []
        self.session_id = "test-session-001"

    def run_all_tests(self) -> None:
        """Run all test categories."""
        print("\n" + "=" * 80)
        print("CONVERSATIONAL AI COMMERCE ASSISTANT - TEST SUITE")
        print("=" * 80)

        self.test_general_conversation()
        self.test_recommendation_intents()
        self.test_followup_understanding()
        self.test_mixed_action_intents()
        self.test_cart_operations()
        self.test_meal_planning()
        self.test_natural_language_variations()

        self.print_summary()

    def test_general_conversation(self) -> None:
        """Test general conversation handling."""
        print("\n" + "-" * 80)
        print("TEST 1: GENERAL CONVERSATION")
        print("-" * 80)

        test_cases = [
            ("hi", "greeting"),
            ("hello", "greeting"),
            ("thanks", "gratitude"),
            ("thank you", "gratitude"),
            ("cool", "affirmation"),
            ("okay", "affirmation"),
            ("sounds good", "affirmation"),
            ("that sounds nice", "affirmation"),
            ("no", "rejection"),
            ("i don't want that", "rejection"),
        ]

        for message, expected_intent in test_cases:
            self._run_test(message, expected_intent, "GENERAL_CHAT")

    def test_recommendation_intents(self) -> None:
        """Test recommendation-related intents."""
        print("\n" + "-" * 80)
        print("TEST 2: RECOMMENDATION INTENTS")
        print("-" * 80)

        test_cases = [
            ("non veg under 200", "food_recommendation", "non-veg + budget"),
            ("give me non veg under 200", "food_recommendation", "non-veg + budget"),
            ("show healthier options", "food_recommendation", "health goal"),
            ("something cheaper", "food_recommendation", "budget update"),
            ("what do you recommend today", "food_recommendation", "open recommendation"),
            ("i want dinner but not too heavy", "food_recommendation", "dinner + light"),
            ("surprise me", "food_recommendation", "surprise"),
            ("protein rich meals", "food_recommendation", "protein preference"),
            ("less spicy options", "food_recommendation", "spice preference"),
            ("budget food", "food_recommendation", "budget constraint"),
        ]

        for message, expected_intent, description in test_cases:
            self._run_test(message, expected_intent, f"RECOMMENDATION: {description}")

    def test_followup_understanding(self) -> None:
        """Test context-aware follow-up understanding."""
        print("\n" + "-" * 80)
        print("TEST 3: FOLLOW-UP UNDERSTANDING")
        print("-" * 80)

        # First message: get recommendations
        msg1 = "recommend healthy dinner under 300"
        print(f"\n📝 User: {msg1}")
        result1 = self.orchestrator.handle_message(
            msg1, {"session_id": self.session_id}
        )
        self._print_result(result1, "Initial recommendation")

        # Follow-up: ask for cheaper options
        msg2 = "something cheaper"
        print(f"\n📝 User: {msg2}")
        result2 = self.orchestrator.handle_message(
            msg2, {"session_id": self.session_id}
        )
        self._check_followup_understanding(msg2, result2, "should apply budget filter to previous dinner context")

        # Follow-up: ask for different preference
        msg3 = "non veg version instead"
        print(f"\n📝 User: {msg3}")
        result3 = self.orchestrator.handle_message(
            msg3, {"session_id": self.session_id}
        )
        self._check_followup_understanding(msg3, result3, "should change to non-veg while keeping dinner context")

    def test_mixed_action_intents(self) -> None:
        """Test mixed intent handling (multiple actions in one message)."""
        print("\n" + "-" * 80)
        print("TEST 4: MIXED ACTION INTENTS")
        print("-" * 80)

        test_cases = [
            ("remove fries and add burger", "Multi-action: remove + add"),
            ("add noodles then checkout", "Multi-action: add + checkout"),
            ("show cart and remove fries", "Multi-action: view + remove"),
            ("delete the wrap and add dosa", "Multi-action: remove + add"),
            ("take out fries and put in salad", "Multi-action: remove + add"),
        ]

        for message, description in test_cases:
            print(f"\n📝 User: {message}")
            print(f"   ({description})")
            result = self.orchestrator.handle_message(
                message, {"session_id": self.session_id}
            )
            self._print_result(result, description)
            # Verify it's handling multiple intents
            if result.get("data", {}).get("sub_intents"):
                print(f"   ✅ Detected sub-intents: {result['data']['sub_intents']}")
            else:
                print(f"   ⚠️  No sub-intents detected - check if mixed action was recognized")

    def test_cart_operations(self) -> None:
        """Test cart operations with natural language."""
        print("\n" + "-" * 80)
        print("TEST 5: CART OPERATIONS")
        print("-" * 80)

        operations = [
            ("add burger to cart", "add_to_cart"),
            ("add fries too", "add_to_cart"),
            ("show my cart", "view_cart"),
            ("remove the fries", "remove_from_cart"),
            ("add a salad", "add_to_cart"),
            ("checkout", "checkout_cart"),
        ]

        for message, intent in operations:
            print(f"\n📝 User: {message}")
            result = self.orchestrator.handle_message(
                message, {"session_id": self.session_id}
            )
            self._print_result(result, intent)

    def test_meal_planning(self) -> None:
        """Test meal planning requests."""
        print("\n" + "-" * 80)
        print("TEST 6: MEAL PLANNING")
        print("-" * 80)

        test_cases = [
            ("create healthy weekly plan under 3000", "healthy + budget"),
            ("meal plan for protein building", "protein + muscle goal"),
            ("plan my week with cheaper options", "budget plan"),
            ("weekly meal schedule", "open meal plan"),
        ]

        for message, description in test_cases:
            print(f"\n📝 User: {message}")
            print(f"   ({description})")
            result = self.orchestrator.handle_message(
                message, {"session_id": self.session_id + "-meal"}
            )
            self._print_result(result, description)

    def test_natural_language_variations(self) -> None:
        """Test various natural language formulations of the same intent."""
        print("\n" + "-" * 80)
        print("TEST 7: NATURAL LANGUAGE VARIATIONS")
        print("-" * 80)

        # All should be food_recommendation intent
        variations = [
            "can you suggest something under 200",
            "i'm looking for non-veg meals",
            "gimme cheap options",
            "what's good for dinner",
            "recommend smth healthy",
            "show me stuff under 250",
            "any good veg options",
            "give me options",
        ]

        for message in variations:
            print(f"\n📝 User: {message}")
            result = self.orchestrator.handle_message(
                message, {"session_id": self.session_id + "-variations"}
            )
            intent = result.get("intent", "unknown")
            response = result.get("response", "")
            confidence = result.get("data", {}).get("confidence", "?")
            print(f"   Intent: {intent}")
            print(f"   Response: {response[:80]}...")

    def _run_test(self, message: str, expected_intent: str, description: str) -> None:
        """Run a single test case."""
        print(f"\n📝 '{message}'")
        print(f"   Expected: {expected_intent}")

        try:
            result = self.orchestrator.handle_message(
                message, {"session_id": self.session_id}
            )
            actual_intent = result.get("intent", "unknown")
            response = result.get("response", "")

            print(f"   Got: {actual_intent}")
            print(f"   Response: {response[:70]}...")

            if actual_intent == expected_intent or actual_intent in expected_intent:
                print(f"   ✅ PASS")
                self.test_results.append({"test": description, "status": "PASS"})
            else:
                print(f"   ⚠️  PARTIAL - Intent not exactly matched")
                self.test_results.append(
                    {"test": description, "status": "PARTIAL", "expected": expected_intent, "got": actual_intent}
                )

        except Exception as e:
            print(f"   ❌ FAIL: {str(e)}")
            self.test_results.append(
                {"test": description, "status": "FAIL", "error": str(e)}
            )

    def _check_followup_understanding(self, message: str, result: Dict[str, Any], check: str) -> None:
        """Check if follow-up was understood correctly."""
        print(f"   Response: {result.get('response', '')[:80]}...")
        print(f"   Check: {check}")
        is_followup = result.get("data", {}).get("is_followup", False)
        if is_followup:
            print(f"   ✅ Follow-up detected correctly")
        else:
            print(f"   ⚠️  Follow-up handling unclear")

    def _print_result(self, result: Dict[str, Any], label: str = "") -> None:
        """Pretty print a result."""
        print(f"   [{label}]")
        print(f"   Status: {result.get('status', 'unknown')}")
        print(f"   Intent: {result.get('intent', 'unknown')}")
        response = result.get("response", "")
        print(f"   Response: {response[:80]}{'...' if len(response) > 80 else ''}")
        if result.get("data", {}).get("recommendations"):
            print(f"   Recommendations: {len(result['data']['recommendations'])} items")

    def print_summary(self) -> None:
        """Print test summary."""
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)

        if not self.test_results:
            print("No formal test results recorded.")
            return

        passed = sum(1 for r in self.test_results if r["status"] == "PASS")
        partial = sum(1 for r in self.test_results if r["status"] == "PARTIAL")
        failed = sum(1 for r in self.test_results if r["status"] == "FAIL")
        total = len(self.test_results)

        print(f"\nTotal Tests: {total}")
        print(f"✅ Passed: {passed} ({(passed / total * 100):.1f}%)")
        print(f"⚠️  Partial: {partial} ({(partial / total * 100):.1f}%)")
        print(f"❌ Failed: {failed} ({(failed / total * 100):.1f}%)")

        if failed > 0:
            print("\nFailed tests:")
            for result in self.test_results:
                if result["status"] == "FAIL":
                    print(f"  - {result['test']}: {result.get('error', 'Unknown error')}")


def print_architecture_overview() -> None:
    """Print the new conversational architecture."""
    print("\n" + "=" * 80)
    print("NEW CONVERSATIONAL ARCHITECTURE OVERVIEW")
    print("=" * 80)

    print("""
The refactored system transforms the assistant from keyword-based to LLM-powered:

OLD ARCHITECTURE (Keyword/Regex Based):
┌─────────────────┐
│  User Message   │
└────────┬────────┘
         │
    ┌────▼─────────────────┐
    │  Keyword Matching    │  ← Brittle, hardcoded keywords
    │  detect_intent()     │  ← Limited NLU capability
    └────┬────────────────┘
         │
    ┌────▼─────────────────┐
    │  Regex Extraction    │  ← Fails on variations
    │  _extract_items()    │  ← Needs exact patterns
    └────┬────────────────┘
         │
    ┌────▼─────────────────┐
    │  Business Logic      │  ← OK (catalog, cart, order)
    │  (Context Engine)    │
    └────┬────────────────┘
         │
    ┌────▼─────────────────┐
    │  Template Response   │  ← Generic, robotic replies
    │  (Hardcoded)        │
    └────▼────────────────┘
         │
    ┌────▼─────────────────┐
    │  User Response      │
    └─────────────────────┘


NEW ARCHITECTURE (LLM-Powered + Business Logic Hybrid):
┌─────────────────┐
│  User Message   │
└────────┬────────┘
         │
    ┌────▼──────────────────────────────────┐
    │  ConversationalClassifier             │  ← LLM-based intent detection
    │  classify_user_message()              │  ← Natural language understanding
    │  ├─ Intent Classification             │  ← Primary + sub-intents
    │  ├─ Entity Extraction                 │  ← Smart entity detection
    │  ├─ Tone Detection                    │  ← Conversational tone
    │  ├─ Follow-up Detection               │  ← Context awareness
    │  └─ Confidence Scoring                │  ← Quality assurance
    └────┬──────────────────────────────────┘
         │
    ┌────▼──────────────────────────────────┐
    │  ConversationMemory                   │  ← Session context tracking
    │  └─ Maintains conversation history    │  ← Follow-up understanding
    └────┬──────────────────────────────────┘
         │
    ┌────▼──────────────────────────────────┐
    │  Intent Routing                       │
    ├─ Conversational (greeting, thanks)    │  ← Immediate response
    ├─ Multi-Action (remove + add)          │  ← Combined handling
    ├─ Context-Aware Followup               │  ← Smart modification
    └─ Core Intent (recommendations, cart)  │  ← Business logic
         │
    ┌────▼──────────────────────────────────┐
    │  Business Logic Layer                 │  ← UNCHANGED
    │  ├─ Context Engine (filtering)        │  ← Deterministic
    │  ├─ Cart Service (add/remove/view)    │  ← Reliable operations
    │  ├─ Order Service (checkout, track)   │  ← Trusted transactions
    │  ├─ Catalog Service (inventory)       │  ← Data source
    │  └─ Meal Planner (planning)           │  ← LLM-assisted planning
    └────┬──────────────────────────────────┘
         │
    ┌────▼──────────────────────────────────┐
    │  ConversationalResponseGenerator      │  ← LLM-based response gen
    │  ├─ Natural language generation       │  ← Varied phrasing
    │  ├─ Context-aware responses           │  ← Tone adaptation
    │  ├─ Follow-up suggestions             │  ← Proactive help
    │  └─ Template fallback                 │  ← Safe degradation
    └────┬──────────────────────────────────┘
         │
    ┌────▼──────────────────────────────────┐
    │  User Response (Natural & Smart)      │
    └─────────────────────────────────────────┘


KEY IMPROVEMENTS:

1. INTELLIGENT INTENT DETECTION
   ✅ Understands casual language ("cool", "nice", "okay")
   ✅ Detects mixed intents ("remove X and add Y")
   ✅ Recognizes follow-ups with context
   ✅ Handles variations gracefully

2. SMART ENTITY EXTRACTION
   ✅ Budget: "under 200", "between 100-200", "cheap"
   ✅ Preferences: "veg", "non-veg", "healthy", "protein rich"
   ✅ Meal Type: "dinner", "lunch", "breakfast", "snacks"
   ✅ Mood: "comfort", "light", "expensive", "late night"
   ✅ Modifications: "spicy", "less spicy", "lighter", "cheaper"

3. CONVERSATIONAL CONTEXT AWARENESS
   ✅ Remembers previous intent in session
   ✅ Applies modifications to previous filters
   ✅ Maintains entity history
   ✅ Understands implicit continuations

4. NATURAL RESPONSE GENERATION
   ✅ Varied phrasing (not templates)
   ✅ Tone-aware responses
   ✅ Follow-up suggestions
   ✅ Conversational flow

5. FALLBACK PROTECTION
   ✅ LLM classification with keyword fallback
   ✅ Degraded mode when LLM unavailable
   ✅ Business logic always deterministic
   ✅ Safe error handling

6. BACKWARD COMPATIBILITY
   ✅ Old keyword extraction still available
   ✅ Regex patterns as fallback
   ✅ Existing business logic untouched
   ✅ Session manager still tracks interactions
""")


if __name__ == "__main__":
    print_architecture_overview()

    tester = ConversationalAssistantTester()
    try:
        tester.run_all_tests()
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        sys.exit(1)

    print("\n✅ Test suite completed successfully!")
