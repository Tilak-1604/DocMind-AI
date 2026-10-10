from google import genai

from app.core.config import settings
from app.repositories.chunk_repository import get_document_chunks

gemini_client = genai.Client(api_key=settings.GOOGLE_API_KEY)


def study_mode(user_id: str, doc_id: str) -> str:
    """
    Generate a study-friendly explanation of the document for exam preparation.

    Args:
        user_id: User identifier for access validation
        doc_id: Document identifier

    Returns:
        Formatted text explanation with bullet points, simplified language,
        highlighted terms, and examples.
    """
    chunks = get_document_chunks(user_id, doc_id)

    if not chunks:
        return "No document content found."

    # Limit chunks for token safety
    content = "\n\n".join(chunks[:15])

    prompt = f"""You are an expert study guide creator and academic tutor. Your task is to transform complex document content into a clear, comprehensive study guide that helps students understand and remember the material effectively.

**MANDATORY OUTPUT STRUCTURE:**

# 📚 Study Guide

## 🎯 Overview
(2-3 sentences explaining what this content is about and why it matters)

## 📖 Core Concepts Explained Simply
For each major concept:
**[Concept Name]**
- Simple Explanation: [Explain as if to a smart high schooler]
- Why It Matters: [Real-world relevance or importance]
- Remember This: [Key takeaway or memory hook]

## 🔑 Key Terms & Definitions
| Term | Definition | Example |
|------|------------|---------|
| [term] | [clear definition] | [practical example] |

## 📝 Important Points to Remember
- **Point 1**: [Critical fact with explanation]
- **Point 2**: [Critical fact with explanation]
- *(Continue for all major points)*

## 🔗 How It All Connects
(Explain the relationships between concepts and the big picture)

## ✅ Quick Review Checklist
- [ ] I understand [concept 1]
- [ ] I can explain [concept 2]
- [ ] I know the difference between [X] and [Y]

**Quality Standards:**
- Use clear, accessible language
- Include concrete examples for abstract concepts
- Highlight exam-relevant information
- Make connections between concepts explicit

**Document Content:**
{content}

Generate the complete study guide:"""

    try:
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt]
        )
        return response.text
    except Exception as e:
        return f"Error generating study guide: {str(e)}"
