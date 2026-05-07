package com.example.backend.entity;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDate;
import java.time.LocalDateTime;

@Entity
@Table(name = "policies")
@Getter @Setter
@NoArgsConstructor @AllArgsConstructor @Builder
public class PolicyEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long policyId;

    @Column(nullable = false)
    private String category; // 취업, 주거, 금융 등

    @Column(nullable = false)
    private String title; // 정책명 (예: 청년도약계좌)

    @Column(columnDefinition = "TEXT")
    private String description; // 정책 요약 설명

    private String target; // 지원 대상

    private String amount; // 지원 금액

    private String deadline; // 신청 기간 텍스트 (예: ~2025.06.30)

    private LocalDate dDayDate; // D-day 계산을 위한 실제 날짜 데이터

    private String linkUrl; // 공식 사이트 바로가기
}