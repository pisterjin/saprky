-- 02. 도메인별 질문 분포
-- 어떤 정책 분야(주거/취업/금융/교육/복지)에 대한 질문이 많은지 확인합니다.

SELECT
    COALESCE(domain, 'unknown')                          AS domain,
    COUNT(*)                                             AS question_count,
    ROUND(COUNT(*)::NUMERIC / SUM(COUNT(*)) OVER () * 100, 1) AS pct,
    COUNT(DISTINCT session_id)                           AS unique_sessions,
    ROUND(AVG(response_time_ms))                         AS avg_response_ms
FROM chat_logs
WHERE created_at >= NOW() - INTERVAL '30 days'
GROUP BY domain
ORDER BY question_count DESC;
