# AI Commerce Knowledge Base V3.3 — Specification & Architecture Guide

> **Single Source of Truth (SSOT)**  
> **Document Version:** 3.3.0 (Release Candidate RC1 / Production Baseline)  
> **Status:** Frozen / Production Baseline (Stage 0 Complete)  
> **Target System:** Swiggy AI Commerce Copilot Backend  
> **Authors:** Principal Product Architect, Staff Software Engineer, Data Architect & Knowledge Graph Team  

---

## 1. PROJECT OVERVIEW & RC1 BASELINE AUDIT

### 1.1 Purpose
The **AI Commerce Knowledge Base V3.3** is the frozen release candidate (RC1) production baseline for the Swiggy AI Commerce Copilot. It defines a multi-dimensional AI Knowledge Graph unifying:
- **Canonical Category Registry:** Centralized category hierarchy in `backend/data/knowledge_base/category_registry.json`.
- **Production-Safe Image Contract:** Strict decoupled image strategy (`image_url: null`, `image_available: false`, `image_source: null`).
- **Provenanced Confidence Vectors:** Explicit `score`, `reason`, `source`, and `calculation_method` for every restaurant and menu item heuristic.
- **Conversational Search Intelligence:** 115+ unique aliases including spoken intent phrases ("I'm hungry", "cheap lunch", "something filling").
- **Zero-Regression Adapter Architecture:** Preserves [catalog_service.py](file:///c:/Users/mohit/Desktop/swiggy-agent/backend/app/services/catalog_service.py) as an untouched Façade layer protecting downstream services.

---

## 2. FOLDER ARCHITECTURE

```text
swiggy-agent/
└── backend/
    ├── app/
    │   └── services/
    │       ├── catalog_service.py        # Untouched Façade / Adapter Layer
    │       ├── knowledge_base_service.py # Core Data Engine & Graph Query Service
    │       ├── context_engine.py         # Recommendation & Scoring Engine
    │       ├── planner.py                # Meal Planning Engine
    │       ├── cart_service.py           # Transactional Cart Service
    │       └── chat_orchestrator.py      # Conversational Routing Layer
    └── data/
        ├── mock_catalog.json             # Legacy Data (Maintained during adapter phase)
        ├── mock_orders.json              # Legacy Order Log
        └── knowledge_base/               # Knowledge Base Root Directory
            ├── generation_log.json       # Stage 0 Frozen Progress & Status Manifest
            ├── category_registry.json    # Canonical Category Master Registry
            ├── schema/                   # Canonical JSON Schemas
            │   ├── schema_version.json
            │   ├── restaurant.schema.json
            │   ├── menu_item.schema.json
            │   └── order_history.schema.json
            ├── restaurants/              # Restaurant Domain
            │   └── restaurants.json      # McDonald's Gold Standard Master Record
            ├── menu/                     # Menu Domain
            │   └── menu_items.json       # McDonald's 15-Domain Gold Standard Items
            └── sources/                  # Read-Only Source PDFs
                ├── mac'd_menu.pdf
                ├── kfc_nutrition values.pdf
                ├── domino_pdf.pdf
                ├── eat-fit-go-meal-guide.pdf
                ├── shamiana-mumbai-vikhroli-menu.pdf
                └── suvarna-mahal-menu.pdf
```

---

## 3. CATEGORY REGISTRY SPECIFICATION

File Location: `backend/data/knowledge_base/category_registry.json`

Every restaurant menu item references `category_id` from this canonical master registry:

| Category ID | Display Name | Parent Category | Display Order | Icon Name |
| :--- | :--- | :--- | :--- | :--- |
| `CAT_BURGERS_VEG` | Vegetarian Burgers | Burgers | 1 | `icon_burger_veg` |
| `CAT_BURGERS_NONVEG` | Non-Vegetarian Burgers | Burgers | 2 | `icon_burger_nonveg` |
| `CAT_BREAKFAST` | Breakfast McMuffins & Sides | Breakfast | 3 | `icon_breakfast` |
| `CAT_SIDES` | Sides & Snacks | Sides & Snacks | 4 | `icon_fries` |
| `CAT_DESSERTS` | Desserts & Soft Serve | Desserts | 5 | `icon_soft_serve` |
| `CAT_BEVERAGES` | Beverages & Drinks | Beverages | 6 | `icon_soda` |
| `CAT_MCCAFE` | McCafé Gourmet Coffee | Beverages | 7 | `icon_mccafe` |

---

## 4. PRODUCTION IMAGE STRATEGY CONTRACT

To prevent hardcoded placeholder URLs in production, every menu item adheres to the strict image contract:
```json
"image_url": null,
"image_available": false,
"image_source": null
```
Future image service integrations or CDN pipelines will populate these fields without modifying database schemas.

---

## 5. PROVENANCED CONFIDENCE SPECIFICATION

Every intelligence heuristic exposes detailed provenance objects:
```json
"confidence": {
  "nutrition": {
    "score": 1.0,
    "reason": "Extracted directly from official McDonald's India (N&E) lab nutrition booklet",
    "source": "mac'd_menu.pdf (Page 2)",
    "calculation_method": "Official Laboratory Assayed Data"
  },
  "micronutrients": {
    "score": 0.35,
    "reason": "Calculated via USDA / AI standard nutritional reference models",
    "source": "AI Estimation Engine V1",
    "calculation_method": "Ingredient Density Projection"
  },
  "health_scores": {
    "score": 0.85,
    "reason": "Derived from deterministic multi-vector nutrient mathematical formulas",
    "source": "Health Score Engine V1",
    "calculation_method": "Weighted Macro/Micro Vector Normalization"
  },
  "mood_tags": {
    "score": 0.80,
    "reason": "Mapped via natural language sensory & intent heuristic matrices",
    "source": "Sensory Classifier V1",
    "calculation_method": "Contextual Semantic Alignment"
  },
  "commerce": {
    "score": 0.85,
    "reason": "Derived from sales co-occurrence heuristics and pricing ratios",
    "source": "Commerce Intelligence Engine V1",
    "calculation_method": "Pairing Matrix Co-Occurrence Heuristics"
  }
}
```

---

## 6. STAGE 0 FREEZE & PRODUCTION BASELINE

- **Status:** Stage 0 Complete
- **Knowledge Base Status:** Production Baseline
- **Gold Standard Reference:** McDonald's (`MCD`, `restaurant_id: 1`)
- **Ready for Development:** `true`

---
*End of Knowledge Base V3.3 Production Baseline Specification Guide.*
