"""Lightweight in-memory cart service for conversational commerce."""

from typing import Any, Dict, List, Optional

try:
    from app.services.catalog_service import CatalogService
    from app.services.order_service import OrderService
except ImportError:
    from .catalog_service import CatalogService
    from .order_service import OrderService


class CartService:
    """In-memory cart management with totals calculation."""

    def __init__(self, catalog_service: Optional[CatalogService] = None, order_service: Optional[OrderService] = None) -> None:
        self.catalog_service = catalog_service or CatalogService()
        self.order_service = order_service or OrderService(self.catalog_service)
        self.carts: Dict[str, Dict[str, Any]] = {}

    def create_cart(self, session_id: str) -> Dict[str, Any]:
        if session_id not in self.carts:
            self.carts[session_id] = {
                "session_id": session_id,
                "items": [],
                "subtotal": 0,
                "delivery_fee": 0,
                "tax": 0,
                "total": 0,
            }
        return self.carts[session_id]

    def add_to_cart(self, session_id: str, item: Dict[str, Any], quantity: int = 1) -> Dict[str, Any]:
        cart = self.create_cart(session_id)
        existing_item = next((entry for entry in cart["items"] if entry["item_id"] == item["item_id"]), None)
        if existing_item:
            existing_item["quantity"] += quantity
        else:
            cart["items"].append(
                {
                    "item_id": item["item_id"],
                    "name": item["name"],
                    "price": int(item["price"]),
                    "restaurant_name": item.get("restaurant_name", ""),
                    "cuisine": item.get("cuisine", ""),
                    "quantity": quantity,
                }
            )
        self._refresh_totals(cart)
        return cart

    def remove_from_cart(self, session_id: str, item_id: int, quantity: Optional[int] = None) -> Dict[str, Any]:
        cart = self.create_cart(session_id)
        item = next((entry for entry in cart["items"] if entry["item_id"] == item_id), None)
        if not item:
            raise ValueError(f"Item {item_id} not found in cart")

        if quantity is None or quantity >= item["quantity"]:
            cart["items"].remove(item)
        else:
            item["quantity"] -= quantity

        self._refresh_totals(cart)
        return cart

    def get_cart(self, session_id: str) -> Dict[str, Any]:
        cart = self.create_cart(session_id)
        self._refresh_totals(cart)
        return cart

    def clear_cart(self, session_id: str) -> None:
        if session_id in self.carts:
            self.carts[session_id] = {
                "session_id": session_id,
                "items": [],
                "subtotal": 0,
                "delivery_fee": 0,
                "tax": 0,
                "total": 0,
            }

    def get_cart_item_ids(self, session_id: str) -> List[int]:
        cart = self.create_cart(session_id)
        item_ids: List[int] = []
        for item in cart["items"]:
            item_ids.extend([item["item_id"]] * item["quantity"])
        return item_ids

    def _refresh_totals(self, cart: Dict[str, Any]) -> None:
        items: List[Dict[str, Any]] = []
        for entry in cart["items"]:
            for _ in range(entry["quantity"]):
                items.append({"price": int(entry["price"])});

        totals = self.order_service.calculate_totals(items) if items else {"subtotal": 0, "delivery_fee": 0, "tax": 0, "total": 0}
        cart["subtotal"] = totals["subtotal"]
        cart["delivery_fee"] = totals["delivery_fee"]
        cart["tax"] = totals["tax"]
        cart["total"] = totals["total"]
