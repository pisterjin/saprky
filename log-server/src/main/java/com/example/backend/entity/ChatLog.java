package com.example.backend.entity;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;
import java.time.ZoneOffset;

@Entity
@Table(name = "chat_logs", indexes = {
    @Index(name = "idx_chat_logs_session",    columnList = "session_id"),
    @Index(name = "idx_chat_logs_created",    columnList = "created_at"),
    @Index(name = "idx_chat_logs_domain",     columnList = "domain"),
    @Index(name = "idx_chat_logs_intent",     columnList = "intent_hash"),
})
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class ChatLog {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "session_id", nullable = false, length = 64)
    private String sessionId;

    @Column(name = "turn_no", nullable = false)
    private Integer turnNo;

    @Column(name = "age_group", length = 16)
    private String ageGroup;

    @Column(name = "gender", length = 8)
    private String gender;

    @Column(name = "region", length = 16)
    private String region;

    @Column(name = "question", columnDefinition = "TEXT", nullable = false)
    private String question;

    @Column(name = "answer", columnDefinition = "TEXT", nullable = false)
    private String answer;

    @Column(name = "domain", length = 16)
    private String domain;

    @Column(name = "is_clarifying")
    private Boolean isClarifying = false;

    @Column(name = "intent_hash", length = 64)
    private String intentHash;

    @Column(name = "retry_count")
    private Integer retryCount = 0;

    @Column(name = "retry_reason", length = 16)
    private String retryReason;

    @Column(name = "masking_hit")
    private Boolean maskingHit = false;

    @Column(name = "masking_sources", length = 32)
    private String maskingSources;

    @Column(name = "response_time_ms")
    private Integer responseTimeMs;

    @Column(name = "client_timestamp")
    private LocalDateTime clientTimestamp;

    @Column(name = "created_at", nullable = false)
    private LocalDateTime createdAt;

    @Builder
    public ChatLog(String sessionId, Integer turnNo, String ageGroup, String gender, String region,
                   String question, String answer, String domain, Boolean isClarifying,
                   String intentHash, Integer retryCount, String retryReason,
                   Boolean maskingHit, String maskingSources, Integer responseTimeMs,
                   LocalDateTime clientTimestamp) {
        this.sessionId       = sessionId;
        this.turnNo          = turnNo;
        this.ageGroup        = ageGroup;
        this.gender          = gender;
        this.region          = region;
        this.question        = question;
        this.answer          = answer;
        this.domain          = domain;
        this.isClarifying    = isClarifying != null ? isClarifying : false;
        this.intentHash      = intentHash;
        this.retryCount      = retryCount != null ? retryCount : 0;
        this.retryReason     = retryReason;
        this.maskingHit      = maskingHit != null ? maskingHit : false;
        this.maskingSources  = maskingSources;
        this.responseTimeMs  = responseTimeMs;
        this.clientTimestamp = clientTimestamp;
        this.createdAt       = LocalDateTime.now(ZoneOffset.UTC);
    }
}
