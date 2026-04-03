package com.example.docmindAI.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Entity
@Table(name = "documents")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Document {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String userId;

    @Column(nullable = false)
    private String name;

    @Column(nullable = false, name = "doc_id", unique = true)
    private String docId; // The unique ID assigned by AI-Service (e.g., timestamp)

    @Column(name = "chunk_count")
    private Integer chunkCount;

    @Column(name = "extraction_status")
    @Builder.Default
    private String extractionStatus = "PENDING";

    @Column(name = "global_summary", columnDefinition = "TEXT")
    private String globalSummary;

    @Column(name = "mind_map_plantuml", columnDefinition = "TEXT")
    private String mindMapPlantuml;

    @Column(name = "upload_date")
    private LocalDateTime uploadDate;

    @PrePersist
    protected void onCreate() {
        this.uploadDate = LocalDateTime.now();
    }
}
