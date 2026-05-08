import json
from typing import Dict, List, Optional

try:
    from app.services.catalog_service import CatalogService
except ImportError:
    from .catalog_service import CatalogService


class OrderService:
    """Service layer for processing and tracking mock food orders."""

    DELIVERY_FEE = 40
    TAX_RATE = 0.10
    ORDER_ID_PREFIX = "ORD-"
    ORDER_ID_BASE = 1000

    def __init__(self, catalog_service: Optional[CatalogService] = None) -> None:
        self.catalog_service = catalog_service or CatalogService()
        self.orders: Dict[str, Dict[str, object]] = {}

    def validate_items(self, item_ids: List[int]) -> List[Dict[str, object]]:
        """Validate item IDs and ensure requested items are available."""
        if not isinstance(item_ids, list) or len(item_ids) == 0:
            raise ValueError("item_ids must be a non-empty list of integers")

        validated_items: List[Dict[str, object]] = []
        for raw_id in item_ids:
            if not isinstance(raw_id, int):
                raise ValueError(f"Invalid item_id: {raw_id}. Item IDs must be integers.")

            try:
                item = self.catalog_service.get_item_by_id(raw_id)
            except ValueError as exc:
                raise ValueError(f"Invalid item_id: {raw_id}") from exc

            if not item.get("available"):
                raise ValueError(f"Item {raw_id} is currently unavailable")

            validated_items.append(item)

        return validated_items

    def calculate_totals(self, items: List[Dict[str, object]]) -> Dict[str, int]:
        """Calculate subtotal, delivery fee, tax, and total for an order."""
        subtotal = sum(int(item.get("price", 0)) for item in items)
        delivery_fee = self.DELIVERY_FEE if subtotal > 0 else 0
        tax = int(round(subtotal * self.TAX_RATE))
        total = subtotal + delivery_fee + tax

        return {
            "subtotal": subtotal,
            "delivery_fee": delivery_fee,
            "tax": tax,
            "total": total,
        }

    def estimate_delivery_time(self, items: List[Dict[str, object]]) -> int:
        """Estimate delivery time based on restaurant delivery times."""
        restaurant_times: List[int] = []
        restaurants = self.catalog_service.get_all_restaurants()

        for item in items:
            restaurant_name = item.get("restaurant_name")
            matched = next(
                (
                    restaurant.get("delivery_time")
                    for restaurant in restaurants
                    if restaurant.get("name") == restaurant_name
                ),
                None,
            )
            if isinstance(matched, int):
                restaurant_times.append(matched)

        if not restaurant_times:
            return 0

        average_time = sum(restaurant_times) / len(restaurant_times)
        return int(round(average_time + 3))

    def generate_order_id(self) -> str:
        """Generate a new sequential order ID."""
        if not self.orders:
            next_id = self.ORDER_ID_BASE + 1
        else:
            existing_ids = [int(order_id.split("-")[1]) for order_id in self.orders.keys()]
            next_id = max(existing_ids) + 1

        return f"{self.ORDER_ID_PREFIX}{next_id}"

    def generate_order_summary(self, order: Dict[str, object]) -> str:
        """Return a human-readable order summary."""
        total = int(order.get("total", 0))
        item_count = len(order.get("items", []))
        status = order.get("status", "confirmed")
        return f"Your order of {item_count} items totaling ₹{total} has been {status}."

    def place_order(self, item_ids: List[int]) -> Dict[str, object]:
        """Validate the order and return a confirmed order payload."""
        validated_items = self.validate_items(item_ids)

        order_items = [
            {
                "item_id": int(item["item_id"]),
                "name": item["name"],
                "price": int(item["price"]),
                "restaurant_name": item["restaurant_name"],
                "cuisine": item["cuisine"],
            }
            for item in validated_items
        ]

        totals = self.calculate_totals(order_items)
        estimated_delivery_time = self.estimate_delivery_time(order_items)
        order_id = self.generate_order_id()
        order = {
            "order_id": order_id,
            "items": order_items,
            "subtotal": totals["subtotal"],
            "delivery_fee": totals["delivery_fee"],
            "tax": totals["tax"],
            "total": totals["total"],
            "estimated_delivery_time": estimated_delivery_time,
            "status": "confirmed",
        }

        self.orders[order_id] = order
        return order

    def get_order_status(self, order_id: str) -> str:
        """Return the current status for a previously placed order."""
        if order_id not in self.orders:
            raise ValueError(f"Order not found: {order_id}")

        return str(self.orders[order_id].get("status", "unknown"))


def _print_result(title: str, payload: object) -> None:
    print(f"\n=== {title} ===")
    if isinstance(payload, dict):
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(payload)


if __name__ == "__main__":
    service = OrderService()

    try:
        valid_order = service.place_order([101, 201, 601])
        _print_result("Valid Order", valid_order)
        _print_result("Order Summary", service.generate_order_summary(valid_order))
        _print_result("Order Status", service.get_order_status(valid_order["order_id"]))
    except ValueError as exc:
        _print_result("Valid Order Failed", str(exc))

    try:
        service.place_order([105])
    except ValueError as exc:
        _print_result("Unavailable Item", str(exc))

    try:
        service.place_order([999])
    except ValueError as exc:
        _print_result("Invalid Item ID", str(exc))
