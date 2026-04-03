from google import genai
from app.core.config import settings
from app.repositories.chunk_repository import get_document_chunks

# Initialize Gemini client
gemini_client = genai.Client(api_key=settings.GOOGLE_API_KEY)


def exam_mode(
    user_id: str, 
    doc_id: str,
    marks_1: int = 2,
    marks_2: int = 5,
    marks_5: int = 3,
    marks_10: int = 0
):
    """
    Generate exam questions with flexible mark distribution.
    
    Args:
        user_id: User identifier for access validation
        doc_id: Document identifier
        marks_1: Number of 1-mark questions (default: 2)
        marks_2: Number of 2-mark questions (default: 5)
        marks_5: Number of 5-mark questions (default: 3)
        marks_10: Number of 10-mark questions (default: 0)
        
    Returns:
        Formatted exam paper with questions and model answers
        
    Raises:
        ValueError: If document not found or access denied
    """
    # Retrieve chunks deterministically
    chunks = get_document_chunks(user_id, doc_id)
    
    if not chunks:
        return "No document content found."
    
    # Limit chunks for safety and token management
    content = "\n\n".join(chunks[:20])
    
    # Calculate totals
    total_questions = marks_1 + marks_2 + marks_5 + marks_10
    total_marks = (marks_1 * 1) + (marks_2 * 2) + (marks_5 * 5) + (marks_10 * 10)
    
    if total_questions == 0:
        return "Error: Please specify at least one question."
    
    # Build question distribution description
    distribution_parts = []
    if marks_1 > 0:
        distribution_parts.append(f"{marks_1} question(s) × 1 mark = {marks_1} marks")
    if marks_2 > 0:
        distribution_parts.append(f"{marks_2} question(s) × 2 marks = {marks_2 * 2} marks")
    if marks_5 > 0:
        distribution_parts.append(f"{marks_5} question(s) × 5 marks = {marks_5 * 5} marks")
    if marks_10 > 0:
        distribution_parts.append(f"{marks_10} question(s) × 10 marks = {marks_10 * 10} marks")
    
    distribution_text = "\n".join(distribution_parts)
    
    prompt = f"""You are an expert academic examiner who creates comprehensive examination papers based on study material.

Your Task:
Generate a complete examination paper with questions and model answers based on the provided content.

EXAM SPECIFICATIONS:
Total Questions: {total_questions}
Total Marks: {total_marks}

Question Distribution:
{distribution_text}

MANDATORY OUTPUT STRUCTURE:

📝 EXAMINATION PAPER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Marks: {total_marks}
Total Questions: {total_questions}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SECTION A: 1-Mark Questions
(Generate {marks_1} questions if specified, each worth 1 mark)
For each question:
Q1. [Question text] (1 mark)

SECTION B: 2-Mark Questions  
(Generate {marks_2} questions if specified, each worth 2 marks)
For each question:
Q{marks_1 + 1}. [Question text] (2 marks)

SECTION C: 5-Mark Questions
(Generate {marks_5} questions if specified, each worth 5 marks)
For each question:
Q{marks_1 + marks_2 + 1}. [Question text] (5 marks)

SECTION D: 10-Mark Questions
(Generate {marks_10} questions if specified, each worth 10 marks)
For each question:
Q{marks_1 + marks_2 + marks_5 + 1}. [Question text] (10 marks)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📖 MODEL ANSWERS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Answer 1: [Comprehensive model answer for Q1]
(Include all key points expected for full marks)

Answer 2: [Comprehensive model answer for Q2]
...

[Continue for all questions]

QUESTION DESIGN GUIDELINES:

1-Mark Questions:
- Focus on definitions, terminology, quick facts
- Test recall and basic understanding
- Keep answers concise (1-2 sentences)
- Examples: "Define X", "What is Y?", "State Z"

2-Mark Questions:
- Require brief explanations or comparisons
- Test conceptual understanding
- Answers should be 2-4 sentences
- Examples: "Explain briefly...", "Differentiate between...", "Give two examples of..."

5-Mark Questions:
- Require detailed explanations or analysis
- Test deep understanding and application
- Answers should be comprehensive (5-8 sentences or structured points)
- Examples: "Explain in detail...", "Discuss the significance of...", "Analyze..."

10-Mark Questions:
- Require extensive analysis, evaluation, or problem-solving
- Test mastery and critical thinking
- Answers should be thorough with multiple aspects covered
- Examples: "Critically evaluate...", "Compare and contrast extensively...", "Solve and explain..."

Quality Standards:
- Questions must be directly answerable from the provided content
- Avoid ambiguous or trick questions
- Ensure mark allocation matches answer depth
- Cover different aspects of the material
- Progress from simpler to more complex concepts
- Model answers must be accurate, complete, and well-structured
- Include all key points, examples, and explanations needed for full marks

Content to Base Questions On:
{content}

Now generate the complete examination paper with all questions and model answers following the structure above."""
    
    try:
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt]
        )
        
        return response.text
    except Exception as e:
        return f"Error generating exam paper: {str(e)}"
