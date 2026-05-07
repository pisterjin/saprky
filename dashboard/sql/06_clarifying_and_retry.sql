-- 06. 재질문(clarifying) 및 재시도(retry) 현황
-- RAG 품질 지표: 정책을 못 찾아서 되물어본 비율, 사용자 재시도 비율을 확인합니다.

-- 도메인별 clarifying 비율
SELECT
    COALESCE(domain, 'unknown')                    AS domain,
    COUNT(*)                                       AS total,
    COUNT(*) FILTER (WHERE is_clarifying)          AS clarifying,
    ROUND(
        COUNT(*) FILTER (WHERE is_clarifying)::NUMERIC
        / NULLIF(COUNT(*), 0) * 100, 1
    )                                              AS clarifying_pct
FROM chat_logs
WHERE created_at >= NOW() - INTERVAL '30 days'
GROUP BY domain
ORDER BY clarifying_pct DESC;

-- 재시도 현황
SELECT
    COALESCE(retry_reason, 'none')                 AS retry_reason,
    COUNT(*)                                       AS count,
    ROUND(AVG(retry_count), 2)                     AS avg_retry_count
FROM chat_logs
WHERE created_at >= NOW() - INTERVAL '30 days'
  AND retry_count > 0
GROUP BY retry_reason
ORDER BY count DESC;

-- 세션당 평균 대화 턴 수
SELECT
    ROUND(AVG(total_turns), 2)  AS avg_turns_per_session,
    MAX(total_turns)            AS max_turns,
    COUNT(*) FILTER (WHERE total_turns >= 5) AS long_sessions
FROM session_meta
WHERE started_at >= NOW() - INTERVAL '30 days';
