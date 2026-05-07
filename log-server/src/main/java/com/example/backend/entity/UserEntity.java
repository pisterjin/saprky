package com.example.backend.entity;

import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.GenericGenerator;
import java.time.LocalDateTime;
import java.util.UUID;

@Entity
@Table(name = "users")
@Getter @Setter
@NoArgsConstructor @AllArgsConstructor @Builder
public class UserEntity {

    @Id
    @GeneratedValue(generator = "UUID")
    @GenericGenerator(name = "UUID", strategy = "org.hibernate.id.UUIDGenerator")
    @Column(name = "user_id", updatable = false, nullable = false)
    private UUID userId; // 설계서 OB-006: UUID 생성 반영

    @Column(nullable = false)
    private String ageRange; // 연령대 (15~18세 등)

    @Column(nullable = false)
    private String gender; // 성별 (남성, 여성 등)

    @Column(nullable = false)
    private String region; // 거주지역 (서울, 경기 등)

    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;

    @PrePersist
    public void prePersist() {
        this.createdAt = LocalDateTime.now();
        this.updatedAt = LocalDateTime.now();
    }

    @PreUpdate
    public void preUpdate() {
        this.updatedAt = LocalDateTime.now();
    }
}