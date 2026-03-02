from fastapi import FastAPI, UploadFile, File, Form
from app.services.ingestion_service import process_pdf_to_pinecone
from app.services.rag_engine import get_relevant_context
from app.services.memory_service import create_conversation

from app.services.document_tools_service import (
    summarize_document,
    generate_flashcards,
    extract_key_topic,
    study_mode,
    generate_mind_map
)
import shutil
import os

# DB table auto-creation on startup
from app.db import engine, Base
from app.models import conversation, message, document  # existing models
from app.models import conversation_summary              # new smart-memory model

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
async def health_check():
    return {"status": "ok", "service": "DocMind AI RAG Engine"}


# ----------------------------
# Upload Document
# ----------------------------
from app.db import SessionLocal
from app.repositories.document_repository import (
    create_document,
    get_document_by_id
)

@app.post("/upload")
async def upload_document(
    user_id: str = Form(...),
    doc_id: str = Form(...),
    file: UploadFile = File(...)
):
    temp_path = f"temp_{file.filename}"

    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # 1️⃣ Process PDF and store embeddings
        chunk_count = process_pdf_to_pinecone(
            file_path=temp_path, 
            doc_id=doc_id, 
            user_id=user_id, 
            document_name=file.filename
        )

        # 2️⃣ Save or Update document metadata in DB
        db = SessionLocal()
        try:
            existing_doc = get_document_by_id(db, doc_id)

            if existing_doc:
                # Update chunk count if re-upload
                existing_doc.chunk_count = chunk_count
                db.commit()
            else:
                create_document(db, doc_id, user_id, chunk_count)

        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

        return {
            "status": "success",
            "doc_id": doc_id,
            "chunks_stored": chunk_count
        }

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

# ----------------------------
# 2️⃣ Create Conversation
# ----------------------------
@app.post("/conversation")
async def start_conversation(user_id: str = Form(...)):
    conversation_id = create_conversation(user_id)
    return {"conversation_id": conversation_id}


# ----------------------------
# 3️⃣ Chat (With Memory)
# ----------------------------
@app.post("/chat")
async def chat(
    user_id: str = Form(...),
    conversation_id: str = Form(...),
    question: str = Form(...)
):
    result = get_relevant_context(
        question=question,
        user_id=user_id,
        conversation_id=conversation_id
    )

    return {
        "answer": result["answer"],
        "sources": result["sources"]
    }
    
    

@app.post("/documents/{doc_id}/summarize")
async def summarize(
    doc_id: str,              # Path parameter
    user_id: str = Form(...)  # Form parameter
):
    return {"summary": summarize_document(user_id, doc_id)}

@app.post("/documents/{doc_id}/flashcards")
async def flashcards(
    doc_id: str,
    user_id: str = Form(...)
):
    return generate_flashcards(user_id, doc_id)

@app.post("/documents/{doc_id}/topics")
async def topics(
    doc_id: str,
    user_id: str = Form(...)
):
    return extract_key_topic(user_id, doc_id)

@app.post("/documents/{doc_id}/study")
async def study(
    doc_id: str,
    user_id: str = Form(...)
):
    return {"study_notes": study_mode(user_id, doc_id)}

@app.post("/documents/{doc_id}/mind-map")
async def mind_map(
    doc_id: str,
    user_id: str = Form(...)
):
    return {"mind_map": generate_mind_map(user_id, doc_id)}