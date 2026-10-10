import json

from kafka import KafkaConsumer, KafkaProducer

from app.workers.action_router import dispatch

REQUEST_TOPIC = "ai_requests"
RESPONSE_TOPIC = "ai_responses"
KAFKA_SERVER = "localhost:9092"


def start_worker():
    print(f"Connecting to Kafka at {KAFKA_SERVER}...")

    try:
        consumer = KafkaConsumer(
            REQUEST_TOPIC,
            bootstrap_servers=[KAFKA_SERVER],
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            group_id="ai-worker-group",
        )

        producer = KafkaProducer(
            bootstrap_servers=[KAFKA_SERVER],
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )

        print(f"Worker started! Listening on: {REQUEST_TOPIC}")
        print(f"Sending responses to: {RESPONSE_TOPIC}")

        for message in consumer:
            try:
                payload = message.value.decode("utf-8")
                data = json.loads(payload)

                print(
                    f"\n[REQUEST] ID: {data.get('request_id')} "
                    f"| Action: {data.get('action', 'CHAT')} "
                    f"| User: {data.get('user_id')}"
                )

                response_data = dispatch(data)

                producer.send(RESPONSE_TOPIC, response_data)
                producer.flush()
                print(f"[RESPONSE] Sent for ID: {data.get('request_id')}")

            except Exception as inner_e:
                print(f"Error processing message: {inner_e}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    start_worker()
