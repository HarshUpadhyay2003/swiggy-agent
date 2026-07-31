"""
Scratch script to perform Phase 0 investigation for Stage 4F.1.
Calculates exact distributions, formulas, metric inconsistencies, and decision boundaries across benchmark queries.
"""

import math
import json
from pathlib import Path
from typing import List, Dict, Any

from app.services.catalog_service import CatalogService
from app.services.recommendation_engine.candidate_retriever import CandidateRetriever
from app.services.recommendation_engine.ranking_engine import RankingEngine
from app.services.recommendation_engine.semantic_recommendation_engine import SemanticRecommendationEngine
from app.services.recommendation_engine.models import RecommendationRequest, Constraint


def run_investigation():
    catalog = CatalogService()
    retriever = CandidateRetriever(catalog)
    ranker = RankingEngine()
    semantic_engine = SemanticRecommendationEngine()

    scenarios = [
        {"name": "Coffee", "query": "Coffee", "constraints": [Constraint(type="category", value="coffee")]},
        {"name": "Desserts", "query": "Desserts", "constraints": [Constraint(type="category", value="dessert")]},
        {"name": "Healthy", "query": "Healthy meals", "constraints": [Constraint(type="health_goal", value="healthy")]},
        {"name": "Italian", "query": "Italian food", "constraints": [Constraint(type="cuisine_type", value="Italian")]},
        {"name": "Pizza", "query": "Pizza", "constraints": [Constraint(type="category", value="pizza")]},
        {"name": "Indian Dinner", "query": "Indian dinner", "constraints": [Constraint(type="cuisine_type", value="Indian"), Constraint(type="meal_type", value="dinner")]},
    ]

    all_evals = []
    scenario_stats = {}

    for sc in scenarios:
        req = RecommendationRequest(constraints=sc["constraints"], top_k=10)
        req.context.raw_query = sc["query"]

        cands, _ = retriever.retrieve_candidates(req)
        ranked = ranker.evaluate_candidates(cands, req)
        accepted, telemetry = semantic_engine.evaluate_and_filter(ranked, req, retriever, ranker)

        # Get full semantic evaluation array for ALL ranked candidates in scenario
        policy = semantic_engine.policy_resolver.resolve_policy(sc["query"].lower(), req.constraints)
        profile = policy.profile

        sc_evals = []
        for ev in ranked:
            cand = ev.candidate
            p_cat = (cand.parent_category or "").lower()
            cat = (cand.category or "").lower()
            cuisine = (cand.cuisine_type or cand.cuisine or "").lower()
            meal_t = (cand.meal_type or "").lower()
            name = (cand.name or "").lower()
            desc = (cand.description or "").lower()
            raw = cand.raw_item if isinstance(cand.raw_item, dict) else {}
            raw_c = str(raw.get("cuisine_type") or raw.get("cuisine") or "").lower()
            raw_cat = str(raw.get("category") or raw.get("parent_category") or "").lower()
            all_cand_text = f"{name} {desc} {p_cat} {cat} {cuisine} {raw_c} {raw_cat}".lower()

            is_forbidden = False
            for f_dom in profile.forbidden_domains:
                if f_dom in p_cat or f_dom in cat or f_dom in name:
                    is_forbidden = True

            domain_match = 0.10 if is_forbidden else (1.00 if any(p in all_cand_text for p in profile.primary_domains) else (0.75 if any(s in all_cand_text for s in profile.secondary_domains) else 0.30))
            category_match = domain_match
            meal_context = 1.00
            req_meal = req.get_constraint_value("meal_type")
            if req_meal:
                req_m_str = str(req_meal).lower()
                if not meal_t or req_m_str in meal_t or "lunch" in meal_t or "dinner" in meal_t or "main" in meal_t or "all-day" in meal_t:
                    meal_context = 1.00
                elif req_m_str == "dinner" and ("snack" in p_cat or "desserts" in p_cat or "beverages" in p_cat):
                    meal_context = 0.20

            suitability_score = 1.00
            if "healthy" in sc["query"].lower() or req.get_constraint_value("health_goal"):
                if ("burger" in p_cat or "burger" in name or "fries" in name) and not cand.healthy:
                    suitability_score = 0.15
                elif cand.healthy or cand.high_protein:
                    suitability_score = 1.00
                else:
                    suitability_score = 0.50

            final_semantic_score = round(
                (domain_match * 0.40) + (category_match * 0.20) + (meal_context * 0.20) + (suitability_score * 0.20),
                2
            )

            is_accepted = any(a.candidate.item_id == cand.item_id for a in accepted)

            item_data = {
                "scenario": sc["name"],
                "query": sc["query"],
                "candidate_name": cand.name,
                "ranking_score": ev.score,
                "semantic_score": final_semantic_score,
                "suitability_score": suitability_score,
                "threshold": policy.semantic_threshold,
                "accepted": is_accepted,
                "reason": ev.ranking_reason if is_accepted else "Rejected: Low semantic suitability",
                "violations": ["Forbidden domain"] if is_forbidden else ([] if is_accepted else ["Below semantic threshold"]),
            }
            sc_evals.append(item_data)
            all_evals.append(item_data)

        # Statistics per scenario
        sem_scores = [e["semantic_score"] for e in sc_evals]
        suit_scores = [e["suitability_score"] for e in sc_evals]
        mean_sem = sum(sem_scores) / len(sem_scores) if sem_scores else 0.0
        median_sem = sorted(sem_scores)[len(sem_scores)//2] if sem_scores else 0.0
        var_sem = sum((x - mean_sem) ** 2 for x in sem_scores) / len(sem_scores) if sem_scores else 0.0
        unique_sem = sorted(list(set(sem_scores)))

        scenario_stats[sc["name"]] = {
            "total_candidates": len(sc_evals),
            "accepted": sum(1 for e in sc_evals if e["accepted"]),
            "rejected": sum(1 for e in sc_evals if not e["accepted"]),
            "mean_semantic": round(mean_sem, 4),
            "median_semantic": round(median_sem, 4),
            "variance_semantic": round(var_sem, 4),
            "stddev_semantic": round(math.sqrt(var_sem), 4),
            "unique_semantic_scores": unique_sem,
            "mean_suitability": round(sum(suit_scores) / len(suit_scores), 4) if suit_scores else 0.0,
            "unique_suitability": sorted(list(set(suit_scores))),
        }

    out_dir = Path("backend/tests/output")
    out_dir.mkdir(parents=True, exist_ok=True)

    with open("backend/scratch_investigation_data.json", "w", encoding="utf-8") as f:
        json.dump({"scenario_stats": scenario_stats, "evaluations": all_evals}, f, indent=2)

    print("SUCCESS: Scratch investigation completed and saved.")

if __name__ == "__main__":
    run_investigation()
