"""JSON Loader for Knowledge Base dataset files."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


class KnowledgeBaseLoadError(Exception):
    """Exception raised when loading Knowledge Base files fails."""
    pass


class KnowledgeBaseJSONLoader:
    """Loads Knowledge Base JSON files from disk safely."""

    def __init__(self, base_dir: Optional[str] = None) -> None:
        if base_dir:
            self.base_dir = Path(base_dir).resolve()
        else:
            self.base_dir = (
                Path(__file__).resolve().parents[3] / "data" / "knowledge_base"
            )

    def _resolve_file_path(self, relative_path: str) -> Path:
        """Resolve full path and ensure file exists."""
        full_path = self.base_dir / relative_path
        if not full_path.exists():
            raise KnowledgeBaseLoadError(f"Required Knowledge Base file not found: {full_path}")
        return full_path

    def _load_json_file(self, full_path: Path) -> Any:
        """Load and parse JSON file from path."""
        try:
            with full_path.open("r", encoding="utf-8") as file:
                return json.load(file)
        except json.JSONDecodeError as exc:
            raise KnowledgeBaseLoadError(f"Failed to parse JSON file {full_path}: {exc}") from exc
        except Exception as exc:
            raise KnowledgeBaseLoadError(f"Error reading file {full_path}: {exc}") from exc

    def load_restaurants(self) -> List[Dict[str, Any]]:
        """Load restaurants master array."""
        path = self._resolve_file_path("restaurants/restaurants.json")
        data = self._load_json_file(path)
        if not isinstance(data, list):
            raise KnowledgeBaseLoadError(f"Expected JSON array in {path}, got {type(data)}")
        return data

    def load_menu_items(self) -> List[Dict[str, Any]]:
        """Load menu items master array."""
        path = self._resolve_file_path("menu/menu_items.json")
        data = self._load_json_file(path)
        if not isinstance(data, list):
            raise KnowledgeBaseLoadError(f"Expected JSON array in {path}, got {type(data)}")
        return data

    def load_combos(self) -> List[Dict[str, Any]]:
        """Load combos array."""
        path = self._resolve_file_path("combos/combos.json")
        data = self._load_json_file(path)
        if not isinstance(data, list):
            raise KnowledgeBaseLoadError(f"Expected JSON array in {path}, got {type(data)}")
        return data

    def load_category_registry(self) -> List[Dict[str, Any]]:
        """Load category registry array."""
        path = self._resolve_file_path("category_registry.json")
        data = self._load_json_file(path)
        if not isinstance(data, list):
            raise KnowledgeBaseLoadError(f"Expected JSON array in {path}, got {type(data)}")
        return data
