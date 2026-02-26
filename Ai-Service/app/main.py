from fastapi import FastAPI, UploadFile, File, Form
from app.services.ingestion_service import process_pdf_to_pinecone
from app.services.rag_engine import get_relevant_context
from app.services.memory_service import create_conversation
import shutil
import os

app = FastAPI()


# ----------------------------
# 1️⃣ Upload Document
# ----------------------------
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
        chunks = process_pdf_to_pinecone(temp_path, doc_id, user_id)

        return {
            "status": "success",
            "chunks_stored": chunks
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