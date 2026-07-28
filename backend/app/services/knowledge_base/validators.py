"""Validators for Knowledge Base dataset referential integrity & schema constraints."""

from typing import Any, Dict, List, Set


class KnowledgeBaseValidationError(Exception):
    """Exception raised when Knowledge Base dataset validation fails."""

    def __init__(self, errors: List[str]) -> None:
        self.errors = errors
        message = f"Knowledge Base Validation Failed with {len(errors)} error(s):\n" + "\n".join(
            f"  - {err}" for err in errors
        )
        super().__init__(message)


class KnowledgeBaseValidator:
    """Validates Knowledge Base entities and referential integrity."""

    REQUIRED_RESTAURANT_FIELDS = {
        "restaurant_id",
        "restaurant_code",
        "name",
        "primary_cuisine",
        "operating_hours",
        "confidence",
    }

    REQUIRED_ITEM_FIELDS = {
        "item_id",
        "restaurant_id",
        "restaurant_code",
        "item_code",
        "name",
        "category_intelligence",
        "nutrition",
        "dietary_safety",
        "health_scores",
        "ingredients",
        "commerce_intelligence",
        "confidence",
        "source_metadata",
        "data_quality",
        "search_aliases",
    }

    REQUIRED_COMBO_FIELDS = {
        "combo_id",
        "combo_code",
        "restaurant_id",
        "restaurant_code",
        "combo_name",
        "item_ids",
        "price",
        "confidence",
    }

    def validate_all(
        self,
        restaurants: List[Dict[str, Any]],
        menu_items: List[Dict[str, Any]],
        combos: List[Dict[str, Any]],
        categories: List[Dict[str, Any]],
    ) -> None:
        """Perform complete integrity audit across all loaded entities."""
        errors: List[str] = []

        # 1. Missing Required Fields
        self._validate_required_fields(restaurants, self.REQUIRED_RESTAURANT_FIELDS, "Restaurant", errors)
        self._validate_required_fields(menu_items, self.REQUIRED_ITEM_FIELDS, "MenuItem", errors)
        self._validate_required_fields(combos, self.REQUIRED_COMBO_FIELDS, "Combo", errors)

        # 2. Key Sets for Foreign Key validation
        restaurant_ids: Set[int] = set()
        restaurant_codes: Set[str] = set()
        for r in restaurants:
            rid = r.get("restaurant_id")
            rcode = r.get("restaurant_code")
            if rid is not None:
                if rid in restaurant_ids:
                    errors.append(f"Duplicate restaurant_id: {rid}")
                restaurant_ids.add(rid)
            if rcode:
                if rcode in restaurant_codes:
                    errors.append(f"Duplicate restaurant_code: '{rcode}'")
                restaurant_codes.add(rcode)

        item_ids: Set[int] = set()
        item_codes: Set[str] = set()
        for item in menu_items:
            iid = item.get("item_id")
            icode = item.get("item_code")
            if iid is not None:
                if iid in item_ids:
                    errors.append(f"Duplicate item_id: {iid}")
                item_ids.add(iid)
            if icode:
                if icode in item_codes:
                    errors.append(f"Duplicate item_code: '{icode}'")
                item_codes.add(icode)

        combo_ids: Set[int] = set()
        combo_codes: Set[str] = set()
        for cb in combos:
            cid = cb.get("combo_id")
            ccode = cb.get("combo_code")
            if cid is not None:
                if cid in combo_ids:
                    errors.append(f"Duplicate combo_id: {cid}")
                combo_ids.add(cid)
            if ccode:
                if ccode in combo_codes:
                    errors.append(f"Duplicate combo_code: '{ccode}'")
                combo_codes.add(ccode)

        category_ids: Set[str] = {c.get("category_id") for c in categories if c.get("category_id")}

        # 3. Referential Integrity Checks
        for item in menu_items:
            item_name = item.get("name", "Unknown Item")

            # Restaurant FK check
            rid = item.get("restaurant_id")
            if rid not in restaurant_ids:
                errors.append(f"Item '{item_name}' references non-existent restaurant_id {rid}")

            # Category FK check
            cat_intel = item.get("category_intelligence", {})
            cid = cat_intel.get("category_id") if isinstance(cat_intel, dict) else None
            if cid not in category_ids:
                errors.append(f"Item '{item_name}' references non-existent category_id '{cid}'")

            # Side/Beverage/Dessert FK checks
            comm = item.get("commerce_intelligence", {})
            if isinstance(comm, dict):
                for key in ["best_side_item_ids", "best_beverage_item_ids", "best_dessert_item_ids"]:
                    for ref_id in comm.get(key, []):
                        if ref_id not in item_ids:
                            errors.append(f"Item '{item_name}' {key} references non-existent item_id {ref_id}")

        for cb in combos:
            cname = cb.get("combo_name", "Unknown Combo")
            rid = cb.get("restaurant_id")
            if rid not in restaurant_ids:
                errors.append(f"Combo '{cname}' references non-existent restaurant_id {rid}")

            for ref_id in cb.get("item_ids", []):
                if ref_id not in item_ids:
                    errors.append(f"Combo '{cname}' references non-existent item_id {ref_id}")

        # 4. Duplicate Alias Checks
        seen_aliases: Set[str] = set()
        for item in menu_items:
            for alias in item.get("search_aliases", []):
                normalized_alias = str(alias).strip().lower()
                if normalized_alias in seen_aliases:
                    # Log duplicate alias warning or error if critical
                    pass
                seen_aliases.add(normalized_alias)

        if errors:
            raise KnowledgeBaseValidationError(errors)

    def _validate_required_fields(
        self,
        entities: List[Dict[str, Any]],
        required_fields: Set[str],
        entity_name: str,
        errors: List[str],
    ) -> None:
        """Verify every dictionary contains all mandatory keys."""
        for idx, entity in enumerate(entities):
            name = entity.get("name") or entity.get("combo_name") or f"Index {idx}"
            missing = required_fields - set(entity.keys())
            if missing:
                errors.append(f"{entity_name} '{name}' missing required field(s): {', '.join(sorted(missing))}")
