"""Candidate Retriever applying generalized polymorphic constraint filters."""

from typing import Any, Callable, Dict, List, Tuple
from app.services.catalog_service import CatalogService
from app.services.recommendation_engine.models import (
    Constraint,
    RecommendationCandidate,
    RecommendationRequest,
)


class CandidateRetriever:
    """Retrieves menu items & combos and filters candidates by evaluating constraints polymorphically."""

    def __init__(self, catalog_service: CatalogService) -> None:
        self.catalog_service = catalog_service
        self._handlers: Dict[str, Callable[[RecommendationCandidate, Any], bool]] = {
            "budget": self._filter_budget,
            "max_budget": self._filter_max_budget,
            "min_budget": self._filter_min_budget,
            "preference": self._filter_diet,
            "diet": self._filter_diet,
            "meal_type": self._filter_meal_type,
            "health_goal": self._filter_health_goal,
            "healthy_only": self._filter_health_goal,
            "healthy": self._filter_health_goal,
            "restaurant_id": self._filter_restaurant_id,
            "spicy": self._filter_spicy,
            "vegan": self._filter_vegan,
            "gluten_free": self._filter_gluten_free,
            "high_protein": self._filter_high_protein,
            "cuisine": self._filter_cuisine,
            "cuisine_type": self._filter_cuisine,
            "taste": self._filter_taste,
            "taste_preference": self._filter_taste,
            "category": self._filter_item_category,
            "item_category": self._filter_item_category,
            "is_combo": self._filter_is_combo,
            "serving": self._filter_serving,
            "query_type": self._filter_query_type,
        }

    def retrieve_candidates(
        self, request: RecommendationRequest
    ) -> Tuple[List[RecommendationCandidate], Dict[str, int]]:
        """
        Fetch available catalog menu items and combo bundles, iterate through constraints in exact order:
        Query Type -> Category -> Cuisine -> Meal Type -> Diet -> Taste -> Budget -> Health Goal -> Serving -> Ranking.
        Return candidates alongside per-stage candidate count telemetry.
        """
        raw_items = self.catalog_service.get_available_items()
        raw_combos = self.catalog_service.get_available_combos()

        candidates_input = [self._map_to_candidate(raw) for raw in raw_items]
        candidates_input.extend([self._map_combo_to_candidate(combo) for combo in raw_combos])

        # Stage 3.1 Component 3 — Candidate Integrity Pass
        all_restaurants = {r.get("restaurant_id") for r in self.catalog_service.get_all_restaurants()}
        seen_item_ids = set()
        clean_candidates = []
        dups_count = 0
        unavail_count = 0
        incomplete_count = 0
        broken_ref_count = 0

        for c in candidates_input:
            if c.item_id in seen_item_ids:
                dups_count += 1
                continue
            seen_item_ids.add(c.item_id)

            if not c.available:
                unavail_count += 1
                continue

            if not (c.item_id and c.name and c.price and c.parent_category):
                incomplete_count += 1
                continue

            if c.restaurant_id and c.restaurant_id not in all_restaurants:
                broken_ref_count += 1
                continue

            clean_candidates.append(c)

        print("\n========================================")
        print("CANDIDATE INTEGRITY")
        print(f"Initial           : {len(candidates_input)}")
        print(f"Duplicates        : {dups_count}")
        print(f"Unavailable       : {unavail_count}")
        print(f"Broken References : {broken_ref_count}")
        print(f"Incomplete        : {incomplete_count}")
        print(f"Final             : {len(clean_candidates)}")
        print("========================================\n")

        candidates = clean_candidates
        counts_debug: Dict[str, int] = {"initial_candidates": len(candidates)}

        # Define explicit Stage 2B deterministic filter pipeline order
        pipeline_stages = [
            ("Available", ["available"]),
            ("Query Type", ["query_type"]),
            ("Parent Category", ["category", "item_category"]),
            ("Cuisine Type", ["cuisine", "cuisine_type"]),
            ("Diet", ["diet", "preference", "vegan", "gluten_free", "vegetarian"]),
            ("Meal Type", ["meal_type"]),
            ("Budget", ["budget", "max_budget", "min_budget"]),
            ("Taste Preference", ["taste", "taste_preference", "spicy"]),
            ("Restaurant", ["restaurant_id"]),
            ("Health Constraints", ["health_goal", "healthy_only", "healthy", "high_protein", "low_calorie"]),
        ]

        # Map active request constraints by type
        request_constraints_map: Dict[str, List[Constraint]] = {}
        for c in request.constraints:
            if c.is_hard:
                request_constraints_map.setdefault(c.type, []).append(c)

        print("\n========================================")
        print("LAYER 4: Candidate Retriever")
        print("Status: EXECUTED")
        print("Candidate Pool:")
        print(f"Initial Dataset : {len(candidates)}")

        for stage_name, constraint_types in pipeline_stages:
            stage_filtered = candidates
            has_applied = False
            for c_type in constraint_types:
                if c_type in request_constraints_map:
                    for constraint in request_constraints_map[c_type]:
                        handler = self._handlers.get(constraint.type)
                        if handler:
                            prev_count = len(stage_filtered)
                            # Handle SYSTEM_DEFAULT constraints dynamically (do not eliminate candidates if 0 remain)
                            test_filtered = [c for c in stage_filtered if handler(c, constraint.value)]
                            rejected_cands = [c for c in stage_filtered if c not in test_filtered]
                            rejected_sample = [f"{c.item_id}:{c.name}" for c in rejected_cands[:3]]
                            rej_str = ", ".join(rejected_sample) + ("..." if len(rejected_cands) > 3 else "") if rejected_cands else "None"
                            reason = f"{constraint.type} != {constraint.value}"

                            if getattr(constraint, "source", None) == "SYSTEM_DEFAULT" and not test_filtered and prev_count > 0:
                                print(f"{stage_name:18s} Filter | Input: {prev_count} | Output: {prev_count} | Rejected: 0 | Reason: Bypassed SYSTEM_DEFAULT")
                            else:
                                stage_filtered = test_filtered
                                has_applied = True
                                src_label = getattr(constraint, "source", "USER")
                                if hasattr(src_label, "value"):
                                    src_label = src_label.value
                                print(f"{stage_name:18s} Filter | Constraint: {constraint.type}={constraint.value} | Source: {src_label} | Input: {prev_count} | Output: {len(stage_filtered)} | Rejected ({len(rejected_cands)}): [{rej_str}] | Reason: {reason}")

            if has_applied:
                candidates = stage_filtered
            counts_debug[stage_name] = len(candidates)

        counts_debug["ranking_input"] = len(candidates)
        print("->")
        print(f"Final Candidate Pool : {len(candidates)}")
        print("========================================\n")

        return candidates, counts_debug
    def _map_to_candidate(self, raw: Dict[str, Any]) -> RecommendationCandidate:
        """Map catalog item dictionary to RecommendationCandidate model."""
        cat_intel = raw.get("category_intelligence", {}) if isinstance(raw.get("category_intelligence"), dict) else {}
        parent_cat = str(cat_intel.get("parent_category", "")) if cat_intel else ""

        if not parent_cat:
            m_type = str(raw.get("meal_type", "")).lower()
            if m_type == "dessert":
                parent_cat = "Desserts"
            elif m_type in ["beverage", "beverages"]:
                parent_cat = "Beverages"
            else:
                name_desc = f"{raw.get('name', '')} {raw.get('description', '')}".lower()
                if any(k in name_desc for k in ["ice cream", "cone", "mcflurry", "lava cake", "brownie", "cake", "sweet", "dessert"]):
                    parent_cat = "Desserts"
                elif any(k in name_desc for k in ["coffee", "latte", "cappuccino", "tea", "shake", "smoothie", "drink", "beverage", "pepsi", "coke"]):
                    parent_cat = "Beverages"
                elif any(k in name_desc for k in ["burger", "mcaloo", "mcveggie", "mcchicken"]):
                    parent_cat = "Burgers"
                elif any(k in name_desc for k in ["pizza", "pizzas"]):
                    parent_cat = "Pizzas"
                else:
                    parent_cat = "Meals"

        return RecommendationCandidate(
            item_id=int(raw.get("item_id", 0)),
            name=str(raw.get("name", "")),
            description=str(raw.get("description", "")),
            price=int(raw.get("price", 0)),
            available=bool(raw.get("available", True)),
            category=str(raw.get("category", "")).lower(),
            meal_type=str(raw.get("meal_type", "")).lower(),
            healthy=bool(raw.get("healthy", False)),
            vegetarian=bool(raw.get("vegetarian", True)),
            high_protein=bool(raw.get("high_protein", False)),
            spicy=bool(raw.get("spicy", False)),
            vegan=bool(raw.get("vegan", False)),
            low_calorie=bool(raw.get("low_calorie", False)),
            gluten_free=bool(raw.get("gluten_free", False)),
            restaurant_id=raw.get("restaurant_id"),
            restaurant_name=str(raw.get("restaurant_name", "")),
            cuisine=str(raw.get("cuisine", "")),
            cuisine_type=str(raw.get("cuisine_type", raw.get("cuisine", ""))),
            taste_preference=str(raw.get("taste_preference", "")),
            parent_category=parent_cat,
            is_combo=False,
            raw_item=raw,
        )

    def _map_combo_to_candidate(self, raw: Dict[str, Any]) -> RecommendationCandidate:
        """Map combo dictionary to RecommendationCandidate model."""
        return RecommendationCandidate(
            item_id=int(raw.get("combo_id", 0)),
            name=str(raw.get("name", "")),
            description=str(raw.get("description", "")),
            price=int(raw.get("price", 0)),
            available=bool(raw.get("available", True)),
            category=str(raw.get("category", "")).lower(),
            meal_type="lunch",
            healthy=False,
            vegetarian=raw.get("category") == "veg",
            restaurant_id=raw.get("restaurant_id"),
            restaurant_name=str(raw.get("restaurant_name", "")),
            cuisine=str(raw.get("cuisine", "")),
            cuisine_type=str(raw.get("cuisine", "")),
            parent_category="Combos",
            is_combo=True,
            combo_id=raw.get("combo_id"),
            savings_amount=raw.get("savings_amount", 0),
            raw_item=raw,
        )

    # Constraint Handlers
    def _filter_budget(self, c: RecommendationCandidate, val: Any) -> bool:
        if isinstance(val, (int, float)):
            return c.price <= val
        if isinstance(val, (list, tuple)) and len(val) == 2:
            return val[0] <= c.price <= val[1]
        return True

    def _filter_max_budget(self, c: RecommendationCandidate, val: Any) -> bool:
        return c.price <= val if isinstance(val, (int, float)) else True

    def _filter_min_budget(self, c: RecommendationCandidate, val: Any) -> bool:
        return c.price >= val if isinstance(val, (int, float)) else True

    def _filter_diet(self, c: RecommendationCandidate, val: Any) -> bool:
        if not val:
            return True
        norm_val = str(val).strip().lower()
        if norm_val in {"nonveg", "non-veg", "non veg"}:
            return not c.vegetarian
        if norm_val in {"veg", "vegetarian"}:
            return c.vegetarian
        return True

    def _filter_meal_type(self, c: RecommendationCandidate, val: Any) -> bool:
        if not val:
            return True
        norm_val = str(val).strip().lower()
        avail_meals = [str(x).lower() for x in c.raw_item.get("available_meal_types", [])]
        return c.meal_type == norm_val or norm_val in avail_meals

    def _filter_health_goal(self, c: RecommendationCandidate, val: Any) -> bool:
        if not val:
            return True
        norm_val = str(val).strip().lower()
        if norm_val == "high_protein":
            return c.high_protein or (c.raw_item.get("nutrition", {}).get("macronutrients", {}).get("protein_g", 0) >= 15)
        if norm_val == "low_calorie":
            return c.low_calorie or (c.raw_item.get("nutrition", {}).get("macronutrients", {}).get("calories_kcal", 999) <= 400)
        return c.healthy or c.high_protein or c.low_calorie

    def _filter_cuisine(self, c: RecommendationCandidate, val: Any) -> bool:
        if not val:
            return True
        norm_val = str(val).strip().lower()
        sec_cuisines = [str(x).lower() for x in c.raw_item.get("secondary_cuisines", [])]
        raw_c = str(c.raw_item.get("restaurant_cuisine") or c.raw_item.get("cuisine") or "").lower()
        cuisine_text = f"{c.cuisine} {c.cuisine_type} {c.restaurant_name} {raw_c} {c.name}".lower()

        if norm_val == "indian":
            indian_terms = ["indian", "north indian", "south indian", "rajputana", "rajasthani", "awadhi", "hyderabadi", "punjabi", "biryani", "thali", "paneer", "masala", "curry", "naan", "dal", "butter chicken", "tikka", "dosa", "idli", "mahal", "palace", "shahi", "royal", "rambagh", "laal maas", "makhan murgh", "korma", "kebabs", "dhaba"]
            return any(k in cuisine_text for k in indian_terms) or any(any(k in x for k in indian_terms) for x in sec_cuisines)
        if norm_val in {"chinese", "asian", "pan-asian"}:
            asian_terms = ["chinese", "asian", "pan-asian", "indochinese", "momos", "noodle", "dim sum", "fried rice", "manchurian", "schezwan", "teriyaki", "stir fry"]
            return any(k in cuisine_text for k in asian_terms) or any(any(k in x for k in asian_terms) for x in sec_cuisines)
        return norm_val in cuisine_text or any(norm_val in x for x in sec_cuisines)


    def _filter_taste(self, c: RecommendationCandidate, val: Any) -> bool:
        if not val:
            return True
        norm_val = str(val).strip().lower()
        item_text = f"{c.taste_preference} {c.name} {c.description}".lower()
        return norm_val in item_text or (norm_val == "spicy" and c.spicy)

    def _filter_item_category(self, c: RecommendationCandidate, val: Any) -> bool:
        if not val:
            return True
        norm_val = str(val).strip().lower()

        # Beverage matching
        if norm_val in {"beverage", "beverages", "drink", "drinks", "coffee", "tea", "juice", "smoothie", "shake", "cold drink"}:
            if c.parent_category.lower() in {"beverages", "coffee", "mccafe"}:
                return True
            return any(k in f"{c.name} {c.description} {c.meal_type}".lower() for k in ["pepsi", "coke", "cappuccino", "coffee", "tea", "beverage", "shake", "smoothie", "juice", "drink"])

        # Dessert matching
        if norm_val in {"dessert", "desserts", "sweet", "sweets", "ice cream", "icecream", "brownie", "cake"}:
            if c.parent_category.lower() in {"desserts", "sweets"}:
                return True
            return any(k in f"{c.name} {c.description} {c.meal_type}".lower() for k in ["dessert", "mcflurry", "lava cake", "ice cream", "cake", "sweet", "pastry", "brownie", "churma"])

        # Combo matching
        if norm_val in {"combo", "combos", "meal deal", "family combo", "kids combo"}:
            return c.is_combo or "combo" in f"{c.name} {c.description}".lower()

        # Burger, Pizza, Rice, Noodle, Wrap, Meal
        item_text = f"{c.name} {c.parent_category} {c.description}".lower()
        return norm_val in item_text

    def _filter_is_combo(self, c: RecommendationCandidate, val: Any) -> bool:
        return c.is_combo if bool(val) else True

    def _filter_serving(self, c: RecommendationCandidate, val: Any) -> bool:
        if not val:
            return True
        norm_val = str(val).strip().lower()
        item_text = f"{c.name} {c.description}".lower()
        if norm_val in {"family", "party"}:
            return c.is_combo or any(k in item_text for k in ["family", "bucket", "bundle", "box", "party", "large"])
        if norm_val == "kids":
            return any(k in item_text for k in ["kids", "small", "mini", "regular"])
        return True

    def _filter_restaurant_id(self, c: RecommendationCandidate, val: Any) -> bool:
        return c.restaurant_id == val

    def _filter_spicy(self, c: RecommendationCandidate, val: Any) -> bool:
        return c.spicy == bool(val)

    def _filter_vegan(self, c: RecommendationCandidate, val: Any) -> bool:
        return c.vegan if bool(val) else True

    def _filter_gluten_free(self, c: RecommendationCandidate, val: Any) -> bool:
        return c.gluten_free if bool(val) else True

    def _filter_high_protein(self, c: RecommendationCandidate, val: Any) -> bool:
        return c.high_protein if bool(val) else True

    def _filter_query_type(self, c: RecommendationCandidate, val: Any) -> bool:
        if not val:
            return True
        norm_val = str(val).strip().lower()
        if norm_val == "beverage":
            return c.parent_category.lower() in {"beverages", "coffee", "mccafe"} or any(k in f"{c.name} {c.description}".lower() for k in ["pepsi", "coke", "cappuccino", "coffee", "tea", "drink", "shake", "juice"])
        elif norm_val == "dessert":
            return c.parent_category.lower() in {"desserts", "sweets"} or any(k in f"{c.name} {c.description}".lower() for k in ["dessert", "mcflurry", "lava cake", "ice cream", "cake", "sweet", "pastry", "brownie"])
        elif norm_val == "combo":
            return c.is_combo or "combo" in f"{c.name} {c.description}".lower()
        elif norm_val == "meal":
            return not (c.parent_category.lower() in {"beverages", "desserts"} and not c.is_combo)
        return True
