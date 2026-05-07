package com.example.backend.entity;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "policy_click_events", indexes = {
    @Index(name = "idx_pce_session",   columnList = "session_id"),
    @Index(name = "idx_pce_policy",    columnList = "policy_id"),
    @Index(name = "idx_pce_clicked",   columnList = "clicked_at"),
})
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class PolicyClickEvent {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "session_id", length = 64)
    private String sessionId;

    @Column(name = "chat_log_id")
    private Long chatLogId;

    @Column(name = "policy_id", length = 64)
    private String policyId;

    @Column(name = "policy_title", length = 500)
    private String policyTitle;

    @Column(name = "category", length = 16)
    private String category;

    @Column(name = "clicked_at")
    private LocalDateTime clickedAt;

    @Builder
    public PolicyClickEvent(String sessionId, Long chatLogId, String policyId,
                            String policyTitle, String category, LocalDateTime clickedAt) {
        this.sessionId   = sessionId;
        this.chatLogId   = chatLogId;
        this.policyId    = policyId;
        this.policyTitle = policyTitle;
        this.category    = category;
        this.clickedAt   = clickedAt != null ? clickedAt : LocalDateTime.now();
    }
}
