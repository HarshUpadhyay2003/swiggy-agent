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


@router.post("/")
async def chat(request: ChatRequest) -> Dict[str, Any]:
    """
    Main chat endpoint for conversational AI orchestration.

    Processes user messages and returns orchestrated responses based on intent detection.
    """
    try:
        result = orchestrator.handle_message(request.message, request.user_context or {})

        # Add timestamp and status
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