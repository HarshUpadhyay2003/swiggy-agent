# Investigation 15 — Root Cause Summary

## Primary Question Answered
**Why does production behave differently from the RC1 tests although all tests pass?**

Because the RC1 unit tests explicitly instantiate and execute **Layer 2.5 (`ConversationIntelligenceEngine`)**, whereas the production call path (`POST /chat` -> `ChatOrchestrator` -> `ContextEngine`) **completely bypasses Layer 2.5** and manually merges previous-turn entities (`last_entities`) into the request context before Layer 2 is reached.

---

## Identified Root Causes (Backed by Empirical Code Evidence)

### Root Cause 1: Layer 2.5 (`ConversationIntelligenceEngine`) is Bypassed in Production
- **Evidence:** Grep search across `backend/app/` reveals **0 references** to `ConversationIntelligenceEngine` in `routes/chat.py`, `chat_orchestrator.py`, `context_engine.py`, or `recommendation_engine.py`.
- **Impact:** Layer 2.5 never executes in production. `RefinementDetector.classify_transition()` and `clear_recommendation_context()` are never called on `NEW_SEARCH` turns.
- **Confidence:** 100%

### Root Cause 2: `ChatOrchestrator._handle_context_aware_followup` Injects Stale Entities
- **Evidence:** In `backend/app/services/chat_orchestrator.py` (L205-224), `_handle_context_aware_followup()` unconditionally executes:
  ```python
  merged_context = dict(user_context)
  merged_context.update(last_entities)  # Injects budget_max: 100
  merged_context.update(entities)
  return self.handle_food_recommendation(message, merged_context)
  ```
- **Impact:** Previous-turn entities are forged as new explicit incoming user constraints in `raw_request`.
- **Confidence:** 100%

### Root Cause 3: Duplicate Conversation Memory Ownership
- **Evidence:** `ChatOrchestrator` maintains legacy `ConversationMemory` (`last_entities`), while Layer 2 maintains `SessionState.recommendation_memory`.
- **Impact:** `ChatOrchestrator` bypasses Layer 2 state management and forcibly merges stale context.
- **Confidence:** 100%
