from fastapi import FastAPI, UploadFile, File, Form
from app.services.ingestion_service import process_pdf_to_pinecone
from app.services.rag_engine import get_relevant_context
import shutil
import os

app = FastAPI()

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
            
@app.get("/search")
async def search_knowledge(user_id: str, question: str):
    print("\n===== SEARCH API CALLED =====")
    context = get_relevant_context(question, user_id)

    return {
        "question": question,
        "retrieved_context": context
    }