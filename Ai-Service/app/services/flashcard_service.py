import json
import re
from google import genai
from app.core.config import settings
from app.repositories.chunk_repository import get_document_chunks

# Initialize Gemini client
gemini_client = genai.Client(api_key=settings.GOOGLE_API_KEY)


def generate_flashcards(user_id: str, doc_id: str, num_cards: int = 10):
    """
    Generate flashcards from document content.
    
    Args:
        user_id: User identifier for access validation
        doc_id: Document identifier
        num_cards: Number of flashcards to generate
        
    Returns:
        List of flashcard dictionaries with 'question' and 'answer' keys,
        or error dictionary if JSON parsing fails
        
    Raises:
        ValueError: If document not found or access denied
    """
    # Retrieve chunks deterministically
    chunks = get_document_chunks(user_id, doc_id)
    
    if not chunks:
        return {"error": "No document content found."}
    
    # Limit chunks for safety and token management
    content = "\n\n".join(chunks[:15])
    
    prompt = f"""
You are an AI that generates flashcards.

Generate exactly {num_cards} flashcards.

STRICT RULES:
- Return ONLY valid JSON.
- Do NOT include markdown.
- Do NOT include explanation.
- Do NOT include extra text.
- Output must be a JSON array only.

Format:
[
  {{
    "question": "Question here",
    "answer": "Answer here"
  }}
]

Content:
{content}
"""
    
    try:
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt]
        )
        
        raw_text = response.text
        
        parsed_json = extract_json_from_text(raw_text)
        
        if parsed_json:
            return parsed_json
        else:
            return {
                "error": "Model did not return valid JSON",
                "raw_response": raw_text
            }
    
    except Exception as e:
        return {
            "error": "Flashcard generation failed",
            "details": str(e)
        }


def extract_json_from_text(text: str):
    """
    Safely extract JSON array from LLM response.
    Handles:
    - Markdown fences
    - Extra explanation text
    - Improper formatting
    """

    if not text:
        return None

    # Try direct parsing first
    try:
        return json.loads(text)
    except:
        pass

    # Remove markdown fences such as ```json or ```
    cleaned = text.strip()
    cleaned = re.sub(r"^```json", "", cleaned)
    cleaned = re.sub(r"^```", "", cleaned)
    cleaned = re.sub(r"```$", "", cleaned)
    cleaned = cleaned.strip()

    # Try extracting JSON array
    match = re.search(r"\[.*\]", cleaned, re.DOTALL)

    if match:
        try:
            return json.loads(match.group())
        except:
            pass

    return None