# 🚀 UAOS - Unified AI Automation Operating System

## 🌐 Live Demo

👉 https://automation-os-frontend.vercel.app

> ⚡ AI-powered automation system that converts natural language into scheduled, multi-step workflows with real-time execution.
> ⚡ Inspired by Zapier (automation), Airflow (orchestration), and local LLMs — unified into a single system.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![React](https://img.shields.io/badge/React-18.0+-61DAFB.svg)](https://reactjs.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 📋 Table of Contents

- [Overview](#overview)
- [System Highlights](#system-highlights)
- [Key Features](#key-features)
- [Key Engineering Concepts](#key-engineering-concepts)
- [Project Structure](#project-structure)
- [Architecture](#architecture)
- [Scheduling Strategy](#scheduling-strategy)
- [AI Planning Flow](#ai-planning-flow)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [Workflows](#workflows)
- [System Capabilities](#system-capabilities)
- [System Design Decisions](#system-design-decisions)
- [Engineering Challenges & Solutions](#engineering-challenges--solutions)
- [Screenshots](#screenshots)
- [API Documentation](#api-documentation)
- [Deployment](#deployment)
- [Example Automations](#example-automations)
- [Contributing](#contributing)

---

## 🎯 Overview

UAOS is a distributed automation operating system that converts natural language into executable workflows with scheduling, monitoring, and fault-tolerant execution.

It functions as a lightweight alternative to tools like Zapier and Airflow, enhanced with AI-driven workflow generation.

### 🚀 Live System

- 🌐 Frontend: https://automation-os-frontend.vercel.app
- 🔗 Backend API: https://uaos-backend.onrender.com/api

> ⚠️ Backend may take 30–60s to wake up (Render free tier)

### Problem Statement

Manual automation setup is time-consuming and requires technical knowledge. UAOS bridges this gap by enabling natural language task creation with intelligent workflow decomposition.

### Why UAOS?

Existing tools like Zapier require manual setup and lack transparency in execution.  
UAOS focuses on:
- AI-driven workflow creation
- Full execution visibility
- Local-first LLM support (no API cost)

### Solution

A full-stack platform combining:
- 🧠 **AI-powered intent parsing** (TF-IDF + LLM)
- ⚙️ **Distributed task execution** (Celery + Redis)
- 🔄 **Smart scheduling** (Celery Beat + DB-driven polling scheduler)
- 📊 **Real-time monitoring** (React dashboard)

---

## ⚡ System Highlights (What Makes This Project Strong)

- 🧠 **LLM + Rule-based Hybrid Planning**
  - Combines TF-IDF intent classification with local LLM (Ollama)
  - Ensures reliability even when LLM fails

- 🔄 **Custom Distributed Scheduling Engine**
  - Built a **DB-driven scheduling system using Celery Beat + polling**
  - Avoids limitations of static schedulers by dynamically evaluating tasks

- 🧵 **Asynchronous Execution Architecture**
  - Decoupled task creation, scheduling, and execution using Celery workers
  - Handles retries, timeouts, and execution logging

- 🛡️ **Robust Error Handling**
  - JSON repair for LLM outputs
  - Retry mechanisms with exponential backoff
  - Execution logging with failure tracking
 
- 🧠 **Natural Language → Executable Workflows**
  - Converts user intent into structured automation pipelines

- 📊 **Execution Observability**
  - Tracks task status, execution time, and logs in real-time dashboard

- ⚙️ **Production-Oriented Design**
  - Connection pooling fixes for PostgreSQL
  - Background worker isolation
  - Safe environment variable handling

## ✨ Key Features

### 🤖 Natural Language Interface
- Parse complex queries: *"Every Monday morning, clean my Downloads and email me a summary"*
- Multi-step workflow decomposition with LLM
- Confidence scoring and fallback strategies

### 🔧 Built-in Workflows
1. **News Digest** - Aggregate news from APIs and email delivery
2. **File Cleanup** - Intelligent file organization and renaming
3. **Invoice Sync** - Gmail → Google Drive automation with OAuth2

### 🎯 Advanced Scheduling
- Dynamic DB-driven scheduling (Celery Beat + polling)
- Natural language schedule parsing: *"every Friday at 6 PM"*
- Timezone-aware (Asia/Kolkata)

### 📡 Real-Time System Visibility
- Execution logs with status tracking (SUCCESS / FAILED / RETRY)
- Task-level monitoring with timestamps and duration

### 🔐 Production Stability Features
- API normalization between frontend and backend
- Defensive handling for undefined/null frontend states
- Schedule validation and normalization

### 📈 Production-Ready Architecture
- Distributed workers with Celery
- Redis message broker
- PostgreSQL persistence
- Execution logging and monitoring

## 📌 Current Status

- ✅ Fully deployed (Frontend + Backend)
- ✅ Scheduler and workers running in production
- ✅ Stable task creation and execution
- ✅ Email workflows operational
- 🚧 Upcoming: Multi-user support, visual workflow builder

## 🧠 Key Engineering Concepts

- Distributed task queues (Celery + Redis)
- DB-driven scheduling system
- Fault-tolerant workflow execution
- LLM + rule-based hybrid architecture
- Service-oriented system design

## 📂 Project Structure

```text
UAOS/
│
├── backend/                         # Flask backend API
│   │
│   ├── app/
│   │   ├── __init__.py              # Flask app factory
│   │   ├── models.py                # Database models
│   │   ├── celery_app.py            # Celery app configuration
│   │   ├── tasks.py                 # Background task definitions
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── routes.py            # REST API routes
│   │   │
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── intent_parser.py     # Rule-based intent parsing
│   │   │   ├── llm_planner_free.py  # LLM workflow planner
│   │   │   └── celery_scheduler.py  # DB-driven scheduler
│   │   │
│   │   ├── engines/
│   │   │   ├── file_engine.py
│   │   │   └── desktop_engine.py
│   │   │
│   │   ├── workflows/
│   │   │   ├── base.py
│   │   │   ├── news_digest.py
│   │   │   ├── file_cleanup.py
│   │   │   ├── invoice_sync.py
│   │   │   ├── document_summary.py
│   │   │   └── email_report.py
│   │
│   ├── config.py                    # Environment configuration
│   ├── run.py                       # Flask app entrypoint
│   ├── celery_beat.py               # Scheduler entrypoint
│   └── requirements.txt
│
├── frontend/                        # React (Vite) dashboard
│   │
│   ├── src/
│   │   ├── App.jsx                  # Main UI
│   │   ├── main.jsx                 # Entry point
│   │   ├── assets/                  # Static assets
│   │   ├── AIAssistant.jsx          # AI assistant panel
│   │   ├── AIOrb.jsx                # UI component
│   │   ├── HologramOrb.jsx          # UI component
│   │   ├── index.css
│   │   └── app.css
│   │
│   ├── index.html
│   ├── package.json
│   ├── tailwind.config.js
│   ├── postcss.config.cjs
│   └── .env.example
│
├── docs/                            # Documentation
│   ├── API.md
│   ├── DEPLOYMENT.md
│   └── screenshots/
│       ├── dashboard.png
│       ├── Task_created.png
│       └── Execution_logs.png
│
├── docker/                          # Docker configs (optional)
  └── docker-compose.yml             # Multi-service setup          
│             
├── render.yaml                      # Render deployment config
├── CONTRIBUTING.md
├── LICENSE
├── .env.example
├── .gitignore
└── README.md
```
---

## 🏗️ Architecture

```text

                     ┌─────────────┐
                     │    User     │
                     └──────┬──────┘
                            │
                            ▼
                ┌──────────────────────┐
                │   React Dashboard    │
                │   (Task Management)  │
                └──────────┬───────────┘
                           │ REST API
                           ▼
                 ┌──────────────────────┐
                 │      Flask API       │
                 │  Task + Workflow API │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │   Intent Parser +    │
                 │    LLM Planner       │
                 │    (Ollama Local)    │
                 └──────────┬───────────┘
                            │
            ┌───────────────┴────────────────┐
            ▼                                ▼
     ┌─────────────┐                 ┌──────────────────┐
     │ PostgreSQL  │                 │ Redis (Broker)   │
     │ Tasks +     │                 │ Message Queue    │
     │ Logs + Plans│                 └────────┬─────────┘
     └─────────────┘                          │
                                              ▼
                                   ┌──────────────────────┐
                                   │    Celery Workers    │
                                   │                      │
                                   │  • News Digest       │
                                   │  • File Cleanup      │
                                   │  • Invoice Sync      │
                                   └──────────┬───────────┘
                                              │
                                              ▼
                                   ┌──────────────────────┐
                                   │   External Services  │
                                   │                      │
                                   │ • NewsAPI            │
                                   │ • Gmail API          │
                                   │ • Google Drive API   │
                                   │ • Local File System  │
                                   └──────────────────────┘

```
> ⚠️ In production, each component (API, worker, scheduler) runs as an independent service for scalability and fault isolation.

### 🔄 Scheduling Strategy

Unlike traditional cron-based systems, UAOS uses a **database-driven scheduling model**:

1. Celery Beat triggers a periodic task (`check_scheduled_tasks`)
2. The system queries PostgreSQL for due tasks (`next_run <= now`)
3. Eligible tasks are dispatched to Celery workers
4. Workers execute workflows and update execution state

This approach enables:
- Dynamic task scheduling (no static cron definitions)
- Real-time updates to schedules
- Better control over task execution and retries
---

## 🧠 AI Planning Flow
This explains how a natural-language task becomes an executable workflow.

```mermaid
flowchart TD

A[User Natural Language Command] --> B[React Dashboard]
B --> C[Flask API]

C --> D[Intent Parsing Layer]
D --> E[LLM Planner - Ollama]

E --> F{Generate Workflow Plan}

F --> G[Workflow Type Detection]
F --> H[Extract Parameters]
F --> I[Schedule Interpretation]

G --> J[Task Configuration JSON]
H --> J
I --> J

J --> K[Store Task in PostgreSQL]

K --> L[Scheduler]
L --> M[Redis Message Queue]

M --> N[Celery Worker]
N --> O[Workflow Execution Engine]

O --> P[External Services]
P --> Q[Execution Logs]

Q --> R[Dashboard Monitoring]

```
### 🛡️ Planning Reliability Enhancements

- JSON repair for malformed LLM outputs
- Validation layer before task creation
- Fallback to rule-based parser on failure
- Retry mechanism for unstable planning outputs

## 🔍 LLM Planning Logic

```mermaid
flowchart TD

A[User Command] --> B{LLM Available?}

B -->|Yes| C[Ollama LLM Planner]
B -->|No| D[Rule-Based Intent Parser]

C --> E[Workflow Plan JSON]
D --> E

E --> F[Validate Plan]

F --> G{Valid?}

G -->|Yes| H[Create Task]
G -->|No| I[Fallback Parser]

H --> J[Store in Database]

```

## 🛠️ Tech Stack

### Backend
- **Framework:** Flask 3.0
- **Database:** PostgreSQL 14
- **ORM:** SQLAlchemy
- **Task Queue:** Celery 5.3 + Redis 5.0
- **Scheduler:** Celery Beat + Custom DB Polling Scheduler
- **AI/ML:** scikit-learn (TF-IDF), Ollama (Llama 3.2 local model)

### Frontend
- **Framework:** React 18 + Vite
- **Styling:** Tailwind CSS
- **Icons:** Lucide React
- **State:** React Hooks

### APIs & Services
- NewsAPI (news aggregation)
- Gmail API (email operations)
- Google Drive API (cloud storage)
- Ollama (local LLM - FREE)

### Deployment
- Backend: Render
- Frontend: Vercel

### Core Infrastructure
- Flask (API layer)
- PostgreSQL (persistent storage)
- Redis (message broker)
- Celery (distributed workers + scheduling)

### AI Layer
- Ollama (local LLM execution)
- TF-IDF (intent classification fallback)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- Redis 5+
- Ollama (for AI planning)

### 1. Clone Repository
```bash
git clone https://github.com/krishtech11/automation-os-core.git
cd UAOS
```

### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create PostgreSQL database
createdb uaos_db

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run migrations
python run.py
```

### 3. PostgreSQL setup example

```sql
CREATE DATABASE uaos_db;
CREATE USER uaos WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE uaos_db TO uaos;
```
---

### 4. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

### 5. Install Ollama (for FREE AI planning)
```bash
# Download and install from https://ollama.ai/download

# Pull the model (one-time, 2GB download)
ollama pull llama3.2:3b

# Start Ollama server
ollama serve
```

### 6. Start Services
```bash
# Terminal 1: Ollama (AI Planning)
ollama serve

# Terminal 2: Redis
redis-server

# Terminal 3: Flask API
cd backend && python run.py

# Terminal 4: Celery Worker
cd backend && celery -A app.celery_app worker --pool=solo --loglevel=info

# Terminal 5: Celery Beat (optional, for scheduled tasks)
cd backend && celery -A app.celery_app beat --loglevel=info
```

### 7. Access Dashboard
👉 https://automation-os-frontend.vercel.app

# Configure SendGrid (for email workflows)
SENDGRID_API_KEY=your_key_here


## 📚 Workflows

### 1. News Digest
**Description:** Fetch news from NewsAPI and email formatted digest

**Configuration:**
```json
{
  "email": "user@example.com",
  "category": "technology",
  "country": "in",
  "limit": 10
}
```

**Example:** *"Send me top 10 tech news every Friday at 6 PM"*

### 2. File Cleanup
**Description:** Scan, rename, and organize files in local folders

**Configuration:**
```json
{
  "folder": "Downloads",
  "file_pattern": "*.pdf",
  "action": "rename",
  "rename_pattern": "date_title"
}
```

**Example:** *"Clean my Downloads folder PDFs daily at 11 PM"*

### 3. Invoice Sync
**Description:** Extract invoices from Gmail and upload to Google Drive

**Configuration:**
```json
{
  "gmail_filter": "has:attachment (invoice OR receipt)",
  "drive_folder": "Invoices",
  "organize_by_date": true
}
```

**Example:** *"Sync Gmail invoices to Drive every Monday"*

---

## 📊 System Capabilities

- Handles asynchronous workflows using distributed workers
- Supports natural language → structured automation pipeline
- Scalable architecture with decoupled components
- Fault-tolerant execution with retry and timeout mechanisms
- Real-time monitoring via execution logs

## 🧩 System Design Decisions

- Chose **Celery over threading** for true asynchronous scalability
- Implemented **DB-driven scheduler** instead of static cron for dynamic task updates
- Used **local LLM (Ollama)** to avoid API cost and ensure offline capability
- Designed **modular workflow engine** for easy extensibility
- Balanced **LLM + rule-based parsing** for reliability and performance

## 🧠 Engineering Challenges & Solutions

### 1. Duplicate Task Execution
**Problem:** Scheduler triggering same task multiple times  
**Solution:**  
- Implemented time-based execution guard using `last_run`
- Ensured `next_run` is updated before execution

---

### 2. Celery + Flask Context Issue
**Problem:** `Working outside of application context` error  
**Solution:**  
- Wrapped Celery tasks with `app.app_context()`  
- Ensured DB operations are context-aware  

---

### 3. Database Connection Exhaustion
**Problem:** PostgreSQL connection slots getting exhausted  
**Solution:**  
- Added `db.session.remove()` cleanup in all tasks  
- Configured SQLAlchemy connection pooling  
- Limited scheduler load using batch queries  

---

### 4. LLM Output Reliability
**Problem:** Invalid JSON from LLM responses  
**Solution:**  
- Implemented JSON repair and validation layer  
- Added fallback to rule-based intent parser  

---

### 5. Scheduler Race Conditions
**Problem:** Multiple executions due to timing mismatch  
**Solution:**  
- Introduced execution guards using `last_run` timestamps  
- Simplified concurrency handling for reliability  

---

## 📸 Screenshots

**Dashboard Overview**
![Dashboard](docs/screenshots/dashboard.png)
**Dashboard (Alternate)**
![Dashboard](docs/screenshots/dashboard1.png)

**Task Creation**
![Create Task](docs/screenshots/Task_created.png)
**Task Creation Alternate**
![Create Task](docs/screenshots/Task_created2.png)

**Execution Logs**
![Logs](docs/screenshots/Execution_logs.png)

---

## 📖 API Documentation

Full API reference is available here:

👉 [View API Docs](docs/API.md)


## 🧪 Example Automations


- Send me top 10 tech news every Friday at 6 PM 
- Send me tech news every minute 
- Clean my Downloads folder PDFs daily  

---

## 🚢 Deployment

UAOS is designed as a **multi-service distributed system** consisting of:

- Flask API (Web Service)
- Celery Worker (Background Processing)
- Celery Beat (Scheduler)
- Redis (Message Broker)
- PostgreSQL (Database)

Each component is deployed independently for scalability.
> ⚠️ Note: UAOS requires multiple services (worker + scheduler + broker) and is deployed as a distributed system.

For detailed deployment steps:

👉 [View Deployment Guide](docs/DEPLOYMENT.md)

### 🌍 Live Deployment

- Frontend (Vercel): https://automation-os-frontend.vercel.app
- Backend (Render): https://uaos-backend.onrender.com

> Note: Free-tier services may have cold start delays.


## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📝 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file.

---

## 👤 Author

**Krishna Arora**
- 🚀 Final Year BTech IT Student | Backend + AI Systems
- 💡 Focus: Distributed Systems, Automation, AI Integration
- GitHub: [@krishtech11](https://github.com/krishtech11)
- LinkedIn: [Krishna Arora](https://linkedin.com/in/krishna-arora-83b87a26b/)
- Email: krishnaarora747@gmail.com

---

## 🙏 Acknowledgments

- NewsAPI for news aggregation
- Google APIs for Gmail and Drive integration
- Ollama team for FREE local LLM
- Meta for Llama 3.2 model
- The open-source community

---

## 📈 System Metrics

- Handles scheduled and on-demand workflows
- Supports multi-step task execution
- Designed for horizontal scalability (worker-based)

---

## ⚖️ Comparison

| Feature | UAOS | Zapier | Airflow |
|--------|------|--------|--------|
| AI Workflow Creation | ✅ | ❌ | ❌ |
| Local LLM Support | ✅ | ❌ | ❌ |
| Visual Builder | 🚧 | ✅ | ❌ |
| Code-Free Automation | ✅ | ✅ | ❌ |

## 🔮 Future Roadmap

- AI-generated workflows from natural language
- Visual drag-and-drop workflow builder
- Plugin system (Gmail, Slack, APIs)
- Multi-user system with role-based access
- Real-time execution monitoring (WebSockets)
---

**⭐ Star this repo if you find it useful!**
