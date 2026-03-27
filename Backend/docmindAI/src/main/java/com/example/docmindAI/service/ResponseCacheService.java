package com.example.docmindAI.service;

import com.example.docmindAI.model.AIResponse;
import org.springframework.stereotype.Service;

import java.util.concurrent.ConcurrentHashMap;

@Service
public class ResponseCacheService {

    // Thread-safe map to store incoming responses by request_id
    private final ConcurrentHashMap<String, AIResponse> responseMap = new ConcurrentHashMap<>();

    public void storeResponse(String requestId, AIResponse response) {
        responseMap.put(requestId, response);
    }

    public AIResponse getResponse(String requestId) {
        // Changed from .remove() to .get() for easier manual testing
        return responseMap.get(requestId);
    }
}
