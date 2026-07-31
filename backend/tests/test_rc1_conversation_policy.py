"""
RC1 Conversation Policy & Context Lifecycle Unit Test Suite.
Verifies Objectives 1-9:
- Separation of Recommendation Context from User Preference
- Transition Classification (NEW_SEARCH, REFINEMENT, DOMAIN_SWITCH, RECOVERY, CLARIFICATION)
- Automatic Recommendation Context Reset on NEW_SEARCH
- Recommendation Context Retention on REFINEMENT
"""

import sys
import unittest
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parents[1]
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.services.session_manager import RecommendationContextMemory, SessionState, ConstraintLifecycleEngine
from app.services.recommendation_engine.conversation_intelligence.refinement_detector import RefinementDetector, TransitionType
from app.services.recommendation_engine.conversation_intelligence.conversation_reset_detector import ConversationResetDetector
from app.services.recommendation_engine.conversation_intelligence.conversation_intelligence import ConversationIntelligenceEngine
from app.services.recommendation_engine.models import Constraint, RecommendationRequest, RecommendationContext
from app.services.recommendation_engine.candidate_retriever import CandidateRetriever
from app.services.catalog_service import CatalogService


class TestRC1ConversationPolicy(unittest.TestCase):

    def setUp(self):
        self.catalog_service = CatalogService()
        self.retriever = CandidateRetriever(self.catalog_service)
        self.lifecycle_engine = ConstraintLifecycleEngine()
        self.intelligence_engine = ConversationIntelligenceEngine()
        self.session_memory = RecommendationContextMemory()

    def test_objective1_context_vs_user_preference(self):
        """Verify Recommendation Context and User Preference separation."""
        mem = RecommendationContextMemory(
            cuisine_type="Italian",
            budget=100.0,
            category="dessert",
            diet="veg"
        )
        removed = mem.clear_recommendation_context()
        self.assertIn("cuisine_type=Italian", removed)
        self.assertIn("budget=100.0", removed)
        self.assertIn("category=dessert", removed)
        # Recommendation context fields cleared
        self.assertIsNone(mem.cuisine_type)
        self.assertIsNone(mem.budget)
        self.assertIsNone(mem.category)

    def test_scenario1_dessert_under_100_then_italian_meals(self):
        """Scenario 1: 'Dessert under 100' -> 'Italian meals' (Budget cleared)."""
        # Turn 1: Dessert under 100
        req1 = RecommendationRequest(constraints=[
            Constraint(type="category", value="dessert"),
            Constraint(type="max_budget", value=100.0)
        ])
        self.lifecycle_engine.process_lifecycle(req1, self.session_memory)
        self.assertEqual(self.session_memory.budget, 100.0)
        self.assertEqual(self.session_memory.category, "dessert")

        # Turn 2: Italian meals (NEW_SEARCH)
        req2 = RecommendationRequest(constraints=[
            Constraint(type="cuisine_type", value="Italian")
        ])
        eff2_req, _, telemetry = self.intelligence_engine.process(
            raw_query="Italian meals",
            request=req2,
            session_memory=self.session_memory,
            candidate_retriever=self.retriever
        )
        self.assertEqual(telemetry.transition_type, TransitionType.NEW_SEARCH.value)
        
        eff2 = self.lifecycle_engine.process_lifecycle(eff2_req, self.session_memory)
        self.assertIsNone(self.session_memory.budget)
        self.assertEqual(self.session_memory.cuisine_type, "Italian")
        
        eff_types = [c.type for c in eff2.constraints]
        self.assertIn("cuisine_type", eff_types)
        self.assertNotIn("max_budget", eff_types)
        self.assertNotIn("budget", eff_types)

    def test_scenario2_healthy_meals_then_under_300(self):
        """Scenario 2: 'Healthy meals' -> 'under 300' (Healthy retained, budget 300 added)."""
        # Turn 1: Healthy meals
        req1 = RecommendationRequest(constraints=[
            Constraint(type="health_goal", value="healthy")
        ])
        self.lifecycle_engine.process_lifecycle(req1, self.session_memory)
        
        # Turn 2: under 300 (REFINEMENT)
        req2 = RecommendationRequest(constraints=[
            Constraint(type="max_budget", value=300.0)
        ])
        eff2_req, _, telemetry = self.intelligence_engine.process(
            raw_query="under 300",
            request=req2,
            session_memory=self.session_memory,
            candidate_retriever=self.retriever
        )
        self.assertEqual(telemetry.transition_type, TransitionType.REFINEMENT.value)
        eff2 = self.lifecycle_engine.process_lifecycle(eff2_req, self.session_memory)
        eff_map = {c.type: c.value for c in eff2.constraints}
        self.assertEqual(eff_map.get("health_goal"), "healthy")
        self.assertEqual(eff_map.get("max_budget"), 300.0)

    def test_scenario3_indian_meals_then_make_it_spicy(self):
        """Scenario 3: 'Indian meals' -> 'make it spicy' (Cuisine retained, taste spicy added)."""
        # Turn 1: Indian meals
        req1 = RecommendationRequest(constraints=[
            Constraint(type="cuisine_type", value="Indian")
        ])
        self.lifecycle_engine.process_lifecycle(req1, self.session_memory)
        
        # Turn 2: make it spicy (REFINEMENT)
        req2 = RecommendationRequest(constraints=[
            Constraint(type="taste_preference", value="spicy")
        ])
        eff2_req, _, telemetry = self.intelligence_engine.process(
            raw_query="make it spicy",
            request=req2,
            session_memory=self.session_memory,
            candidate_retriever=self.retriever
        )
        self.assertEqual(telemetry.transition_type, TransitionType.REFINEMENT.value)
        eff2 = self.lifecycle_engine.process_lifecycle(eff2_req, self.session_memory)
        eff_map = {c.type: c.value for c in eff2.constraints}
        self.assertEqual(eff_map.get("cuisine_type"), "Indian")
        self.assertEqual(eff_map.get("taste_preference"), "spicy")

    def test_scenario4_never_mind_then_coffee(self):
        """Scenario 4: 'Never mind' -> 'Coffee' (Fresh beverage search)."""
        # Turn 1: Dessert under 100
        req1 = RecommendationRequest(constraints=[
            Constraint(type="category", value="dessert"),
            Constraint(type="max_budget", value=100.0)
        ])
        self.lifecycle_engine.process_lifecycle(req1, self.session_memory)
        
        # Turn 2: Never mind (Reset trigger phrase)
        req2 = RecommendationRequest(constraints=[])
        eff2_req, _, telemetry2 = self.intelligence_engine.process(
            raw_query="Never mind",
            request=req2,
            session_memory=self.session_memory,
            candidate_retriever=self.retriever
        )
        self.assertEqual(telemetry2.transition_type, TransitionType.NEW_SEARCH.value)
        self.lifecycle_engine.process_lifecycle(eff2_req, self.session_memory)
        self.assertIsNone(self.session_memory.budget)
        
        # Turn 3: Coffee
        req3 = RecommendationRequest(constraints=[
            Constraint(type="category", value="coffee")
        ])
        eff3_req, _, telemetry3 = self.intelligence_engine.process(
            raw_query="Coffee",
            request=req3,
            session_memory=self.session_memory,
            candidate_retriever=self.retriever
        )
        eff3 = self.lifecycle_engine.process_lifecycle(eff3_req, self.session_memory)
        eff_map = {c.type: c.value for c in eff3.constraints}
        self.assertEqual(eff_map.get("category"), "coffee")
        self.assertNotIn("max_budget", eff_map)

    def test_scenario5_recommend_dinner(self):
        """Scenario 5: 'Recommend dinner' (General dinner recommendations without stale constraints)."""
        # Set stale budget/cuisine in memory
        self.session_memory.budget = 100.0
        self.session_memory.cuisine_type = "Italian"

        req = RecommendationRequest(constraints=[
            Constraint(type="meal_type", value="dinner")
        ])
        eff_req, _, telemetry = self.intelligence_engine.process(
            raw_query="Recommend dinner",
            request=req,
            session_memory=self.session_memory,
            candidate_retriever=self.retriever
        )
        self.assertEqual(telemetry.transition_type, TransitionType.NEW_SEARCH.value)
        eff = self.lifecycle_engine.process_lifecycle(eff_req, self.session_memory)
        self.assertIsNone(self.session_memory.budget)
        self.assertIsNone(self.session_memory.cuisine_type)
        eff_map = {c.type: c.value for c in eff.constraints}
        self.assertEqual(eff_map.get("meal_type"), "dinner")

    def test_scenario6_italian_meals_then_desserts(self):
        """Scenario 6: 'Italian meals' -> 'Desserts' (Cuisine removed, Dessert context active)."""
        # Turn 1: Italian meals
        req1 = RecommendationRequest(constraints=[
            Constraint(type="cuisine_type", value="Italian")
        ])
        self.lifecycle_engine.process_lifecycle(req1, self.session_memory)
        
        # Turn 2: Desserts (NEW_SEARCH / Category switch)
        req2 = RecommendationRequest(constraints=[
            Constraint(type="category", value="dessert")
        ])
        eff2_req, _, telemetry = self.intelligence_engine.process(
            raw_query="Desserts",
            request=req2,
            session_memory=self.session_memory,
            candidate_retriever=self.retriever
        )
        self.assertEqual(telemetry.transition_type, TransitionType.NEW_SEARCH.value)
        eff2 = self.lifecycle_engine.process_lifecycle(eff2_req, self.session_memory)
        self.assertIsNone(self.session_memory.cuisine_type)
        self.assertEqual(self.session_memory.category, "dessert")

    def test_scenario7_pizza_then_coffee(self):
        """Scenario 7: 'Pizza' -> 'Coffee' (Pizza context removed, Coffee context active)."""
        # Turn 1: Pizza
        req1 = RecommendationRequest(constraints=[
            Constraint(type="category", value="pizza")
        ])
        self.lifecycle_engine.process_lifecycle(req1, self.session_memory)
        
        # Turn 2: Coffee
        req2 = RecommendationRequest(constraints=[
            Constraint(type="category", value="coffee")
        ])
        eff2_req, _, telemetry = self.intelligence_engine.process(
            raw_query="Coffee",
            request=req2,
            session_memory=self.session_memory,
            candidate_retriever=self.retriever
        )
        self.assertEqual(telemetry.transition_type, TransitionType.NEW_SEARCH.value)
        eff2 = self.lifecycle_engine.process_lifecycle(eff2_req, self.session_memory)
        self.assertEqual(self.session_memory.category, "coffee")

    def test_scenario8_coffee_then_under_200(self):
        """Scenario 8: 'Coffee' -> 'under 200' (Budget refinement, Coffee retained)."""
        # Turn 1: Coffee
        req1 = RecommendationRequest(constraints=[
            Constraint(type="category", value="coffee")
        ])
        self.lifecycle_engine.process_lifecycle(req1, self.session_memory)
        
        # Turn 2: under 200
        req2 = RecommendationRequest(constraints=[
            Constraint(type="max_budget", value=200.0)
        ])
        eff2_req, _, telemetry = self.intelligence_engine.process(
            raw_query="under 200",
            request=req2,
            session_memory=self.session_memory,
            candidate_retriever=self.retriever
        )
        self.assertEqual(telemetry.transition_type, TransitionType.REFINEMENT.value)
        eff2 = self.lifecycle_engine.process_lifecycle(eff2_req, self.session_memory)
        eff_map = {c.type: c.value for c in eff2.constraints}
        self.assertEqual(eff_map.get("category"), "coffee")
        self.assertEqual(eff_map.get("max_budget"), 200.0)


if __name__ == "__main__":
    unittest.main()
