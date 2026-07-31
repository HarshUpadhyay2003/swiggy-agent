# Investigation 6 & 7 — Memory Lifecycle & Effective Recommendation Request Audit

## Memory Lifecycle Audit

### Scenario: `"Dessert under 100"` → `"Italian meals"`

#### TEST ENVIRONMENT EXECUTION

```text
BEFORE TURN 2:
  - Conversation Memory    : cuisine_type=None, category="dessert", budget=100.0
  - Recommendation Context : category="dessert", budget=100.0
  - Persistent Preferences  : None

CLASSIFICATION: NEW_SEARCH

AFTER CLASSIFICATION & RESET:
  - Removed Constraints    : ['category=dessert', 'budget=100.0']
  - Retained Constraints   : None
  - Added Constraints     : ['cuisine_type=Italian']
  - Merged Constraints    : ['cuisine_type=Italian']

EFFECTIVE REQUEST (Layer 2 Output):
  EffectiveRecommendationRequest(
      cuisine_type="Italian",
      max_budget=None,
      category=None
  )
```

#### PRODUCTION ENVIRONMENT EXECUTION

```text
BEFORE TURN 2:
  - ChatOrchestrator conversation_memory.last_entities : {"budget_max": 100.0, "category": "dessert"}
  - SessionState.recommendation_memory                 : category="dessert", budget=100.0
  - Persistent Preferences                              : None

ORCHESTRATOR FOLLOW-UP MERGE:
  - ChatOrchestrator._handle_context_aware_followup() injects last_entities {"budget_max": 100.0} into user_context!
  - _extract_recommendation_context creates context = {"cuisine_type": "Italian", "max_budget": 100.0}

AFTER LAYER 2 (ConstraintLifecycleEngine):
  - Removed Constraints    : None
  - Retained Constraints   : ['category=dessert', 'budget=100.0']
  - Added Constraints     : ['cuisine_type=Italian', 'max_budget=100.0']
  - Merged Constraints    : ['cuisine_type=Italian', 'max_budget=100.0', 'category=dessert']

EFFECTIVE REQUEST (Layer 2 Output):
  EffectiveRecommendationRequest(
      cuisine_type="Italian",
      max_budget=100.0,
      category="dessert"
  )
```

---

## Stale Constraint Verification

- **Did stale constraints exist in Production?** **YES.** `max_budget=100.0` and `category=dessert` survived and contaminated the effective request for `"Italian meals"`.
- **Did stale constraints exist in Test?** **NO.** `clear_recommendation_context()` wiped them on `NEW_SEARCH`.
