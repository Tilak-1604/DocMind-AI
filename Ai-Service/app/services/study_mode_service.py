from google import genai
from app.core.config import settings
from app.repositories.chunk_repository import get_document_chunks

# Initialize Gemini client
gemini_client = genai.Client(api_key=settings.GOOGLE_API_KEY)


def study_mode(user_id: str, doc_id: str):
    """
    Generate study mode explanation for exam preparation.
    
    Args:
        user_id: User identifier for access validation
        doc_id: Document identifier
        
    Returns:
        Formatted text explanation with bullet points, simplified language,
        highlighted terms, and examples
        
    Raises:
        ValueError: If document not found or access denied
    """
    # Retrieve chunks deterministically
    chunks = get_document_chunks(user_id, doc_id)
    
    if not chunks:
        return "No document content found."
    
    # Limit chunks for safety and token management
    content = "\n\n".join(chunks[:20])
    
    prompt = f"""
Explain this for exam preparation:

- Use bullet points
- Simplify language
- Highlight important terms
- Add examples

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
        return f"Error generating study mode explanation: {str(e)}"
