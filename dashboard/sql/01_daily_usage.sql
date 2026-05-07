-- 01. 일별 사용량
-- 날짜별 세션 수, 총 질문 수, 평균 응답시간을 확인합니다.

SELECT
    DATE(cl.created_at)                          AS date,
    COUNT(DISTINCT cl.session_id)                AS sessions,
    COUNT(*)                                     AS total_questions,
    ROUND(AVG(cl.response_time_ms))              AS avg_response_ms,
    COUNT(*) FILTER (WHERE cl.is_clarifying)     AS clarifying_count,
    ROUND(
        COUNT(*) FILTER (WHERE cl.is_clarifying)::NUMERIC
        / NULLIF(COUNT(*), 0) * 100, 1
    )                                            AS clarifying_pct
FROM chat_logs cl
WHERE cl.created_at >= NOW() - INTERVAL '30 days'
GROUP BY DATE(cl.created_at)
ORDER BY date DESC;
