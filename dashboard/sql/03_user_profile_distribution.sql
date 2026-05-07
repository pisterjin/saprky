-- 03. 사용자 프로필 분포
-- 연령대·성별·지역별 사용자 분포를 확인합니다.
-- (session_meta 기준 — 세션당 1행)

-- 연령대별
SELECT
    age_group,
    COUNT(*) AS sessions,
    ROUND(COUNT(*)::NUMERIC / SUM(COUNT(*)) OVER () * 100, 1) AS pct
FROM session_meta
WHERE started_at >= NOW() - INTERVAL '30 days'
GROUP BY age_group
ORDER BY sessions DESC;

-- 지역별
SELECT
    COALESCE(region, 'unknown') AS region,
    COUNT(*) AS sessions,
    ROUND(COUNT(*)::NUMERIC / SUM(COUNT(*)) OVER () * 100, 1) AS pct
FROM session_meta
WHERE started_at >= NOW() - INTERVAL '30 days'
GROUP BY region
ORDER BY sessions DESC;

-- 성별
SELECT
    COALESCE(gender, 'unknown') AS gender,
    COUNT(*) AS sessions,
    ROUND(COUNT(*)::NUMERIC / SUM(COUNT(*)) OVER () * 100, 1) AS pct
FROM session_meta
WHERE started_at >= NOW() - INTERVAL '30 days'
GROUP BY gender
ORDER BY sessions DESC;
