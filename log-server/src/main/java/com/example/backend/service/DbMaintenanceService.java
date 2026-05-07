package com.example.backend.service;

import com.example.backend.repository.ChatLogRepository;
import com.example.backend.repository.PolicyClickEventRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;

@Slf4j
@Service
@RequiredArgsConstructor
public class DbMaintenanceService {

    private final ChatLogRepository chatLogRepo;
    private final PolicyClickEventRepository clickRepo;
    private final JdbcTemplate jdbc;

    @Value("${db.maintenance.retention-days:90}")
    private int retentionDays;

    @Value("${db.maintenance.warn-rows:500000}")
    private long warnRows;

    @Value("${db.maintenance.warn-size-mb:500}")
    private long warnSizeMb;

    /** 매일 02:00 KST — 보존 기간 초과 로그 삭제 */
    @Scheduled(cron = "0 0 2 * * *", zone = "Asia/Seoul")
    @Transactional
    public void cleanupOldLogs() {
        LocalDateTime cutoff = LocalDateTime.now().minusDays(retentionDays);
        int deletedLogs   = chatLogRepo.deleteByCreatedAtBefore(cutoff);
        int deletedClicks = clickRepo.deleteByClickedAtBefore(cutoff);
        log.info("[DB Cleanup] {}일 이전 레코드 삭제 — chat_logs: {}건, policy_click_events: {}건",
                retentionDays, deletedLogs, deletedClicks);
    }

    /** 매일 01:00 KST — DB 크기 및 행 수 점검 */
    @Scheduled(cron = "0 0 1 * * *", zone = "Asia/Seoul")
    public void checkDbCapacity() {
        long chatRows  = chatLogRepo.count();
        long clickRows = clickRepo.count();
        long totalRows = chatRows + clickRows;

        Long sizeBytes = jdbc.queryForObject(
                "SELECT pg_database_size(current_database())", Long.class);
        long sizeMb = (sizeBytes != null ? sizeBytes : 0L) / (1024 * 1024);

        log.info("[DB Monitor] chat_logs: {}건 | click_events: {}건 | DB 크기: {}MB",
                chatRows, clickRows, sizeMb);

        if (totalRows >= warnRows) {
            log.warn("[DB Monitor] ⚠️ 전체 로그 {}건 — 임계치({}건) 초과. 보존 기간 단축 또는 아카이브 검토 필요",
                    totalRows, warnRows);
        }
        if (sizeMb >= warnSizeMb) {
            log.warn("[DB Monitor] ⚠️ DB 크기 {}MB — 임계치({}MB) 초과. 디스크 용량 점검 필요",
                    sizeMb, warnSizeMb);
        }
    }
}
