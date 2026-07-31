"""
Layer 3 — Schema Field Matcher
Translates extracted logical constraints into a FieldMatchPlan using schema_mapping.py.
Performs field mapping ONLY. Never filters dataset, scores, or ranks candidates.
"""

from typing import Dict, Any, List
from app.services.recommendation_engine.models import RecommendationRequest, FieldMatchPlan
from app.services.recommendation_engine.schema_mapping import FIELD_MAPPING


class SchemaFieldMatcher:
    """Layer 3: Maps RecommendationRequest logical constraints to target dataset fields."""

    def build_field_match_plan(self, request: RecommendationRequest) -> FieldMatchPlan:
        """Translates RecommendationRequest constraints into a FieldMatchPlan."""
        plan_mappings: Dict[str, List[str]] = {}
        active_constraints: Dict[str, Any] = {}

        for c in request.constraints:
            if c.is_hard and c.value is not None:
                c_type = str(c.type).lower()
                target_fields = FIELD_MAPPING.get(c_type, [c_type])
                plan_mappings[c_type] = target_fields
                active_constraints[c_type] = c.value

        status = "EXECUTED" if plan_mappings else "SKIPPED (No Active Constraints)"
        print("\n========================================")
        print("LAYER 3: Schema Field Matcher")
        print(f"Status: {status}")
        print("FieldMatchPlan:")
        for c_key, target_cols in plan_mappings.items():
            print(f"  {c_key:18s} -> {target_cols}")
        print("========================================\n")

        return FieldMatchPlan(
            field_mappings=plan_mappings,
            active_constraints=active_constraints,
        )
