# Swiggy AI Copilot — Known Limitations (Stage RC-1)

## Current Scope Limits (Demo V1)

1. **Mock Data Scope:**
   - Catalog data is backed by local JSON mock datasets (`mock_catalog.json`, `mock_orders.json`, and knowledge base JSON files) rather than a live PostgreSQL production database.

2. **Single-Store Cart Enforcement:**
   - Cart additions enforce items from a single restaurant at a time (Swiggy standard policy). Multi-restaurant checkout is restricted.

3. **External Payment Gateway:**
   - Order checkout simulates order creation and returns order confirmation JSON without connecting to a live payment gateway (Razorpay/Stripe).

4. **Groq API Rate Limits:**
   - LLM calls utilize Groq `llama-3.3-70b-versatile`. High concurrency requests are throttled gracefully via fallback keyword-based intent resolution.
