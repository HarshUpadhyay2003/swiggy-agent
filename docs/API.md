# Swiggy AI Copilot — API Reference (Stage RC-1)

## Base URL
`/` (Local default: `http://localhost:8000`)

---

## System Endpoints

### 1. Health Check
`GET /health`

**Response (200 OK):**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "release": "RC-1",
  "environment": "production",
  "uptime_seconds": 124.5,
  "knowledge_base_loaded": true,
  "catalog_loaded": true
}
```

### 2. Version Information
`GET /version`

**Response (200 OK):**
```json
{
  "name": "Swiggy AI Copilot",
  "version": "1.0.0",
  "release": "RC-1",
  "architecture": "Stage2C",
  "ranking": "Stage4D",
  "semantic": "Stage4F1",
  "build": "2026-07",
  "python": "3.11.0"
}
```

---

## Core Application Endpoints

### 3. Chat Assistant Endpoint
`POST /chat`

**Request Body:**
```json
{
  "message": "Recommend a healthy Indian dinner under ₹400",
  "session_id": "session-12345"
}
```

**Response (200 OK):**
```json
{
  "response": "Here are 3 healthy Indian dinner recommendations under ₹400...",
  "intent": "RECOMMENDATION",
  "recommendations": [
    {
      "item_id": 501,
      "name": "Jaituni Mirch Paneer Tikka",
      "price": 320,
      "restaurant_name": "Biryani By Kilo",
      "confidence": 0.88,
      "reason": "Top matched healthy Indian item within ₹400 budget"
    }
  ]
}
```

### 4. Cart Management
`GET /cart`  
`POST /cart/add`  
`POST /cart/clear`  

### 5. Order & Checkout
`POST /order/checkout`  

### 6. Meal Planner
`POST /planner`  
