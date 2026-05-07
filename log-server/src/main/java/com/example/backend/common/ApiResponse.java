package com.example.backend.common;

import lombok.Builder;
import lombok.Getter;

// common/ApiResponse.java
@Getter
@Builder
public class ApiResponse<T> {
    private boolean success;
    private String errorCode;
    private String message;
    private T data;

    public static <T> ApiResponse<T> ok(T data) {
        return ApiResponse.<T>builder()
                .success(true).data(data).build();
    }

    public static <T> ApiResponse<T> error(String errorCode, String message) {
        return ApiResponse.<T>builder()
                .success(false)
                .errorCode(errorCode)
                .message(message)
                .build();
    }
}