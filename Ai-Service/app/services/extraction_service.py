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

# Initialize Groq client
groq_client = Groq(api_key=settings.GROQ_API_KEY)

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
                prompt = f"""Extract structured information from the following text.
You must output ONLY valid JSON that matches the following schema:
{{
  "chunk_summary": "A brief 2-3 sentence summary of the chunk.",
  "key_concepts": [
    {{"term": "concept name", "definition": "concept definition"}}
  ],
  "hierarchical_topics": ["broad topic", "sub-topic", "specific topic"],
  "important_facts": ["fact 1", "fact 2"]
}}

Text:
{chunk_text}
"""
                
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
    
    final_prompt = f"""Create a final structured summary with the following sections:

1. Executive Summary
2. Key Points
3. Important Definitions
4. Exam Notes

Content:
{final_content}
"""
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
    
    prompt = f"""Generate a valid PlantUML mind map structure from the following topics.
Return ONLY the PlantUML syntax, starting with @startmindmap and ending with @endmindmap.
Do not use markdown formatting. 

Topics:
{unique_topics}
"""
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
