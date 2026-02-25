import pdfplumber
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pinecone import Pinecone
from google import genai
from app.core.config import settings

# 🔹 Initialize Gemini
gemini_client = genai.Client(api_key=settings.GOOGLE_API_KEY)

# 🔹 Initialize Pinecone
pc = Pinecone(api_key=settings.PINECONE_API_KEY)
index = pc.Index(settings.PINECONE_INDEX_NAME)


def process_pdf_to_pinecone(file_path: str, doc_id: str, user_id: str):

    print("\n=========== PDF INGESTION DEBUG ===========")

    # 1️⃣ Extract text
    raw_text = ""

    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                raw_text += text + "\n"

    print("Extracted text length:", len(raw_text))

    # 2️⃣ Chunk text
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = splitter.split_text(raw_text)

    print("Total chunks created:", len(chunks))
    print("Color word present?:", any("colour" in c.lower() for c in chunks))

    vectors = []

    for i, chunk in enumerate(chunks):

        print(f"\nProcessing chunk {i}")

        # 3️⃣ Generate embedding from Gemini
        response = gemini_client.models.embed_content(
            model="gemini-embedding-001",
            contents=chunk
        )

        embedding = response.embeddings[0].values
        print("Embedding length:", len(embedding))

        vectors.append({
            "id": f"{doc_id}#chunk{i}",
            "values": embedding,
            "metadata": {
                "doc_id": str(doc_id),
                "user_id": str(user_id),
                "chunk_index": i,
                "text": chunk
            }
        })

    # 4️⃣ Upsert to Pinecone
    index.upsert(
        vectors=vectors,
        namespace=str(user_id)
    )

    print("Vectors upserted to Pinecone:", len(vectors))
    print("==========================================\n")

    return len(chunks)