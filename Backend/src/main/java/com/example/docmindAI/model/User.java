package com.example.docmindAI.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Entity
@Table(name = "users")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(unique = true, nullable = false)
    private String email;

    @com.fasterxml.jackson.annotation.JsonIgnore
    private String password;

    private String name;

    private String picture;

    @Column(unique = true)
    private String providerId; // Google "sub"

    private String provider; // "GOOGLE" or "LOCAL"

    private String role; // e.g., USER, ADMIN

    private java.time.LocalDateTime createdAt;

    @PrePersist
    protected void onCreate() {
        this.createdAt = java.time.LocalDateTime.now();
        if (this.role == null) {
            this.role = "USER"; // Default role
        }
        if (this.provider == null) {
            this.provider = "LOCAL"; // Default provider for manual registration
        }
    }
}
