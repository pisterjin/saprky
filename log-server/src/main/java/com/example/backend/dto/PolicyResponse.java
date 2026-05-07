package com.example.backend.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class PolicyResponse {
    // 1. 카테고리 태그 (예: 취업, 주거, 금융) [cite: 140, 151, 162]
    private String category;

    // 2. D-day 배지 (예: D-12, 상시) [cite: 141, 163]
    private String dDay;

    // 3. 정책명 [cite: 142, 153, 164]
    private String title;

    // 4. 한 줄 요약 설명 [cite: 143, 154, 165]
    private String summary;

    // 5. 신청 기간 (예: ~2025.06.30, 상시 신청) [cite: 144, 145, 166, 167]
    private String applicationPeriod;

    // 6. 지원 대상 (예: 만 15~34세 미취업 청년) [cite: 146, 147, 168, 169]
    private String target;

    // 7. 지원 금액 (예: 최대 480만원) [cite: 148, 149, 170, 171]
    private String amount;

    // 8. 공식 사이트 바로가기 URL [cite: 150, 161, 172]
    private String linkUrl;
}