"""
Test conversations dataset for Recommendation Pipeline Verification Framework.
Contains multi-turn conversations testing Ephemeral Memory, Session Memory, Domain Switching, Semantic Cleanup, and Budget Persistence.
"""

TEST_CONVERSATIONS = [
    {
        "id": "conv_1",
        "name": "Conversation 1 — Ephemeral Memory Expiration & Time Defaults",
        "messages": [
            "Suggest dinner",
            "Healthy meals",
            "Suggest meals"
        ]
    },
    {
        "id": "conv_2",
        "name": "Conversation 2 — Session Memory Accumulation & Budget Persistence",
        "messages": [
            "Indian meals",
            "under 300",
            "spicy",
            "Suggest meals"
        ]
    },
    {
        "id": "conv_3",
        "name": "Conversation 3 — Domain Switching (Meal -> Dessert -> Beverage)",
        "messages": [
            "Suggest dinner under 500",
            "Desserts under 200",
            "Suggest beverages"
        ]
    },
    {
        "id": "conv_4",
        "name": "Conversation 4 — Semantic Memory Cleanup (Cuisine/Health -> Burgers)",
        "messages": [
            "Healthy Indian meals under 400",
            "Suggest burgers"
        ]
    },
    {
        "id": "conv_5",
        "name": "Conversation 5 — Specific Category Focus Protection",
        "messages": [
            "Suggest burgers",
            "Suggest coffee"
        ]
    },
    {
        "id": "conv_6",
        "name": "Conversation 6 — Multi-Turn Budget Refinement & Expiration",
        "messages": [
            "Italian meals",
            "under 500",
            "spicy",
            "under 300"
        ]
    },
    {
        "id": "conv_7",
        "name": "Conversation 7 — High Protein & Fitness Memory Boundaries",
        "messages": [
            "High protein dinner",
            "Suggest meals"
        ]
    },
    {
        "id": "conv_8",
        "name": "Conversation 8 — Complete 9-Turn Stress Sequence",
        "messages": [
            "Suggest dinner",
            "Healthy meals",
            "Indian meals",
            "under 300",
            "Suggest burgers",
            "Desserts",
            "Coffee",
            "Italian breakfast",
            "Suggest meals"
        ]
    }
]
