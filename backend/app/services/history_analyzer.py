"""
History Analyzer Service

Analyzes user order history to extract insights about spending patterns,
ordering behavior, and health indicators.
"""

from datetime import datetime
from typing import Any


def analyze_history(order_list: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Main function to analyze order history.
    
    Args:
        order_list: List of order dictionaries with item_name, price, timestamp
        
    Returns:
        Dictionary containing analysis results
    """
    if not order_list:
        return _empty_analysis()
    
    # Validate and filter valid orders
    valid_orders = _validate_orders(order_list)
    
    if not valid_orders:
        return _empty_analysis()
    
    # Calculate all metrics
    avg_spend = calculate_average_spend(valid_orders)
    top_items = get_top_items(valid_orders, top_n=3)
    
    # Late night metrics
    late_night = detect_late_night_orders(valid_orders)
    late_night_pct = calculate_late_night_percentage(valid_orders)
    
    # Improved monthly/weekly spend calculation
    weekly_spend = estimate_weekly_spend(valid_orders)
    monthly_spend = weekly_spend * 4
    
    # Spend category based on average spend
    spend_category = get_spend_category(avg_spend)
    
    # Improved health score with ratio-based logic
    health, junk_ratio = compute_health_score(valid_orders)
    
    # Clean pattern string generation (only meaningful insights)
    pattern = _generate_ordering_pattern(late_night_pct, junk_ratio)
    
    # Budget risk based on weekly spend
    budget_risk = calculate_budget_risk(weekly_spend)
    
    # Generate user insight from combined metrics
    user_insight = generate_user_insight(late_night, budget_risk, health, late_night_pct)
    
    return {
        "average_spend_per_order": round(avg_spend, 2),
        "most_frequent_items": top_items,
        "late_night_ordering": late_night,
        "late_night_percentage": late_night_pct,
        "estimated_monthly_spend": _round_to_nearest_50(monthly_spend),
        "weekly_spend_estimate": _round_to_nearest_50(weekly_spend),
        "health_score": health,
        "spend_category": spend_category,
        "ordering_pattern": pattern,
        "budget_risk": budget_risk,
        "user_insight": user_insight
    }


def calculate_average_spend(orders: list[dict[str, Any]]) -> float:
    """
    Calculate average spend per order.
    
    Args:
        orders: List of valid order dictionaries
        
    Returns:
        Average spend amount
    """
    if not orders:
        return 0.0
    
    total = sum(order.get("price", 0) for order in orders)
    return total / len(orders)


def get_top_items(orders: list[dict[str, Any]], top_n: int = 3) -> list[str]:
    """
    Get most frequently ordered items (normalized).
    
    Args:
        orders: List of order dictionaries
        top_n: Number of top items to return
        
    Returns:
        List of most frequent item names (title case)
    """
    if not orders:
        return []
    
    item_counts: dict[str, int] = {}
    for order in orders:
        # Normalize: lowercase and strip whitespace
        item_name = order.get("item_name", "").lower().strip()
        if item_name:
            item_counts[item_name] = item_counts.get(item_name, 0) + 1
    
    # Sort by count descending
    sorted_items = sorted(item_counts.items(), key=lambda x: x[1], reverse=True)
    
    # Return title case for clean output
    return [item.title() for item, _ in sorted_items[:top_n]]


def detect_late_night_orders(orders: list[dict[str, Any]]) -> bool:
    """
    Detect if user frequently orders after 10 PM.
    
    Args:
        orders: List of order dictionaries
        
    Returns:
        True if more than 30% of orders are after 10 PM
    """
    if not orders:
        return False
    
    late_night_count = 0
    for order in orders:
        timestamp = order.get("timestamp")
        if timestamp:
            try:
                order_time = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                if order_time.hour >= 22:
                    late_night_count += 1
            except (ValueError, TypeError):
                continue
    
    late_night_ratio = late_night_count / len(orders)
    return late_night_ratio > 0.3


def calculate_late_night_percentage(orders: list[dict[str, Any]]) -> int:
    """
    Calculate percentage of orders placed after 10 PM.
    
    Logic:
    - Count orders after 10 PM (hour >= 22)
    - Calculate: (late_night_orders / total_orders) * 100
    - Round to nearest integer
    
    Args:
        orders: List of order dictionaries
        
    Returns:
        Integer percentage of late night orders
    """
    if not orders:
        return 0
    
    late_night_count = 0
    for order in orders:
        timestamp = order.get("timestamp")
        if timestamp:
            try:
                order_time = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                if order_time.hour >= 22:
                    late_night_count += 1
            except (ValueError, TypeError):
                continue
    
    percentage = (late_night_count / len(orders)) * 100
    return round(percentage)


def get_spend_category(avg_spend: float) -> str:
    """
    Determine spend category based on average spend per order.
    
    Thresholds:
    - > 300 → "high"
    - 150–300 → "medium"
    - < 150 → "low"
    
    Args:
        avg_spend: Average spend per order
        
    Returns:
        Spend category: 'low', 'medium', or 'high'
    """
    if avg_spend > 300:
        return "high"
    elif avg_spend >= 150:
        return "medium"
    else:
        return "low"


def estimate_monthly_spend(orders: list[dict[str, Any]]) -> float:
    """
    Estimate monthly spend based on order history.
    
    Logic:
    - Calculate unique days in dataset using timestamps
    - Compute orders_per_day = total_orders / unique_days
    - weekly_orders = orders_per_day * 7
    - weekly_spend = weekly_orders * average_spend
    - monthly_spend = weekly_spend * 4
    
    Args:
        orders: List of order dictionaries
        
    Returns:
        Estimated monthly spend
    """
    if not orders:
        return 0.0
    
    avg_spend = calculate_average_spend(orders)
    
    if len(orders) < 2:
        return avg_spend * 10  # Assume 10 orders/month if only 1 order
    
    # Find unique days from timestamps
    dates = set()
    for order in orders:
        timestamp = order.get("timestamp")
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                dates.add(dt.date())
            except (ValueError, TypeError):
                continue
    
    unique_days = len(dates)
    if unique_days == 0:
        return avg_spend * 10
    
    orders_per_day = len(orders) / unique_days
    weekly_orders = orders_per_day * 7
    weekly_spend = weekly_orders * avg_spend
    monthly_spend = weekly_spend * 4
    
    return monthly_spend


def compute_health_score(orders: list[dict[str, Any]]) -> tuple[str, float]:
    """
    Compute health score based on junk food ratio.
    
    Logic:
    - Define junk_items and healthy_items
    - Count junk and healthy orders
    - Compute junk_ratio = junk_orders / total_orders
    - Return score based on ratio thresholds:
        - junk_ratio > 0.6 → "low"
        - 0.3–0.6 → "medium"
        - < 0.3 → "high"
    
    Args:
        orders: List of order dictionaries
        
    Returns:
        Tuple of (health_score, junk_ratio)
    """
    if not orders:
        return "medium", 0.0
    
    # Define junk and healthy item keywords
    junk_items = ["pizza", "burger", "fries", "wings", "fried", "momos"]
    healthy_items = ["salad", "juice", "grilled", "dal"]
    
    junk_count = 0
    healthy_count = 0
    
    for order in orders:
        item_name = order.get("item_name", "").lower()
        
        # Check for junk food keywords
        if any(junk in item_name for junk in junk_items):
            junk_count += 1
        # Check for healthy food keywords
        if any(healthy in item_name for healthy in healthy_items):
            healthy_count += 1
    
    total = len(orders)
    junk_ratio = junk_count / total if total > 0 else 0.0
    
    # Determine health score based on junk ratio thresholds
    if junk_ratio > 0.6:
        health = "low"
    elif junk_ratio >= 0.3:
        health = "medium"
    else:
        health = "high"
    
    return health, junk_ratio


def _validate_orders(orders: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Validate and filter orders with required fields.
    
    Args:
        orders: List of raw order dictionaries
        
    Returns:
        List of valid orders
    """
    valid_orders = []
    for order in orders:
        if not isinstance(order, dict):
            continue
        if "item_name" not in order or "price" not in order:
            continue
        try:
            price = float(order["price"])
            if price < 0:
                continue
            valid_orders.append({
                "item_name": str(order["item_name"]),
                "price": price,
                "timestamp": order.get("timestamp", "")
            })
        except (ValueError, TypeError):
            continue
    return valid_orders


def estimate_weekly_spend(orders: list[dict[str, Any]]) -> float:
    """
    Estimate weekly spend based on order history.
    
    Logic:
    - Calculate unique days in dataset using timestamps
    - Compute orders_per_day = total_orders / unique_days
    - weekly_orders = orders_per_day * 7
    - weekly_spend = weekly_orders * average_spend
    
    Args:
        orders: List of order dictionaries
        
    Returns:
        Estimated weekly spend
    """
    if not orders:
        return 0.0
    
    avg_spend = calculate_average_spend(orders)
    
    if len(orders) < 2:
        return avg_spend * 2.5  # Assume ~2.5 orders/week
    
    # Find unique days from timestamps
    dates = set()
    for order in orders:
        timestamp = order.get("timestamp")
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                dates.add(dt.date())
            except (ValueError, TypeError):
                continue
    
    unique_days = len(dates)
    if unique_days == 0:
        return avg_spend * 2.5
    
    orders_per_day = len(orders) / unique_days
    weekly_orders = orders_per_day * 7
    weekly_spend = weekly_orders * avg_spend
    
    return weekly_spend


def calculate_budget_risk(weekly_spend: float) -> str:
    """
    Calculate budget risk based on weekly spend.
    
    Thresholds:
    - weekly_spend > 1500 → "high"
    - 800–1500 → "medium"
    - < 800 → "low"
    
    Args:
        weekly_spend: Estimated weekly spend amount
        
    Returns:
        Budget risk level: 'low', 'medium', or 'high'
    """
    if weekly_spend > 1500:
        return "high"
    elif weekly_spend >= 800:
        return "medium"
    else:
        return "low"


def generate_user_insight(late_night: bool, budget_risk: str, health: str, late_night_pct: int) -> str:
    """
    Generate a single insight sentence combining late night, budget, and health.
    
    Logic:
    - Check late night ordering
    - Check budget risk level
    - Check health score
    - Combine into one actionable sentence
    
    Args:
        late_night: Whether user orders late at night
        budget_risk: Budget risk level
        health: Health score
        late_night_pct: Percentage of late night orders
        
    Returns:
        Insight sentence string
    """
    insights = []
    
    # Late night insight
    if late_night:
        frequency = "frequently" if late_night_pct > 50 else "occasionally"
        insights.append(f"You {frequency} order late at night")
    
    # Budget risk insight
    if budget_risk == "high":
        insights.append("are overspending weekly")
    elif budget_risk == "medium":
        insights.append("have moderate weekly spending")
    else:
        insights.append("are managing your budget well")
    
    # Health insight
    if health == "low":
        insights.append("and should reduce junk food consumption")
    elif health == "high":
        insights.append("and maintain healthy eating habits")
    # Don't add health phrase for "medium" to keep it concise
    
    # Combine into single sentence using "and" for natural flow
    if len(insights) >= 2:
        if len(insights) == 3:
            return f"{insights[0]}, {insights[1]}, and {insights[2]}."
        elif len(insights) == 2:
            return f"{insights[0]} and {insights[1]}."
    
    return "No significant insights available."


def _empty_analysis() -> dict[str, Any]:
    """
    Return empty analysis result.
    
    Returns:
        Default empty analysis dictionary
    """
    return {
        "average_spend_per_order": 0,
        "most_frequent_items": [],
        "late_night_ordering": False,
        "late_night_percentage": 0,
        "estimated_monthly_spend": 0,
        "weekly_spend_estimate": 0,
        "health_score": "medium",
        "spend_category": "low",
        "ordering_pattern": "No order history available",
        "budget_risk": "low",
        "user_insight": "No order history to analyze."
    }


def _round_to_nearest_50(value: float) -> int:
    """
    Round monetary value to nearest 50 for cleaner product-centric output.
    
    Args:
        value: Raw monetary value
        
    Returns:
        Value rounded to nearest 50
    """
    return int(round(value / 50) * 50)


def _generate_ordering_pattern(
    late_night_pct: int,
    junk_ratio: float
) -> str:
    """
    Generate clean ordering pattern with only meaningful insights.
    
    Includes only relevant phrases:
    - "late-night-heavy" (if late_night_pct > 50)
    - "high junk consumption" (if junk_ratio > 0.6)
    - "balanced diet" (if mixed)
    
    Joined with comma, no redundant phrases.
    
    Args:
        late_night_pct: Percentage of late night orders
        junk_ratio: Ratio of junk food orders
        
    Returns:
        Clean pattern description string
    """
    patterns = []
    
    # Time-based pattern (only if > 50% late night)
    if late_night_pct > 50:
        patterns.append("late-night-heavy")
    
    # Health-based pattern
    if junk_ratio > 0.6:
        patterns.append("high junk consumption")
    elif junk_ratio < 0.3:
        patterns.append("health-conscious")
    else:
        patterns.append("balanced diet")
    
    # Join with comma
    return ", ".join(patterns) if patterns else "No significant pattern"