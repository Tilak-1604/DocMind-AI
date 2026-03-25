import json
from kafka import KafkaConsumer, KafkaProducer

# Configuration
REQUEST_TOPIC = 'ai_requests'
RESPONSE_TOPIC = 'ai_responses'
KAFKA_SERVER = 'localhost:9092'

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
            payload = message.value.decode('utf-8')
            print(f"Received Request: {payload}")

            # Prepare Response
            response_data = {
                "request": payload,
                "response": f"AI Processed: {payload}",
                "status": "SUCCESS"
            }

            # Send Response
            producer.send(RESPONSE_TOPIC, response_data)
            producer.flush()
            print(f"Sent Response: {response_data}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    start_worker()
