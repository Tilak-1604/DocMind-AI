from google import genai
from pinecone import Pinecone
from app.core.config import settings

gemini_client = genai.Client(api_key=settings.GOOGLE_API_KEY)
pc = Pinecone(api_key=settings.PINECONE_API_KEY)
index = pc.Index(settings.PINECONE_INDEX_NAME)


def get_relevant_context(question: str, user_id: str, top_k: int = 3):

    print("\n================ QUESTION DEBUG ================")
    print("Question:", question)

    # 1️⃣ Embed question
    response = gemini_client.models.embed_content(
        model="gemini-embedding-001",
        contents=question
    )
    question_embedding = response.embeddings[0].values

    # 2️⃣ Query Pinecone
    results = index.query(
        namespace=str(user_id),
        vector=question_embedding,
        top_k=top_k,
        include_metadata=True
    )

    context_chunks = []

    for match in results["matches"]:
        text = match["metadata"].get("text", "")
        print("\n---- Retrieved Chunk ----")
        print(text[:200])
        context_chunks.append(text)

    context = "\n\n---\n\n".join(context_chunks)

    print("\nFINAL CONTEXT SENT TO LLM:\n", context[:800])

    # 3️⃣ STRICT RAG PROMPT
    prompt = f"""
You are a document assistant.

Answer ONLY using the provided context.
If the answer is not found in context, say:
"Answer not found in document."

Context:
{context}

Question:
{question}

Answer:
"""

    # 4️⃣ Generate Answer
    response = gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    answer = response.text

    print("\nFINAL ANSWER:\n", answer)
    print("================================================\n")

    return answer