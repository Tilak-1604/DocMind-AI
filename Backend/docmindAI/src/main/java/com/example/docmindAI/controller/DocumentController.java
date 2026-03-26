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
}
