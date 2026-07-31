# Investigation 6 Detail — Memory Lifecycle Trace

## State Transitions Trace

### Production Scenario Trace: `"Dessert under 100"` followed by `"Italian meals"`

```text
STEP 1: Turn 1 ("Dessert under 100")
  - ChatOrchestrator stores entities in conversation_memory: {"budget_max": 100.0, "category": "dessert"}
  - SessionState.recommendation_memory stores: category="dessert", budget=100.0
  - Active Domain set to: "recommendations"

STEP 2: Turn 2 ("Italian meals")
  - ChatOrchestrator receives request.
  - Active domain is "recommendations".
  - ChatOrchestrator._handle_context_aware_followup() executes:
      merged_context = dict(user_context)
      merged_context.update(last_entities)  # <--- INJECTS budget_max=100.0
      merged_context.update(entities)       # <--- INJECTS cuisine_type="Italian"
  - ContextEngine.recommend_food receives: {"cuisine_type": "Italian", "max_budget": 100.0}
  - ContextEngine builds RecommendationRequest([cuisine_type=Italian, max_budget=100.0])
  - Layer 2 process_lifecycle merges them.
  - Result: max_budget=100.0 is treated as an explicit incoming user constraint for Turn 2!
```
