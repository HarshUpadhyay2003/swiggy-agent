"""
Stage 4F.1 Phase 1 — Semantic Evidence Layer.
Collects raw evidence vectors for candidate evaluations without applying weights or percentages.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.services.recommendation_engine.models import RecommendationCandidate, RecommendationRequest
from app.services.recommendation_engine.semantic_profile_resolver import SemanticProfile
from app.services.recommendation_engine.semantic_policy_resolver import SemanticPolicy


class SemanticEvidence(BaseModel):
    """Raw evidence vector extracted for a candidate."""

    candidate_id: int
    candidate_name: str
    domain_match: float = 0.0          # 0.0 to 1.0 raw matching ratio
    category_match: float = 0.0        # 0.0 to 1.0 raw matching ratio
    meal_match: float = 0.0            # 0.0 to 1.0 raw matching ratio
    cuisine_match: float = 0.0         # 0.0 to 1.0 raw matching ratio
    diet_match: float = 1.0            # 1.0 if satisfied, 0.0 if violated
    health_match: float = 1.0          # 0.0 to 1.0 health alignment ratio
    conversation_match: float = 1.0    # 0.0 to 1.0 conversation continuity ratio
    context_match: float = 1.0         # 0.0 to 1.0 occasion/environment ratio
    constraint_coverage: float = 1.0    # Ratio of active request constraints satisfied
    policy_matches: List[str] = Field(default_factory=list)
    policy_violations: List[str] = Field(default_factory=list)
    required_context: List[str] = Field(default_factory=list)
    missing_context: List[str] = Field(default_factory=list)
    forbidden_context: List[str] = Field(default_factory=list)


class SemanticEvaluator:
    """Extracts raw candidate evidence without applying weights or thresholds."""

    def evaluate_evidence(
        self,
        candidate: RecommendationCandidate,
        request: RecommendationRequest,
        policy: SemanticPolicy,
    ) -> SemanticEvidence:
        profile = policy.profile

        name = (candidate.name or "").lower()
        desc = (candidate.description or "").lower()
        p_cat = (candidate.parent_category or "").lower()
        cat = (candidate.category or "").lower()
        cuisine = (candidate.cuisine_type or candidate.cuisine or "").lower()
        meal_t = (candidate.meal_type or "").lower()
        raw = candidate.raw_item if isinstance(candidate.raw_item, dict) else {}
        raw_c = str(raw.get("cuisine_type") or raw.get("cuisine") or "").lower()
        raw_cat = str(raw.get("category") or raw.get("parent_category") or "").lower()

        all_text = f"{name} {desc} {p_cat} {cat} {cuisine} {raw_c} {raw_cat}".lower()

        policy_matches = []
        policy_violations = []
        forbidden_found = []

        # Check forbidden domains
        for f_dom in profile.forbidden_domains:
            if f_dom in p_cat or f_dom in cat or f_dom in name:
                forbidden_found.append(f_dom)
                policy_violations.append(f"Forbidden domain '{f_dom}' found in item attributes")

        # 1. Domain match evidence
        domain_match = 0.0
        if forbidden_found:
            domain_match = 0.10
        elif profile.primary_domains:
            matches_primary = [p for p in profile.primary_domains if p in all_text]
            matches_secondary = [s for s in profile.secondary_domains if s in all_text]

            if matches_primary:
                domain_match = 1.00
                policy_matches.append(f"Primary domain terms matched: {', '.join(matches_primary)}")
            elif matches_secondary and policy.allow_secondary_domain:
                domain_match = 0.75
                policy_matches.append(f"Secondary domain terms matched: {', '.join(matches_secondary)}")
            else:
                domain_match = 0.30
                policy_violations.append("Candidate does not match primary or secondary semantic domains")
        else:
            domain_match = 1.00

        # 2. Category match evidence
        category_match = domain_match

        # 3. Cuisine match evidence
        req_cuisine = request.get_constraint_value("cuisine_type") or request.get_constraint_value("cuisine")
        cuisine_match = 1.00
        if req_cuisine:
            req_c_str = str(req_cuisine).lower()
            if req_c_str in cuisine or req_c_str in raw_c or req_c_str in name or req_c_str in p_cat:
                cuisine_match = 1.00
                policy_matches.append(f"Cuisine '{req_cuisine}' matched")
            else:
                cuisine_match = 0.40
                policy_violations.append(f"Cuisine '{req_cuisine}' not explicitly found")

        # 4. Meal match evidence
        req_meal = request.get_constraint_value("meal_type")
        meal_match = 1.00
        if req_meal:
            req_m_str = str(req_meal).lower()
            if not meal_t or req_m_str in meal_t or "lunch" in meal_t or "dinner" in meal_t or "main" in meal_t or "all-day" in meal_t:
                meal_match = 1.00
                policy_matches.append(f"Meal context '{req_meal}' matched")
            elif req_m_str == "dinner" and ("snack" in p_cat or "desserts" in p_cat or "beverages" in p_cat):
                meal_match = 0.20
                policy_violations.append(f"Item parent category '{candidate.parent_category}' conflicts with requested Dinner meal")
            elif req_m_str == "breakfast" and ("dinner" in meal_t or "heavy" in desc):
                meal_match = 0.30
                policy_violations.append("Heavy dinner item conflicts with requested Breakfast meal")

        # 5. Diet match evidence
        diet_match = 1.00
        req_diet = request.get_constraint_value("diet") or request.get_constraint_value("preference")
        if req_diet:
            req_d_str = str(req_diet).lower()
            if req_d_str in {"veg", "vegetarian"} and not candidate.vegetarian:
                diet_match = 0.00
                policy_violations.append("Non-vegetarian item violates requested Vegetarian constraint")
            else:
                policy_matches.append(f"Dietary constraint '{req_diet}' satisfied")

        # 6. Health match evidence
        health_match = 1.00
        query_text = (request.context.raw_query or "").lower()
        if "healthy" in query_text or request.get_constraint_value("health_goal"):
            if ("burger" in p_cat or "burger" in name or "fries" in name) and not candidate.healthy:
                health_match = 0.15
                policy_violations.append("Fast-food burger/fries is unsuitable for Healthy Meals")
            elif candidate.healthy or candidate.high_protein:
                health_match = 1.00
                policy_matches.append("Item features healthy/high-protein catalog attributes")
            else:
                health_match = 0.50

        # 7. Constraint Coverage
        satisfied_count = 0
        total_constraints = len(request.constraints)
        if total_constraints > 0:
            for c in request.constraints:
                c_val = str(c.value).lower()
                if c.type in {"max_budget", "budget"}:
                    if isinstance(c.value, (int, float)) and candidate.price <= c.value:
                        satisfied_count += 1
                elif c_val in all_text or c_val in meal_t or c_val in cuisine:
                    satisfied_count += 1
                elif c.type in {"preference", "diet"} and candidate.vegetarian:
                    satisfied_count += 1
            constraint_coverage = round(satisfied_count / total_constraints, 2)
        else:
            constraint_coverage = 1.00

        missing_context = []
        if req_meal and meal_match < 0.50:
            missing_context.append(f"Meal context: {req_meal}")

        return SemanticEvidence(
            candidate_id=int(candidate.item_id),
            candidate_name=candidate.name,
            domain_match=round(domain_match, 2),
            category_match=round(category_match, 2),
            meal_match=round(meal_match, 2),
            cuisine_match=round(cuisine_match, 2),
            diet_match=round(diet_match, 2),
            health_match=round(health_match, 2),
            conversation_match=1.00,
            context_match=round(meal_match, 2),
            constraint_coverage=constraint_coverage,
            policy_matches=policy_matches,
            policy_violations=policy_violations,
            required_context=list(profile.required_context.keys()) if hasattr(profile, "required_context") else [],
            missing_context=missing_context,
            forbidden_context=forbidden_found,
        )
