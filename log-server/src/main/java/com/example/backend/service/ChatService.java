package com.example.backend.service;

import com.example.backend.dto.ChatRequest;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class ChatService {

    private final LogService logService;

    public String processMessage(ChatRequest request) {
        String userMsg = request.getMessage();
        String userId = request.getUserId();
        String sessionId = request.getSessionId();

        logService.info("CHAT-SERVICE", "사용자 질문 수신: " + userMsg);

        // 실제 챗봇 답변 로직 (예시)
        String botAnswer = "답변: " + userMsg + "에 대한 정보입니다.";

        // 답변 기록도 남기기
        logService.info("CHAT-SERVICE", "챗봇 답변 발송");

        return botAnswer;
    }
}