"""
Test Script for Phase 1 (History Analyzer) and Phase 2 (Goal Engine)

Validates the full flow: mock_orders.json → history analyzer → goal engine
"""

import json
import os
from pathlib import Path
from typing import Any

from app.services.goal_engine import generate_summary, suggest_goals
from app.services.history_analyzer import analyze_history


def load_orders(file_path: Path) -> list[dict[str, Any]]:
    """
    Load orders from JSON file.
    
    Args:
        file_path: Path to mock_orders.json
        
    Returns:
        List of order dictionaries
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Data file not found: {file_path}")
    
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    if not isinstance(data, list):
        raise ValueError("Expected list of orders in JSON file")
    
    return data


def create_test_cases(orders: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """
    Create 3 test cases from the order list.
    
    Args:
        orders: Full list of orders
        
    Returns:
        Dictionary with test case names and their order subsets
    """
    return {
        "FULL DATA": orders,
        "RECENT ORDERS": orders[-5:] if len(orders) >= 5 else orders,
        "PARTIAL SLICE": orders[3:10] if len(orders) > 3 else orders
    }


def run_flow(order_list: list[dict[str, Any]]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """
    Run the full flow: history analyzer → goal engine.
    
    Args:
        order_list: List of orders
        
    Returns:
        Tuple of (analysis_result, goals_list)
    """
    # Phase 1: Analyze history
    analysis = analyze_history(order_list)
    
    # Phase 2: Generate goals
    goals = suggest_goals(analysis)
    
    return analysis, goals


def print_separator(title: str) -> None:
    """Print a formatted separator with title."""
    width = 40
    print("\n" + "=" * width)
    print(f"TEST CASE: {title}")
    print("=" * width)


def print_section(title: str) -> None:
    """Print a section header."""
    print(f"\n--- {title} ---")


def print_top_goal(goals: list[dict[str, Any]]) -> None:
    """
    Print the top priority goal.
    
    Args:
        goals: List of goal dictionaries
    """
    if not goals:
        print("\n⚠ No goals generated")
        return
    
    # Find highest priority goal
    priority_order = {"high": 0, "medium": 1, "low": 2}
    sorted_goals = sorted(goals, key=lambda g: priority_order.get(g.get("priority", "low"), 2))
    top_goal = sorted_goals[0]
    
    print(f"\n🎯 Top Goal: {top_goal['goal_name']} ({top_goal['priority'].upper()} Priority)")


def run_tests() -> None:
    """
    Main test runner function.
    """
    # Determine data file path
    base_dir = Path(__file__).parent
    data_file = base_dir/ "data" / "mock_orders.json"
    
    print("🚀 Starting Phase 1 & 2 Validation Tests")
    print(f"📂 Loading data from: {data_file}")
    
    # Load orders
    try:
        orders = load_orders(data_file)
        print(f"✅ Loaded {len(orders)} orders successfully")
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return
    
    # Create test cases
    test_cases = create_test_cases(orders)
    
    # Run each test case
    for case_name, case_orders in test_cases.items():
        print_separator(case_name)
        print(f"📊 Orders in dataset: {len(case_orders)}")
        
        # Run flow
        analysis, goals = run_flow(case_orders)
        
        # Print history analysis
        print_section("History Analysis")
        print(json.dumps(analysis, indent=2))
        
        # Print suggested goals
        print_section("Suggested Goals")
        print(json.dumps(goals, indent=2))
        
        # Print summary
        print_section("Summary")
        summary = generate_summary(goals)
        print(summary)
        
        # Print top goal
        print_top_goal(goals)
    
    print("\n" + "=" * 40)
    print("✅ All tests completed successfully!")
    print("=" * 40)


if __name__ == "__main__":
    run_tests()