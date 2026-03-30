# 📖 UAOS API Documentation

UAOS exposes a RESTful API for managing tasks, workflows, and execution logs.

---

## 🌐 Base URL

* **Local:** http://localhost:5000/api
* **Production:** https://your-backend-url.onrender.com/api

---

## 🔐 Authentication

> ⚠️ Currently, authentication is not implemented.
> Future versions will include JWT-based authentication.

---

## 📌 Endpoints Overview

| Method | Endpoint            | Description             |
| ------ | ------------------- | ----------------------- |
| POST   | /tasks              | Create a new task       |
| GET    | /tasks              | Retrieve all tasks      |
| POST   | /tasks/{id}/execute | Trigger task manually   |
| GET    | /logs               | Retrieve execution logs |

---

# 🧩 Task APIs

## ➕ Create Task

**Endpoint:**
POST /api/tasks

**Description:**
Creates a new automation task using natural language input.

### Request Body

```json
{
  "raw_text": "Send me tech news daily",
  "schedule": "daily",
  "use_llm": true
}
```

### Fields

| Field    | Type    | Required | Description                                       |
| -------- | ------- | -------- | ------------------------------------------------- |
| raw_text | string  | ✅        | Natural language instruction                      |
| schedule | string  | ✅        | Schedule type (daily, weekly, every_minute, etc.) |
| use_llm  | boolean | ❌        | Use LLM for workflow generation                   |

---

### Response

```json
{
  "id": 1,
  "message": "Task created successfully",
  "task": {
    "id": 1,
    "parsed_type": "NEWS_DIGEST",
    "schedule": "daily_18_0",
    "confidence": 0.95,
    "next_run": "2026-02-23T18:00:00+05:30"
  }
}
```

---

## 📥 Get All Tasks

**Endpoint:**
GET /api/tasks

**Description:**
Returns all created tasks along with their status and execution details.

### Response

```json
{
  "tasks": [
    {
      "id": 1,
      "raw_text": "Send me tech news daily",
      "parsed_type": "NEWS_DIGEST",
      "status": "ACTIVE",
      "next_run": "2026-02-23T18:00:00+05:30",
      "total_executions": 5
    }
  ]
}
```

---

## ⚡ Execute Task Manually

**Endpoint:**
POST /api/tasks/{id}/execute

**Description:**
Triggers immediate execution of a task, bypassing the scheduler.

### Response

```json
{
  "message": "Task execution triggered",
  "task_id": 1
}
```

---

# 📊 Logs API

## 📜 Get Execution Logs

**Endpoint:**
GET /api/logs

**Description:**
Fetches execution logs for all tasks.

### Response

```json
{
  "logs": [
    {
      "id": 1,
      "task_id": 1,
      "status": "SUCCESS",
      "message": "Sent 10 news articles",
      "start_time": "2026-02-22T18:00:00+05:30",
      "duration": 2.5
    }
  ]
}
```

---

# ⚙️ Status Definitions

| Status  | Meaning                                |
| ------- | -------------------------------------- |
| PENDING | Task is scheduled but not yet executed |
| RUNNING | Task is currently executing            |
| SUCCESS | Task completed successfully            |
| FAILED  | Task execution failed                  |
| RETRY   | Task is being retried after failure    |

---

# ⏱️ Scheduling Formats

| Input           | Meaning                       |
| --------------- | ----------------------------- |
| daily           | Runs once per day             |
| weekly          | Runs once per week            |
| every_minute    | Runs every minute             |
| custom (parsed) | Derived from natural language |

---

# ⚠️ Error Handling

### Common Errors

| Code | Description           |
| ---- | --------------------- |
| 400  | Invalid request data  |
| 404  | Task not found        |
| 500  | Internal server error |

---

# 🔮 Future Improvements

* JWT-based authentication
* Pagination for tasks and logs
* Filtering and search support
* WebSocket-based real-time logs
* Workflow-level APIs

---

# 📬 Support

For issues or questions, open an issue on the GitHub repository.
