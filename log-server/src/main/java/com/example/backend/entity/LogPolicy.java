package com.example.backend.entity;

import jakarta.persistence.*;
import lombok.*;

@Entity
@Table(name = "log_policies", indexes = {
    @Index(name = "idx_log_policies_chat",     columnList = "chat_log_id"),
    @Index(name = "idx_log_policies_policy",   columnList = "policy_id"),
    @Index(name = "idx_log_policies_category", columnList = "category"),
})
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class LogPolicy {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "chat_log_id", nullable = false,
                foreignKey = @ForeignKey(name = "fk_log_policies_chat_log",
                                         value = ConstraintMode.CONSTRAINT))
    private ChatLog chatLog;

    @Column(name = "policy_id", nullable = false, length = 64)
    private String policyId;

    @Column(name = "policy_title", length = 500)
    private String policyTitle;

    @Column(name = "category", length = 16)
    private String category;

    @Column(name = "source", length = 16)
    private String source;

    @Column(name = "rank_pos")
    private Integer rankPos;

    @Builder
    public LogPolicy(ChatLog chatLog, String policyId, String policyTitle,
                     String category, String source, Integer rankPos) {
        this.chatLog     = chatLog;
        this.policyId    = policyId;
        this.policyTitle = policyTitle;
        this.category    = category;
        this.source      = source;
        this.rankPos     = rankPos;
    }
}
