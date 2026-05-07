-- 05. 응답 시간 분포
-- AI 응답속도 현황 및 느린 쿼리를 파악합니다.

-- 전체 통계
SELECT
    ROUND(AVG(response_time_ms))    AS avg_ms,
    MIN(response_time_ms)           AS min_ms,
    MAX(response_time_ms)           AS max_ms,
    PERCENTILE_CONT(0.5)  WITHIN GROUP (ORDER BY response_time_ms) AS p50_ms,
    PERCENTILE_CONT(0.90) WITHIN GROUP (ORDER BY response_time_ms) AS p90_ms,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY response_time_ms) AS p95_ms,
    COUNT(*) FILTER (WHERE response_time_ms > 10000)  AS over_10s_count,
    COUNT(*) FILTER (WHERE response_time_ms > 30000)  AS over_30s_count
FROM chat_logs
WHERE created_at >= NOW() - INTERVAL '7 days'
  AND response_time_ms IS NOT NULL;

-- 도메인별 응답시간
SELECT
    COALESCE(domain, 'unknown')     AS domain,
    COUNT(*)                        AS count,
    ROUND(AVG(response_time_ms))    AS avg_ms,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY response_time_ms) AS p95_ms
FROM chat_logs
WHERE created_at >= NOW() - INTERVAL '7 days'
  AND response_time_ms IS NOT NULL
GROUP BY domain
ORDER BY avg_ms DESC;
