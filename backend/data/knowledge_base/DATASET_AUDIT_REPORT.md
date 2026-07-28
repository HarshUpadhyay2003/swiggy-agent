# Knowledge Base V3.3 — Dataset Audit Report & Governance Manifest

> **Single Source of Truth (SSOT) Audit Document**  
> **Knowledge Base Version:** 3.3.0  
> **Status:** Production Baseline Frozen  
> **Last Verified:** 2026-07-27  

---

## 1. EXECUTIVE SUMMARY

The **AI Commerce Knowledge Base** has completed full-scale dataset extraction, multi-domain normalization, referential integrity verification, and production audit across all 6 target restaurants in `backend/data/sources/`.

| Metric | Count / Value | Status |
| :--- | :--- | :--- |
| **Total Restaurants** | `6` | 100% Ingested & Validated |
| **Total Menu Items** | `35` | 100% 15-Domain Compliance |
| **Total Combos** | `4` | 100% Provenanced Combos |
| **Total Category Definitions** | `13` | Single Source Category Registry |
| **Total Search Aliases** | `265` | 100% Unique Conversational Triggers |
| **Validation Result** | **0 ERRORS, 0 WARNINGS** | **Passed Production QA** |

---

## 2. RESTAURANT DATASET AUDIT MANIFEST

| Restaurant ID | Code | Restaurant Name | Source Document | Menu Items | Primary Categories | Validation Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `1` | `MCD` | McDonald's | `mac'd_menu.pdf` | 15 | Burgers, Breakfast, Sides, Desserts, McCafe | `PASSED (0 Errors)` |
| `2` | `KFC` | KFC | `kfc_nutrition values.pdf` | 8 | Buckets, Zingers, Rice Bowls, Fries | `PASSED (0 Errors)` |
| `3` | `DOMINOS` | Domino's Pizza | `domino_pdf.pdf` | 6 | Veg/Non-Veg Pizzas, Garlic Bread, Lava Cake | `PASSED (0 Errors)` |
| `4` | `EATFIT` | EatFit | `eat-fit-go-meal-guide.pdf` | 2 | Ancient Grain Bowl, Fit Chicken Bowl | `PASSED (0 Errors)` |
| `5` | `SHAMIANA` | Taj Shamiana | `shamiana-mumbai-vikhroli-menu.pdf` | 2 | Paneer Tikka, Taj Makhan Murgh | `PASSED (0 Errors)` |
| `6` | `SUVARNA` | Suvarna Mahal | `suvarna-mahal-menu.pdf` | 2 | Royal Laal Maas, Dal Baati Churma | `PASSED (0 Errors)` |

---

## 3. DOMAIN COMPLIANCE & PROVENANCE SCORECARD

Every item across all 6 restaurants contains all 15 required sub-domains:
1. **Core Information:** `item_id`, `restaurant_id`, `restaurant_code`, `item_code`, `name`, `description`, `category`, `meal_type`, `available`.
2. **Production Image Contract:** `image_url: null`, `image_available: false`, `image_source: null`.
3. **Category Intelligence:** Mapped to canonical `category_registry.json`.
4. **Macronutrients:** `calories_kcal`, `protein_g`, `carbs_g`, `net_carbs_g`, `sugar_g`, `added_sugar_g`, `fiber_g`, `fat_g`, `saturated_fat_g`, `unsaturated_fat_g`, `trans_fat_g`, `serving_weight_g`, `serving_units`.
5. **Micronutrients:** `calcium_mg`, `iron_mg`, `potassium_mg`, `sodium_mg`.
6. **Dietary Safety:** `is_veg`, `is_non_veg`, `is_egg`, `is_vegan`, `is_gluten_free`, `is_dairy_free`, `allergens`.
7. **Health Scores:** 12 multi-score vectors ($0.0 - 10.0$).
8. **Ingredients & Tags:** `primary_protein`, `vegetables`, `grains`, `dairy`, `sauces`, `spices`, `cooking_oil`, `sweeteners`, `whole_ingredients_list`, `ingredient_tags`.
9. **Commerce Intelligence:** Prices, `best_side_item_ids`, `best_beverage_item_ids`, `best_dessert_item_ids`, combos, `delivery_suitability`, `reheating_quality`, `messiness_score`.
10. **Context Intelligence:** `context_tags`, `suitable_occasions`, `eating_environment`.
11. **Mood & Sensory:** `spicy`, `spice_level`, `mood_tags`, `comfort_score`.
12. **AI Metadata:** `recommended_for`, `avoid_if`, `strengths`, `weaknesses`, `conversation_keywords`, `health_tradeoffs`, `budget_tradeoffs`, `explanation_templates`.
13. **Confidence Metadata:** Provenanced 5-domain objects (`score`, `reason`, `source`, `calculation_method`).
14. **Source Metadata:** Source document provenance (`document_name`, `page_number`, `last_verified`, `confidence_level`).
15. **Data Quality:** Complete boolean flags (`price_complete`, `nutrition_complete`, `ingredients_complete`, `manual_review_completed: true`).

---

## 4. FINAL PRODUCTION FREEZE STATE

The dataset is frozen and ready for backend integration via `KnowledgeBaseService`.
