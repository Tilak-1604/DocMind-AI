import os
import shutil

from fastapi import APIRouter, BackgroundTasks, File, Form, UploadFile

from app.core.database import SessionLocal
from app.repositories.document_repository import create_document, get_document_by_id
from app.schemas.document import UploadResponse
from app.schemas.tools import (
    ExamResponse,
    FlashcardItem,
    MindMapResponse,
    StudyResponse,
    SummaryResponse,
    TopicsResponse,
)
from app.services.ingestion.extraction_service import run_background_extraction
from app.services.ingestion.ingestion_service import process_pdf_to_pinecone
from app.services.tools.exam_mode_service import exam_mode
from app.services.tools.flashcard_service import generate_flashcards
from app.services.tools.mind_map_service import generate_mind_map
from app.services.tools.study_mode_service import study_mode
from app.services.tools.summarization_service import summarize_document
from app.services.tools.topic_service import extract_key_topics

router = APIRouter(prefix="/documents", tags=["documents"])


# ─────────────────────────────────────────────
# Upload Document
# ─────────────────────────────────────────────

@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    user_id: str = Form(...),
    doc_id: str = Form(...),
    file: UploadFile = File(...),
):
    temp_path = f"temp_{file.filename}"

    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # 1. Process PDF and store embeddings in Pinecone
        chunk_count = process_pdf_to_pinecone(
            file_path=temp_path,
            doc_id=doc_id,
            user_id=user_id,
            document_name=file.filename,
        )

        # 2. Save or update document metadata in DB
        db = SessionLocal()
        try:
            existing_doc = get_document_by_id(db, doc_id)
            if existing_doc:
                existing_doc.chunk_count = chunk_count
                db.commit()
            else:
                create_document(db, doc_id, user_id, chunk_count, name=file.filename)
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

        # 3. Kick off background AI extraction
        background_tasks.add_task(run_background_extraction, user_id, doc_id)

        return UploadResponse(
            status="processing_features",
            doc_id=doc_id,
            chunks_stored=chunk_count,
        )

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


# ─────────────────────────────────────────────
# Document AI Tools
# ─────────────────────────────────────────────

@router.post("/{doc_id}/summarize", response_model=SummaryResponse)
async def summarize(doc_id: str, user_id: str = Form(...)):
    return SummaryResponse(summary=summarize_document(user_id, doc_id))


@router.post("/{doc_id}/flashcards")
async def flashcards(doc_id: str, user_id: str = Form(...)):
    return generate_flashcards(user_id, doc_id)


@router.post("/{doc_id}/topics")
async def topics(doc_id: str, user_id: str = Form(...)):
    return extract_key_topics(user_id, doc_id)


@router.post("/{doc_id}/study", response_model=StudyResponse)
async def study(doc_id: str, user_id: str = Form(...)):
    return StudyResponse(study_notes=study_mode(user_id, doc_id))


@router.post("/{doc_id}/mind-map", response_model=MindMapResponse)
async def mind_map(doc_id: str, user_id: str = Form(...)):
    return MindMapResponse(mind_map=generate_mind_map(user_id, doc_id))


@router.post("/{doc_id}/exam", response_model=ExamResponse)
async def exam(
    doc_id: str,
    user_id: str = Form(...),
    marks_1: int = Form(2),
    marks_2: int = Form(5),
    marks_5: int = Form(3),
    marks_10: int = Form(0),
):
    return ExamResponse(
        exam_paper=exam_mode(user_id, doc_id, marks_1, marks_2, marks_5, marks_10)
    )
