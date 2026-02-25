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