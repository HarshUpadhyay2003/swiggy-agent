"""In-memory indexing engine for O(1) Knowledge Base lookups."""

from typing import Any, Dict, List, Optional


class KnowledgeBaseIndexes:
    """Builds and manages O(1) fast lookup indexes for Knowledge Base entities."""

    def __init__(self) -> None:
        self.restaurant_by_id: Dict[int, Dict[str, Any]] = {}
        self.restaurant_by_code: Dict[str, Dict[str, Any]] = {}
        self.item_by_id: Dict[int, Dict[str, Any]] = {}
        self.item_by_code: Dict[str, Dict[str, Any]] = {}
        self.combo_by_id: Dict[int, Dict[str, Any]] = {}
        self.category_by_id: Dict[str, Dict[str, Any]] = {}
        self.restaurant_to_items: Dict[int, List[Dict[str, Any]]] = {}
        self.category_to_items: Dict[str, List[Dict[str, Any]]] = {}
        self.alias_index: Dict[str, List[Dict[str, Any]]] = {}

    def build_indexes(
        self,
        restaurants: List[Dict[str, Any]],
        menu_items: List[Dict[str, Any]],
        combos: List[Dict[str, Any]],
        categories: List[Dict[str, Any]],
    ) -> None:
        """Build all in-memory indexes from loaded entity arrays."""
        self.clear()

        # 1. Restaurants Index
        for r in restaurants:
            rid = r.get("restaurant_id")
            rcode = r.get("restaurant_code")
            if rid is not None:
                self.restaurant_by_id[rid] = r
                self.restaurant_to_items[rid] = []
            if rcode:
                self.restaurant_by_code[str(rcode).upper()] = r

        # 2. Categories Index
        for c in categories:
            cid = c.get("category_id")
            if cid:
                self.category_by_id[str(cid).upper()] = c
                self.category_to_items[str(cid).upper()] = []

        # 3. Menu Items & Aliases Index
        for item in menu_items:
            iid = item.get("item_id")
            icode = item.get("item_code")
            rid = item.get("restaurant_id")

            if iid is not None:
                self.item_by_id[iid] = item
            if icode:
                self.item_by_code[str(icode).upper()] = item

            if rid is not None and rid in self.restaurant_to_items:
                self.restaurant_to_items[rid].append(item)

            cat_intel = item.get("category_intelligence", {})
            cid = cat_intel.get("category_id") if isinstance(cat_intel, dict) else None
            if cid:
                norm_cid = str(cid).upper()
                if norm_cid not in self.category_to_items:
                    self.category_to_items[norm_cid] = []
                self.category_to_items[norm_cid].append(item)

            # Build search alias index
            for alias in item.get("search_aliases", []):
                norm_alias = str(alias).strip().lower()
                if norm_alias not in self.alias_index:
                    self.alias_index[norm_alias] = []
                if item not in self.alias_index[norm_alias]:
                    self.alias_index[norm_alias].append(item)

        # 4. Combos Index
        for cb in combos:
            cid = cb.get("combo_id")
            if cid is not None:
                self.combo_by_id[cid] = cb

    def clear(self) -> None:
        """Clear all in-memory indexes."""
        self.restaurant_by_id.clear()
        self.restaurant_by_code.clear()
        self.item_by_id.clear()
        self.item_by_code.clear()
        self.combo_by_id.clear()
        self.category_by_id.clear()
        self.restaurant_to_items.clear()
        self.category_to_items.clear()
        self.alias_index.clear()
