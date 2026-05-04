# 🚀 Helix SROP — AI Support System

**Author:** Vaibhav Chaudhary

---

## 📌 Overview

Helix SROP is an **AI-powered support orchestration platform** that routes user queries to specialized agents using an **LLM-based decision system**, retrieves knowledge using **RAG (Retrieval-Augmented Generation)**, and provides **transparent execution traces** for observability.

The system is designed with a **modular, agent-based architecture inspired by Google ADK**, enabling scalable and extensible AI workflows.

---

## ⚙️ Setup Instructions

```bash
git clone https://github.com/chvaibhav2003/Helix-SROP-Vaibhav.git
cd helix-srop-assignment

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run RAG ingestion
python -m app.rag.ingest --path docs/

# Start server
uvicorn app.main:app --reload
```

---

## 🧪 Quick Test

### 1️⃣ Create Session

```bash
curl -X POST http://localhost:8000/v1/sessions \
-H "Content-Type: application/json" \
-d '{"user_id": "u_demo", "plan_tier": "pro"}'
```

### 2️⃣ Chat

```bash
curl -X POST http://localhost:8000/v1/chat/<SESSION_ID> \
-H "Content-Type: application/json" \
-d '{"content": "How do I rotate a deploy key?"}'
```

### 3️⃣ Trace

```bash
curl http://localhost:8000/v1/traces/<TRACE_ID>
```

---

## 🏗️ Architecture

```text
User Request
     ↓
FastAPI API Layer
     ↓
Pipeline (State + Orchestration)
     ↓
LLM Router (Intent Classification)
     ↓
 ┌───────────────┬────────────────┐
 │ KnowledgeAgent │ AccountAgent   │
 └───────┬────────┴───────┬────────┘
         ↓                ↓
   RAG (Vector DB)   Account Tools
         ↓                ↓
      Response        Response
         ↓
   Trace Logging (DB)
```

---

## 🧠 Key Components

### 🔹 1. LLM-Based Routing

* Uses **local LLM (Ollama - phi3)** to classify intent:

  * `knowledge` → documentation queries
  * `account` → user-specific queries
* Includes **fallback logic** for reliability

---

### 🔹 2. Knowledge Agent (RAG)

* Uses:

  * **Chunking (heading-aware + overlap)**
  * **Sentence Transformers embeddings**
  * **ChromaDB vector store**
* Retrieves top-k relevant chunks
* Uses LLM to generate contextual answers

---

### 🔹 3. Account Agent

* Handles:

  * Build queries
  * Account usage/status
* Uses tool abstraction (`get_recent_builds`, `get_account_status`)
* Currently implemented with mock data (as allowed)

---

### 🔹 4. Pipeline (Core Engine)

Handles:

* Session state loading
* LLM routing
* Agent execution
* Trace recording
* DB persistence

---

### 🔹 5. Trace System (Observability)

Each request generates a `trace_id` with:

* Routed agent
* Tool calls
* Retrieved document chunks
* Latency

👉 Enables **debugging, monitoring, and transparency**

---

## 🗄️ Database Design

* **Users**
* **Sessions** (with serialized state)
* **Messages**
* **Agent Traces**

Uses **SQLite (async SQLAlchemy)** for simplicity.

---

## 🧩 Design Decisions

### ✅ State Persistence

Used **DB-backed session state** instead of in-memory:

* Survives restarts
* Enables multi-turn context
* Production-ready pattern

---

### ✅ Chunking Strategy

Used **heading-aware + overlap chunking**:

* Preserves semantic structure
* Improves retrieval accuracy
* Avoids context loss at boundaries

---

### ✅ Vector Store (ChromaDB)

Chosen over FAISS because:

* Persistent storage
* Built-in metadata filtering
* Easier integration for production-like systems

---

### ✅ LLM Choice (Ollama - Local)

* Avoids API limits and cost
* Enables offline inference
* Demonstrates practical deployment approach

---

## ⚠️ Known Limitations

* Full Google ADK AgentTool integration not implemented
* Mock data used for account tools
* No advanced retry/caching strategies
* Limited evaluation/testing coverage

---

## 🚀 What I’d Do With More Time

* Full **Google ADK integration (AgentTool + event stream parsing)**
* Add **reranking layer for RAG**
* Implement **streaming responses (SSE)**
* Add **evaluation harness**
* Improve **tool reliability + retries**
* Add **Docker deployment**

---

## ⏱️ Time Spent

| Phase                    | Time       |
| ------------------------ | ---------- |
| Setup + DB + FastAPI     | 2–3 hrs    |
| RAG ingest + retrieval   | 4–5 hrs    |
| Agent architecture       | 3–4 hrs    |
| Pipeline + tracing       | 3–4 hrs    |
| LLM integration (Ollama) | 2 hrs      |
| Debugging + testing      | 3–4 hrs    |
| **Total**                | ~18–22 hrs |

---

## 🏆 Extensions Implemented

* ✅ RAG pipeline
* ✅ LLM-based routing
* ✅ Local LLM (Ollama)
* ✅ Trace observability
* ✅ Fault-tolerant fallback system

---

## 💡 Final Notes

This system follows an **ADK-inspired architecture**:

* Root orchestrator agent
* Specialized sub-agents
* Tool abstraction layer
* LLM-driven decision-making

It is designed to be **easily extendable into a full production-grade agent system**.

---

## 🎥 Demo Video

👉 *(Add your Loom link here)*

---

## 🙌 Thank You

Looking forward to feedback!
