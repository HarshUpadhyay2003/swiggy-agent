# Investigation 1 — Complete Production Call Graph

## Request Scenario
Turn 1: `"Dessert under 100"`  
Turn 2: `"Italian meals"`

## Full Production Execution Chain

```text
HTTP POST /chat
↓
FastAPI Router (backend/app/routes/chat.py: L34)
↓
Chat Endpoint (chat function, L35-86)
↓
ChatOrchestrator.handle_message() (backend/app/services/chat_orchestrator.py: L474)
↓
ConversationalClassifier.classify_user_message() (chat_orchestrator.py: L494)
↓
ChatOrchestrator Intent Router (chat_orchestrator.py: L647)
↓ [Matches is_followup / active_domain="recommendations"]
ChatOrchestrator._handle_context_aware_followup() (chat_orchestrator.py: L170-225)
↓ [Directly merges last_entities {"budget_max": 100} into user_context]
ChatOrchestrator.handle_food_recommendation() (chat_orchestrator.py: L676)
↓
ChatOrchestrator._extract_recommendation_context() (chat_orchestrator.py: L1346)
↓
ContextEngine.recommend_food() (backend/app/services/context_engine.py: L24)
↓ [Translates dict context into RecommendationRequest with max_budget=100]
ConstraintLifecycleEngine.process_lifecycle() (backend/app/services/session_manager.py: L315)
↓ [BYPASSES Layer 2.5 ConversationIntelligenceEngine]
RecommendationEngine.generate_recommendations() (backend/app/services/recommendation_engine/recommendation_engine.py: L53)
↓
CandidateRetriever.retrieve_candidates() (candidate_retriever.py)
↓ [Filters Italian candidates with price > 100]
RankingEngine.rank_candidates()
↓
SemanticRecommendationEngine.evaluate_candidates()
↓
RecommendationValidator.validate_recommendations()
↓
ResponseGenerator.generate_response()
↓
API Response
```

## Stage Call Details

| Stage # | Stage Name | File Path | Line Range | Input Payload | Output Payload |
|---|---|---|---|---|---|
| 1 | FastAPI Router | `backend/app/routes/chat.py` | L34-86 | `ChatRequest(message="Italian meals", user_context={"session_id": "s1"})` | JSON Response object |
| 2 | Chat Orchestrator | `backend/app/services/chat_orchestrator.py` | L474-674 | `message="Italian meals"`, `user_context={"session_id": "s1"}` | Dict with intent, response, data |
| 3 | Follow-up Handler | `backend/app/services/chat_orchestrator.py` | L170-225 | `user_context`, `last_entities={"budget_max": 100}` | `handle_food_recommendation` call |
| 4 | Context Extractor | `backend/app/services/chat_orchestrator.py` | L1346-1450 | `message="Italian meals"`, `user_context={"budget_max": 100}` | `context={"cuisine_type": "Italian", "max_budget": 100}` |
| 5 | Context Engine | `backend/app/services/context_engine.py` | L24-188 | `context={"cuisine_type": "Italian", "max_budget": 100}` | `RecommendationRequest(constraints=[cuisine_type=Italian, max_budget=100])` |
| 6 | Layer 2 Lifecycle | `backend/app/services/session_manager.py` | L315-380 | `RecommendationRequest`, `session_memory` | `EffectiveRecommendationRequest` with stale budget |
| 7 | Layer 2.5 Intelligence | `backend/app/services/.../conversation_intelligence.py` | N/A | **NOT CALLED (BYPASSED)** | **NONE** |
| 8 | Recommendation Engine | `backend/app/services/.../recommendation_engine.py` | L53-160 | `EffectiveRecommendationRequest` | `List[RecommendationResult]` |
