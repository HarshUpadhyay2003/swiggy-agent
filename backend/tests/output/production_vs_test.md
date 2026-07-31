# Investigation 14 — Production vs Test Environment Audit

## Environment Comparison

| Dimension | Test Environment (`test_rc1_conversation_policy.py`) | Production Environment (`POST /chat`) |
|---|---|---|
| **Entry Point** | Directly instantiates `ConversationIntelligenceEngine()` and `ConstraintLifecycleEngine()` | Enters FastAPI `POST /chat` -> `ChatOrchestrator` -> `ContextEngine` |
| **Layer 2.5 Registration** | **EXPLICITLY WIRED** into test runner | **NOT INSTANTIATED** in `ChatOrchestrator` or `ContextEngine` |
| **Session Manager Instance** | Shared instance passed explicitly | `session_manager` singleton inside `ChatOrchestrator` |
| **Follow-up Routing** | Bypassed | Controlled by `ChatOrchestrator._handle_context_aware_followup` |
| **Context Extraction** | Explicit `RecommendationRequest` constructed in test methods | Extracted via regex in `ChatOrchestrator._extract_recommendation_context` |

---

## Key Discrepancy

In tests, `ConversationIntelligenceEngine.process()` is explicitly invoked to evaluate transition types (`NEW_SEARCH` vs `REFINEMENT`) and clear context memory. In production, `ChatOrchestrator` handles routing and bypasses Layer 2.5 entirely, manually merging previous-turn entities into the current request context.
