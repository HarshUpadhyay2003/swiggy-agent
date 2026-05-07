"""
Profile Routes Module

FastAPI routes for user profile analysis and goal suggestions.
"""

import json
import os
from typing import Any

from fastapi import APIRouter, HTTPException

from app.services.goal_engine import generate_summary, suggest_goals
from app.services.history_analyzer import analyze_history

router = APIRouter()


def load_orders_from_file() -> list[dict[str, Any]]:
    """
    Load orders from mock_orders.json file.

    Returns:
        List of order dictionaries

    Raises:
        HTTPException: If file not found, invalid JSON, or empty file
    """
    # Construct path to data file
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    data_file = os.path.join(base_dir, "data", "mock_orders.json")

    if not os.path.exists(data_file):
        raise HTTPException(status_code=404, detail="Orders data file not found")

    try:
        with open(data_file, "r", encoding="utf-8") as f:
            content = f.read().strip()

        if not content:
            raise HTTPException(status_code=400, detail="Orders file is empty")

        orders = json.loads(content)

        if not isinstance(orders, list):
            raise HTTPException(status_code=400, detail="Invalid data format: expected a list of orders")

        if not orders:
            raise HTTPException(status_code=400, detail="No orders found in dataset")

        return orders

    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading orders: {str(e)}")


@router.get("/analyze-history")
async def analyze_order_history() -> dict[str, Any]:
    """
    Analyze user order history.

    Returns:
        Dictionary containing history analysis results
    """
    try:
        orders = load_orders_from_file()
        analysis = analyze_history(orders)
        return analysis
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/suggest-goals")
async def suggest_user_goals() -> list[dict[str, Any]]:
    """
    Suggest personalized goals based on order history.

    Returns:
        List of goal dictionaries
    """
    try:
        orders = load_orders_from_file()
        analysis = analyze_history(orders)
        goals = suggest_goals(analysis)
        return goals
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Goal suggestion failed: {str(e)}")


@router.get("/full-profile")
async def get_full_profile() -> dict[str, Any]:
    """
    Get complete user profile including analysis, goals, and summary.

    Returns:
        Dictionary with history_analysis, goals, and summary
    """
    try:
        orders = load_orders_from_file()
        analysis = analyze_history(orders)
        goals = suggest_goals(analysis)
        summary = generate_summary(goals)

        return {
            "history_analysis": analysis,
            "goals": goals,
            "summary": summary
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Profile generation failed: {str(e)}")


@router.get("/test-system")
async def test_system() -> dict[str, Any]:
    """
    Test system status and available modules.

    Returns:
        Dictionary with system status and modules
    """
    return {
        "status": "working",
        "modules": [
            "history_analyzer",
            "goal_engine"
        ]
    }