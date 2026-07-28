"""Unit tests for KnowledgeBaseIndexes."""

from app.services.knowledge_base.indexes import KnowledgeBaseIndexes


def test_indexing_and_o1_lookup():
    """Test fast lookup index generation and retrieval."""
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

    # Verify ID & Code lookups
    assert indexes.restaurant_by_id.get(1)["name"] == "McDonald's"
    assert indexes.restaurant_by_code.get("MCD")["restaurant_id"] == 1
    assert indexes.category_by_id.get("CAT_BURGERS_VEG")["display_name"] == "Vegetarian Burgers"
    assert indexes.item_by_id.get(101)["name"] == "McAloo Tikki"
    assert indexes.item_by_code.get("MCD_BURGER_001")["item_id"] == 101
    assert indexes.combo_by_id.get(2001)["combo_name"] == "Zinger Box"

    # Verify relational mappings
    assert len(indexes.restaurant_to_items.get(1)) == 1
    assert len(indexes.category_to_items.get("CAT_BURGERS_VEG")) == 1

    # Verify alias index
    assert len(indexes.alias_index.get("mcaloo")) == 1
    assert indexes.alias_index.get("mcaloo")[0]["item_id"] == 101
