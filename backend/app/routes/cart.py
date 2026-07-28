import logging
import traceback
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel, Field, validator

from app.services.cart_service import CartService

logger = logging.getLogger("checkout_routes")
router = APIRouter()

# Global CartService singleton for cart routes
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
    cart_id: Optional[str] = None

    @validator("session_id")
    def session_id_must_not_be_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("session_id cannot be empty")
        return value.strip()


@router.get("")
async def get_cart(session_id: str) -> Dict[str, Any]:
    """Return the cart for a given session."""
    if not session_id or not session_id.strip():
        logger.error("[CART] get_cart failed: empty session_id")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "INVALID_SESSION",
                "reason": "session_id is required",
                "details": "session_id query parameter must be a non-empty string",
                "field": "session_id",
            },
        )
    cart = cart_service.get_cart(session_id.strip())
    return {"status": "success", "data": {"cart": cart}}


@router.post("/add")
async def add_item_to_cart(request: CartActionRequest) -> Dict[str, Any]:
    """Add an item to the user's cart."""
    logger.info(f"[CART] add_item_to_cart request: session='{request.session_id}', item_id={request.item_id}, qty={request.quantity}")
    try:
        item = cart_service.catalog_service.get_item_by_id(request.item_id)
    except ValueError as exc:
        logger.error(f"[CART] Item lookup failed for item_id={request.item_id}: {exc}")
        raise HTTPException(
            status_code=404,
            detail={
                "error": "ITEM_NOT_FOUND",
                "reason": f"Item with ID {request.item_id} does not exist",
                "details": str(exc),
                "field": "item_id",
            },
        )

    if not item.get("available"):
        logger.warning(f"[CART] Unavailable item add attempt: item_id={request.item_id}")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "ITEM_UNAVAILABLE",
                "reason": f"Item '{item.get('name')}' is currently unavailable",
                "details": "Only available items can be added to the cart",
                "field": "item_id",
            },
        )

    cart = cart_service.add_to_cart(request.session_id, item, request.quantity or 1)
    return {"status": "success", "data": {"cart": cart}}


@router.post("/remove")
async def remove_item_from_cart(request: CartActionRequest) -> Dict[str, Any]:
    """Remove an item or quantity from the user's cart."""
    logger.info(f"[CART] remove_item_from_cart request: session='{request.session_id}', item_id={request.item_id}")
    try:
        cart = cart_service.remove_from_cart(request.session_id, request.item_id, request.quantity)
        return {"status": "success", "data": {"cart": cart}}
    except ValueError as exc:
        logger.error(f"[CART] Remove item failed: {exc}")
        raise HTTPException(
            status_code=404,
            detail={
                "error": "ITEM_NOT_IN_CART",
                "reason": str(exc),
                "details": f"Item {request.item_id} was not found in active session cart",
                "field": "item_id",
            },
        )


@router.post("/checkout")
async def checkout_cart(request: SessionRequest) -> Dict[str, Any]:
    """Checkout the current cart and place an order."""
    session_id = request.session_id.strip()

    logger.info("==========================================")
    logger.info(f"[CHECKOUT] Incoming Checkout Request for session_id='{session_id}'")

    cart = cart_service.get_cart(session_id)
    items_count = len(cart.get("items", []))
    logger.info(f"[CHECKOUT] Session Items Count: {items_count}")

    if not cart.get("items"):
        logger.error(f"[CHECKOUT] Validation Failed: Cart is empty for session_id='{session_id}'")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "CHECKOUT_VALIDATION_FAILED",
                "reason": "Session cart is empty",
                "details": f"No items were found in the cart for session '{session_id}'. Add items to cart before checkout.",
                "field": "cart_items",
            },
        )

    item_ids = cart_service.get_cart_item_ids(session_id)
    logger.info(f"[CHECKOUT] Received Item IDs for Order: {item_ids}")

    try:
        order = cart_service.order_service.place_order(item_ids)
        logger.info(f"[CHECKOUT] Order Placed Successfully: Order ID='{order.get('order_id')}', Total=₹{order.get('total')}")
    except ValueError as exc:
        logger.error(f"[CHECKOUT] Order Creation Failed: {exc}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "ORDER_PLACEMENT_FAILED",
                "reason": str(exc),
                "details": "Order processing failed during item validation or pricing calculations.",
                "field": "order",
            },
        )
    except Exception as exc:
        logger.error(f"[CHECKOUT] Unexpected System Failure during Order Creation: {exc}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "INTERNAL_CHECKOUT_ERROR",
                "reason": str(exc),
                "details": "Unexpected backend error occurred while creating order.",
            },
        )

    cart_service.clear_cart(session_id)
    updated_cart = cart_service.get_cart(session_id)
    logger.info(f"[CHECKOUT] Cart cleared for session_id='{session_id}'")
    logger.info("==========================================")

    return {"status": "success", "data": {"order": order, "cart": updated_cart}}
