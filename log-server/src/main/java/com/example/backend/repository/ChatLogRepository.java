package com.example.backend.repository;

import com.example.backend.entity.ChatLog;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import java.time.LocalDateTime;
import java.util.List;

public interface ChatLogRepository extends JpaRepository<ChatLog, Long> {

    List<ChatLog> findBySessionIdOrderByTurnNoAsc(String sessionId);

    @Modifying
    @Query("DELETE FROM ChatLog c WHERE c.createdAt < :before")
    int deleteByCreatedAtBefore(@Param("before") LocalDateTime before);

    @Query("""
        SELECT COUNT(DISTINCT c.sessionId) FROM ChatLog c
        WHERE c.createdAt >= :from AND c.createdAt <= :to
    """)
    Long countDistinctSessions(@Param("from") LocalDateTime from, @Param("to") LocalDateTime to);

    @Query("""
        SELECT COUNT(c) FROM ChatLog c
        WHERE c.createdAt >= :from AND c.createdAt <= :to
    """)
    Long countTurns(@Param("from") LocalDateTime from, @Param("to") LocalDateTime to);

    @Query("""
        SELECT AVG(c.responseTimeMs) FROM ChatLog c
        WHERE c.createdAt >= :from AND c.createdAt <= :to AND c.responseTimeMs IS NOT NULL
    """)
    Double avgResponseMs(@Param("from") LocalDateTime from, @Param("to") LocalDateTime to);

    @Query("""
        SELECT COUNT(c) FROM ChatLog c
        WHERE c.createdAt >= :from AND c.createdAt <= :to AND c.maskingHit = true
    """)
    Long countMaskingHits(@Param("from") LocalDateTime from, @Param("to") LocalDateTime to);

    @Query("""
        SELECT COUNT(c) FROM ChatLog c
        WHERE c.createdAt >= :from AND c.createdAt <= :to AND c.isClarifying = true
    """)
    Long countClarifying(@Param("from") LocalDateTime from, @Param("to") LocalDateTime to);

    // 일별 통계 (native — JPQL은 DATE() 미지원)
    @Query(value = """
        SELECT DATE(created_at) AS date,
               COUNT(DISTINCT session_id) AS sessions,
               COUNT(*) AS questions,
               ROUND(AVG(response_time_ms)) AS avg_ms,
               COUNT(*) FILTER (WHERE is_clarifying) AS clarifying
        FROM chat_logs
        WHERE created_at >= :from
        GROUP BY DATE(created_at)
        ORDER BY date DESC
    """, nativeQuery = true)
    List<Object[]> dailyStats(@Param("from") LocalDateTime from);

    // 도메인별 분포
    @Query(value = """
        SELECT COALESCE(domain, 'unknown') AS domain, COUNT(*) AS cnt
        FROM chat_logs
        WHERE created_at >= :from
        GROUP BY domain
        ORDER BY cnt DESC
    """, nativeQuery = true)
    List<Object[]> domainDistribution(@Param("from") LocalDateTime from);

    // 도메인별 clarifying 비율
    @Query(value = """
        SELECT COALESCE(domain, 'unknown') AS domain,
               COUNT(*) AS total,
               COUNT(*) FILTER (WHERE is_clarifying) AS clarifying
        FROM chat_logs
        WHERE created_at >= :from
        GROUP BY domain
        ORDER BY total DESC
    """, nativeQuery = true)
    List<Object[]> clarifyingByDomain(@Param("from") LocalDateTime from);
}
