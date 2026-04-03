package com.example.docmindAI.controller;

import com.example.docmindAI.service.DocumentService;
import com.example.docmindAI.model.User;
import com.example.docmindAI.model.Document;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import java.util.List;

@RestController
@RequestMapping("/api/documents")
public class DocumentController {

    @Autowired
    private DocumentService documentService;

    @GetMapping
    public ResponseEntity<List<Document>> listDocuments(@AuthenticationPrincipal User user) {
        if (user == null) return ResponseEntity.status(401).build();
        String userId = user.getId() != null ? user.getId().toString() : user.getEmail();
        return ResponseEntity.ok(documentService.listDocuments(userId));
    }

    @PostMapping("/upload")
    public ResponseEntity<?> uploadDocument(
            @RequestParam("file") MultipartFile file,
            @RequestParam("user_id") String userId,
            @RequestParam("doc_id") String docId) {

        ResponseEntity<String> aiResponse = documentService.uploadToAiService(file, userId, docId);
        
        if (aiResponse.getStatusCode().is2xxSuccessful()) {
            Document doc = documentService.saveDocument(userId, docId, file.getOriginalFilename());
            return ResponseEntity.ok(doc);
        }
        
        return aiResponse;
    }

    @PostMapping("/start-conversation")
    public ResponseEntity<String> startConversation(@AuthenticationPrincipal User user) {
        if (user == null) return ResponseEntity.status(401).build();
        String userId = user.getId() != null ? user.getId().toString() : user.getEmail();
        return documentService.startConversation(userId);
    }

    @PostMapping("/chat")
    public ResponseEntity<String> chat(
            @AuthenticationPrincipal User user,
            @RequestParam("conversation_id") String conversationId,
            @RequestParam("question") String question,
            @RequestParam(value = "document_ids", required = false) List<String> documentIds) {
        if (user == null) return ResponseEntity.status(401).build();
        String userId = user.getId() != null ? user.getId().toString() : user.getEmail();
        return documentService.chat(userId, conversationId, question, documentIds);
    }

    @PostMapping("/{docId}/summarize")
    public ResponseEntity<String> summarize(
            @PathVariable("docId") String docId,
            @AuthenticationPrincipal User user) {
        if (user == null) return ResponseEntity.status(401).build();
        String userId = user.getId() != null ? user.getId().toString() : user.getEmail();
        return documentService.summarize(userId, docId);
    }

    @PostMapping("/{docId}/flashcards")
    public ResponseEntity<String> flashcards(
            @PathVariable("docId") String docId,
            @AuthenticationPrincipal User user) {
        if (user == null) return ResponseEntity.status(401).build();
        String userId = user.getId() != null ? user.getId().toString() : user.getEmail();
        return documentService.generateFlashcards(userId, docId);
    }

    @PostMapping("/{docId}/study")
    public ResponseEntity<String> study(
            @PathVariable("docId") String docId,
            @AuthenticationPrincipal User user) {
        if (user == null) return ResponseEntity.status(401).build();
        String userId = user.getId() != null ? user.getId().toString() : user.getEmail();
        return documentService.studyMode(userId, docId);
    }

    @PostMapping("/{docId}/mind-map")
    public ResponseEntity<String> mindMap(
            @PathVariable("docId") String docId,
            @AuthenticationPrincipal User user) {
        if (user == null) return ResponseEntity.status(401).build();
        String userId = user.getId() != null ? user.getId().toString() : user.getEmail();
        return documentService.generateMindMap(userId, docId);
    }

    @PostMapping("/{docId}/exam")
    public ResponseEntity<String> exam(
            @PathVariable("docId") String docId,
            @AuthenticationPrincipal User user,
            @RequestParam(value = "marks_1", required = false) Integer marks1,
            @RequestParam(value = "marks_2", required = false) Integer marks2,
            @RequestParam(value = "marks_5", required = false) Integer marks5,
            @RequestParam(value = "marks_10", required = false) Integer marks10) {
        if (user == null) return ResponseEntity.status(401).build();
        String userId = user.getId() != null ? user.getId().toString() : user.getEmail();
        return documentService.generateExam(userId, docId, marks1, marks2, marks5, marks10);
    }
}
