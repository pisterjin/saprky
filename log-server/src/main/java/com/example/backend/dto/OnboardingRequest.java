package com.example.backend.dto;

import lombok.Getter;

@Getter
public class OnboardingRequest {
    private String ageGroup;  // "15~18세", "19~24세", "25~29세", "30~34세"
    private String gender;    // "남성", "여성", "선택 안 함"
    private String region;    // "서울", "경기", "부산", "인천", "기타"
}