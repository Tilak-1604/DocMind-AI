package com.example.docmindAI.controller;

import com.example.docmindAI.model.AIRequest;
import com.example.docmindAI.model.AIResponse;
import com.example.docmindAI.service.KafkaProducerService;
import com.example.docmindAI.service.ResponseCacheService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.UUID;

@RestController
@RequestMapping("/api/kafka")
public class KafkaController {

    @Autowired
    private KafkaProducerService kafkaProducerService;

    @Autowired
    private ResponseCacheService responseCacheService;

    @PostMapping("/send")
    public ResponseEntity<?> sendMessage(
            @RequestParam("action") String action,
            @RequestParam(value = "doc_id", required = false) String docId,
            @RequestParam(value = "question", required = false) String question,
            @RequestParam("user_id") String userId,
            @RequestParam("conversation_id") String conversationId) {

        String requestId = UUID.randomUUID().toString();
        AIRequest request = new AIRequest(requestId, action, userId, conversationId, docId, question);
        kafkaProducerService.sendMessage(request);
        
        return ResponseEntity.ok()
            .body("{\"request_id\": \"" + requestId + "\", \"message\": \"Message sent to Kafka topic.\"}");
    }

    @GetMapping("/response/{requestId}")
    public ResponseEntity<?> getResponse(@PathVariable String requestId) {
        AIResponse response = responseCacheService.getResponse(requestId);
        if (response != null) {
            return ResponseEntity.ok(response);
        } else {
            // Return 202 Accepted if processing is not yet complete
            return ResponseEntity.status(202).body("{\"status\": \"PROCESSING\"}");
        }
    }
}
