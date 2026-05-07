package com.example.backend.entity;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;

// 1. LogEntity (로그 설계 보완 반영)
@Entity
@Getter
@NoArgsConstructor
public class LogEntity {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String userId;
    private String sessionId;

    @Column(columnDefinition = "TEXT")
    private String request;

    @Column(columnDefinition = "TEXT")
    private String response;

    private Long latencyMs;
    private LocalDateTime createdAt;
    private String logType; // CHAT, ERROR, POLICY 등

    @Builder
    public LogEntity(String userId, String sessionId, String request, String response, Long latencyMs, String logType) {
        this.userId = userId;
        this.sessionId = sessionId;
        this.request = request;
        this.response = response;
        this.latencyMs = latencyMs;
        this.logType = logType;
        this.createdAt = LocalDateTime.now();
    }


}

