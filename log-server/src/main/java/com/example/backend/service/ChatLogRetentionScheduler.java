package com.example.backend.service;

import com.example.backend.repository.ChatLogRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.time.ZoneOffset;

@Slf4j
@Component
@RequiredArgsConstructor
public class ChatLogRetentionScheduler {

    private final ChatLogRepository chatLogRepository;

    // 매일 새벽 3시 실행 — 수집일로부터 1년 경과 로그 영구 삭제
    @Scheduled(cron = "0 0 3 * * *")
    @Transactional
    public void purgeExpiredLogs() {
        LocalDateTime cutoff = LocalDateTime.now(ZoneOffset.UTC).minusYears(1);
        int deleted = chatLogRepository.deleteByCreatedAtBefore(cutoff);
        log.info("[RetentionPolicy] chat_logs 파기 완료: {}건 (기준: {})", deleted, cutoff);
    }
}
