"""Unit tests for KnowledgeBaseService orchestrator."""

from app.services.knowledge_base.knowledge_base_service import KnowledgeBaseService


def test_service_initialization_and_queries():
    """Test KnowledgeBaseService auto-loads and executes queries cleanly."""
    service = KnowledgeBaseService()

    # Statistics check
    stats = service.get_statistics()
    assert stats["is_loaded"] is True
    assert stats["total_restaurants"] >= 6
    assert stats["total_menu_items"] >= 35

    # Restaurant queries
    mcd = service.get_restaurant(1)
    assert mcd is not None
    assert mcd["name"] == "McDonald's"

    kfc = service.get_restaurant_by_code("KFC")
    assert kfc is not None
    assert kfc["restaurant_id"] == 2

    # Item queries
    item_101 = service.get_item(101)
    assert item_101 is not None
    assert item_101["name"] == "McAloo Tikki Burger"

    item_code = service.get_item_by_code("KFC_CHICKEN_001")
    assert item_code is not None
    assert item_code["item_id"] == 201

    # Relational queries
    mcd_items = service.get_items_for_restaurant(1)
    assert len(mcd_items) >= 15

    burger_items = service.get_items_for_category("CAT_BURGERS_VEG")
    assert len(burger_items) >= 3

    # Alias search query
    fries_matches = service.search_alias("fries")
    assert len(fries_matches) >= 1


def test_service_reload():
    """Test reloading Knowledge Base data."""
    service = KnowledgeBaseService()
    assert service.cache.is_loaded is True

    service.reload()
    assert service.cache.is_loaded is True
    assert len(service.get_all_restaurants()) >= 6
