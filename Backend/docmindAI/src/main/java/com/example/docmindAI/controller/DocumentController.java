package com.example.docmindAI.controller;

import com.example.docmindAI.service.DocumentService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

@RestController
@RequestMapping("/api/documents")
public class DocumentController {

    @Autowired
    private DocumentService documentService;

    @PostMapping("/upload")
    public ResponseEntity<String> uploadDocument(
            @RequestParam("file") MultipartFile file,
            @RequestParam("user_id") String userId,
            @RequestParam("doc_id") String docId) {

        return documentService.uploadToAiService(file, userId, docId);
    }

    @PostMapping("/start-conversation")
    public ResponseEntity<String> startConversation(@RequestParam("user_id") String userId) {
        return documentService.startConversation(userId);
    }

    @PostMapping("/chat")
    public ResponseEntity<String> chat(
            @RequestParam("user_id") String userId,
            @RequestParam("conversation_id") String conversationId,
            @RequestParam("question") String question) {
        return documentService.chat(userId, conversationId, question);
    }

    @PostMapping("/{docId}/summarize")
    public ResponseEntity<String> summarize(
            @PathVariable("docId") String docId,
            @RequestParam("user_id") String userId) {
        return documentService.summarize(userId, docId);
    }

    @PostMapping("/{docId}/flashcards")
    public ResponseEntity<String> flashcards(
            @PathVariable("docId") String docId,
            @RequestParam("user_id") String userId) {
        return documentService.generateFlashcards(userId, docId);
    }

    @PostMapping("/{docId}/study")
    public ResponseEntity<String> study(
            @PathVariable("docId") String docId,
            @RequestParam("user_id") String userId) {
        return documentService.studyMode(userId, docId);
    }

    @PostMapping("/{docId}/mind-map")
    public ResponseEntity<String> mindMap(
            @PathVariable("docId") String docId,
            @RequestParam("user_id") String userId) {
        return documentService.generateMindMap(userId, docId);
    }
}
