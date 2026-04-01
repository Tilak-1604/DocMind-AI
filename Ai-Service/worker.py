import json
import threading
from concurrent.futures import ThreadPoolExecutor
from kafka import KafkaConsumer, KafkaProducer

# Configuration
REQUEST_TOPIC = 'ai_requests'
RESPONSE_TOPIC = 'ai_responses'
KAFKA_SERVER = 'localhost:9092'
WORKER_THREADS = 4  # Concurrent AI request handlers

from app.services.rag_engine import get_relevant_context
from app.services.document_tools_service import (
    summarize_document,
    generate_flashcards,
    extract_key_topic,
    study_mode,
    generate_mind_map
)

def _process_message(data: dict, producer: KafkaProducer, producer_lock: threading.Lock):
    """Handle a single decoded AI request and send the response."""
    request_id = data.get("request_id")
    action = data.get("action", "CHAT")
    user_id = data.get("user_id")
    conversation_id = data.get("conversation_id")
    doc_id = data.get("doc_id")
    question = data.get("question")

    print(f"\n[REQUEST] ID: {request_id} | Action: {action} | User: {user_id} | Doc: {doc_id}")

    answer = ""
    sources = []
    status = "SUCCESS"

    # Route by Action
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
            flashcards_data = generate_flashcards(user_id, doc_id)
            answer = json.dumps(flashcards_data)

        elif action == "TOPICS":
            json_result = extract_key_topic(user_id, doc_id)
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

    # Send Structured Response via Kafka (serialized to avoid concurrent flush races)
    response_data = {
        "request_id": request_id,
        "answer": answer,
        "sources": sources,
        "status": status
    }
    with producer_lock:
        producer.send(RESPONSE_TOPIC, response_data)
        producer.flush()
    print(f"[RESPONSE] Sent for ID: {request_id}")


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
        print(f"Processing messages with {WORKER_THREADS} concurrent threads.")

        producer_lock = threading.Lock()
        with ThreadPoolExecutor(max_workers=WORKER_THREADS) as executor:
            for message in consumer:
                try:
                    # Decode & Parse JSON
                    payload = message.value.decode('utf-8')
                    data = json.loads(payload)
                    # Dispatch to thread pool — non-blocking
                    executor.submit(_process_message, data, producer, producer_lock)
                except Exception as inner_e:
                    print(f"Error dispatching message: {inner_e}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    start_worker()
