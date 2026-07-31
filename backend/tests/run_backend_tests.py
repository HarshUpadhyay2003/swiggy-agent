"""Standard unittest test runner for Stage 1A, Stage 1B, Stage 2A, Stage 2B, Stage 2C, and Checkout Regression test suites."""

import sys
import unittest
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parents[1]
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Stage 1A Imports
from app.services.knowledge_base.json_loader import KnowledgeBaseJSONLoader, KnowledgeBaseLoadError
from app.services.knowledge_base.validators import KnowledgeBaseValidator, KnowledgeBaseValidationError
from app.services.knowledge_base.indexes import KnowledgeBaseIndexes
from app.services.knowledge_base.knowledge_base_service import KnowledgeBaseService

# Stage 1B Imports
from app.services.catalog.catalog_adapter import CatalogAdapter
from app.services.catalog_service import CatalogService
from app.services.context_engine import ContextEngine
from app.services.planner import MealPlanner
from app.services.cart_service import CartService
from app.services.order_service import OrderService

# Stage 2A & 2B Imports
from app.services.recommendation_engine import (
    CandidateRetriever,
    Constraint,
    DecisionReasonBuilder,
    RankingEngine,
    ReasonBuilder,
    RecommendationCandidate,
    RecommendationContext,
    RecommendationEngine,
    RecommendationReason,
    RecommendationRequest,
    RecommendationResult,
    RecommendationScore,
    RecommendationStrategyChain,
)

# Checkout Regression Import
from tests.test_checkout_regression import TestCheckoutRegression


# STAGE 1A TEST SUITES
class TestJSONLoader(unittest.TestCase):
    def test_load_real_knowledge_base(self):
        loader = KnowledgeBaseJSONLoader()
        restaurants = loader.load_restaurants()
        menu_items = loader.load_menu_items()
        combos = loader.load_combos()
        categories = loader.load_category_registry()

        self.assertIsInstance(restaurants, list)
        self.assertGreaterEqual(len(restaurants), 6)
        self.assertIsInstance(menu_items, list)
        self.assertGreaterEqual(len(menu_items), 35)

    def test_missing_file_raises_error(self):
        loader = KnowledgeBaseJSONLoader(base_dir="non_existent_directory_xyz")
        with self.assertRaises(KnowledgeBaseLoadError):
            loader.load_restaurants()


class TestValidator(unittest.TestCase):
    def test_validator_passes_on_real_data(self):
        loader = KnowledgeBaseJSONLoader()
        restaurants = loader.load_restaurants()
        menu_items = loader.load_menu_items()
        combos = loader.load_combos()
        categories = loader.load_category_registry()

        validator = KnowledgeBaseValidator()
        validator.validate_all(restaurants, menu_items, combos, categories)

    def test_duplicate_restaurant_id_fails(self):
        validator = KnowledgeBaseValidator()
        restaurants = [
            {"restaurant_id": 1, "restaurant_code": "MCD", "name": "McD", "primary_cuisine": "Fast Food", "operating_hours": {}, "confidence": {}},
            {"restaurant_id": 1, "restaurant_code": "MCD2", "name": "McD2", "primary_cuisine": "Fast Food", "operating_hours": {}, "confidence": {}},
        ]
        with self.assertRaises(KnowledgeBaseValidationError):
            validator.validate_all(restaurants, [], [], [])


class TestIndexes(unittest.TestCase):
    def test_indexing_and_o1_lookup(self):
        indexes = KnowledgeBaseIndexes()
        restaurants = [{"restaurant_id": 1, "restaurant_code": "MCD", "name": "McDonald's"}]
        categories = [{"category_id": "CAT_BURGERS_VEG", "display_name": "Vegetarian Burgers"}]
        menu_items = [{
            "item_id": 101,
            "restaurant_id": 1,
            "item_code": "MCD_BURGER_001",
            "name": "McAloo Tikki",
            "category_intelligence": {"category_id": "CAT_BURGERS_VEG"},
            "search_aliases": ["mcaloo", "aloo tikki"]
        }]
        combos = [{"combo_id": 2001, "combo_code": "KFC_COMBO_001", "combo_name": "Zinger Box"}]

        indexes.build_indexes(restaurants, menu_items, combos, categories)

        self.assertEqual(indexes.restaurant_by_id.get(1)["name"], "McDonald's")
        self.assertEqual(indexes.item_by_id.get(101)["name"], "McAloo Tikki")
        self.assertEqual(len(indexes.alias_index.get("mcaloo")), 1)


class TestKnowledgeBaseService(unittest.TestCase):
    def test_service_initialization_and_queries(self):
        service = KnowledgeBaseService()
        stats = service.get_statistics()
        self.assertTrue(stats["is_loaded"])
        self.assertGreaterEqual(stats["total_restaurants"], 6)
        self.assertGreaterEqual(stats["total_menu_items"], 35)

        mcd = service.get_restaurant(1)
        self.assertIsNotNone(mcd)
        self.assertEqual(mcd["name"], "McDonald's")

        item_101 = service.get_item(101)
        self.assertIsNotNone(item_101)

        fries_matches = service.search_alias("fries")
        self.assertGreaterEqual(len(fries_matches), 1)


# STAGE 1B TEST SUITES
class TestCatalogAdapter(unittest.TestCase):
    def test_to_legacy_item_mapping(self):
        kb_item = {
            "item_id": 101,
            "name": "McAloo Tikki Burger",
            "description": "Golden fried potato patty",
            "meal_type": "LUNCH",
            "available": True,
            "dietary_safety": {"is_veg": True, "is_vegan": False, "is_gluten_free": False},
            "health_scores": {"overall_health_score": 7.5},
            "nutrition": {"macronutrients": {"protein_g": 8.5, "calories_kcal": 339.5}},
            "mood_sensory": {"spicy": False},
            "commerce_intelligence": {"price": 65},
            "restaurant_id": 1,
        }
        restaurant = {"restaurant_id": 1, "name": "McDonald's", "primary_cuisine": "Fast Food"}

        legacy_item = CatalogAdapter.to_legacy_item(kb_item, restaurant)
        self.assertEqual(legacy_item["item_id"], 101)
        self.assertEqual(legacy_item["name"], "McAloo Tikki Burger")
        self.assertEqual(legacy_item["price"], 65)
        self.assertEqual(legacy_item["category"], "veg")
        self.assertEqual(legacy_item["restaurant_name"], "McDonald's")

    def test_to_legacy_restaurant_mapping(self):
        kb_restaurant = {"restaurant_id": 1, "name": "McDonald's", "primary_cuisine": "Fast Food", "rating": 4.5, "delivery_time_mins": 25}
        legacy_rest = CatalogAdapter.to_legacy_restaurant(kb_restaurant, [])
        self.assertEqual(legacy_rest["delivery_time"], 25)


class TestCatalogServiceMigrated(unittest.TestCase):
    def setUp(self):
        self.service = CatalogService()

    def test_get_all_restaurants(self):
        restaurants = self.service.get_all_restaurants()
        self.assertGreaterEqual(len(restaurants), 6)

    def test_get_available_items(self):
        items = self.service.get_available_items()
        self.assertGreaterEqual(len(items), 35)

    def test_get_item_by_id(self):
        item = self.service.get_item_by_id(101)
        self.assertEqual(item["name"], "McAloo Tikki Burger")

    def test_search_items(self):
        results = self.service.search_items("burger")
        self.assertGreaterEqual(len(results), 1)


class TestBackwardCompatibilityIntegration(unittest.TestCase):
    def setUp(self):
        self.catalog_service = CatalogService()
        self.context_engine = ContextEngine(self.catalog_service)
        self.meal_planner = MealPlanner(self.catalog_service)
        self.cart_service = CartService(self.catalog_service)
        self.order_service = OrderService(self.catalog_service)

    def test_context_engine_recommendations(self):
        res = self.context_engine.recommend_food({"preference": "veg", "max_budget": 300})
        self.assertGreater(len(res["recommendations"]), 0)

    def test_cart_service_add_and_totals(self):
        item = self.catalog_service.get_item_by_id(101)
        cart = self.cart_service.add_to_cart("session_1b", item, quantity=2)
        self.assertGreater(cart["total"], 0)

    def test_order_service_place_order(self):
        order = self.order_service.place_order([101, 201])
        self.assertEqual(len(order["items"]), 2)
        self.assertGreater(order["estimated_delivery_time"], 0)


# STAGE 2A & 2B TEST SUITES
class TestStage2BRecommendationEngine(unittest.TestCase):
    def setUp(self):
        self.catalog = CatalogService()
        self.engine = RecommendationEngine(self.catalog)

    def test_scenario_healthy_lunch_under_300(self):
        req = RecommendationRequest(
            constraints=[
                Constraint(type="preference", value="non-veg"),
                Constraint(type="meal_type", value="lunch"),
                Constraint(type="max_budget", value=300),
                Constraint(type="healthy_only", value=True),
            ],
            top_k=3,
        )
        results = self.engine.generate_recommendations(req)
        self.assertGreater(len(results), 0)
        for res in results:
            self.assertEqual(res.candidate.category, "non-veg")
            self.assertEqual(res.candidate.meal_type, "lunch")
            self.assertLessEqual(res.candidate.price, 300)
            self.assertTrue(res.candidate.healthy or res.candidate.high_protein or res.candidate.low_calorie)

    def test_scenario_debug_telemetry(self):
        req = RecommendationRequest(
            constraints=[
                Constraint(type="preference", value="veg"),
                Constraint(type="max_budget", value=200),
            ],
            context=RecommendationContext(debug_mode=True),
        )
        results = self.engine.generate_recommendations(req)
        self.assertGreater(len(results), 0)
        first_res = results[0]
        self.assertIsNotNone(first_res.debug)
        self.assertEqual(first_res.debug.strategy, "explicit_constraints")

    def test_context_engine_migration(self):
        ce = ContextEngine(self.catalog)
        res = ce.recommend_food({"preference": "veg", "max_budget": 300, "debug_mode": True})
        self.assertIn("recommendations", res)
        self.assertGreater(len(res["recommendations"]), 0)
        self.assertIn("debug", res["recommendations"][0])


class TestStage33SemanticAssertions(unittest.TestCase):
    """Stage 3.3 Semantic Harness Tests (Tests A through F)."""

    def setUp(self):
        from app.services.chat_orchestrator import ChatOrchestrator
        self.orchestrator = ChatOrchestrator()
        self.catalog = CatalogService()
        self.engine = RecommendationEngine(self.catalog)

    def test_a_pure_extraction_healthy_meals(self):
        """Test A: 'Healthy meals' should extract query_type=meal & health_goal=healthy, meal_type=None (no late night pollution)."""
        ctx = self.orchestrator._extract_recommendation_context("Healthy meals", {"session_id": "test_sess_a"})
        self.assertNotIn("meal_type", ctx)
        self.assertEqual(ctx.get("health_goal"), "healthy")
        self.assertEqual(ctx.get("query_type"), "meal")

    def test_b_ephemeral_category_expiration(self):
        """Test B: 'Suggest burgers' -> 'Coffee' -> Burger removed, Coffee active."""
        sess = self.orchestrator.session_manager.create_session("test_sess_b")
        req1 = RecommendationRequest(constraints=[Constraint(type="category", value="burgers")])
        eff1 = self.orchestrator.session_manager.sessions["test_sess_b"].recommendation_memory
        lifecycle = self.orchestrator.session_manager.sessions["test_sess_b"]
        
        # Turn 1: burgers
        eff_req1 = self.orchestrator.session_manager.sessions["test_sess_b"]
        from app.services.session_manager import ConstraintLifecycleEngine
        engine = ConstraintLifecycleEngine()
        res1 = engine.process_lifecycle(req1, sess.recommendation_memory, current_turn=1)
        self.assertEqual(sess.recommendation_memory.category, "burgers")

        # Turn 2: coffee (category change clears previous category and cuisine)
        req2 = RecommendationRequest(constraints=[Constraint(type="category", value="beverages")])
        res2 = engine.process_lifecycle(req2, sess.recommendation_memory, current_turn=2)
        self.assertEqual(sess.recommendation_memory.category, "beverages")
        self.assertIsNone(sess.recommendation_memory.cuisine_type)

    def test_c_multi_turn_constraint_accumulation(self):
        """Test C: Indian -> Budget 300 -> Spicy => all three constraints active."""
        sess = self.orchestrator.session_manager.create_session("test_sess_c")
        from app.services.session_manager import ConstraintLifecycleEngine
        engine = ConstraintLifecycleEngine()

        # Turn 1: Indian
        req1 = RecommendationRequest(constraints=[Constraint(type="cuisine_type", value="Indian")])
        eff1 = engine.process_lifecycle(req1, sess.recommendation_memory, current_turn=1)

        # Turn 2: Budget 300
        req2 = RecommendationRequest(constraints=[Constraint(type="max_budget", value=300)])
        eff2 = engine.process_lifecycle(req2, sess.recommendation_memory, current_turn=2)

        # Turn 3: Spicy
        req3 = RecommendationRequest(constraints=[Constraint(type="taste_preference", value="spicy")])
        eff3 = engine.process_lifecycle(req3, sess.recommendation_memory, current_turn=3)

        active_types = {c.type for c in eff3.constraints}
        self.assertIn("cuisine_type", active_types)
        self.assertIn("max_budget", active_types)
        self.assertIn("taste_preference", active_types)

    def test_d_candidate_integrity_and_dataset_match(self):
        """Test D: Candidate retriever candidates match expected dataset candidate pool."""
        req = RecommendationRequest(constraints=[Constraint(type="cuisine_type", value="Indian")])
        cands, debug = self.engine.retriever.retrieve_candidates(req)
        self.assertGreater(len(cands), 0)
        valid_ids = {i.get("id") or i.get("item_id") for i in self.catalog.get_available_items()}
        valid_ids.update({c.get("id") or c.get("combo_id") or c.get("item_id") for c in self.catalog.get_available_combos()})
        for c in cands:
            self.assertIn(c.item_id, valid_ids)

    def test_e_score_ordering(self):
        """Test E: Layer 5 CandidateEvaluations are computed with score breakdowns and positive total scores."""
        req = RecommendationRequest(constraints=[Constraint(type="max_budget", value=500)], top_k=10)
        cands, _ = self.engine.retriever.retrieve_candidates(req)
        evals = self.engine.ranker.evaluate_candidates(cands, req)
        self.assertGreater(len(evals), 1)
        for ev in evals:
            self.assertGreater(ev.score, 0)
            self.assertGreater(len(ev.score_breakdown), 0)

    def test_f_validator_protected_constraints(self):
        """Test F: Validator verifies every returned candidate satisfies protected hard constraints."""
        req = RecommendationRequest(constraints=[
            Constraint(type="preference", value="veg"),
            Constraint(type="max_budget", value=250),
        ])
        results = self.engine.generate_recommendations(req)
        self.assertGreater(len(results), 0)
        for r in results:
            self.assertTrue(r.candidate.vegetarian)
            self.assertLessEqual(r.candidate.price, 250)


if __name__ == "__main__":
    unittest.main(verbosity=2)
