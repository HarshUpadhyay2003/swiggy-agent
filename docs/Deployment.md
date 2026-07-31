# Swiggy AI Copilot — Deployment Guide (Stage RC-1)

## Environment Requirements
- Python 3.10+
- Node.js 18+ (for Frontend)
- Uvicorn / Gunicorn WSGI server

---

## Local Development Deployment

### 1. Backend Setup
```bash
cd backend
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

---

## Cloud Deployment (Render / Vercel)

### Backend Deployment on Render
The project includes a production `render.yaml` specification:

```yaml
services:
  - type: web
    name: swiggy-agent-backend
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: ENVIRONMENT
        value: production
      - key: GROQ_API_KEY
        sync: false
```

### Frontend Deployment on Vercel
Set environment variable on Vercel:
`VITE_API_BASE_URL=https://swiggy-agent-backend.onrender.com`
