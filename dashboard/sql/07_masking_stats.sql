-- 07. 개인정보 마스킹 감지 현황
-- 사용자 입력에서 개인정보(이름·전화번호·주소 등)가 감지된 빈도를 확인합니다.

-- 전체 마스킹 감지 비율
SELECT
    COUNT(*)                                       AS total_messages,
    COUNT(*) FILTER (WHERE masking_hit)            AS masked_count,
    ROUND(
        COUNT(*) FILTER (WHERE masking_hit)::NUMERIC
        / NULLIF(COUNT(*), 0) * 100, 2
    )                                              AS masking_rate_pct
FROM chat_logs
WHERE created_at >= NOW() - INTERVAL '30 days';

-- 마스킹 소스별 빈도 (masking_sources: 'name,phone' 형태의 콤마 구분 문자열)
SELECT
    TRIM(source)        AS masking_source,
    COUNT(*)            AS count
FROM chat_logs,
     LATERAL UNNEST(STRING_TO_ARRAY(masking_sources, ',')) AS source
WHERE masking_hit = TRUE
  AND masking_sources IS NOT NULL
  AND created_at >= NOW() - INTERVAL '30 days'
GROUP BY TRIM(source)
ORDER BY count DESC;

-- 일별 마스킹 감지 추이
SELECT
    DATE(created_at)                               AS date,
    COUNT(*)                                       AS total,
    COUNT(*) FILTER (WHERE masking_hit)            AS masked,
    ROUND(
        COUNT(*) FILTER (WHERE masking_hit)::NUMERIC
        / NULLIF(COUNT(*), 0) * 100, 1
    )                                              AS masking_pct
FROM chat_logs
WHERE created_at >= NOW() - INTERVAL '14 days'
GROUP BY DATE(created_at)
ORDER BY date DESC;
