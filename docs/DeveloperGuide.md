# Swiggy AI Copilot — Developer Guide (Stage RC-1)

## Code Base Organization

```
backend/
├── app/
│   ├── config/             # Centralized Settings & Config
│   ├── models/             # Pydantic Schemas & DTOs
│   ├── routes/             # FastAPI API Endpoint Routers
│   ├── services/           # Core Business Logic & Orchestration
│   │   ├── catalog/        # Catalog Data Adapters
│   │   ├── knowledge_base/ # KB Indexing, Searching & Validation
│   │   └── recommendation_engine/
│   │       ├── conversation_intelligence/  # Multi-turn Refinement & Recovery
│   │       ├── candidate_retriever.py
│   │       ├── ranking_engine.py
│   │       ├── semantic_recommendation_engine.py
│   │       └── models.py
│   └── main.py             # FastAPI App Entry Point
├── config/                 # Root Configuration Package
├── tests/
│   ├── run_backend_tests.py            # Master Test Runner
│   ├── stage4f1_calibration_test.py    # Semantic Calibration Tests
│   ├── recommendation_pipeline_test.py # E2E Pipeline Tests
│   ├── diagnostics/                    # Deep Audit Scripts
│   ├── output/
│   │   ├── latest/                     # Active Reports
│   │   └── archive/                    # Historical Runs
│   └── archive/                        # Obsolete / Refactored Tests
└── archive/                # Archived Scratch & One-off Scripts
```

---

## Coding Guidelines

1. **Layer Isolation:** Never bypass intermediate layers. Request normalization -> Retrieval -> Ranking -> Semantic Evaluation -> Validation -> Response.
2. **Logging Standard:** Use `logging.getLogger("swiggy_agent")` instead of `print()`.
3. **No Hardcoded Values:** Import constants from `app.config.settings`.
4. **Pydantic Validation:** All incoming and outgoing data structures must be validated with Pydantic V2 models.
