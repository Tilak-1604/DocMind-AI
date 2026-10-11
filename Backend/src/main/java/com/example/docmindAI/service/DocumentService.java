package com.example.docmindAI.service;

import com.example.docmindAI.model.Document;
import com.example.docmindAI.repository.DocumentRepository;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.RestClient;
import org.springframework.web.client.RestClientResponseException;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.List;

@Service
@Slf4j
public class DocumentService {

    @Autowired
    private RestClient aiRestClient;

    @Autowired
    private DocumentRepository documentRepository;

    public Document saveDocument(String userId, String docId, String fileName) {
        Document doc = Document.builder()
                .userId(userId)
                .docId(docId)
                .name(fileName)
                .build();
        return documentRepository.save(doc);
    }

    public List<Document> listDocuments(String userId) {
        return documentRepository.findByUserIdOrderByUploadDateDesc(userId);
    }

    public ResponseEntity<String> uploadToAiService(MultipartFile file, String userId, String docId) {
        try {
            MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
            body.add("user_id", userId);
            body.add("doc_id", docId);

            // Convert MultipartFile to a Resource that RestClient can send
            ByteArrayResource resource = new ByteArrayResource(file.getBytes()) {
                @Override
                public String getFilename() {
                    return file.getOriginalFilename();
                }
            };
            body.add("file", resource);

            return aiRestClient.post()
                    .uri("/documents/upload")
                    .contentType(MediaType.MULTIPART_FORM_DATA)
                    .body(body)
                    .retrieve()
                    .toEntity(String.class);

        } catch (IOException e) {
            log.error("File processing error: {}", e.getMessage(), e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("File processing error: " + e.getMessage());
        } catch (RestClientResponseException e) {
            log.error("AI-Service HTTP error {}: {}", e.getStatusCode(), e.getResponseBodyAsString());
            return ResponseEntity.status(e.getStatusCode())
                    .body(e.getResponseBodyAsString());
        } catch (Exception e) {
            log.error("AI-Service connection error: {}", e.getMessage(), e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("AI-Service Connection Error: " + e.getMessage());
        }
    }

    public ResponseEntity<String> startConversation(String userId) {
        MultiValueMap<String, String> body = new LinkedMultiValueMap<>();
        body.add("user_id", userId);
        return callAiServiceForm("/conversation", body);
    }

    public ResponseEntity<String> chat(String userId, String conversationId, String question, List<String> documentIds) {
        MultiValueMap<String, String> body = new LinkedMultiValueMap<>();
        body.add("user_id", userId);
        body.add("conversation_id", conversationId);
        body.add("question", question);

        if (documentIds != null && !documentIds.isEmpty()) {
            body.add("document_ids", String.join(",", documentIds));
        }

        return callAiServiceForm("/chat", body);
    }

    public ResponseEntity<String> summarize(String userId, String docId) {
        MultiValueMap<String, String> body = new LinkedMultiValueMap<>();
        body.add("user_id", userId);
        return callAiServiceForm("/documents/" + docId + "/summarize", body);
    }

    public ResponseEntity<String> generateFlashcards(String userId, String docId) {
        MultiValueMap<String, String> body = new LinkedMultiValueMap<>();
        body.add("user_id", userId);
        return callAiServiceForm("/documents/" + docId + "/flashcards", body);
    }

    public ResponseEntity<String> studyMode(String userId, String docId) {
        MultiValueMap<String, String> body = new LinkedMultiValueMap<>();
        body.add("user_id", userId);
        return callAiServiceForm("/documents/" + docId + "/study", body);
    }

    public ResponseEntity<String> generateMindMap(String userId, String docId) {
        MultiValueMap<String, String> body = new LinkedMultiValueMap<>();
        body.add("user_id", userId);
        return callAiServiceForm("/documents/" + docId + "/mind-map", body);
    }

    public ResponseEntity<String> generateExam(String userId, String docId, Integer marks1, Integer marks2, Integer marks5, Integer marks10) {
        MultiValueMap<String, String> body = new LinkedMultiValueMap<>();
        body.add("user_id", userId);

        if (marks1 != null) {
            body.add("marks_1", String.valueOf(marks1));
        }
        if (marks2 != null) {
            body.add("marks_2", String.valueOf(marks2));
        }
        if (marks5 != null) {
            body.add("marks_5", String.valueOf(marks5));
        }
        if (marks10 != null) {
            body.add("marks_10", String.valueOf(marks10));
        }

        return callAiServiceForm("/documents/" + docId + "/exam", body);
    }

    private ResponseEntity<String> callAiServiceForm(String path, MultiValueMap<String, String> body) {
        try {
            return aiRestClient.post()
                    .uri(path)
                    .contentType(MediaType.APPLICATION_FORM_URLENCODED)
                    .body(body)
                    .retrieve()
                    .toEntity(String.class);
        } catch (RestClientResponseException e) {
            log.error("AI-Service HTTP error at {} [{}]: {}", path, e.getStatusCode(), e.getResponseBodyAsString());
            return ResponseEntity.status(e.getStatusCode())
                    .body(e.getResponseBodyAsString());
        } catch (Exception e) {
            log.error("AI-Service error at {}: {}", path, e.getMessage(), e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("Error calling AI Service at " + path + ": " + e.getMessage());
        }
    }
}

