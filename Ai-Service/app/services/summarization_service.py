from typing import List
from google import genai
from app.core.config import settings
from app.repositories.chunk_repository import get_document_chunks

# Initialize Gemini client
gemini_client = genai.Client(api_key=settings.GOOGLE_API_KEY)


def summarize_document(user_id: str, doc_id: str) -> str:
    """
    Generate a structured document summary using Map-Reduce pattern.
    
    Process:
    1. Retrieve all document chunks deterministically
    2. Split into batches of 5 chunks
    3. Summarize each batch into key ideas and definitions
    4. Combine partial summaries
    5. Generate final structured summary with sections
    
    Args:
        user_id: User identifier for access validation
        doc_id: Document identifier
        
    Returns:
        Structured summary text with Executive Summary, Key Points, 
        Important Definitions, and Exam Notes sections
        
    Raises:
        ValueError: If document not found or access denied
    """
    # Retrieve chunks deterministically
    chunks = get_document_chunks(user_id, doc_id)
    
    if not chunks:
        return "No document content found."
    
    # Prevent token explosion by limiting total chunks processed
    max_chunks = 50  # Adjust based on model limits
    if len(chunks) > max_chunks:
        chunks = chunks[:max_chunks]
    
    batch_size = 5
    partial_summaries: List[str] = []
    
    # Map phase: Summarize each batch
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        content = "\n\n".join(batch)
        
        prompt = f"""Summarize this content into key ideas and definitions.

        Content:
        {content}
        """
        
        try:
            response = gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[prompt]
            )
            partial_summaries.append(response.text.strip())
        except Exception as e:
            # Log error and continue with available summaries
            print(f"Error summarizing batch {i//batch_size}: {e}")
            continue
    
    if not partial_summaries:
        return "Unable to generate summary due to processing errors."
    
    # Reduce phase: Combine partial summaries
    final_content = "\n\n".join(partial_summaries)
    
    # Final structured summary generation
    final_prompt = f"""Create a final structured summary with the following sections:

    1. Executive Summary
    2. Key Points
    3. Important Definitions
    4. Exam Notes

    Content:
    {final_content}
    """
    
    try:
        final_response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[final_prompt]
        )
        return final_response.text.strip()
    except Exception as e:
        print(f"Error generating final summary: {e}")
        return "Error generating final summary."
