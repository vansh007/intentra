# 🚀 **Intentra — AI-Powered Memory & Intent Engine**

**Intentra** is an AI-powered semantic memory system that transforms saved content into actionable intelligence.

Instead of just bookmarking links, Intentra:

- **Generates AI summaries**
- **Classifies user intent**
- **Stores semantic embeddings (pgvector)**
- **Enables vector similarity search**
- **Tracks engagement & behavioral decay**
- **Suggests actions based on user intent**

---

## 🏗 **Architecture**

**Chrome Extension**  
        ↓  
**FastAPI Backend (Render)**  
        ↓  
**PostgreSQL + pgvector**  
        ↓  
**Gemini API (Embeddings + Intent)**

---

## 📦 **Project Structure**

```
intentra/
│
├── backend/        # FastAPI + AI engine
├── extension/      # Chrome extension
├── dashboard/      # Frontend UI
└── README.md
```

---

## ⚙️ **Backend**

### **Tech Stack**

- **FastAPI**
- **SQLAlchemy (Async)**
- **PostgreSQL**
- **pgvector**
- **Gemini API**
- **Docker**

### **Features**

- **Intent classification**
- **AI-generated summaries**
- **Embedding storage (vector(3072))**
- **Behavioral scoring**
- **Suggested action engine**
- **Vector similarity search**

---

## 🔌 **Chrome Extension**

The extension allows users to:

- **Save selected text from any webpage**
- **Send content to the backend**
- **Trigger AI processing**
- **Access saved memory instantly**

---

## 📊 **Dashboard**

The dashboard provides a simple UI to:

- **View saved memories**
- **See AI summaries**
- **Track engagement**
- **Explore insights**

---

## 🧪 **Local Development Setup**

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/intentra.git
   cd intentra/backend
   ```

2. **Configure environment variables**

   Create a `.env` file inside the `backend/` directory:
   ```env
   DATABASE_URL=postgresql+asyncpg://intentra_user:intentra_pass@localhost:5432/intentra_db
   GEMINI_API_KEY=YOUR_KEY
   APP_ENV=development
   ```

3. **Start PostgreSQL (Docker)**
   ```bash
   docker-compose up -d
   ```

   Enable `pgvector` inside PostgreSQL:
   ```sql
   CREATE EXTENSION vector;
   ```

4. **Run the FastAPI server**
   ```bash
   uvicorn app.main:app --reload
   ```

   Open:
   [http://localhost:8000/docs](http://localhost:8000/docs)  
   to access the interactive API documentation.

---

## 🚀 **Deployment**

### **Backend & Database**

- **Deployed using Render:**
  - Managed PostgreSQL
  - `pgvector` extension enabled
  - Docker-based FastAPI deployment

### **Frontend**

- **Static dashboard (Render / Vercel)**
- **Chrome extension loaded locally or published**

---

## 🔐 **Environment Variables**

| **Variable**      | **Description**                     |
|-------------------|-------------------------------------|
| `DATABASE_URL`    | PostgreSQL connection string        |
| `GEMINI_API_KEY`  | Google Gemini API key               |
| `APP_ENV`         | development or production           |

---

## 🧠 **Core Concept**

**Intentra** is not just a bookmark manager.

It is:

- **A semantic memory engine**
- **A behavioral intelligence layer**
- **An intent activation system**