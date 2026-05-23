from typing import Any, Dict, List, Optional

try:
    from app.services.catalog_service import CatalogService
    from app.services.cart_service import CartService
    from app.services.planner import MealPlanner
except ImportError:
    from .catalog_service import CatalogService
    from .cart_service import CartService
    from .planner import MealPlanner


class ActionExecutor:
    """Executes an action graph transactionally across different domains."""

    def __init__(self, cart_service: CartService, catalog_service: CatalogService, meal_planner: MealPlanner) -> None:
        self.cart_service = cart_service
        self.catalog_service = catalog_service
        self.meal_planner = meal_planner

    def execute_batch(
        self, 
        session_id: str, 
        session_state: Any, 
        actions: List[Dict[str, Any]], 
        message: str,
        user_preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a batch of parsed LLM actions affecting cart or planner domains.
        Calculates updates atomically.
        """
        results: Dict[str, Any] = {
            "actions_executed": [],
            "cart": None,
            "meal_plan": None
        }

        cart_ops = []
        planner_ops = []

        for action in actions:
            action_type = action.get("type", "")
            if action_type.startswith("cart_"):
                cart_ops.append(action)
            elif action_type.startswith("planner_"):
                planner_ops.append(action)

        # Execute Cart Actions
        if cart_ops:
            final_cart, executed = self.cart_service.batch_update_cart(session_id, cart_ops)
            results["cart"] = final_cart
            results["actions_executed"].extend(executed)

        # Execute Planner Actions
        if planner_ops:
            existing_plan = None
            if session_state and session_state.planner_state and session_state.planner_state.active_plan:
                existing_plan = session_state.planner_state.active_plan
                
            executed = []
            current_plan = existing_plan
            
            for op in planner_ops:
                action_type = op.get("type")
                if action_type == "planner_modify" and current_plan:
                    # Map action data to entities format expected by modify_existing_plan
                    entities = {
                        "target_day": op.get("target_day"),
                        "target_meal": op.get("target_meal"),
                        "replacement_request": op.get("item") or op.get("replacement"),
                    }
                    current_plan = self.meal_planner.modify_existing_plan(current_plan, entities, message, user_preferences)
                    executed.append(f"Updated planner ({op.get('target_meal') or 'meals'})")
            
            if current_plan:
                results["meal_plan"] = current_plan
                results["actions_executed"].extend(executed)

        return results