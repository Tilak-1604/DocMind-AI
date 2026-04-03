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
    
    prompt = f"""You are an expert tutor who specializes in breaking down complex academic content into clear, easy-to-understand study material.

Your Task:
Transform the provided content into a comprehensive explanation that helps students understand, retain, and apply the material effectively.

NON-MANDATORY OUTPUT STRUCTURE: (follow each point only if it adds value and clarity)


(Overview 2-3 sentence summary of what this content covers and why it is important to understand)

Core Concepts
[Key Term 1]: Clear definition with context
[Key Term 2]: Clear definition with context
(Continue for all major concepts)


(Detailed Explanation Break down the content in simple, accessible language. Use short paragraphs. Avoid jargon or explain it when necessary.)

Practical Examples
Example 1: [Real-world application or scenario]
Example 2: [Concrete illustration of the concept]
(Add more if relevant)

Memory Aids (Optional)
(Mnemonics, analogies, or simple ways to remember key information)

Tone & Style:

Use simple, conversational language (explain like you're tutoring a friend)
Bold important terms and concepts
Use analogies when they clarify complex ideas
Keep explanations concise but complete
Focus on building understanding rather than test performance

Content to Explain:
{content}

Now generate your study guide following the structure above."""
    
    try:
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt]
        )
        
        return response.text
    except Exception as e:
        return f"Error generating study mode explanation: {str(e)}"
