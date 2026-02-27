from google import genai
from app.core.config import settings
from app.repositories.chunk_repository import get_document_chunks

# Initialize Gemini client
gemini_client = genai.Client(api_key=settings.GOOGLE_API_KEY)


def extract_key_topics(user_id: str, doc_id: str):
    """
    Extract important topics and definitions from document content.
    
    Args:
        user_id: User identifier for access validation
        doc_id: Document identifier
        
    Returns:
        JSON string containing topics with titles and definitions
        
    Raises:
        ValueError: If document not found or access denied
    """
    # Retrieve chunks deterministically
    chunks = get_document_chunks(user_id, doc_id)
    
    if not chunks:
        return '{"error": "No document content found."}'
    
    # Limit chunks for safety and token management
    content = "\n\n".join(chunks[:20])
    
    prompt = f"""
Extract important topics and definitions.

Return JSON:
{{
  "topics": [
    {{"title": "...", "definition": "..."}}
  ]
}}

Content:
{content}
"""
    
    try:
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt]
        )
        
        return response.text
    except Exception as e:
        return f'{{"error": "Error extracting topics: {str(e)}"}}'
