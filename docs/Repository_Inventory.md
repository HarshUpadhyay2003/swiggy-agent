# Repository Inventory (Phase 0 Freeze)

**Git Branch:** `feature/ai-commerce-v2`  
**Status:** Feature Complete (Stage 4F.1) — Repository Freeze  
**Date:** July 31, 2026  

---

## 1. Production Files (`backend/app/`)

### Core API & Entry Point
- `backend/app/main.py` - FastAPI app initialization, middleware, routes, exception handlers.
- `backend/app/models/user_profile.py` - Pydantic model for user profile data.

### Routers (`backend/app/routes/`)
- `backend/app/routes/cart.py`
- `backend/app/routes/chat.py`
- `backend/app/routes/context.py`
- `backend/app/routes/order.py`
- `backend/app/routes/plan.py`
- `backend/app/routes/profile.py`
- `backend/app/routes/telemetry.py`

### Services (`backend/app/services/`)
- `action_executor.py`
- `cart_service.py`
- `catalog_service.py`
- `catalog/catalog_adapter.py`
- `chat_orchestrator.py`
- `context_engine.py`
- `conversational_classifier.py`
- `conversational_response_generator.py`
- `goal_engine.py`
- `history_analyzer.py`
- `llm_service.py`
- `order_service.py`
- `planner.py`
- `session_manager.py`
- `knowledge_base/` (`cache.py`, `indexes.py`, `json_loader.py`, `knowledge_base_service.py`, `validators.py`)

### Recommendation Engine (`backend/app/services/recommendation_engine/`)
- `candidate_retriever.py`
- `decision_engine.py`
- `explanation_builder.py`
- `models.py`
- `ranking_engine.py`
- `reason_builder.py`
- `recommendation_engine.py`
- `recommendation_validator.py`
- `request_normalizer.py`
- `schema_field_matcher.py`
- `schema_mapping.py`
- `semantic_calibrator.py`
- `semantic_evaluator.py`
- `semantic_explanation_engine.py`
- `semantic_metrics.py`
- `semantic_policy_resolver.py`
- `semantic_profile_resolver.py`
- `semantic_recommendation_engine.py`
- `strategy_chain.py`
- `suitability_estimator.py`
- `telemetry.py`
- `conversation_intelligence/` (`clarification_engine.py`, `constraint_policy_engine.py`, `conversation_intelligence.py`, `conversation_reset_detector.py`, `recovery_engine.py`, `refinement_detector.py`)

---

## 2. Unit & Integration Test Files (`backend/tests/`)

- `test_backward_compatibility.py`
- `test_candidate_retriever.py`
- `test_catalog_adapter.py`
- `test_catalog_service.py`
- `test_checkout_regression.py`
- `test_context_engine_integration.py`
- `test_explanation_builder.py`
- `test_indexes.py`
- `test_json_loader.py`
- `test_knowledge_base_service.py`
- `test_planner_integration.py`
- `test_ranking_engine.py`
- `test_reason_builder.py`
- `test_recommendation_engine.py`
- `test_validators.py`

---

## 3. Stage Pipeline Regression Tests (`backend/tests/`)

- `stage4a_intent_test.py`
- `stage4c_ranking_test.py`
- `stage4d_calibration_test.py`
- `stage4e_conversation_test.py`
- `stage4f_semantic_test.py`
- `stage4f1_calibration_test.py`
- `recommendation_pipeline_test.py`
- `run_backend_tests.py`

---

## 4. Diagnostic Files (`backend/tests/`)

- `ranking_deep_audit.py`
- `stage4b_investigation.py`
- `run_smoke_test.py`

---

## 5. Legacy & Scratch Files (Targets for `backend/archive/`)

- `backend/test_stage2a.py`
- `backend/test_stage2a1.py`
- `backend/test_goal_engine.py`
- `backend/test_conversational_system.py`
- `backend/scratch_investigate_stage4f1.py`
- `backend/scratch_trace.py`
- `backend/scratch_investigation_data.json`
- `backend/generate_phase0_reports.py`

---

## 6. Output & Generated Reports (`backend/tests/output/`)

- `stage4f1_report.md` (Active)
- `stage4f1_summary.md` (Active)
- `decision_boundary_analysis.md` (Historical)
- `metric_consistency_report.md` (Historical)
- `recommendation_explanation_audit.md` (Historical)
- `semantic_calibration_curve.md` (Historical)
- `semantic_metrics_statistics.json` (Historical)
- `semantic_similarity_distribution.json` (Historical)
- `semantic_suitability_distribution.json` (Historical)
- `stage4f1_terminal_logs.txt` (Historical)

---

## 7. Configuration & Environment Files

- `backend/requirements.txt`
- `backend/render.yaml`
- `backend/.env`
- `backend/.env.example`
- `backend/.gitignore`

---

## 8. Frontend Assets (`frontend/`)

- `frontend/src/` (Components, App.jsx, api.js, main.jsx, index.css)
- `frontend/package.json`
- `frontend/vite.config.js`
