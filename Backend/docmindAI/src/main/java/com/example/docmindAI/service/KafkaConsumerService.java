package com.example.docmindAI.service;

import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Service;

@Service
public class KafkaConsumerService {

    @KafkaListener(topics = "ai_responses", groupId = "spring-boot-group")
    public void consume(String message) {
        System.out.println("Received Response from Python: " + message);
    }
}
