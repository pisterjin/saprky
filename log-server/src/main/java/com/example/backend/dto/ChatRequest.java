package com.example.backend.dto;

import lombok.Getter;
import lombok.Setter;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class ChatRequest {
    private String message;
    private String userId;
    private String sessionId;
}

