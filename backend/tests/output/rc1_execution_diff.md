# Investigation 3 — Side-by-Side Call Graph Comparison

## Comparison Table

| Pipeline Stage | Test Path | Production Path | Same Execution Path? | DIVERGENCE REASON / POINT OF FAILURE |
|---|---|---|---|---|
| **API Endpoint / Router** | Bypass (`unittest`) | `POST /chat` (`chat.py`) | ❌ No | Production enters FastAPI router & ChatOrchestrator |
| **Chat Orchestrator** | Bypass | `ChatOrchestrator.handle_message` | ❌ No | Orchestrator handles classification & followup logic |
| **Follow-up Merger** | Bypass | `_handle_context_aware_followup` | ❌ No | **DIVERGENCE 1:** Injects `last_entities` (`budget_max: 100`) directly into `user_context` |
| **Context Extraction** | Explicit `RecommendationRequest` | `_extract_recommendation_context` | ❌ No | Extracted context receives injected `max_budget=100` |
| **Context Engine Adapter** | Bypass | `ContextEngine.recommend_food` | ❌ No | Translates dictionary context into `RecommendationRequest` |
| **Layer 2.5 Conversation Intelligence** | ✅ **EXECUTED** (`ConversationIntelligenceEngine`) | ❌ **BYPASSED (0 calls)** | ❌ **No** | **DIVERGENCE 2 (PRIMARY ROOT CAUSE):** Layer 2.5 is NEVER called in production |
| **Layer 2 State Lifecycle** | ✅ `process_lifecycle` | ✅ `process_lifecycle` | ⚠️ Partial | Production passes corrupted `raw_request` containing injected budget |
| **Candidate Retriever** | ✅ `CandidateRetriever` | ✅ `CandidateRetriever` | ✅ Yes | Production retriever filters out Italian items due to budget <= 100 |
| **Ranking Engine** | ✅ `RankingEngine` | ✅ `RankingEngine` | ✅ Yes | Identical execution |
| **Semantic Engine** | ✅ `SemanticRecommendationEngine` | ✅ `SemanticRecommendationEngine` | ✅ Yes | Identical execution |
| **Validator** | ✅ `RecommendationValidator` | ✅ `RecommendationValidator` | ✅ Yes | Identical execution |
| **Response Generator** | ✅ Standard Response | ✅ `ResponseGenerator` | ⚠️ Partial | Production yields fallback because 0 candidates survived budget filter |

---

## 💥 First Point of Failure (Highest Priority Finding)

The production call graph diverges at **ChatOrchestrator intent routing & Layer 2.5 integration**:

1. **`ChatOrchestrator._handle_context_aware_followup` (Line 205)**: Manually merges `last_entities` (`budget_max: 100`) into incoming `user_context` BEFORE creating `RecommendationRequest`.
2. **Layer 2.5 Bypass**: Production never instantiates or executes `ConversationIntelligenceEngine.process()`. `RefinementDetector` and `clear_recommendation_context()` are completely bypassed in production.
