import json
from kafka import KafkaConsumer, KafkaProducer

# Configuration
REQUEST_TOPIC = 'ai_requests'
RESPONSE_TOPIC = 'ai_responses'
KAFKA_SERVER = 'localhost:9092'

from app.services.rag_engine import get_relevant_context
from app.services.document_tools_service import (
    summarize_document,
    generate_flashcards,
    extract_key_topic,
    study_mode,
    generate_mind_map
)

def start_worker():
    print(f"Connecting to Kafka at {KAFKA_SERVER}...")
    
    try:
        # Initialize Consumer
        consumer = KafkaConsumer(
            REQUEST_TOPIC,
            bootstrap_servers=[KAFKA_SERVER],
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='ai-worker-group'
        )

        # Initialize Producer
        producer = KafkaProducer(
            bootstrap_servers=[KAFKA_SERVER],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        
        print(f"Worker started! Listening on: {REQUEST_TOPIC}")
        print(f"Sending responses to: {RESPONSE_TOPIC}")

        for message in consumer:
            try:
                # 1. Decode & Parse JSON
                payload = message.value.decode('utf-8')
                data = json.loads(payload)
                
                request_id = data.get("request_id")
                action = data.get("action", "CHAT") # Default to CHAT if not provided
                user_id = data.get("user_id")
                conversation_id = data.get("conversation_id")
                doc_id = data.get("doc_id")
                question = data.get("question")

                print(f"\n[REQUEST] ID: {request_id} | Action: {action} | User: {user_id} | Doc: {doc_id}")
                
                answer = ""
                sources = []
                status = "SUCCESS"

                # 2. Route by Action
                try:
                    if action == "CHAT":
                        result = get_relevant_context(
                            question=question,
                            user_id=user_id,
                            conversation_id=conversation_id
                        )
                        answer = result.get("answer", "")
                        sources = result.get("sources", [])
                        
                    elif action == "SUMMARIZE":
                        answer = summarize_document(user_id, doc_id)
                        
                    elif action == "FLASHCARDS":
                        # Flashcards returns a list of dicts, so we'll JSON serialize it to a string for the 'answer' field
                        flashcards_data = generate_flashcards(user_id, doc_id)
                        answer = json.dumps(flashcards_data)
                        
                    elif action == "TOPICS":
                        # Returns a JSON string directly
                        json_result = extract_key_topic(user_id, doc_id)
                        # We return the raw string as answer
                        answer = json_result
                        
                    elif action == "STUDY_MODE":
                        answer = study_mode(user_id, doc_id)
                        
                    elif action == "MIND_MAP":
                        answer = generate_mind_map(user_id, doc_id)
                        
                    else:
                        status = "ERROR"
                        answer = f"Unknown action: {action}"
                except Exception as eval_e:
                    status = "ERROR"
                    answer = f"Error executing action {action}: {str(eval_e)}"
                    print(f"Error executing action {action}: {eval_e}")

                # 3. Prepare Structured Response
                response_data = {
                    "request_id": request_id,
                    "answer": answer,
                    "sources": sources,
                    "status": status
                }

                # 4. Send Response via Kafka
                producer.send(RESPONSE_TOPIC, response_data)
                producer.flush()
                print(f"[RESPONSE] Sent for ID: {request_id}")

            except Exception as inner_e:
                print(f"Error processing message: {inner_e}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    start_worker()
