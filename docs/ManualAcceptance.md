# Swiggy AI Copilot — Manual Acceptance Test Results (Phase 11)

**Execution Date:** July 31, 2026  
**Environment:** Local Development (Backend: FastAPI `:8000`, Frontend: React Vite `:5173`)  
**Status:** ALL 8 SCENARIOS PASSED ✅  

---

## Acceptance Test Scenarios & Results

| # | User Conversation Scenario | Expected Behavior | Observed Result | Status |
|---|---|---|---|---|
| 1 | "Healthy dinner" | Returns healthy dinner options (salads, grain bowls) | Returned Ancient Grain Bowl & Caesar Salad | PASS ✅ |
| 2 | "Spicy Indian dinner under ₹300" | Applies spicy, Indian, dinner, and budget ≤ 300 | Returned Laal Maas & Jardaloo Salli Boti | PASS ✅ |
| 3 | "Italian food" | Switches cuisine domain to Italian without leakage | Returned Peppy Paneer & Margherita Pizza | PASS ✅ |
| 4 | "Under ₹200" (refinement) | Retains Italian context, narrows max budget | Returned Stuffed Garlic Breadsticks | PASS ✅ |
| 5 | "Desserts" | Switches domain to dessert category | Returned Gulab Jamun & Choco Lava Cake | PASS ✅ |
| 6 | "Never mind, give me coffee" | Resets current query intent, returns beverages | Returned McCafé Cappuccino | PASS ✅ |
| 7 | "Italian pizza under ₹100" | Triggers recovery due to strict budget constraint | Returned lowest price pizza with recovery note | PASS ✅ |
| 8 | "I'm hungry. Recommend something." | Fresh reset recommendation prompt | Prompted top popular multi-cuisine items | PASS ✅ |

---

## Performance & UX Metrics
- **Frontend Errors:** 0
- **Backend Exceptions:** 0
- **CORS Issues:** None
- **Average Latency:** ~180ms
