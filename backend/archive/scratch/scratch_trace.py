"""
Backend Investigation — Comprehensive Trace Script for Recommendation Pipeline.
DO NOT MODIFY ANY PROJECT SOURCE CODE. THIS IS A READ-ONLY AUDIT.

Tracing:
1. "meals under 300"
2. "Italian meals under 500"
"""

import os
import sys
import json
from typing import Dict, Any, List

# Ensure app imports work
sys.path.insert(0, os.path.abspath("."))

from app.services.chat_orchestrator import ChatOrchestrator
from app.services.context_engine import ContextEngine
from app.services.recommendation_engine.candidate_retriever import CandidateRetriever
from app.services.recommendation_engine.strategy_chain import StrategyChain
from app.services.recommendation_engine.ranking_engine import RankingEngine
from app.services.recommendation_engine.diversity_reranker import DiversityReranker
from app.services.conversational_response_generator import ConversationalResponseGenerator
from app.services.catalog.catalog_service import CatalogService
from app.services.catalog.catalog_adapter import CatalogAdapter
from app.services.recommendation_engine.models import RecommendationRequest, RecommendationContext, Constraint


def trace_prompt(orchestrator: ChatOrchestrator, prompt: str, session_id: str):
    print("\n" + "=" * 80)
    print(f"AUDIT TRACE FOR PROMPT: '{prompt}' (Session ID: {session_id})")
    print("=" * 80)

    # Clear session first to ensure clean state
    orchestrator.session_manager.clear_session(session_id)
    session_state = orchestrator.session_manager.create_session(session_id)
    rec_mem = session_state.recommendation_memory
    prev_memory = rec_mem.to_dict()

    user_context = {"session_id": session_id, "user_id": "audit_user"}

    # 1. Intent Detection
    classification = orchestrator.classifier.classify_user_message(prompt, {"active_domain": "general"})
    llm_intent = classification.get("intent")
    
    # 2. Extract Recommendation Context
    extracted_context = orchestrator._extract_recommendation_context(prompt, user_context, session_state)
    updated_memory = rec_mem.to_dict()

    print("\n--- 1. EXTRACTED CONSTRAINTS ---")
    fields = ["query_type", "meal_type", "max_budget", "budget", "diet", "preference", "taste_preference", "category", "cuisine_type", "restaurant_id", "health_goal", "serving"]
    for f in fields:
        print(f"  {f:20s}: {extracted_context.get(f)}")

    print("\n--- 2. RECOMMENDATION MEMORY ---")
    print(f"  Previous: {prev_memory}")
    print(f"  Updated : {updated_memory}")

    # 3. Step-by-Step Filter Tracing in CandidateRetriever
    print("\n--- 3 & 4 & 5. CANDIDATE RETRIEVAL FILTER BREAKDOWN ---")
    catalog_service = orchestrator.catalog_service
    retriever = CandidateRetriever(catalog_service=catalog_service)
    raw_items = catalog_service.get_available_items()
    all_candidates = [retriever._map_to_candidate(raw) for raw in raw_items]

    print(f"Initial Candidates Count: {len(all_candidates)}")
    current_candidates = list(all_candidates)

    # Let's inspect step-by-step filters in the exact order retriever applies them
    req = orchestrator.context_engine._build_recommendation_request(extracted_context)
    
    # Filter 1: Query Type
    qtype_val = req.get_constraint_value("query_type")
    c_after_qtype = [c for c in current_candidates if retriever._filter_query_type(c, qtype_val)]
    rejected_qtype = [c for c in current_candidates if c not in c_after_qtype]
    print(f"\n[Filter 1: query_type = '{qtype_val}'] -> Remaining: {len(c_after_qtype)}")
    for r in rejected_qtype:
        print(f"  REJECTED: '{r.name}' (parent_cat: '{r.parent_category}', meal_type: '{r.meal_type}') by query_type")
    current_candidates = c_after_qtype

    # Filter 2: Category / Item Category
    cat_val = req.get_constraint_value("category") or req.get_constraint_value("item_category")
    c_after_cat = [c for c in current_candidates if retriever._filter_item_category(c, cat_val)]
    rejected_cat = [c for c in current_candidates if c not in c_after_cat]
    print(f"\n[Filter 2: category = '{cat_val}'] -> Remaining: {len(c_after_cat)}")
    for r in rejected_cat:
        print(f"  REJECTED: '{r.name}' (parent_cat: '{r.parent_category}', category: '{r.category}') by category")
    current_candidates = c_after_cat

    # Filter 3: Cuisine
    cuisine_val = req.get_constraint_value("cuisine_type") or req.get_constraint_value("cuisine")
    c_after_cuisine = [c for c in current_candidates if retriever._filter_cuisine(c, cuisine_val)]
    rejected_cuisine = [c for c in current_candidates if c not in c_after_cuisine]
    print(f"\n[Filter 3: cuisine = '{cuisine_val}'] -> Remaining: {len(c_after_cuisine)}")
    for r in rejected_cuisine:
        print(f"  REJECTED: '{r.name}' (cuisine: '{r.cuisine}', cuisine_type: '{r.cuisine_type}', rest: '{r.restaurant_name}') by cuisine")
    current_candidates = c_after_cuisine

    # Filter 4: Meal Type
    meal_val = req.get_constraint_value("meal_type")
    c_after_meal = [c for c in current_candidates if retriever._filter_meal_type(c, meal_val)]
    rejected_meal = [c for c in current_candidates if c not in c_after_meal]
    print(f"\n[Filter 4: meal_type = '{meal_val}'] -> Remaining: {len(c_after_meal)}")
    for r in rejected_meal:
        print(f"  REJECTED: '{r.name}' (meal_type: '{r.meal_type}') by meal_type")
    current_candidates = c_after_meal

    # Filter 5: Diet
    diet_val = req.get_constraint_value("diet") or req.get_constraint_value("preference")
    c_after_diet = [c for c in current_candidates if retriever._filter_diet(c, diet_val)]
    rejected_diet = [c for c in current_candidates if c not in c_after_diet]
    print(f"\n[Filter 5: diet = '{diet_val}'] -> Remaining: {len(c_after_diet)}")
    for r in rejected_diet:
        print(f"  REJECTED: '{r.name}' (veg: {r.vegetarian}) by diet")
    current_candidates = c_after_diet

    # Filter 6: Taste
    taste_val = req.get_constraint_value("taste_preference") or req.get_constraint_value("taste")
    c_after_taste = [c for c in current_candidates if retriever._filter_taste(c, taste_val)]
    rejected_taste = [c for c in current_candidates if c not in c_after_taste]
    print(f"\n[Filter 6: taste = '{taste_val}'] -> Remaining: {len(c_after_taste)}")
    for r in rejected_taste:
        print(f"  REJECTED: '{r.name}' (taste: '{r.taste_preference}') by taste")
    current_candidates = c_after_taste

    # Filter 7: Budget
    budget_val = req.get_constraint_value("max_budget") or req.get_constraint_value("budget")
    c_after_budget = [c for c in current_candidates if retriever._filter_max_budget(c, budget_val)]
    rejected_budget = [c for c in current_candidates if c not in c_after_budget]
    print(f"\n[Filter 7: max_budget = '{budget_val}'] -> Remaining: {len(c_after_budget)}")
    for r in rejected_budget:
        print(f"  REJECTED: '{r.name}' (price: ₹{r.price}) by max_budget")
    current_candidates = c_after_budget

    print("\n--- EXACT SURVIVING CANDIDATES AFTER RETRIEVAL ---")
    for idx, c in enumerate(current_candidates, 1):
        print(f"  {idx}. '{c.name}' | Price: ₹{c.price} | Cuisine: '{c.cuisine_type}' | MealType: '{c.meal_type}' | ParentCat: '{c.parent_category}'")

    # 4. Strategy Chain Execution
    print("\n--- STRATEGY CHAIN EXECUTION ---")
    chain_candidates, counts_debug = orchestrator.context_engine.recommendation_engine.strategy_chain.execute_chain(retriever, req)
    print(f"Candidates returned by Strategy Chain: {len(chain_candidates)}")
    for idx, c in enumerate(chain_candidates, 1):
        print(f"  {idx}. '{c.name}' | Price: ₹{c.price}")

    # 5. Ranking Engine Breakdown
    print("\n--- 6. RANKING ENGINE COMPONENT SCORING ---")
    ranker = orchestrator.context_engine.recommendation_engine.ranker
    scored_pairs = ranker.score_candidates(chain_candidates, req)

    for cand, score_obj in scored_pairs:
        print(f"\nCandidate: '{cand.name}' (Price: ₹{cand.price}, Rest: '{cand.restaurant_name}')")
        print(f"  TOTAL SCORE: {score_obj.total_score}")
        for comp in score_obj.component_scores:
            print(f"    - {comp.component:20s}: {comp.score:6.2f} ({comp.reason})")

    # 6. Diversity Reranker
    print("\n--- DIVERSITY RERANKER EXECUTION ---")
    reranker = orchestrator.context_engine.recommendation_engine.diversity_reranker
    reranked_pairs = reranker.rerank(scored_pairs, req)
    print(f"Candidates after Diversity Reranker: {len(reranked_pairs)}")
    for idx, (c, s) in enumerate(reranked_pairs, 1):
        print(f"  {idx}. '{c.name}' | Final Rerank Score: {s.total_score}")

    # 7. ContextEngine Output & Conversational Response Generator Tracing
    print("\n--- 7 & 8. CONTEXT ENGINE & RESPONSE GENERATOR TRACING ---")
    result_recommend_food = orchestrator.context_engine.recommend_food(extracted_context)
    recs_data = result_recommend_food.get("recommendations", [])
    print(f"ContextEngine.recommend_food returned recommendations count: {len(recs_data)}")
    for idx, r in enumerate(recs_data, 1):
        print(f"  {idx}. {r.get('item_name')} | ₹{r.get('price')} | Cuisine: '{r.get('cuisine_type')}' | ParentCat: '{r.get('parent_category')}'")

    print(f"ContextEngine.recommend_food Reasoning String: \"{result_recommend_food.get('reasoning')}\"")

    full_orchestrator_result = orchestrator.handle_message(prompt, user_context)
    print(f"\nOrchestrator handle_message Intent: {full_orchestrator_result.get('intent')}")
    print(f"Orchestrator handle_message Data Recommendations Count: {len(full_orchestrator_result.get('data', {}).get('recommendations', []))}")
    print(f"Orchestrator Response Output String: \"{full_orchestrator_result.get('response')}\"")


def dataset_audit(catalog_service: CatalogService):
    print("\n" + "=" * 80)
    print("9. DATASET VERIFICATION & METADATA AUDIT")
    print("=" * 80)
    raw_items = catalog_service.get_available_items()
    print(f"Total Items in Available Catalog: {len(raw_items)}")

    # Audit categories, cuisines, meal_types, parent_categories
    by_query_type = {}
    by_parent_category = {}
    by_cuisine = {}
    by_meal_type = {}

    missing_metadata_items = []

    for item in raw_items:
        name = item.get("name", "Unknown")
        item_id = item.get("item_id")
        price = item.get("price")
        cuisine = item.get("cuisine_type") or item.get("cuisine")
        meal_type = item.get("meal_type")
        cat_intel = item.get("category_intelligence", {}) if isinstance(item.get("category_intelligence"), dict) else {}
        parent_cat = item.get("parent_category") or cat_intel.get("parent_category")

        # Check for missing/inconsistent fields
        issues = []
        if not cuisine:
            issues.append("Missing cuisine")
        if not meal_type:
            issues.append("Missing meal_type")
        if not parent_cat:
            issues.append("Missing parent_category")

        if issues:
            missing_metadata_items.append({"item_id": item_id, "name": name, "issues": issues})

        by_parent_category[parent_cat] = by_parent_category.get(parent_cat, 0) + 1
        by_cuisine[cuisine] = by_cuisine.get(cuisine, 0) + 1
        by_meal_type[meal_type] = by_meal_type.get(meal_type, 0) + 1

    print("\n--- Breakdown by Parent Category ---")
    for k, v in by_parent_category.items():
        print(f"  {str(k):30s}: {v}")

    print("\n--- Breakdown by Cuisine ---")
    for k, v in by_cuisine.items():
        print(f"  {str(k):30s}: {v}")

    print("\n--- Breakdown by Meal Type ---")
    for k, v in by_meal_type.items():
        print(f"  {str(k):30s}: {v}")

    print(f"\nItems with missing/inconsistent metadata: {len(missing_metadata_items)}")
    for item in missing_metadata_items[:15]:
        print(f"  ID {item['item_id']:3d} | {item['name']:35s} | Issues: {item['issues']}")


if __name__ == "__main__":
    orchestrator = ChatOrchestrator()
    dataset_audit(orchestrator.catalog_service)

    trace_prompt(orchestrator, "meals under 300", "audit-session-1")
    trace_prompt(orchestrator, "Italian meals under 500", "audit-session-2")
