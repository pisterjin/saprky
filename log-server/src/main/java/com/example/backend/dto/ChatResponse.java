package com.example.backend.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ChatResponse {
    private String userQuery;       // 사용자가 던진 질문
    private String botAnswer;      // 봇이 생성한 답변 내용
    private List<String> policies; // 추천된 정책 ID 또는 이름들
    private long responseTimeMs;   // 응답에 걸린 시간 (밀리초)
    private String status;         // SUCCESS, FAIL 등
}

