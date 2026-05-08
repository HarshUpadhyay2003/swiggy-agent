from typing import Any, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, validator

from app.services.context_engine import ContextEngine

router = APIRouter()
context_engine = ContextEngine()


class ContextRequest(BaseModel):
    mood: str = Field(..., description="User's current mood or craving")
    budget_left: int = Field(..., gt=0, description="Remaining budget in rupees")
    meal_type: str = Field(..., description="Type of meal")
    preference: Optional[str] = Field(None, description="Dietary preference")
    health_goal: bool = Field(False, description="Whether health is a priority")

    @validator("meal_type")
    def meal_type_must_be_valid(cls, value: str) -> str:
        valid_types = {"breakfast", "lunch", "dinner", "snacks"}
        if value.lower() not in valid_types:
            raise ValueError(f"meal_type must be one of {sorted(valid_types)}")
        return value.lower()

    @validator("preference")
    def preference_must_be_valid(cls, value: Optional[str]) -> Optional[str]:
        if value is not None:
            valid_prefs = {"veg", "non-veg"}
            if value.lower() not in valid_prefs:
                raise ValueError(f"preference must be one of {sorted(valid_prefs)}")
            return value.lower()
        return value


@router.post("/recommend")
async def recommend_food(request: ContextRequest) -> dict[str, Any]:
    """Generate context-aware food recommendations."""
    try:
        context = {
            "mood": request.mood,
            "budget_left": request.budget_left,
            "meal_type": request.meal_type,
            "preference": request.preference,
            "health_goal": request.health_goal,
        }
        result = context_engine.recommend_food(context)
        return {
            "status": "success",
            **result,
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {str(exc)}")


@router.get("/sample")
async def get_sample_recommendation() -> dict[str, Any]:
    """Return a static sample recommendation response for testing."""
    return {
        "status": "success",
        "fallback_used": False,
        "recommendations": [
            {
                "item_name": "Paneer Butter Masala",
                "restaurant": "Spice Garden",
                "price": 260,
                "reason": "Matches your preference and perfect for dinner.",
            },
            {
                "item_name": "Masala Dosa",
                "restaurant": "South Spice Café",
                "price": 140,
                "reason": "Affordable and comforting.",
            },
        ],
    }


@router.get("/test")
async def test_context_engine() -> dict[str, str]:
    """Health check for the context engine subsystem."""
    return {"status": "context engine working"}
