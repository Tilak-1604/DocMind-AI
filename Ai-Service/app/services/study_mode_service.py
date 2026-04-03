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
    
    prompt = f"""You are an expert exam preparation tutor specializing in breaking down complex academic content into clear, memorable study material.

**Your Task:**
Transform the provided content into a comprehensive exam-ready explanation that helps students understand, retain, and apply the material.

**MANDATORY OUTPUT STRUCTURE:**

**📚 Overview**  
(2-3 sentence summary of what this content covers and why it's important for exams)

**🎯 Core Concepts**  
- **[Key Term 1]**: Clear definition with context
- **[Key Term 2]**: Clear definition with context
- *(Continue for all major concepts)*

**📝 Detailed Explanation**  
(Break down the content in simple, accessible language. Use short paragraphs. Avoid jargon or explain it when necessary.)

**💡 Practical Examples**  
- Example 1: [Real-world application or scenario]
- Example 2: [Concrete illustration of the concept]
- *(Add more if relevant)*

**🔑 Key Takeaways for Exams**  
- Point 1: [Essential fact to remember]
- Point 2: [Critical concept to understand]
- Point 3: [Common exam question topic]
- *(3-5 points maximum)*

**⚠️ Common Mistakes to Avoid**  
- Mistake 1: [What students often get wrong]
- Mistake 2: [Misconception to avoid]

**🧠 Memory Aids**  
(Mnemonics, acronyms, or simple ways to remember key information)

**Tone & Style:**
- Use simple, conversational language (explain like you're tutoring a friend)
- Bold important terms and concepts
- Use analogies when they clarify complex ideas
- Keep explanations concise but complete
- Focus on exam-relevant information

**Content to Explain:**
{content}

Now generate your exam preparation guide following the exact structure above:"""
    
    try:
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt]
        )
        
        return response.text
    except Exception as e:
        return f"Error generating study mode explanation: {str(e)}"
