# Investigation 2 — Complete Test Call Graph

## Request Scenario
Turn 1: `"Dessert under 100"`  
Turn 2: `"Italian meals"`

## Test Execution Chain (`test_rc1_conversation_policy.py`)

```text
unittest.main()
↓
TestRC1ConversationPolicy.test_scenario1_dessert_under_100_then_italian_meals()
↓ [Turn 1]
ConstraintLifecycleEngine.process_lifecycle(req1, session_memory)
↓ [session_memory updated with budget=100, category=dessert]
↓ [Turn 2]
ConversationIntelligenceEngine.process("Italian meals", req2, session_memory, retriever)
↓
RefinementDetector.classify_transition("Italian meals", req2, session_memory, retriever)
↓ [Classified as TransitionType.NEW_SEARCH]
session_memory.clear_recommendation_context()
↓ [budget & category removed from session_memory]
ConstraintLifecycleEngine.process_lifecycle(eff2_req, session_memory)
↓ [Effective request built containing ONLY cuisine_type=Italian]
CandidateRetriever.retrieve_candidates()
↓ [Returns 18 valid Italian items]
Test Assertions Pass 100%
```

## Stage Call Details in Test

| Stage # | Stage Name | File Path | Line Range | Input Payload | Output Payload |
|---|---|---|---|---|---|
| 1 | Test Harness | `backend/tests/test_rc1_conversation_policy.py` | L54-84 | Scenario 1 setup | `unittest` assertion result |
| 2 | Layer 2.5 Intelligence | `backend/app/services/.../conversation_intelligence.py` | L40-105 | `raw_query="Italian meals"`, `req2`, `session_memory` | `eff2_req`, `candidate_pool`, `telemetry` |
| 3 | Refinement Detector | `backend/app/services/.../refinement_detector.py` | L52-95 | `raw_query="Italian meals"`, `request`, `memory` | `TransitionType.NEW_SEARCH` |
| 4 | Memory Reset | `backend/app/services/session_manager.py` | L50-75 | `clear_recommendation_context()` | `['category=dessert', 'budget=100.0']` removed |
| 5 | Layer 2 Lifecycle | `backend/app/services/session_manager.py` | L315-380 | `eff2_req`, `cleaned session_memory` | `EffectiveRecommendationRequest(cuisine_type=Italian)` |
| 6 | Candidate Retriever | `backend/app/services/.../candidate_retriever.py` | L45-120 | `EffectiveRecommendationRequest` | 18 Italian Candidates |
