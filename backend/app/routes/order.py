from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, validator

from app.services.order_service import OrderService

router = APIRouter()
order_service = OrderService()


class OrderRequest(BaseModel):
    items: list[int] = Field(..., description="List of item IDs to order")

    @validator("items")
    def items_must_not_be_empty(cls, value: list[int]) -> list[int]:
        if not isinstance(value, list) or len(value) == 0:
            raise ValueError("items list cannot be empty")
        return value


@router.post("/place")
async def place_order(request: OrderRequest) -> dict[str, Any]:
    """Place a new order using catalog item IDs."""
    try:
        order = order_service.place_order(request.items)
        summary = order_service.generate_order_summary(order)
        return {
            "status": "success",
            "order": order,
            "summary": summary,
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Order placement failed: {str(exc)}")


@router.get("/status/{order_id}")
async def get_order_status(order_id: str) -> dict[str, Any]:
    """Return order status for a previously placed order."""
    try:
        status = order_service.get_order_status(order_id)
        return {
            "order_id": order_id,
            "status": status,
        }
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch order status: {str(exc)}")


@router.get("/history")
async def get_order_history() -> dict[str, Any]:
    """Return all mock orders stored in memory."""
    try:
        return {
            "status": "success",
            "orders": list(order_service.orders.values()),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to load order history: {str(exc)}")


@router.get("/test")
async def test_ordering_system() -> dict[str, str]:
    """Health check for the ordering subsystem."""
    return {"status": "ordering system working"}
