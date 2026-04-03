import json
from typing import List, Dict, Any
from groq import Groq
from pydantic import BaseModel
from pydantic.json import pydantic_encoder
from app.core.config import settings
from app.db import SessionLocal
from app.repositories.chunk_repository import get_document_chunks
from app.repositories.document_repository import get_document_by_id
from app.models.extracted_data import ExtractedChunk

# Initialize Groq client (optional for startup)
groq_client = None
if settings.GROQ_API_KEY:
    groq_client = Groq(api_key=settings.GROQ_API_KEY)
else:
    print("WARNING: GROQ_API_KEY not found. Extraction features will be disabled.")

# Define Pydantic models for structured output
class KeyConcept(BaseModel):
    term: str
    definition: str

class ExtractedData(BaseModel):
    chunk_summary: str
    key_concepts: List[KeyConcept]
    hierarchical_topics: List[str]
    important_facts: List[str]

def run_background_extraction(user_id: str, doc_id: str):
    """
    Background task to extract structured data from all document chunks
    and generate final global summary and mind map.
    """
    db = SessionLocal()
    try:
        # Mark document as processing
        document = get_document_by_id(db, doc_id)
        if not document:
            print(f"Extraction failed: Document {doc_id} not found.")
            return

        document.extraction_status = "PENDING"
        db.commit()

        # Fetch chunks
        chunks = get_document_chunks(user_id, doc_id)
        if not chunks:
            document.extraction_status = "FAILED"
            db.commit()
            return

        print(f"Starting background extraction for doc {doc_id} with {len(chunks)} chunks...")

        # Process each chunk
        chunk_summaries = []
        all_topics = []

        max_chunks = 50 # Limit to avoid excessive processing
        if len(chunks) > max_chunks:
            chunks = chunks[:max_chunks]

        for i, chunk_text in enumerate(chunks):
            print(f"Extracting data for chunk {i+1}/{len(chunks)}...")
            try:
                prompt = f"""You are a precision data extraction specialist. Your task is to analyze the provided text and extract structured information with maximum accuracy and completeness.

**EXTRACTION REQUIREMENTS:**

You must output ONLY valid JSON that matches this exact schema:

{{
  "chunk_summary": "A comprehensive 2-3 sentence summary capturing the main ideas and purpose of this text segment.",
  "key_concepts": [
    {{
      "term": "Precise concept or term name",
      "definition": "Clear, complete definition with context and relevance"
    }}
  ],
  "hierarchical_topics": [
    "Broad overarching category",
    "Mid-level sub-topic",
    "Specific detailed topic"
  ],
  "important_facts": [
    "Critical fact 1 (include numbers, dates, names, or key assertions)",
    "Critical fact 2",
    "Critical fact 3"
  ]
}}

**EXTRACTION GUIDELINES:**

1. **chunk_summary**: 
   - Capture the essence and main purpose
   - Include the most significant information
   - Make it self-contained and understandable alone

2. **key_concepts**: 
   - Extract 3-7 major concepts or terms
   - Provide clear, academic-quality definitions
   - Include context about why each concept matters

3. **hierarchical_topics**: 
   - Organize from general to specific (3-5 levels)
   - Create a logical taxonomy of the content
   - Use clear, descriptive topic names

4. **important_facts**: 
   - Extract 5-10 critical, exam-worthy facts
   - Include specific details: numbers, dates, names, formulas
   - Prioritize verifiable, concrete information

**Quality Standards:**
- Be thorough and precise
- Maintain academic rigor
- Preserve technical accuracy
- Extract maximum value from every sentence

**Text to Analyze:**
{chunk_text}

Output only the JSON, no additional text:"""
                
                if not groq_client:
                    print(f"Skipping extraction for chunk {i}: Groq client not initialized.")
                    continue

                response = groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"},
                    temperature=0.2
                )

                extracted_data = json.loads(response.choices[0].message.content)
                
                # Save to database
                db_chunk = ExtractedChunk(
                    id=f"{doc_id}_ext_{i}",
                    doc_id=doc_id,
                    user_id=user_id,
                    chunk_index=i,
                    chunk_summary=extracted_data.get("chunk_summary", ""),
                    key_concepts=extracted_data.get("key_concepts", []),
                    hierarchical_topics=extracted_data.get("hierarchical_topics", []),
                    important_facts=extracted_data.get("important_facts", [])
                )
                db.add(db_chunk)
                
                chunk_summaries.append(extracted_data.get("chunk_summary", ""))
                all_topics.extend(extracted_data.get("hierarchical_topics", []))

            except Exception as e:
                print(f"Error extracting chunk {i}: {e}")
                continue
        
        db.commit()

        # Step 2: Generate Global Summary using chunk_summaries
        print(f"Generating global summary for doc {doc_id}...")
        global_summary = _generate_global_summary(chunk_summaries)
        
        # Step 3: Generate Mind Map PlantUML using all_topics
        print(f"Generating mind map for doc {doc_id}...")
        mind_map_plantuml = _generate_mind_map(all_topics, document.id)

        # Update Document
        document.global_summary = global_summary
        document.mind_map_plantuml = mind_map_plantuml
        document.extraction_status = "COMPLETED"
        db.commit()
        print(f"Background extraction completed for doc {doc_id}.")

    except Exception as e:
        print(f"Background extraction failed: {e}")
        db.rollback()
        # Try to mark as failed if document still exists in memory
        try:
            doc = get_document_by_id(db, doc_id)
            if doc:
                doc.extraction_status = "FAILED"
                db.commit()
        except:
            pass
    finally:
        db.close()


def _generate_global_summary(chunk_summaries: List[str]) -> str:
    if not chunk_summaries:
        return "No summary could be generated."
        
    final_content = "\\n\\n".join(chunk_summaries)
    
    final_prompt = f"""You are an expert document synthesizer. Your task is to create a comprehensive, professionally structured summary from multiple text segments.

**MANDATORY OUTPUT STRUCTURE:**

# 📊 Executive Summary
(3-5 sentence high-level overview of the entire document's purpose, scope, and main conclusions)

# 🔑 Key Points
- **Major Point 1**: [Detailed explanation]
- **Major Point 2**: [Detailed explanation]  
- **Major Point 3**: [Detailed explanation]
- *(Continue for all significant points - aim for 5-8 total)*

# 📖 Important Definitions
- **[Term 1]**: Precise definition with context
- **[Term 2]**: Precise definition with context
- *(List all critical terms and concepts)*

# 🎓 Exam Notes & Critical Information
- **Must-Know Fact 1**: [Why it's important for exams]
- **Must-Know Fact 2**: [Why it's important for exams]
- **Must-Know Fact 3**: [Why it's important for exams]
- *(Focus on exam-critical, testable information)*

# 💭 Synthesis & Insights
(How the different parts connect, overarching themes, and broader implications)

**Quality Requirements:**
- Eliminate redundancy while preserving all unique information
- Use clear, professional academic language
- Organize information logically by theme, not by source order
- Ensure completeness - don't omit important details
- Make it exam-ready and study-friendly

**Content to Synthesize:**
{final_content}

Generate your comprehensive structured summary:"""
    if not groq_client:
        return "Global summary skipped (Groq client not initialized)."

    try:
        final_response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": final_prompt}]
        )
        return final_response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating final summary: {e}")
        return "Error generating final summary."


def _generate_mind_map(topics: List[str], doc_id: str) -> str:
    if not topics:
        return "@startmindmap\\n* Document\\n@endmindmap"
        
    unique_topics = list(set(topics))
    # Basic deduplication and grouping
    
    prompt = f"""You are a mind map architecture expert. Your task is to transform a list of topics into a clear, well-organized PlantUML mind map structure.

**CRITICAL REQUIREMENTS:**

1. **Output Format**: 
   - Return ONLY valid PlantUML syntax
   - Start with @startmindmap
   - End with @endmindmap
   - NO markdown code blocks
   - NO explanatory text

2. **Structure Guidelines**:
   - Use the document title or main theme as the central node
   - Organize topics into 3-5 major branches
   - Group related topics under common parent nodes
   - Create logical hierarchies (general → specific)
   - Keep depth to 3-4 levels maximum for readability

3. **Syntax Rules**:
   - Use * for root node
   - Use ** for right-side branches
   - Use *** for right-side sub-branches
   - Use left_ for left-side branches if needed
   - Keep node labels concise (2-5 words)

4. **Quality Standards**:
   - Eliminate duplicate topics
   - Merge similar or overlapping concepts
   - Prioritize the most important topics
   - Create meaningful groupings
   - Ensure visual balance

**Topics to Organize:**
{unique_topics}

**Example Structure:**
@startmindmap
* Central Theme
** Main Category 1
*** Subcategory 1.1
*** Subcategory 1.2
** Main Category 2
*** Subcategory 2.1
@endmindmap

Generate the PlantUML mind map now:"""
    if not groq_client:
        return "@startmindmap\n* Mindmap disabled (Groq skipped)\n@endmindmap"

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        result = response.choices[0].message.content.replace('```plantuml', '').replace('```', '').strip()
        if not result.startswith('@startmindmap'):
            result = "@startmindmap\\n" + result
        if not result.endswith('@endmindmap'):
            result = result + "\\n@endmindmap"
        return result
    except Exception as e:
        print(f"Error generating mind map: {e}")
        return "@startmindmap\\n* Error generating map\\n@endmindmap"
