import pdfplumber
import uuid
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pinecone import Pinecone
from google import genai
from app.core.config import settings
from app.repositories.document_repository import create_document
from app.db import SessionLocal

# 🔹 Initialize Gemini
gemini_client = genai.Client(api_key=settings.GOOGLE_API_KEY)

# 🔹 Initialize Pinecone
pc = Pinecone(api_key=settings.PINECONE_API_KEY)
index = pc.Index(settings.PINECONE_INDEX_NAME)


def process_pdf_to_pinecone(file_path: str, doc_id: str, user_id: str, document_name: str):

    print(f"\n=========== PDF INGESTION DEBUG: {document_name} ===========")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    vectors = []
    total_chunks = 0
    document_base_name = os.path.basename(document_name).replace(" ", "_")

    # 1️⃣ Extract text per page
    with pdfplumber.open(file_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            if not text:
                continue

            # 2️⃣ Chunk text specifically for this page
            page_chunks = splitter.split_text(text)

            for chunk_index, chunk in enumerate(page_chunks):
                print(f"Processing Page {page_num} - Chunk {chunk_index}")

                # 3️⃣ Generate embedding from Gemini
                response = gemini_client.models.embed_content(
                    model="gemini-embedding-001",
                    contents=chunk
                )

                embedding = response.embeddings[0].values
                
                # 4️⃣ Format the rigorous unique Chunk ID
                unique_chunk_uuid = str(uuid.uuid4())
                chunk_id = f"{user_id}_{document_base_name}_p{page_num}_c{chunk_index}_{unique_chunk_uuid}"

                vectors.append({
                    "id": chunk_id,
                    "values": embedding,
                    "metadata": {
                        "text": chunk,
                        "document_name": document_name,
                        "page_number": page_num,
                        "user_id": str(user_id)
                    }
                })

                total_chunks += 1

    # 5️⃣ Upsert to Pinecone
    # Pinecone upserts must be done in batches to avoid payload size limits (batch of 100)
    batch_size = 100
    for i in range(0, len(vectors), batch_size):
        batch = vectors[i:i + batch_size]
        index.upsert(
            vectors=batch,
            namespace=str(user_id)
        )
        print(f"Upserted batch of {len(batch)} vectors to Pinecone...")

    print("Total vectors upserted to Pinecone:", total_chunks)

    # 6️⃣ Save document metadata to database
    db = SessionLocal()
    try:
        create_document(db, doc_id, user_id, total_chunks)
        print("Document metadata saved to database")
    finally:
        db.close()

    print("==========================================\n")

    return total_chunks
