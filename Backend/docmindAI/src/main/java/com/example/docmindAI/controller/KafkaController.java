package com.example.docmindAI.controller;

import com.example.docmindAI.model.AIRequest;
import com.example.docmindAI.service.KafkaProducerService;
import org.springframework.beans.factory.annotation.Autowired;
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

    @PostMapping("/send")
    public String sendMessage(
            @RequestParam("question") String question,
            @RequestParam("user_id") String userId,
            @RequestParam("conversation_id") String conversationId) {

        String requestId = UUID.randomUUID().toString();
        AIRequest request = new AIRequest(requestId, userId, conversationId, question);
        kafkaProducerService.sendMessage(request);
        return "JSON Message sent to Kafka topic. RequestID: " + requestId;
    }
}
