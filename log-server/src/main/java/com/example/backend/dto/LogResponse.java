package com.example.backend.dto; 

import lombok.Getter;
import lombok.AllArgsConstructor;
import java.time.LocalDateTime;

@Getter
@AllArgsConstructor
public class LogResponse {
    private Long id;
    private String userId;
    private String logType;
    private String request;
    private String response;
    private LocalDateTime createdAt;
}