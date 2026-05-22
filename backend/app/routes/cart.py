from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, validator

from app.services.cart_service import CartService

router = APIRouter()
cart_service = CartService()


class CartActionRequest(BaseModel):
    session_id: str = Field(..., min_length=1, description="Session identifier")
    item_id: int = Field(..., gt=0, description="Catalog item ID")
    quantity: Optional[int] = Field(1, ge=1, description="Quantity to add or remove")

    @validator("session_id")
    def session_id_must_not_be_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("session_id cannot be empty")
        return value.strip()


class SessionRequest(BaseModel):
    session_id: str = Field(..., min_length=1, description="Session identifier")

    @validator("session_id")
    def session_id_must_not_be_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("session_id cannot be empty")
        return value.strip()


@router.get("")
async def get_cart(session_id: str) -> Dict[str, Any]:
    """Return the cart for a given session."""
    cart = cart_service.get_cart(session_id)
    return {"status": "success", "data": {"cart": cart}}


@router.post("/add")
async def add_item_to_cart(request: CartActionRequest) -> Dict[str, Any]:
    """Add an item to the user's cart."""
    try:
        item = cart_service.catalog_service.get_item_by_id(request.item_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    if not item.get("available"):
        raise HTTPException(status_code=400, detail="This item is not currently available.")

    cart = cart_service.add_to_cart(request.session_id, item, request.quantity or 1)
    return {"status": "success", "data": {"cart": cart}}


@router.post("/remove")
async def remove_item_from_cart(request: CartActionRequest) -> Dict[str, Any]:
    """Remove an item or quantity from the user's cart."""
    try:
        cart = cart_service.remove_from_cart(request.session_id, request.item_id, request.quantity)
        return {"status": "success", "data": {"cart": cart}}
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/checkout")
async def checkout_cart(request: SessionRequest) -> Dict[str, Any]:
    """Checkout the current cart and place an order."""
    cart = cart_service.get_cart(request.session_id)
    if not cart["items"]:
        raise HTTPException(status_code=400, detail="Your cart is empty.")

    item_ids = cart_service.get_cart_item_ids(request.session_id)
    try:
        order = cart_service.order_service.place_order(item_ids)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    cart_service.clear_cart(request.session_id)
    updated_cart = cart_service.get_cart(request.session_id)
    return {"status": "success", "data": {"order": order, "cart": updated_cart}}
