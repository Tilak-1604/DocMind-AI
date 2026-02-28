from google import genai
from pinecone import Pinecone
from app.core.config import settings
from app.services.memory_service import get_recent_messages, save_message

gemini_client = genai.Client(api_key=settings.GOOGLE_API_KEY)
pc = Pinecone(api_key=settings.PINECONE_API_KEY)
index = pc.Index(settings.PINECONE_INDEX_NAME)


def get_relevant_context(
    question: str,
    user_id: str,
    conversation_id: str,
    top_k: int = 5
):

    print("\n================ QUESTION DEBUG ================")
    print("Question:", question)

    # ----------------------------------
    # 1️⃣ Load Conversation Memory
    # ----------------------------------
    memory_messages = get_recent_messages(conversation_id)

    formatted_history = ""
    for msg in memory_messages:
        formatted_history += f"{msg.role.upper()}: {msg.content}\n"

    # ----------------------------------
    # 2️⃣ Embed Question
    # ----------------------------------
    response = gemini_client.models.embed_content(
        model="gemini-embedding-001",
        contents=question
    )

    question_embedding = response.embeddings[0].values

    # ----------------------------------
    # 3️⃣ Query Pinecone
    # ----------------------------------
    results = index.query(
        namespace=str(user_id),
        vector=question_embedding,
        top_k=top_k,
        include_metadata=True
    )

    context_chunks = []
    source_ids = []
    score_threshold = 0.20

    for match in results["matches"]:
        score = match["score"]

        if score >= score_threshold:
            meta = match["metadata"]
            text = meta.get("text", "")
            doc_name = meta.get("document_name", "Unknown Document")
            page_num = meta.get("page_number", "Unknown Page")
            
            # Format chunks with explicit citation metadata
            formatted_chunk = f"[Source: {doc_name} (Page {page_num})]\n{text}"
            context_chunks.append(formatted_chunk)
            source_ids.append(match["id"])

    if not context_chunks:
        answer = "I cannot find this information in the uploaded documents."
        save_message(conversation_id, "user", question)
        save_message(conversation_id, "assistant", answer)
        return {
            "answer": answer,
            "sources": []
        }

    context = "\n\n---\n\n".join(context_chunks)

    # ----------------------------------
    # 4️⃣ Build Strict Conversational Prompt
    # ----------------------------------
    prompt = f"""
You are a document-based AI assistant.
Answer ONLY using the provided context.
If the answer is not found in the context, respond with:
"I cannot find this information in the uploaded documents."
Do NOT use external knowledge.
Always cite the source document name and page number when possible.

----------------------
Context:
{context}

----------------------
Conversation History:
{formatted_history}

----------------------
Question:
{question}

Answer:
"""

    # ----------------------------------
    # 5️⃣ Generate Answer
    # ----------------------------------
    try:
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt]
        )
        answer = response.text
    except Exception as e:
        print("LLM ERROR:", str(e))
        answer = "Error generating answer."

    # ----------------------------------
    # 6️⃣ Save Conversation Memory
    # ----------------------------------
    save_message(conversation_id, "user", question)
    save_message(conversation_id, "assistant", answer)

    print("\nFINAL ANSWER:\n", answer)
    print("================================================\n")

    return {
        "answer": answer,
        "sources": source_ids
    }