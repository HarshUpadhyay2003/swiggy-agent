# Investigation 4 & 5 — Conversation Policy & Transition Classification Audit

## Layer 2.5 Execution Verification

Did `ConversationIntelligenceEngine` (Layer 2.5) execute during production requests?

| Manual Query / Flow | Entered Layer 2.5? | Reason / Bypass Location |
|---|---|---|
| `"Dessert under 100"` | **NO** | `ChatOrchestrator` calls `ContextEngine.recommend_food()` directly, which calls `ConstraintLifecycleEngine.process_lifecycle()` without Layer 2.5. |
| `"Italian meals"` | **NO** | Bypassed in `ChatOrchestrator` / `ContextEngine`. |
| `"Healthy meals"` | **NO** | Bypassed in `ChatOrchestrator` / `ContextEngine`. |
| `"under 300"` | **NO** | Bypassed in `ChatOrchestrator` / `ContextEngine`. |

---

## Transition Classification Audit (Replay of Core Scenarios in Test vs Production)

### Scenario A: `"Dessert under 100"` → `"Italian meals"`
- **Raw Input:** `"Italian meals"`
- **Expected Classification:** `NEW_SEARCH`
- **Test Classification:** `NEW_SEARCH` (Confidence: 0.95, Reason: Category/Cuisine primary concept switch detected)
- **Production Classification:** **NOT EXECUTED** (`ChatOrchestrator` treats turn as `is_followup=True` because `active_domain=="recommendations"`, merging `last_entities`).

### Scenario B: `"Healthy meals"` → `"under 300"`
- **Raw Input:** `"under 300"`
- **Expected Classification:** `REFINEMENT`
- **Test Classification:** `REFINEMENT` (Confidence: 0.95, Reason: Budget modifier connector `"under"` matched)
- **Production Classification:** **NOT EXECUTED** in Layer 2.5. (Handled via manual entity merge in `_handle_context_aware_followup`).

### Scenario C: `"Indian meals"` → `"make it spicy"`
- **Raw Input:** `"make it spicy"`
- **Expected Classification:** `REFINEMENT`
- **Test Classification:** `REFINEMENT` (Confidence: 0.95, Reason: Taste modifier connector `"make it spicy"` matched)
- **Production Classification:** **NOT EXECUTED** in Layer 2.5.

### Scenario D: `"Never mind"` → `"Recommend dinner"`
- **Raw Input:** `"Recommend dinner"`
- **Expected Classification:** `NEW_SEARCH`
- **Test Classification:** `NEW_SEARCH` (Confidence: 0.95, Reason: Reset phrase `"Never mind"` / general intent `"Recommend dinner"`)
- **Production Classification:** **NOT EXECUTED** in Layer 2.5.
