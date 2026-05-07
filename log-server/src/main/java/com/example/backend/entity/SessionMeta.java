package com.example.backend.entity;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "session_meta")
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class SessionMeta {

    @Id
    @Column(name = "session_id", length = 64)
    private String sessionId;

    @Column(name = "started_at", nullable = false)
    private LocalDateTime startedAt;

    @Column(name = "last_activity_at", nullable = false)
    private LocalDateTime lastActivityAt;

    @Column(name = "ended_at")
    private LocalDateTime endedAt;

    @Column(name = "total_turns")
    private Integer totalTurns = 0;

    @Column(name = "onboarding_completed")
    private Boolean onboardingCompleted = false;

    @Column(name = "profile_edited_count")
    private Integer profileEditedCount = 0;

    @Column(name = "first_domain", length = 16)
    private String firstDomain;

    @Column(name = "age_group", length = 16)
    private String ageGroup;

    @Column(name = "gender", length = 8)
    private String gender;

    @Column(name = "region", length = 16)
    private String region;

    @Builder
    public SessionMeta(String sessionId, LocalDateTime startedAt, String ageGroup,
                       String gender, String region) {
        this.sessionId   = sessionId;
        this.startedAt   = startedAt;
        this.lastActivityAt = startedAt;
        this.ageGroup    = ageGroup;
        this.gender      = gender;
        this.region      = region;
    }

    public void onTurn(String domain, LocalDateTime now) {
        this.totalTurns     = (this.totalTurns == null ? 0 : this.totalTurns) + 1;
        this.lastActivityAt = now;
        if (this.firstDomain == null && domain != null) this.firstDomain = domain;
        if (this.totalTurns >= 1) this.onboardingCompleted = true;
    }
}
