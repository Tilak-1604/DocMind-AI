package com.example.docmindAI.service;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;

@Service
public class DocumentService {

    @Autowired
    private RestTemplate restTemplate;

    private static final String AI_SERVICE_URL = "http://localhost:8000/upload";

    public ResponseEntity<String> uploadToAiService(MultipartFile file, String userId, String docId) {
        try {
            // Prepare headers
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.MULTIPART_FORM_DATA);

            // Prepare body
            MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
            body.add("user_id", userId);
            body.add("doc_id", docId);

            // Convert MultipartFile to a Resource that RestTemplate can send
            ByteArrayResource resource = new ByteArrayResource(file.getBytes()) {
                @Override
                public String getFilename() {
                    return file.getOriginalFilename();
                }
            };
            body.add("file", resource);

            HttpEntity<MultiValueMap<String, Object>> requestEntity = new HttpEntity<>(body, headers);

            // POST to Python AI-Service
            return restTemplate.postForEntity(AI_SERVICE_URL, requestEntity, String.class);

        } catch (IOException e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("File processing error: " + e.getMessage());
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("AI-Service Connection Error: " + e.getMessage());
        }
    }

    public ResponseEntity<String> startConversation(String userId) {
        MultiValueMap<String, String> body = new LinkedMultiValueMap<>();
        body.add("user_id", userId);
        return callAiService("http://localhost:8000/conversation", body);
    }

    public ResponseEntity<String> chat(String userId, String conversationId, String question) {
        MultiValueMap<String, String> body = new LinkedMultiValueMap<>();
        body.add("user_id", userId);
        body.add("conversation_id", conversationId);
        body.add("question", question);
        return callAiService("http://localhost:8000/chat", body);
    }

    public ResponseEntity<String> summarize(String userId, String docId) {
        MultiValueMap<String, String> body = new LinkedMultiValueMap<>();
        body.add("user_id", userId);
        return callAiService("http://localhost:8000/documents/" + docId + "/summarize", body);
    }

    public ResponseEntity<String> generateFlashcards(String userId, String docId) {
        MultiValueMap<String, String> body = new LinkedMultiValueMap<>();
        body.add("user_id", userId);
        return callAiService("http://localhost:8000/documents/" + docId + "/flashcards", body);
    }

    public ResponseEntity<String> studyMode(String userId, String docId) {
        MultiValueMap<String, String> body = new LinkedMultiValueMap<>();
        body.add("user_id", userId);
        return callAiService("http://localhost:8000/documents/" + docId + "/study", body);
    }

    public ResponseEntity<String> generateMindMap(String userId, String docId) {
        MultiValueMap<String, String> body = new LinkedMultiValueMap<>();
        body.add("user_id", userId);
        return callAiService("http://localhost:8000/documents/" + docId + "/mind-map", body);
    }

    private ResponseEntity<String> callAiService(String url, MultiValueMap<String, String> body) {
        try {
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.MULTIPART_FORM_DATA);
            HttpEntity<MultiValueMap<String, String>> requestEntity = new HttpEntity<>(body, headers);
            return restTemplate.postForEntity(url, requestEntity, String.class);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("Error calling AI Service at " + url + ": " + e.getMessage());
        }
    }
}
