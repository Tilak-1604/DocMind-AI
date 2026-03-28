import pdfplumber
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pinecone import Pinecone
from google import genai
from app.core.config import settings
from app.repositories.document_repository import create_document
from app.db import SessionLocal

EMBEDDING_WORKERS = 10  # Concurrent Gemini embedding threads

# 🔹 Initialize Gemini
gemini_client = genai.Client(api_key=settings.GOOGLE_API_KEY)

# 🔹 Initialize Pinecone
pc = Pinecone(api_key=settings.PINECONE_API_KEY)
index = pc.Index(settings.PINECONE_INDEX_NAME)


def _embed_chunk(args: tuple) -> tuple:
    """Embed a single text chunk. Returns (global_index, embedding, chunk_text, page_num)."""
    global_index, chunk_text, page_num = args
    response = gemini_client.models.embed_content(
        model="gemini-embedding-001",
        contents=chunk_text
    )
    return global_index, response.embeddings[0].values, chunk_text, page_num


def process_pdf_to_pinecone(file_path: str, doc_id: str, user_id: str, document_name: str):

    print(f"\n=========== PDF INGESTION DEBUG: {document_name} ===========")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    # 1️⃣ Extract all chunks from the PDF first (fast, CPU-bound)
    raw_chunks = []  # List of (global_index, chunk_text, page_num)
    with pdfplumber.open(file_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            if not text:
                continue
            page_chunks = splitter.split_text(text)
            for chunk in page_chunks:
                raw_chunks.append((len(raw_chunks), chunk, page_num))

    total_chunks = len(raw_chunks)
    print(f"Extracted {total_chunks} chunks. Embedding in parallel with {EMBEDDING_WORKERS} workers...")

    # 2️⃣ Embed all chunks concurrently (I/O-bound: Gemini API calls)
    embedded: dict[int, tuple] = {}  # global_index -> (embedding, chunk_text, page_num)
    with ThreadPoolExecutor(max_workers=EMBEDDING_WORKERS) as executor:
        chunk_futures = {executor.submit(_embed_chunk, args): args[0] for args in raw_chunks}
        for future in as_completed(chunk_futures):
            try:
                global_index, embedding, chunk_text, page_num = future.result()
                embedded[global_index] = (embedding, chunk_text, page_num)
                print(f"Embedded chunk {global_index + 1}/{total_chunks}")
            except Exception as e:
                print(f"Error embedding chunk {chunk_futures[future]}: {e}")

    # 3️⃣ Assemble vectors in deterministic order
    vectors = []
    for i in range(total_chunks):
        if i not in embedded:
            continue
        embedding, chunk_text, page_num = embedded[i]
        chunk_id = f"{doc_id}#chunk{i}"
        vectors.append({
            "id": chunk_id,
            "values": embedding,
            "metadata": {
                "text": chunk_text,
                "document_name": document_name,
                "page_number": page_num,
                "user_id": str(user_id)
            }
        })

    # Adjust total_chunks to reflect successfully embedded chunks
    total_chunks = len(vectors)

    # 4️⃣ Upsert to Pinecone in batches to avoid payload size limits (batch of 100)
    batch_size = 100
    for i in range(0, len(vectors), batch_size):
        batch = vectors[i:i + batch_size]
        index.upsert(
            vectors=batch,
            namespace=str(user_id)
        )
        print(f"Upserted batch of {len(batch)} vectors to Pinecone...")

    print("Total vectors upserted to Pinecone:", total_chunks)

    # 5️⃣ Save document metadata to database
    db = SessionLocal()
    try:
        create_document(db, doc_id, user_id, total_chunks)
        print("Document metadata saved to database")
    finally:
        db.close()

    print("==========================================\n")

    return total_chunks
