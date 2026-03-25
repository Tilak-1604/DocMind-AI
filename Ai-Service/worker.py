from kafka import KafkaConsumer

# Configuration
TOPIC_NAME = 'ai_requests'
KAFKA_SERVER = 'localhost:9092'

def start_worker():
    print(f"Connecting to Kafka at {KAFKA_SERVER}...")
    
    try:
        consumer = KafkaConsumer(
            TOPIC_NAME,
            bootstrap_servers=[KAFKA_SERVER],
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='ai-worker-group'
        )
        
        print(f"Worker started! Listening for messages on topic: {TOPIC_NAME}")
        print("Press Ctrl+C to stop.")

        for message in consumer:
            # Decode the message value from bytes to string
            payload = message.value.decode('utf-8')
            print(f"Received: {payload}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    start_worker()
