# Investigation 13 — Runtime State Ownership Audit

## Component State Ownership Map

| Component | Class / Property | Owned State / Responsibility | Duplicated Elsewhere? |
|---|---|---|---|
| **Chat Orchestrator** | `self.conversation_memories[session_id]` (`ConversationMemory`) | Stores raw text turns, `last_intent`, `last_entities` | ❌ **YES (DUPLICATE)** — Duplicates Layer 2 `SessionState` |
| **Session Manager** | `SessionState.recommendation_memory` (`RecommendationContextMemory`) | Stores structured recommendation constraints & user preferences | ✅ **AUTHORITATIVE OWNER** |
| **Context Engine** | Adapter Layer | Translates context dicts to `RecommendationRequest` | ❌ No state owned |
| **Recommendation Engine** | Stateless Pipeline | Processes `EffectiveRecommendationRequest` | ❌ No state owned |

---

## Duplicate Ownership Highlight

- **State Conflict:** Both `ChatOrchestrator` (`ConversationMemory`) and `SessionManager` (`RecommendationContextMemory`) track historical conversation entities.
- **Architectural Violation:** `ChatOrchestrator` attempts to perform context lifecycle management manually in `_handle_context_aware_followup` using `last_entities`, bypassing `SessionManager` and `ConversationIntelligenceEngine` (Layer 2.5).
