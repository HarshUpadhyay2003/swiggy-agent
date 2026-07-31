"""
Layer 6 — Recommendation Validator
Validates CandidateEvaluation list against request hard constraints (query_type, category, cuisine_type, diet, meal_type, max_budget).
Outputs structured ValidationResult and LAYER 6 telemetry. Never reranks, retrieves, or silently substitutes candidates.
"""

from typing import List, Tuple, Optional
from app.services.recommendation_engine.models import CandidateEvaluation, RecommendationRequest, ValidationResult


class RecommendationValidator:
    """Layer 6: Validates ranked CandidateEvaluation objects against request hard constraints."""

    def validate_evaluations(
        self,
        evaluations: List[CandidateEvaluation],
        request: RecommendationRequest,
    ) -> Tuple[List[CandidateEvaluation], ValidationResult]:
        """
        Validates CandidateEvaluation list against hard constraints.
        Returns: (validated_evaluations, ValidationResult)
        """
        query_type = request.get_constraint_value("query_type")
        category = request.get_constraint_value("category") or request.get_constraint_value("item_category")
        cuisine = request.get_constraint_value("cuisine_type") or request.get_constraint_value("cuisine")
        diet = request.get_constraint_value("diet") or request.get_constraint_value("preference")
        meal_type = request.get_constraint_value("meal_type")
        max_budget = request.get_constraint_value("max_budget") or request.get_constraint_value("budget")

        protected: List[str] = []
        relaxable: List[str] = []

        if query_type:
            protected.append(f"query_type={query_type}")
        if cuisine:
            protected.append(f"cuisine={cuisine}")
        if meal_type:
            protected.append(f"meal_type={meal_type}")
        if diet:
            protected.append(f"diet={diet}")
        if max_budget:
            relaxable.append(f"max_budget={max_budget}")

        if not evaluations:
            val_res = ValidationResult(
                is_valid=False,
                primary_failure="retrieval_empty",
                protected_constraints=protected,
                relaxable_constraints=relaxable,
                candidates_before_failure=0,
                candidates_after_failure=0,
                failure_reason="No candidates available for validation.",
            )
            print("\n========================================")
            print("LAYER 6: Recommendation Validator")
            print("Validation: FAIL (No candidates retrieved)")
            print("========================================\n")
            return [], val_res

        validated_evals: List[CandidateEvaluation] = []
        primary_fail: Optional[str] = None
        fail_reason: str = ""
        rejection_breakdown: Dict[str, int] = {}
        rejected_names_by_reason: Dict[str, List[str]] = {}

        for ev in evaluations:
            cand = ev.candidate
            # 1. Validate query_type
            if query_type:
                q_lower = str(query_type).lower()
                c_parent = str(cand.parent_category or "").lower()
                c_meal = str(cand.meal_type or "").lower()
                if q_lower == "beverage" and c_parent != "beverages" and c_meal != "beverages":
                    ev.validation_status = "FAIL"
                    primary_fail = primary_fail or "query_type"
                    rejection_breakdown["QueryType"] = rejection_breakdown.get("QueryType", 0) + 1
                    rejected_names_by_reason.setdefault("QueryType", []).append(cand.name)
                    continue
                elif q_lower == "dessert" and c_parent != "desserts" and c_meal != "dessert":
                    ev.validation_status = "FAIL"
                    primary_fail = primary_fail or "query_type"
                    rejection_breakdown["QueryType"] = rejection_breakdown.get("QueryType", 0) + 1
                    rejected_names_by_reason.setdefault("QueryType", []).append(cand.name)
                    continue

            # 2. Validate explicit category
            if category:
                cat_lower = str(category).lower()
                if cat_lower not in ["meal", "meals", "food"]:
                    item_text = f"{cand.name} {cand.parent_category} {cand.description}".lower()
                    if cat_lower not in item_text:
                        ev.validation_status = "FAIL"
                        primary_fail = primary_fail or "category"
                        rejection_breakdown["Category"] = rejection_breakdown.get("Category", 0) + 1
                        rejected_names_by_reason.setdefault("Category", []).append(cand.name)
                        continue

            # 3. Validate explicit cuisine
            if cuisine:
                cuis_lower = str(cuisine).lower()
                c_cuis = str(cand.cuisine_type or cand.cuisine or "").lower()
                if cuis_lower not in c_cuis and c_cuis not in cuis_lower:
                    ev.validation_status = "FAIL"
                    primary_fail = primary_fail or "cuisine"
                    rejection_breakdown["Cuisine"] = rejection_breakdown.get("Cuisine", 0) + 1
                    rejected_names_by_reason.setdefault("Cuisine", []).append(cand.name)
                    continue

            # 4. Validate diet
            if diet:
                diet_lower = str(diet).lower()
                if diet_lower in ["veg", "vegetarian"] and not cand.vegetarian:
                    ev.validation_status = "FAIL"
                    primary_fail = primary_fail or "diet"
                    rejection_breakdown["Diet"] = rejection_breakdown.get("Diet", 0) + 1
                    rejected_names_by_reason.setdefault("Diet", []).append(cand.name)
                    continue
                elif diet_lower in ["non-veg", "nonveg"] and cand.vegetarian:
                    ev.validation_status = "FAIL"
                    primary_fail = primary_fail or "diet"
                    rejection_breakdown["Diet"] = rejection_breakdown.get("Diet", 0) + 1
                    rejected_names_by_reason.setdefault("Diet", []).append(cand.name)
                    continue

            # 5. Validate max budget
            if max_budget is not None and isinstance(max_budget, (int, float)):
                if cand.price > float(max_budget):
                    ev.validation_status = "FAIL"
                    primary_fail = primary_fail or "max_budget"
                    rejection_breakdown["Budget"] = rejection_breakdown.get("Budget", 0) + 1
                    rejected_names_by_reason.setdefault("Budget", []).append(cand.name)
                    continue

            ev.validation_status = "PASS"
            validated_evals.append(ev)

        status_flag = "PASS" if validated_evals else "FAIL"
        if not validated_evals:
            fail_reason = f"Constraint '{primary_fail}' eliminated all candidates."

        val_res = ValidationResult(
            is_valid=bool(validated_evals),
            primary_failure=primary_fail,
            protected_constraints=protected,
            relaxable_constraints=relaxable,
            candidates_before_failure=len(evaluations),
            candidates_after_failure=len(validated_evals),
            failure_reason=fail_reason or "All candidates satisfied requested constraints.",
            rejection_breakdown=rejection_breakdown,
            rejected_candidates_by_reason=rejected_names_by_reason,
        )

        print("\n========================================")
        print("LAYER 6: Recommendation Validator")
        print("Status: EXECUTED")
        print(f"Validation Decision: {status_flag}")
        print(f"Protected Constraints: {protected}")
        print(f"Relaxable Constraints: {relaxable}")
        print("Rejections:")
        if rejection_breakdown:
            for k, count in rejection_breakdown.items():
                rej_names = rejected_names_by_reason.get(k, [])
                sample_names = ", ".join(rej_names[:3]) + ("..." if len(rej_names) > 3 else "")
                print(f"  Rejected ({k}): {count} items [{sample_names}]")
        else:
            print("  None")
        print(f"Fallback Strategy  : {'None (Exact Match)' if status_flag == 'PASS' else 'Relaxation Strategy Chain'}")
        print(f"Remaining Candidates: {len(validated_evals)} items")
        print(f"Reason             : {val_res.failure_reason}")
        print("========================================\n")

        return validated_evals, val_res
