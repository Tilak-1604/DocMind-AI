import pdfplumber
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pinecone import Pinecone
from google import genai
from app.core.config import settings

# Initialize Gemini
gemini_client = genai.Client(api_key=settings.GOOGLE_API_KEY)

# Initialize Pinecone
pc = Pinecone(api_key=settings.PINECONE_API_KEY)
index = pc.Index(settings.PINECONE_INDEX_NAME)


def process_pdf_to_pinecone(file_path: str, doc_id: str, user_id: str, document_name: str) -> int:
    """
    Parse a PDF, chunk it, embed each chunk via Gemini, and upsert to Pinecone.

    Returns:
        Total number of chunks stored.
    """
    print(f"\n=========== PDF INGESTION DEBUG: {document_name} ===========")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    vectors = []
    total_chunks = 0

    # 1. Extract text per page
    with pdfplumber.open(file_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            if not text:
                continue

            # 2. Chunk text for this page
            page_chunks = splitter.split_text(text)

            for chunk_index, chunk in enumerate(page_chunks):
                print(f"Processing Page {page_num} - Chunk {chunk_index}")

                # 3. Generate embedding via Gemini
                response = gemini_client.models.embed_content(
                    model="gemini-embedding-001",
                    contents=chunk
                )
                embedding = response.embeddings[0].values

                # 4. Build deterministic chunk ID (used for ordered fetch later)
                chunk_id = f"{doc_id}#chunk{total_chunks}"

                vectors.append({
                    "id": chunk_id,
                    "values": embedding,
                    "metadata": {
                        "text": chunk,
                        "document_name": document_name,
                        "page_number": page_num,
                        "user_id": str(user_id),
                        "doc_id": str(doc_id),
                    },
                })

                total_chunks += 1

    # 5. Upsert to Pinecone in batches
    batch_size = 100
    for i in range(0, len(vectors), batch_size):
        batch = vectors[i:i + batch_size]
        index.upsert(vectors=batch, namespace=str(user_id))
        print(f"Upserted batch of {len(batch)} vectors to Pinecone...")

    print(f"Total vectors upserted to Pinecone: {total_chunks}")
    print("==========================================\n")

    return total_chunks
