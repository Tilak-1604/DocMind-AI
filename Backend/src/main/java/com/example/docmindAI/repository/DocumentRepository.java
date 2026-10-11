package com.example.docmindAI.repository;

import com.example.docmindAI.model.Document;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface DocumentRepository extends JpaRepository<Document, Long> {
    List<Document> findByUserIdOrderByUploadDateDesc(String userId);
    Optional<Document> findByDocId(String docId);
}
