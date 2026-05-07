package com.example.backend.common;

public class PolicyNotFoundException extends RuntimeException {
    public PolicyNotFoundException(Long id) {
        super("정책을 찾을 수 없습니다. id=" + id);
    }
}