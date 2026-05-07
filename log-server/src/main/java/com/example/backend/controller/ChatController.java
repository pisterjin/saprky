package com.example.backend.controller;

import com.example.backend.dto.ChatRequest;
import com.example.backend.service.ChatService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/chat")
@RequiredArgsConstructor

public class ChatController {

    private final ChatService chatService;

    @PostMapping("/send")
    public String sendMessage(@RequestBody ChatRequest request) {
        // ChatService의 processMessage 메서드를 호출하여 답변 반환
        return chatService.processMessage(request);
    }

}

