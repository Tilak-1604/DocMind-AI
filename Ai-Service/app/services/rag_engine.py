"""
rag_engine.py — Conversational RAG Engine (Production-Grade)

Five core enhancements:
  1. Query Rewriting       — Gemini rewrites ambiguous follow-ups before embedding
  2. Structured Prompt     — Role, grounding, citation, multi-source merging
  3. Retrieval Fallback    — Retry with top_k=8 + threshold=0.15 if recall is low
  4. Smart Memory          — Gemini summarizes old turns; inject summary + recent 4
  5. Intent Detection      — Adapts answer format based on question prefix
"""

from google import genai
from pinecone import Pinecone
from app.core.config import settings
from app.services.memory_service import (
    get_recent_messages,
    save_message,
    get_message_count,
    get_old_messages_for_compression,
    get_conversation_summary,
    save_conversation_summary,
)

# ─────────────────────────────────────────────
# Client Initialization
# ─────────────────────────────────────────────
gemini_client = genai.Client(api_key=settings.GOOGLE_API_KEY)
pc = Pinecone(api_key=settings.PINECONE_API_KEY)
index = pc.Index(settings.PINECONE_INDEX_NAME)

MEMORY_COMPRESSION_THRESHOLD = 6   # Compress when total turns exceed this
RECENT_TURNS_LIMIT = 4              # Always keep last 4 messages verbatim
MIN_CHUNKS_BEFORE_FALLBACK = 2     # Trigger fallback if fewer chunks retrieved
FALLBACK_TOP_K = 8
FALLBACK_THRESHOLD = 0.15
PRIMARY_TOP_K = 5
PRIMARY_THRESHOLD = 0.20


# ─────────────────────────────────────────────
# Feature 1: Query Rewriting
# ─────────────────────────────────────────────
def rewrite_query(original_question: str, conversation_history: str) -> str:
    """
    Uses Gemini to rewrite a vague/follow-up question into a fully
    self-contained standalone query suitable for semantic search.
    Returns original if rewriting fails or adds no value.
    """
    if not conversation_history.strip():
        return original_question

    rewrite_prompt = f"""You are an expert query optimization specialist for semantic search systems.

**Your Task:**
Transform a conversational follow-up question into a fully self-contained, semantically rich standalone query optimized for document retrieval.

**REWRITING RULES:**

1. **Self-Containment**: The rewritten query must be completely understandable without any conversation history
2. **Pronoun Resolution**: Replace ALL pronouns (it, its, they, that, this, these, those, he, she) with their specific referents from the conversation
3. **Context Enrichment**: Add relevant context from the conversation that clarifies the user's intent
4. **Semantic Optimization**: Use clear, specific terminology that will match relevant document content
5. **Preserve Intent**: Maintain the exact meaning and scope of the original question
6. **No Explanation**: Output ONLY the rewritten question - no preamble, no commentary

**Special Cases:**
- If the question is already fully self-contained and clear → Return it unchanged
- If the question references "the previous answer" → Incorporate the key topic from that answer
- If multiple topics are in history → Focus on the most recent relevant context

**Conversation History:**
{conversation_history}

**Follow-up Question:**
{original_question}

**Rewritten Standalone Query:**"""

    try:
        response = gemini_client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[rewrite_prompt]
        )
        rewritten = response.text.strip()
        print(f"[QUERY REWRITE] Original: '{original_question}'")
        print(f"[QUERY REWRITE] Rewritten: '{rewritten}'")
        return rewritten if rewritten else original_question
    except Exception as e:
        print(f"[QUERY REWRITE] Failed, using original. Error: {e}")
        return original_question


# ─────────────────────────────────────────────
# Feature 5: Intent Detection
# ─────────────────────────────────────────────
def detect_intent(question: str) -> str:
    """Detects the response format intent from the question prefix."""
    q = question.strip().lower()
    if q.startswith("compare"):
        return "compare"
    if q.startswith("summarize") or q.startswith("summarise"):
        return "summarize"
    if q.startswith("list"):
        return "list"
    if q.startswith("explain simply") or q.startswith("explain in simple"):
        return "explain_simple"
    if q.startswith("define"):
        return "define"
    return "default"


def get_intent_style_instruction(intent: str) -> str:
    """Returns the style instruction block for the given intent."""
    styles = {
        "compare": (
            "Response Style: COMPARISON MODE\n"
            "- Structure the answer as a side-by-side comparison.\n"
            "- Use a table or clearly labeled sections (e.g., 'Concept A:' / 'Concept B:').\n"
            "- Highlight key differences and similarities."
        ),
        "summarize": (
            "Response Style: SUMMARY MODE\n"
            "- Provide a concise, high-level summary.\n"
            "- Use 3-5 bullet points. Avoid unnecessary detail."
        ),
        "list": (
            "Response Style: LIST MODE\n"
            "- Return a clean numbered or bulleted list.\n"
            "- One item per line. No long paragraphs."
        ),
        "explain_simple": (
            "Response Style: SIMPLIFIED EXPLANATION MODE\n"
            "- Use plain, simple language suitable for a beginner.\n"
            "- Avoid jargon. Use analogies if helpful."
        ),
        "define": (
            "Response Style: DEFINITION MODE\n"
            "- Start with a clear, concise definition.\n"
            "- Then provide supporting detail from the document."
        ),
        "default": (
            "Response Style: DEFAULT\n"
            "- Provide a thorough, well-structured answer.\n"
            "- Use headings and bullet points where appropriate."
        ),
    }
    return styles.get(intent, styles["default"])


# ─────────────────────────────────────────────
# Feature 4: Smart Memory Compression
# ─────────────────────────────────────────────
def maybe_compress_memory(conversation_id: str) -> str | None:
    """
    Checks if memory compression is needed.
    If message count > threshold AND no summary exists yet,
    compresses older messages with Gemini and stores the summary.
    
    Returns the summary text (existing or newly created), or None.
    """
    # Always try to return existing summary first
    existing_summary = get_conversation_summary(conversation_id)

    total_messages = get_message_count(conversation_id)
    print(f"[MEMORY] Total messages in conversation: {total_messages}")

    if total_messages > MEMORY_COMPRESSION_THRESHOLD and existing_summary is None:
        # Only compress once — when threshold is first crossed
        old_messages = get_old_messages_for_compression(
            conversation_id, keep_recent=RECENT_TURNS_LIMIT
        )

        if not old_messages:
            return None

        messages_text = "\n".join(
            f"{m.role.upper()}: {m.content}" for m in old_messages
        )

        compress_prompt = f"""You are an expert conversation summarizer specializing in preserving critical context for AI assistants.

**Your Task:**
Create a concise yet comprehensive summary of this conversation history that preserves all information needed to answer future follow-up questions accurately.

**SUMMARIZATION REQUIREMENTS:**

**What to Preserve:**
- Main topics and themes discussed
- Key facts, data points, and specific details mentioned
- Important questions asked and their answers
- Any context about user preferences or requirements
- Technical terms, names, dates, or numbers
- The logical flow and progression of topics

**What to Omit:**
- Greeting pleasantries and filler words
- Repetitive information
- Meta-discussion about the conversation itself
- Unnecessary elaboration or verbose explanations

**Output Format:**
Write a flowing paragraph summary (not bullet points) that reads naturally and efficiently captures the conversation essence. Keep it under 200 words while being comprehensive.

**Quality Standards:**
- Maintain factual accuracy - never add information not present
- Use precise language and key terminology from the original
- Organize information logically by topic
- Make it useful for understanding follow-up questions

**Conversation to Summarize:**
{messages_text}

**Concise Summary:**"""

        try:
            resp = gemini_client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[compress_prompt]
            )
            new_summary = resp.text.strip()
            save_conversation_summary(conversation_id, new_summary)
            print(f"[MEMORY] Compressed {len(old_messages)} messages into summary.")
            return new_summary
        except Exception as e:
            print(f"[MEMORY] Compression failed: {e}")
            return None

    return existing_summary


# ─────────────────────────────────────────────
# Core RAG Engine
# ─────────────────────────────────────────────
def get_relevant_context(
    question: str,
    user_id: str,
    conversation_id: str,
    document_ids: list[str] = None
):
    print("\n================ RAG ENGINE START ================")
    print(f"[INPUT] User: {user_id} | Question: {question} | Docs: {document_ids}")

    # ──────────────────────────────────────────
    # Step 1: Load recent messages for history
    # ──────────────────────────────────────────
    recent_messages = get_recent_messages(conversation_id, limit=RECENT_TURNS_LIMIT)
    formatted_history = "\n".join(
        f"{m.role.upper()}: {m.content}" for m in recent_messages
    )

    # ──────────────────────────────────────────
    # Step 2: Query Rewriting (Feature 1)
    # ──────────────────────────────────────────
    search_query = rewrite_query(question, formatted_history)

    # ──────────────────────────────────────────
    # Step 3: Embed the rewritten query
    # ──────────────────────────────────────────
    embed_response = gemini_client.models.embed_content(
        model="gemini-embedding-001",
        contents=search_query
    )
    query_embedding = embed_response.embeddings[0].values

    # ──────────────────────────────────────────
    # Step 4: Pinecone Retrieval + Fallback (Feature 3)
    # ──────────────────────────────────────────
    def run_pinecone_query(top_k: int, threshold: float):
        query_params = {
            "namespace": str(user_id),
            "vector": query_embedding,
            "top_k": top_k,
            "include_metadata": True
        }
        
        if document_ids:
            query_params["filter"] = {"doc_id": {"$in": document_ids}}

        results = index.query(**query_params)
        chunks, sources = [], []
        for match in results.get("matches", []):
            if match["score"] >= threshold:
                meta = match["metadata"]
                text = meta.get("text", "")
                doc_name = meta.get("document_name", "Unknown Document")
                page_num = meta.get("page_number", "?")
                chunks.append(f"[Source: {doc_name} (Page {page_num})]\n{text}")
                sources.append(match["id"])
        return chunks, sources

    print(f"[RETRIEVAL] Primary query: top_k={PRIMARY_TOP_K}, threshold={PRIMARY_THRESHOLD}")
    context_chunks, source_ids = run_pinecone_query(PRIMARY_TOP_K, PRIMARY_THRESHOLD)
    print(f"[RETRIEVAL] Chunks found: {len(context_chunks)}")

    # Fallback if recall is low
    if len(context_chunks) < MIN_CHUNKS_BEFORE_FALLBACK:
        print(f"[RETRIEVAL] ⚠️  FALLBACK TRIGGERED — retrying top_k={FALLBACK_TOP_K}, threshold={FALLBACK_THRESHOLD}")
        context_chunks, source_ids = run_pinecone_query(FALLBACK_TOP_K, FALLBACK_THRESHOLD)
        print(f"[RETRIEVAL] Fallback chunks found: {len(context_chunks)}")

    # No context found even after fallback
    if not context_chunks:
        answer = "I cannot find this information in the uploaded documents."
        save_message(conversation_id, "user", question)
        save_message(conversation_id, "assistant", answer)
        return {"answer": answer, "sources": []}

    context_block = "\n\n---\n\n".join(context_chunks)

    # ──────────────────────────────────────────
    # Step 5: Smart Memory Compression (Feature 4)
    # ──────────────────────────────────────────
    conversation_summary = maybe_compress_memory(conversation_id)
    summary_block = conversation_summary if conversation_summary else "No prior conversation summary."

    # ──────────────────────────────────────────
    # Step 6: Intent Detection (Feature 5)
    # ──────────────────────────────────────────
    intent = detect_intent(question)
    style_instruction = get_intent_style_instruction(intent)
    print(f"[INTENT] Detected: {intent}")

    # ──────────────────────────────────────────
    # Step 7: Structured Prompt Construction (Feature 2)
    # ──────────────────────────────────────────
    prompt = f"""You are Docsmind, an expert, precise, and highly structured AI assistant specialized in analyzing PDFs and other documents using Retrieval-Augmented Generation (RAG).

Your core rules:
1. **Ground every answer strictly in the provided context only.** Never hallucinate, invent, or use external knowledge.
2. If the answer cannot be found in the context, respond with: "I could not find sufficient information in the provided document to answer this question accurately."
3. Always produce **clean, professional, and perfectly structured** responses using Markdown.
4. Never use vague or free-flowing paragraphs. Every response must follow a consistent, readable format.

**MANDATORY OUTPUT STRUCTURE** (use this exact structure for every response):

**📌 Summary**  
(One or two sentence overview of the answer)

**📋 Detailed Answer**  
(Complete, clear explanation based only on the document)

**🔑 Key Points**  
- Bullet point 1
- Bullet point 2
- ...

**📍 Document References**  
- Page X / Section Y: [exact quote or paraphrase]
- Page A / Section B: [exact quote or paraphrase]
(Only include references that actually exist in the retrieved context)

**💡 Additional Insights** (only if relevant and present in the document)  
(Extra useful information or connections found in the document)

**Tone & Style:**
- Professional, confident, and helpful
- Concise yet complete
- Zero filler words or unnecessary phrases
- Use bold and italics only when they improve clarity

{style_instruction}

══════════════════════════
CONTEXT (Retrieved from uploaded documents):
{context_block}

══════════════════════════
CONVERSATION SUMMARY (Older turns):
{summary_block}

══════════════════════════
RECENT MESSAGES:
{formatted_history if formatted_history else "No recent messages."}

══════════════════════════
CURRENT QUESTION:
{question}

Now generate your response following the exact structure above:"""

    # ──────────────────────────────────────────
    # Step 8: Generate Answer with Gemini
    # ──────────────────────────────────────────
    try:
        gen_response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt]
        )
        answer = gen_response.text
    except Exception as e:
        print(f"[LLM ERROR] {e}")
        answer = "An error occurred while generating the answer. Please try again."

    # ──────────────────────────────────────────
    # Step 9: Persist original question + answer
    # ──────────────────────────────────────────
    save_message(conversation_id, "user", question)
    save_message(conversation_id, "assistant", answer)

    print(f"\n[FINAL ANSWER]\n{answer}")
    print("================ RAG ENGINE END ================\n")

    return {
        "answer": answer,
        "sources": source_ids
    }