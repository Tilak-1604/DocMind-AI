import json
from kafka import KafkaConsumer, KafkaProducer

# Configuration
REQUEST_TOPIC = 'ai_requests'
RESPONSE_TOPIC = 'ai_responses'
KAFKA_SERVER = 'localhost:9092'

from app.services.rag_engine import get_relevant_context

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
                user_id = data.get("user_id")
                conversation_id = data.get("conversation_id")
                question = data.get("question")

                print(f"\n[REQUEST] ID: {request_id} | User: {user_id} | Question: {question}")

                # 2. Call RAG Engine
                result = get_relevant_context(
                    question=question,
                    user_id=user_id,
                    conversation_id=conversation_id
                )

                # 3. Prepare Structured Response
                response_data = {
                    "request_id": request_id,
                    "answer": result["answer"],
                    "sources": result["sources"],
                    "status": "SUCCESS"
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
