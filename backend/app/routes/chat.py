"""
Chat API Routes

Unified conversational AI orchestration endpoints.
"""

from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, validator

from app.services.chat_orchestrator import ChatOrchestrator


class ChatRequest(BaseModel):
    """Request model for chat messages."""

    message: str = Field(..., min_length=1, max_length=1000, description="User message")
    user_context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="User context data")

    @validator("message")
    def validate_message(cls, v):
        """Validate and clean message."""
        if not v or not v.strip():
            raise ValueError("Message cannot be empty")
        return v.strip()


router = APIRouter()
orchestrator = ChatOrchestrator()


@router.post("")
async def chat(request: ChatRequest) -> Dict[str, Any]:
    """
    Main chat endpoint for conversational AI orchestration.

    Processes user messages and returns orchestrated responses based on intent detection.
    """
    try:
        session_id = (request.user_context or {}).get("session_id", "unknown")
        print("========================================")
        print("[BACKEND LOG] INCOMING REQUEST")
        print(f"[BACKEND LOG] Message: {request.message}")
        print(f"[BACKEND LOG] Session ID: {session_id}")
        print(f"[BACKEND LOG] Context: {request.user_context}")

        result = orchestrator.handle_message(request.message, request.user_context or {})

        response = {
            "status": "success",
            "intent": result.get("intent", "unknown"),
            "response": result.get("response", ""),
            "data": {
                k: v for k, v in result.items()
                if k not in ["intent", "response"]
            },
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

        print("----------------------------------------")
        print("[BACKEND LOG] RETURNING PAYLOAD")
        print(f"[BACKEND LOG] status: {response.get('status')}")
        print(f"[BACKEND LOG] intent: {response.get('intent')}")
        print(f"[BACKEND LOG] response length: {len(response.get('response', ''))}")
        data_obj = response.get("data", {})
        print(f"[BACKEND LOG] data keys: {list(data_obj.keys())}")

        if "recommendations" in data_obj:
            recs = data_obj.get("recommendations", [])
            print(f"[BACKEND LOG] recommendations count: {len(recs)}")
            if recs and len(recs) > 0:
                first = recs[0]
                print(f"[BACKEND LOG] first recommendation: {first.get('name') or first.get('item_name')}, restaurant: {first.get('restaurant_name')}, price: {first.get('price')}")

        if "meal_plan" in data_obj or "planner" in data_obj:
            plan = data_obj.get("meal_plan") or data_obj.get("planner")
            print(f"[BACKEND LOG] meal_plan keys: {list(plan.keys()) if isinstance(plan, dict) else 'non-dict'}")

        if "cart" in data_obj:
            cart_obj = data_obj.get("cart", {})
            print(f"[BACKEND LOG] cart items count: {len(cart_obj.get('items', [])) if isinstance(cart_obj, dict) else 'N/A'}")
        print("========================================")

        return response

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Chat orchestration failed: {str(e)}"
        )


@router.get("/test")
async def test_chat() -> Dict[str, str]:
    """
    Test endpoint to verify chat orchestrator is working.
    """
    return {"status": "chat orchestrator working"}


@router.get("/sample")
async def sample_chat() -> Dict[str, Any]:
    """
    Sample endpoint returning a realistic orchestrator response for testing.
    """
    try:
        # Use a realistic sample request
        sample_message = "I want something cheap and comforting tonight"
        sample_context = {"budget_left": 200, "preference": "veg"}

        result = orchestrator.handle_message(sample_message, sample_context)

        response = {
            "status": "success",
            "intent": result.get("intent", "unknown"),
            "response": result.get("response", ""),
            "data": {
                k: v for k, v in result.items()
                if k not in ["intent", "response"]
            },
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

        return response

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Sample chat failed: {str(e)}"
        )