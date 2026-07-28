"""Unit tests for KnowledgeBaseJSONLoader."""

import json
import pytest
from pathlib import Path
from app.services.knowledge_base.json_loader import KnowledgeBaseJSONLoader, KnowledgeBaseLoadError


def test_load_real_knowledge_base():
    """Test loading existing production datasets from default path."""
    loader = KnowledgeBaseJSONLoader()
    restaurants = loader.load_restaurants()
    menu_items = loader.load_menu_items()
    combos = loader.load_combos()
    categories = loader.load_category_registry()

    assert isinstance(restaurants, list)
    assert len(restaurants) >= 6
    assert isinstance(menu_items, list)
    assert len(menu_items) >= 35
    assert isinstance(combos, list)
    assert isinstance(categories, list)


def test_missing_file_raises_error(tmp_path):
    """Test loader raises KnowledgeBaseLoadError when file is missing."""
    empty_dir = tmp_path / "empty_kb"
    empty_dir.mkdir()

    loader = KnowledgeBaseJSONLoader(base_dir=str(empty_dir))
    with pytest.raises(KnowledgeBaseLoadError, match="not found"):
        loader.load_restaurants()


def test_invalid_json_raises_error(tmp_path):
    """Test loader raises KnowledgeBaseLoadError when JSON is malformed."""
    kb_dir = tmp_path / "corrupt_kb"
    rest_dir = kb_dir / "restaurants"
    rest_dir.mkdir(parents=True)

    corrupt_file = rest_dir / "restaurants.json"
    corrupt_file.write_text("{ malformed json }", encoding="utf-8")

    loader = KnowledgeBaseJSONLoader(base_dir=str(kb_dir))
    with pytest.raises(KnowledgeBaseLoadError, match="Failed to parse JSON"):
        loader.load_restaurants()
