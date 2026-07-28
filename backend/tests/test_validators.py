"""Unit tests for KnowledgeBaseValidator."""

import pytest
from app.services.knowledge_base.validators import KnowledgeBaseValidator, KnowledgeBaseValidationError


def test_validator_passes_on_real_data():
    """Test validator succeeds on valid Knowledge Base entities."""
    from app.services.knowledge_base.json_loader import KnowledgeBaseJSONLoader

    loader = KnowledgeBaseJSONLoader()
    restaurants = loader.load_restaurants()
    menu_items = loader.load_menu_items()
    combos = loader.load_combos()
    categories = loader.load_category_registry()

    validator = KnowledgeBaseValidator()
    # Should not raise exception
    validator.validate_all(restaurants, menu_items, combos, categories)


def test_duplicate_restaurant_id_fails():
    """Test validator catches duplicate restaurant IDs."""
    validator = KnowledgeBaseValidator()
    restaurants = [
        {"restaurant_id": 1, "restaurant_code": "MCD", "name": "McD", "primary_cuisine": "Fast Food", "operating_hours": {}, "confidence": {}},
        {"restaurant_id": 1, "restaurant_code": "MCD2", "name": "McD2", "primary_cuisine": "Fast Food", "operating_hours": {}, "confidence": {}},
    ]
    with pytest.raises(KnowledgeBaseValidationError, match="Duplicate restaurant_id"):
        validator.validate_all(restaurants, [], [], [])


def test_broken_restaurant_reference_fails():
    """Test validator catches menu items referencing missing restaurant IDs."""
    validator = KnowledgeBaseValidator()
    restaurants = [{"restaurant_id": 1, "restaurant_code": "MCD", "name": "McD", "primary_cuisine": "Fast Food", "operating_hours": {}, "confidence": {}}]
    categories = [{"category_id": "CAT_VEG"}]
    menu_items = [{
        "item_id": 101,
        "restaurant_id": 999,  # Non-existent
        "restaurant_code": "NON",
        "item_code": "ITEM_1",
        "name": "Item 1",
        "category_intelligence": {"category_id": "CAT_VEG"},
        "nutrition": {}, "dietary_safety": {}, "health_scores": {}, "ingredients": {},
        "commerce_intelligence": {}, "confidence": {}, "source_metadata": {}, "data_quality": {}, "search_aliases": []
    }]

    with pytest.raises(KnowledgeBaseValidationError, match="references non-existent restaurant_id"):
        validator.validate_all(restaurants, menu_items, [], categories)
