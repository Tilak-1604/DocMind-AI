package com.example.docmindAI.service;

import com.example.docmindAI.model.AIResponse;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Service;

@Service
public class KafkaConsumerService {

    @Autowired
    private ObjectMapper objectMapper;

    @Autowired
    private ResponseCacheService responseCacheService;

    @KafkaListener(topics = "ai_responses", groupId = "spring-boot-group")
    public void consume(String message) {
        try {
            AIResponse response = objectMapper.readValue(message, AIResponse.class);
            
            // Store the response for the frontend to poll
            responseCacheService.storeResponse(response.getRequest_id(), response);

            System.out.println("\n--- RECEIVED AI RESPONSE ---");
            System.out.println("Request ID: " + response.getRequest_id());
            System.out.println("Answer: " + response.getAnswer());
            System.out.println("Sources: " + response.getSources());
            System.out.println("---------------------------\n");
        } catch (Exception e) {
            System.err.println("Error parsing AI Response: " + e.getMessage());
            System.out.println("Raw message: " + message);
        }
    }
}
