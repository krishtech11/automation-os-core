# 🚢 UAOS Deployment Guide

This document explains how to deploy UAOS in both **local development** and **production environments**.

---

# 🧱 System Components

UAOS is a distributed system consisting of:

* **Frontend:** React (Vercel)
* **Backend API:** Flask (Render)
* **Worker:** Celery Worker (Render / background service)
* **Scheduler:** Celery Beat (Render / background service)
* **Database:** PostgreSQL
* **Message Broker:** Redis

---

# 🌐 Production Deployment

## 🔹 Frontend (Vercel)

1. Push frontend code to GitHub
2. Go to Vercel
3. Import repository
4. Configure:

   * Framework: Vite
   * Build Command: `npm run build`
   * Output Directory: `dist`

### Environment Variables

```env
VITE_API_BASE_URL=https://your-backend-url.onrender.com/api
```

---

## 🔹 Backend (Render)

1. Go to Render
2. Create a **Web Service**
3. Connect GitHub repo

### Settings

* Runtime: Python 3.10+
* Build Command:

```bash
pip install -r requirements.txt
```

* Start Command:

```bash
gunicorn run:app
```

---

## 🔹 Celery Worker (Render Background Service)

Create a **Background Worker** on Render.

### Start Command:

```bash
celery -A app.celery_app worker --loglevel=info
```

---

## 🔹 Celery Beat (Scheduler)

Create another background service.

### Start Command:

```bash
celery -A app.celery_app beat --loglevel=info
```

---

## 🔹 PostgreSQL

Use:

* Render PostgreSQL
  or
* External provider (Neon, Supabase)

### Required Variables:

```env
DATABASE_URL=your_postgres_url
```

---

## 🔹 Redis

Use:

* Render Redis
  or
* Upstash Redis

```env
REDIS_URL=your_redis_url
```

---

# 🔐 Environment Variables (Backend)

```env
DATABASE_URL=...
REDIS_URL=...
SENDGRID_API_KEY=...
OLLAMA_BASE_URL=http://localhost:11434
SECRET_KEY=your_secret
```

---

# 🧪 Local Development Setup

## 1. Start Services

```bash
# Redis
redis-server

# Backend
cd backend
python run.py

# Celery Worker
celery -A app.celery_app worker --pool=solo --loglevel=info

# Celery Beat
celery -A app.celery_app beat --loglevel=info
```

---

## 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## 3. Ollama (AI Planner)

```bash
ollama serve
ollama pull llama3.2:3b
```

---

# 📊 Deployment Architecture

```text
User → Vercel (Frontend)
      → Render (Flask API)
          → PostgreSQL (DB)
          → Redis (Queue)
              → Celery Worker
              → Celery Beat
```

---

# ⚠️ Important Notes

* All services must be running for full functionality
* Worker and Beat must be deployed separately
* Ensure environment variables are correctly configured
* Use production-ready database (not SQLite)

---

# 🐳 Docker Deployment (Optional)

```bash
docker-compose build
docker-compose up -d
```

---

# 🔍 Health Check (Recommended)

Add a health endpoint:

```
GET /health
```

Expected response:

```json
{
  "status": "ok"
}
```

---

# 🚧 Common Issues

## ❌ Tasks not executing

* Check Redis connection
* Ensure Celery worker is running

## ❌ Scheduler not triggering

* Ensure Celery Beat is active

## ❌ API not responding

* Check Render logs
* Verify environment variables

---

# 🔮 Future Improvements

* CI/CD pipeline (GitHub Actions)
* Auto-scaling workers
* Monitoring (Prometheus / Grafana)
* Centralized logging

---

# 📬 Support

For deployment issues, open a GitHub issue.
