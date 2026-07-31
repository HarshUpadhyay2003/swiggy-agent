"""
Stage 4E Clarification Engine Module.
Detects ambiguous intent (e.g. "Chicken", "Coffee", "Healthy") when ambiguity exceeds threshold
and prompts structured clarification options instead of making arbitrary assumptions.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class ClarificationOption(BaseModel):
    option_id: str
    label: str
    implied_constraint_type: str
    implied_constraint_value: str


class ClarificationResponse(BaseModel):
    is_ambiguous: bool
    ambiguous_term: str
    clarification_prompt: str
    options: List[ClarificationOption]


class ClarificationEngine:
    """Detects intent ambiguity and generates structured user clarification prompts."""

    AMBIGUITY_MAP: Dict[str, Dict[str, Any]] = {
        "chicken": {
            "prompt": "Which type of chicken meal would you prefer?",
            "options": [
                ClarificationOption(option_id="opt_burger", label="Chicken Burgers & Wraps", implied_constraint_type="category", implied_constraint_value="burger"),
                ClarificationOption(option_id="opt_grilled", label="Healthy Grilled & Grain Bowls", implied_constraint_type="health_goal", implied_constraint_value="healthy"),
                ClarificationOption(option_id="opt_curry", label="Indian Chicken Curry & Rice", implied_constraint_type="cuisine_type", implied_constraint_value="Indian"),
            ]
        },
        "coffee": {
            "prompt": "What kind of coffee beverage are you looking for?",
            "options": [
                ClarificationOption(option_id="opt_cold", label="Iced Cold Coffee & Frappes", implied_constraint_type="taste_preference", implied_constraint_value="cold"),
                ClarificationOption(option_id="opt_hot", label="Hot Cappuccino & Espresso", implied_constraint_type="taste_preference", implied_constraint_value="hot"),
            ]
        },
        "healthy": {
            "prompt": "What is your primary health goal today?",
            "options": [
                ClarificationOption(option_id="opt_protein", label="High Protein Meals", implied_constraint_type="health_goal", implied_constraint_value="high_protein"),
                ClarificationOption(option_id="opt_lowcal", label="Low Calorie / Weight Loss", implied_constraint_type="health_goal", implied_constraint_value="weight_loss"),
                ClarificationOption(option_id="opt_keto", label="Keto & Salad Bowls", implied_constraint_type="diet", implied_constraint_value="keto"),
            ]
        },
    }

    def check_ambiguity(self, raw_query: str, extracted_constraints: List[Any]) -> Optional[ClarificationResponse]:
        """Checks if user prompt is ambiguous and requires clarification."""
        query_text = (raw_query or "").lower().strip()
        if query_text in self.AMBIGUITY_MAP and not extracted_constraints:
            info = self.AMBIGUITY_MAP[query_text]
            return ClarificationResponse(
                is_ambiguous=True,
                ambiguous_term=query_text,
                clarification_prompt=info["prompt"],
                options=info["options"],
            )
        return None
