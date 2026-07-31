# RC1.1 — Production Integration Investigation Summary

## Final Executive Finding
The RC1 conversation policy tests passed in isolation because the test suite directly instantiated and invoked **Layer 2.5 (`ConversationIntelligenceEngine`)**. However, in the production environment (`POST /chat`), **Layer 2.5 was never wired into `ChatOrchestrator` or `ContextEngine`**.

Additionally, `ChatOrchestrator._handle_context_aware_followup()` manually merged `last_entities` from previous turns (`budget_max: 100`) directly into incoming `user_context`, causing `"Italian meals"` to be received by retrieval as `Italian + max_budget=100`.

---

## Deliverables Generated in `backend/tests/output/`

1. [`rc1_production_callgraph.md`](file:///c:/Users/mohit/Desktop/swiggy-agent/backend/tests/output/rc1_production_callgraph.md) — Trace of production request path (`POST /chat`)
2. [`rc1_test_callgraph.md`](file:///c:/Users/mohit/Desktop/swiggy-agent/backend/tests/output/rc1_test_callgraph.md) — Trace of test request path (`test_rc1_conversation_policy.py`)
3. [`rc1_execution_diff.md`](file:///c:/Users/mohit/Desktop/swiggy-agent/backend/tests/output/rc1_execution_diff.md) — Side-by-side call graph comparison table & divergence points
4. [`conversation_policy_runtime.md`](file:///c:/Users/mohit/Desktop/swiggy-agent/backend/tests/output/conversation_policy_runtime.md) — Layer 2.5 execution verification & scenario audit
5. [`effective_request_audit.md`](file:///c:/Users/mohit/Desktop/swiggy-agent/backend/tests/output/effective_request_audit.md) — Memory lifecycle audit & stale constraint proof
6. [`candidate_pipeline_trace.md`](file:///c:/Users/mohit/Desktop/swiggy-agent/backend/tests/output/candidate_pipeline_trace.md) — Retriever, Ranking, Semantic & Response pipeline trace
7. [`layer25_execution.md`](file:///c:/Users/mohit/Desktop/swiggy-agent/backend/tests/output/layer25_execution.md) — Evidence of Layer 2.5 bypass in production
8. [`memory_lifecycle_trace.md`](file:///c:/Users/mohit/Desktop/swiggy-agent/backend/tests/output/memory_lifecycle_trace.md) — Step-by-step state transition breakdown
9. [`runtime_state_ownership.md`](file:///c:/Users/mohit/Desktop/swiggy-agent/backend/tests/output/runtime_state_ownership.md) — Component state ownership map & duplicate ownership highlight
10. [`production_vs_test.md`](file:///c:/Users/mohit/Desktop/swiggy-agent/backend/tests/output/production_vs_test.md) — Environment comparison between test runner & production server
11. [`root_cause_report.md`](file:///c:/Users/mohit/Desktop/swiggy-agent/backend/tests/output/root_cause_report.md) — Root causes backed by empirical code evidence
12. [`rc1_investigation_summary.md`](file:///c:/Users/mohit/Desktop/swiggy-agent/backend/tests/output/rc1_investigation_summary.md) — This investigation summary report

---

## Strict Read-Only Compliance
- **No production code was modified.**
- **No tests were modified.**
- **No implementation plan was created.**
- **No fix was applied.**

Investigation is complete. Stopping per final stop condition.
