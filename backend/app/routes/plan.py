"""
Planner Routes Module

FastAPI routes for meal planner APIs.
"""

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, validator

from app.services.planner import MealPlanner

router = APIRouter()


class MealPlanRequest(BaseModel):
    goal: str
    budget: int = Field(..., gt=0, description="Weekly budget in INR")
    preferences: str

    @validator("preferences")
    def validate_preferences(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in {"veg", "non-veg"}:
            raise ValueError("preferences must be either 'veg' or 'non-veg'")
        return normalized


def get_sample_meal_plan() -> dict[str, Any]:
    """Return a static sample meal plan for frontend demos."""
    return {
        "day_1": {"breakfast": "Poha", "lunch": "Dal Rice", "dinner": "Vegetable Curry with Chapati", "estimated_cost": 220},
        "day_2": {"breakfast": "Upma", "lunch": "Chana Masala with Rice", "dinner": "Paneer Bhurji with Roti", "estimated_cost": 240},
        "day_3": {"breakfast": "Idli with Sambar", "lunch": "Mixed Vegetable Curry with Rice", "dinner": "Moong Dal Khichdi", "estimated_cost": 230},
        "day_4": {"breakfast": "Dalia", "lunch": "Rajma with Rice", "dinner": "Palak Paneer with Roti", "estimated_cost": 250},
        "day_5": {"breakfast": "Vegetable Sandwich", "lunch": "Lentil Soup with Rice", "dinner": "Aloo Gobi with Chapati", "estimated_cost": 210},
        "day_6": {"breakfast": "Methi Thepla", "lunch": "Soyabean Curry with Rice", "dinner": "Mixed Sabzi with Roti", "estimated_cost": 220},
        "day_7": {"breakfast": "Besan Chilla", "lunch": "Vegetable Biryani", "dinner": "Tomato Rasam with Idli", "estimated_cost": 225}
    }


@router.post("/generate")
async def generate_meal_plan(request: MealPlanRequest) -> dict[str, Any]:
    """Generate a weekly meal plan based on user preferences."""
    planner = MealPlanner()

    try:
        meal_plan = planner.generate_meal_plan(request.dict())
        return {
            "status": "success",
            "meal_plan": meal_plan,
            "request": request.dict()
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Meal plan generation failed: {str(exc)}")


@router.get("/sample")
async def sample_meal_plan() -> dict[str, Any]:
    """Return a static sample meal plan for frontend development and testing."""
    return {
        "status": "success",
        "sample_meal_plan": get_sample_meal_plan()
    }


@router.get("/test")
async def test_planner() -> dict[str, Any]:
    """Return planner health status."""
    return {"status": "planner working"}
