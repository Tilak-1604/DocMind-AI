# 📚 AI Knowledge Assistant (RAG-based)

An AI-powered document assistant that allows users to:

- Upload PDFs
- Ask questions from their own documents
- Get AI-generated answers grounded in their data

Built using:
- FastAPI
- Gemini (Google GenAI)
- Pinecone (Vector Database)
- PDF Processing

---

## 🚀 Features

- 📄 PDF Upload
- 🧠 Text Chunking
- 🔢 Embedding Generation (Gemini)
- 🗂 Vector Storage (Pinecone)
- 🔎 Semantic Search
- 🤖 Context-grounded AI Answers (RAG)

---

## 🏗 Architecture

```
User Question
      ↓
Gemini Embedding
      ↓
Pinecone Vector Search
      ↓
Top K Chunks Retrieved
      ↓
Gemini LLM (Grounded Answer)
      ↓
Final Response
```

---

## 🛠 Tech Stack

- FastAPI
- Google GenAI SDK
- Pinecone Vector DB
- pdfplumber
- Uvicorn

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME
```

---

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
```

Activate:

Windows:
```bash
venv\Scripts\activate
```

Mac/Linux:
```bash
source venv/bin/activate
```

---

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4️⃣ Setup Environment Variables

Create a `.env` file:

```env
GOOGLE_API_KEY=your_google_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=your_index_name
```

---

### 5️⃣ Create Pinecone Index

- Dimension: 3072
- Metric: cosine
- Pod Type: serverless (recommended)

---

### 6️⃣ Run Server

```bash
uvicorn app.main:app --reload
```

Server will run at:

```
http://127.0.0.1:8000
```

---

## 📤 API Endpoints

---

### 📄 Upload PDF

**POST** `/upload`

Form Data:
- user_id
- doc_id
- file (PDF)

Example (Postman):
```
POST http://127.0.0.1:8000/upload
```

---

### 🔎 Ask Question

**GET** `/search`

Query Params:
- user_id
- question

Example:
```
http://127.0.0.1:8000/search?user_id=user1&question=What is color of cow?
```

Response:
```json
{
  "question": "...",
  "answer": "..."
}
```

---

## 🔐 Notes

- Each user has isolated namespace in Pinecone
- Uses Gemini embeddings for semantic search
- Uses strict RAG prompting to prevent hallucination

---

## 📌 Future Improvements

- Chat memory
- Multi-document support
- Flashcard generation
- Source citation
- Streaming responses
- Authentication system

---

## 👨‍💻 Author

Built as part of AI Knowledge Assistant project.



💬 Conversational Chat Memory (New Feature)

This project now supports Conversational RAG with Short-Term Memory, allowing users to ask follow-up questions such as:

“What is its disadvantage?”

“Explain the second point.”

“Compare it with the previous concept.”

“Explain it in simple terms.”

🧠 How Chat Memory Works

The system now maintains a conversation session using:

MySQL database

Unique conversation_id

Windowed short-term memory (last 3–5 Q&A pairs)

🔄 Updated Conversational Flow
User Question
      ↓
Load Recent Messages (MySQL)
      ↓
Embed (Conversation History + Question)
      ↓
Pinecone Vector Search
      ↓
Retrieve Top K Chunks
      ↓
Gemini LLM (Grounded Answer)
      ↓
Save Q&A to MySQL
      ↓
Return Final Response
🗄 Chat Memory Architecture
Database Design

Two tables are used:

1️⃣ conversations

id

user_id

created_at

2️⃣ messages

id

conversation_id

role (user / assistant)

content

created_at

📤 Additional API Endpoints
💬 Create Conversation

POST /conversation

Form Data:

user_id

Response:

{
  "conversation_id": "uuid"
}

Each chat session must start by creating a conversation.

💬 Conversational Chat

POST /chat

Form Data:

user_id

conversation_id

question

Response:

{
  "answer": "...",
  "sources": ["doc1#chunk2"]
}
🧩 Memory Strategy

Only last few messages are loaded (windowed memory)

Embedding strategy:

embed(history + question)

This ensures Pinecone retrieval understands context

Prevents hallucination in follow-up questions

🔧 Additional Setup Required for Chat Memory
Install Dependencies

Add MySQL + SQLAlchemy support:

pip install sqlalchemy pymysql
Update Environment Variables

Add database connection in .env:

DATABASE_URL=mysql+pymysql://root:password@localhost:3306/ai_assistant
Create MySQL Database
CREATE DATABASE ai_assistant;

Tables will be auto-created on first run.

🎯 What This Adds to the System

The system now supports:

Context-aware follow-up questions

Session-based conversation tracking

Short-term conversational memory

Improved retrieval for vague references ("it", "that")

Production-style conversational RAG architecture