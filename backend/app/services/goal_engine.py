"""
Goal Engine Service

Generates personalized user goals based on analyzed history data.
Phase 2 of the Swiggy AI Agent system.
"""

from typing import Any


def suggest_goals(user_profile: dict) -> list[dict[str, Any]]:
    """
    Generate personalized goals based on user profile data.
    
    Args:
        user_profile: Dictionary containing user history analysis results
        
    Returns:
        List of 3 goal dictionaries with id, name, description, priority, reasoning
    """
    if not user_profile:
        return _default_goals()
    
    goals = []
    goal_id = 1
    
    # Extract profile values with defaults
    budget_risk = user_profile.get("budget_risk", "low")
    weekly_spend = user_profile.get("weekly_spend_estimate", 0)
    health_score = user_profile.get("health_score", "medium")
    late_night_pct = user_profile.get("late_night_percentage", 0)
    spending = user_profile.get("average_spend_per_order", 0)
    spend_category = user_profile.get("spend_category", "medium")
    
    # Goal 1: Reduce Spending (adaptive priority)
    spending_goal = _create_spending_goal(budget_risk, weekly_spend, spending, spend_category)
    if spending_goal:
        goals.append(spending_goal)
        goal_id += 1
    
    # Goal 2: Improve Eating Habits (adaptive priority)
    eating_goal = _create_eating_goal(health_score, late_night_pct)
    if eating_goal:
        goals.append(eating_goal)
        goal_id += 1
    
    # Goal 3: Maintain Lifestyle (always included)
    maintain_goal = _create_maintain_goal(budget_risk, health_score, late_night_pct)
    goals.append(maintain_goal)
    
    return goals


def _create_spending_goal(budget_risk: str, weekly_spend: int, spending: float, spend_category: str) -> dict[str, Any]:
    """
    Create spending reduction goal with adaptive priority.
    
    Priority Logic:
    - high if budget_risk = high AND spend_category != low
    - medium if budget_risk = medium OR weekly_spend > 1500
    - low if spend_category = low (already spending less)
    """
    # Check trigger conditions
    should_include = budget_risk == "high" or weekly_spend > 1500 or budget_risk == "medium"
    
    if not should_include and budget_risk != "medium":
        return {}
    
    # Determine adaptive priority
    if budget_risk == "high" and spend_category != "low":
        priority = "high"
    elif budget_risk == "medium" or weekly_spend > 1500:
        priority = "medium"
    else:
        priority = "low"
    
    # Generate varied reasoning based on data
    reasoning_variants = [
        f"Your current weekly spend of ₹{weekly_spend} exceeds recommended limits",
        f"Analysis shows spending patterns that need optimization",
        f"Budget management is crucial given your order frequency"
    ]
    
    if budget_risk == "high":
        reasoning = reasoning_variants[0]
    elif budget_risk == "medium":
        reasoning = reasoning_variants[1]
    else:
        reasoning = reasoning_variants[2]
    
    return {
        "goal_id": 1,
        "goal_name": "Reduce Spending",
        "description": "Optimize your weekly food expenses to stay within budget",
        "priority": priority,
        "reasoning": f"{reasoning}."
    }


def _create_eating_goal(health_score: str, late_night_pct: int) -> dict[str, Any]:
    """
    Create eating habits improvement goal with adaptive priority.
    
    Priority Logic:
    - high if health_score = low OR late_night_percentage > 50
    - medium if health_score = medium OR late_night > 40
    - low if health_score = high
    """
    # Check trigger conditions
    should_include = health_score in ["low", "medium", "high"] or late_night_pct > 40
    
    if not should_include:
        return {}
    
    # Determine adaptive priority based on late night percentage
    if health_score == "low" or late_night_pct > 50:
        priority = "high"
    elif health_score == "medium" or late_night_pct > 40:
        priority = "medium"
    else:
        priority = "low"
    
    # Generate varied reasoning
    if late_night_pct > 50:
        reasoning = f"Over {late_night_pct}% of your orders occur after 10 PM, impacting sleep and health"
    elif health_score == "low":
        reasoning = "High junk food consumption is affecting your health score"
    elif health_score == "medium":
        reasoning = "Your dietary choices have opportunities for improvement"
    elif late_night_pct > 40:
        reasoning = f"Late-night ordering ({late_night_pct}%) contributes to unhealthy patterns"
    else:
        reasoning = "Maintaining healthy eating patterns is essential for wellbeing"
    
    return {
        "goal_id": 2,
        "goal_name": "Improve Eating Habits",
        "description": "Reduce late-night and unhealthy food consumption",
        "priority": priority,
        "reasoning": f"{reasoning}."
    }


def _create_maintain_goal(budget_risk: str, health_score: str, late_night_pct: int) -> dict[str, Any]:
    """
    Create lifestyle maintenance goal with adaptive priority.
    
    Priority Logic:
    - low if budget_risk = high OR health_score = low OR late_night > 50
    - medium if balanced
    - low if health_score = high (already healthy)
    """
    # Determine priority based on overall balance
    if budget_risk == "high" or health_score == "low" or late_night_pct > 50:
        priority = "low"
    elif health_score == "high":
        priority = "low"  # Already healthy, maintain mode
    else:
        priority = "medium"
    
    # Generate varied reasoning
    if priority == "low" and (budget_risk == "high" or late_night_pct > 50):
        reasoning = "Focus on higher-priority goals first; maintain stable habits where possible"
    elif health_score == "high":
        reasoning = "Your healthy eating patterns are commendable; continue maintaining them"
    else:
        reasoning = "Your lifestyle habits are reasonably balanced with areas for targeted enhancement"
    
    return {
        "goal_id": 3,
        "goal_name": "Maintain Lifestyle",
        "description": "Continue healthy eating patterns while working on other goals",
        "priority": priority,
        "reasoning": reasoning
    }


def generate_summary(goals: list[dict[str, Any]]) -> str:
    """
    Generate a human-readable summary from goals list.
    
    Args:
        goals: List of goal dictionaries
        
    Returns:
        Summary sentence string
    """
    if not goals:
        return "No goals available to generate summary."
    
    # Extract goal names and priorities
    high_priority = [g["goal_name"] for g in goals if g.get("priority") == "high"]
    medium_priority = [g["goal_name"] for g in goals if g.get("priority") == "medium"]
    
    # Build summary
    if high_priority:
        # Capitalize properly
        goal_text = ", ".join([g.lower().replace(g.lower()[0], g.lower()[0].upper(), 1) for g in high_priority])
        return f"Based on your habits, we recommend focusing on {goal_text}."
    elif medium_priority:
        return f"Consider working on {', '.join(medium_priority).lower()} to improve your overall profile."
    else:
        return "Your current habits are well-balanced. Keep up the good work!"


def _default_goals() -> list[dict[str, Any]]:
    """
    Return default goals when user profile is empty.
    
    Returns:
        List of default goal dictionaries
    """
    return [
        {
            "goal_id": 1,
            "goal_name": "Analyze Spending",
            "description": "Start tracking your food expenses",
            "priority": "medium",
            "reasoning": "No spending data available to generate personalized goals"
        },
        {
            "goal_id": 2,
            "goal_name": "Review Eating Patterns",
            "description": "Monitor your food ordering habits",
            "priority": "medium",
            "reasoning": "No ordering data available to analyze eating patterns"
        },
        {
            "goal_id": 3,
            "goal_name": "Set Budget Limits",
            "description": "Define weekly and monthly food budgets",
            "priority": "low",
            "reasoning": "Establish financial boundaries for food spending"
        }
    ]


# Example usage for testing
if __name__ == "__main__":
    # Sample user profile from Phase 1
    sample_profile = {
        "average_spend_per_order": 270,
        "late_night_percentage": 53,
        "health_score": "medium",
        "spend_category": "medium",
        "budget_risk": "high",
        "ordering_pattern": "late-night-heavy, balanced diet",
        "user_insight": "You frequently order late at night and are overspending weekly.",
        "weekly_spend_estimate": 2200
    }
    
    # Generate goals
    goals = suggest_goals(sample_profile)
    
    print("=== Generated Goals ===")
    for goal in goals:
        print(f"\nGoal {goal['goal_id']}: {goal['goal_name']}")
        print(f"  Description: {goal['description']}")
        print(f"  Priority: {goal['priority']}")
        print(f"  Reasoning: {goal['reasoning']}")
    
    print("\n=== Summary ===")
    print(generate_summary(goals))