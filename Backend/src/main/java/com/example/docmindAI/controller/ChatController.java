package com.example.docmindAI.controller;

import com.example.docmindAI.model.ChatMessage;
import com.example.docmindAI.model.ChatSession;
import com.example.docmindAI.model.User;
import com.example.docmindAI.repository.ChatMessageRepository;
import com.example.docmindAI.repository.ChatSessionRepository;
import lombok.Data;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

import com.example.docmindAI.model.Document;
import com.example.docmindAI.repository.DocumentRepository;

@RestController
@RequestMapping("/api/chats")
@RequiredArgsConstructor
@Slf4j
public class ChatController {

    private final ChatSessionRepository chatSessionRepository;
    private final ChatMessageRepository chatMessageRepository;
    private final DocumentRepository documentRepository;

    // List all chat sessions for the authenticated user
    @GetMapping
    public ResponseEntity<List<ChatSession>> listSessions(@AuthenticationPrincipal User user) {
        if (user == null) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
        }
        List<ChatSession> sessions = chatSessionRepository.findByUserIdOrderByUpdatedAtDesc(
                user.getId() != null ? user.getId().toString() : user.getEmail()
        );
        return ResponseEntity.ok(sessions);
    }

    // Get all messages for a specific chat session
    @GetMapping("/{sessionId}")
    public ResponseEntity<?> getSession(@PathVariable Long sessionId, @AuthenticationPrincipal User user) {
        if (user == null) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
        }

        var sessionOpt = chatSessionRepository.findById(sessionId);
        if (sessionOpt.isEmpty()) {
            return ResponseEntity.notFound().build();
        }

        ChatSession session = sessionOpt.get();
        List<ChatMessage> messages = chatMessageRepository.findByChatSessionIdOrderByCreatedAtAsc(sessionId);

        return ResponseEntity.ok(Map.of(
                "session", session,
                "messages", messages
        ));
    }

    // Create a new chat session
    @PostMapping
    public ResponseEntity<ChatSession> createSession(@RequestBody CreateSessionRequest request,
                                                      @AuthenticationPrincipal User user) {
        if (user == null) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
        }

        String userId = user.getId() != null ? user.getId().toString() : user.getEmail();

        List<Document> docs = documentRepository.findAllById(request.getDocumentIds());

        ChatSession session = ChatSession.builder()
                .userId(userId)
                .title(request.getTitle() != null ? request.getTitle() : "New Chat")
                .documents(docs)
                .conversationId(request.getConversationId())
                .build();

        chatSessionRepository.save(session);
        log.info("Chat session created: {} for user {}", session.getId(), userId);
        return ResponseEntity.status(HttpStatus.CREATED).body(session);
    }

    // Save a message to a chat session
    @PostMapping("/{sessionId}/messages")
    public ResponseEntity<ChatMessage> saveMessage(@PathVariable Long sessionId,
                                                    @RequestBody SaveMessageRequest request,
                                                    @AuthenticationPrincipal User user) {
        if (user == null) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
        }

        var sessionOpt = chatSessionRepository.findById(sessionId);
        if (sessionOpt.isEmpty()) {
            return ResponseEntity.notFound().build();
        }

        ChatSession session = sessionOpt.get();

        // Auto-generate title from first user message
        if ("New Chat".equals(session.getTitle()) && "user".equals(request.getRole())) {
            String title = request.getContent();
            if (title.length() > 60) {
                title = title.substring(0, 57) + "...";
            }
            session.setTitle(title);
        }

        // Update the session's updatedAt timestamp
        chatSessionRepository.save(session);

        ChatMessage message = ChatMessage.builder()
                .chatSessionId(sessionId)
                .role(request.getRole())
                .content(request.getContent())
                .build();

        chatMessageRepository.save(message);
        return ResponseEntity.status(HttpStatus.CREATED).body(message);
    }

    // Delete a chat session and all its messages
    @DeleteMapping("/{sessionId}")
    @Transactional
    public ResponseEntity<?> deleteSession(@PathVariable Long sessionId, @AuthenticationPrincipal User user) {
        if (user == null) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
        }

        var sessionOpt = chatSessionRepository.findById(sessionId);
        if (sessionOpt.isEmpty()) {
            return ResponseEntity.notFound().build();
        }

        chatMessageRepository.deleteByChatSessionId(sessionId);
        chatSessionRepository.deleteById(sessionId);
        log.info("Chat session {} deleted", sessionId);
        return ResponseEntity.ok(Map.of("message", "Session deleted"));
    }

    // Update documents mapped to a chat session
    @PutMapping("/{sessionId}/documents")
    public ResponseEntity<?> updateSessionDocuments(@PathVariable Long sessionId,
                                                    @RequestBody UpdateSessionDocumentsRequest request,
                                                    @AuthenticationPrincipal User user) {
        if (user == null) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
        }
        
        String userId = user.getId() != null ? user.getId().toString() : user.getEmail();

        if (request.getDocumentIds() == null || request.getDocumentIds().isEmpty()) {
            return ResponseEntity.badRequest().body(Map.of("error", "Document list cannot be empty"));
        }

        var sessionOpt = chatSessionRepository.findById(sessionId);
        if (sessionOpt.isEmpty()) {
            return ResponseEntity.notFound().build();
        }
        
        ChatSession session = sessionOpt.get();
        if (!session.getUserId().equals(userId)) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN).body(Map.of("error", "Unauthorized access to session"));
        }

        List<Document> docs = documentRepository.findAllById(request.getDocumentIds());
        if (docs.size() != request.getDocumentIds().size()) {
            return ResponseEntity.badRequest().body(Map.of("error", "Some documents were not found"));
        }
        
        for (Document doc : docs) {
            if (!doc.getUserId().equals(userId)) {
                return ResponseEntity.status(HttpStatus.FORBIDDEN).body(Map.of("error", "Unauthorized access to document: " + doc.getName()));
            }
        }

        session.setDocuments(docs);
        chatSessionRepository.save(session);
        log.info("Chat session {} documents updated by user {}", sessionId, userId);
        
        return ResponseEntity.ok(Map.of(
            "message", "Context updated",
            "documents", docs
        ));
    }
}

@Data
class CreateSessionRequest {
    private String title;
    private List<Long> documentIds;
    private String conversationId;
}

@Data
class SaveMessageRequest {
    private String role;
    private String content;
}

@Data
class UpdateSessionDocumentsRequest {
    private List<Long> documentIds;
}
