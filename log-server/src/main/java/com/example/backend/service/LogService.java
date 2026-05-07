package com.example.backend.service;

import com.example.backend.entity.LogEntity;
import com.example.backend.repository.LogRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
@Service
@RequiredArgsConstructor
public class LogService {

    private final LogRepository logRepository;

    // 1. 일반 로그 저장
    @Async
    @Transactional
    public void info(String serviceName, String message) {
        saveLog(serviceName, "INFO", message, null);
    }

    // 2. 에러 로그 저장 (설계서 ER-001 등 대응)
    @Async
    @Transactional
    public void error(String serviceName, String message, String details) {
        saveLog(serviceName, "ERROR", message, details);
    }

    // 3. 공통 저장 로직
    // saveLog() 수정
    private void saveLog(String serviceName, String level, String message, String details) {
        LogEntity log = LogEntity.builder()
                .userId(null)           // 호출부에서 넘겨받거나 null
                .sessionId(serviceName) // serviceName → sessionId로 활용
                .request(message)       // message → request로 활용
                .response(details)      // details → response로 활용
                .latencyMs(null)
                .logType(level)         // "INFO" / "ERROR" → logType
                .build();
        logRepository.save(log);
    }
    // 4. 로그 조회 (필요 시)
    public Page<LogEntity> getAllLogs(int page, int size) {
        return logRepository.findAll(
                PageRequest.of(page, size, Sort.by("createdAt").descending())
        );
    }
    // 메시지만 받으면 기본값으로 저장해주는 편리한 메서드
    public void saveLog(String message) {
        this.info("GENERAL", message);
    }

    public Page<LogEntity> getLogs(int page, int size) {
        return logRepository.findAll(
                PageRequest.of(page, size, Sort.by("createdAt").descending())
        );
    }

    public Page<LogEntity> getLogsByLevel(String level, int page, int size) {
        return logRepository.findByLogType(
                level, PageRequest.of(page, size, Sort.by("createdAt").descending())
        );
    }

    public void savePolicy(String userId, String sessionId, String s) {
    }

    public void saveError(String userId, String sessionId, String s) {
    }
}


