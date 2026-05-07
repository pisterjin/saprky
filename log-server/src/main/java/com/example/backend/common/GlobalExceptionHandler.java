package com.example.backend.common;

import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

@Slf4j
@RestControllerAdvice
public class GlobalExceptionHandler {

    // ER-002: AI 서버 오류 (일반 서버 에러)
    @ExceptionHandler(RuntimeException.class)
    public ResponseEntity<ApiResponse<Void>> handleRuntimeException(RuntimeException e) {
        log.error("서버 오류 발생: {}", e.getMessage());
        return ResponseEntity
                .status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(ApiResponse.error("ER-002", "잠시 후 다시 시도해주세요"));
    }

    // ER-003: 정책 없음 (빈 결과)
    @ExceptionHandler(PolicyNotFoundException.class)
    public ResponseEntity<ApiResponse<Void>> handlePolicyNotFoundException(PolicyNotFoundException e) {
        log.warn("정책 없음: {}", e.getMessage());
        return ResponseEntity
                .status(HttpStatus.NOT_FOUND)
                .body(ApiResponse.error("ER-003", "조건에 맞는 정책을 찾지 못했어요"));
    }

    // ER-001: 로딩 중 타임아웃
    @ExceptionHandler(java.util.concurrent.TimeoutException.class)
    public ResponseEntity<ApiResponse<Void>> handleTimeoutException(Exception e) {
        log.warn("타임아웃 발생: {}", e.getMessage());
        return ResponseEntity
                .status(HttpStatus.REQUEST_TIMEOUT)
                .body(ApiResponse.error("ER-001", "응답이 지연되고 있어요. 잠시 후 다시 시도해주세요"));
    }

    // 그 외 모든 예외
    @ExceptionHandler(Exception.class)
    public ResponseEntity<ApiResponse<Void>> handleException(Exception e) {
        log.error("알 수 없는 오류: {}", e.getMessage());
        return ResponseEntity
                .status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(ApiResponse.error("ER-002", "잠시 후 다시 시도해주세요"));
    }
}