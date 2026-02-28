from typing import List
from google import genai
from app.core.config import settings
from app.repositories.chunk_repository import get_document_chunks

# Initialize Gemini client
gemini_client = genai.Client(api_key=settings.GOOGLE_API_KEY)


def generate_mind_map(user_id: str, doc_id: str) -> str:
    """
    Generate a PlantUML mind map for the given document.
    
    Process:
    1. Retrieve all document chunks deterministically
    2. Split into batches of 5 chunks
    3. Summarize each batch into key ideas and subtopics to keep token count manageable
    4. Combine partial hierarchical summaries
    5. Generate a final valid PlantUML mind map structure
    
    Args:
        user_id: User identifier for access validation
        doc_id: Document identifier
        
    Returns:
        PlantUML formatted string containing the mind map.
        
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
    
    # Map phase: Outline each batch
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        content = "\n\n".join(batch)
        
        prompt = f"""Extract the core topics and subtopics from this content to help form a mind map. Keep it hierarchical and concise.

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
            print(f"Error outlining batch {i//batch_size}: {e}")
            continue
    
    if not partial_summaries:
        return "Unable to generate mind map due to processing errors."
    
    # Reduce phase: Combine partial summaries
    final_content = "\n\n".join(partial_summaries)
    
    # Final structured mind map generation in PlantUML format
    final_prompt = f"""You are a tool that generates PlantUML mind maps. 
    Based on the following hierarchical summaries, create a single, comprehensive PlantUML mindmap. 
    Use the `@startmindmap` and `@endmindmap` tags. 
    Use `*` for the root, `**` for the first level of branches, `***` for the second level, and so on.
    Keep the node titles concise.
    Return ONLY the valid PlantUML code, not wrapped in any markdown code blocks, just the raw text starting with @startmindmap and ending with @endmindmap.

    Content:
    {final_content}
    """
    
    try:
        final_response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[final_prompt]
        )
        return final_response.text.strip().replace("```plantuml", "").replace("```", "").strip()
    except Exception as e:
        print(f"Error generating final mind map: {e}")
        return "Error generating mind map."
