-- 04. 인기 정책 TOP 20 (클릭 기준)
-- 사용자가 실제로 클릭한 정책 카드를 집계합니다.

SELECT
    pce.policy_id,
    lp.policy_title,
    lp.category,
    COUNT(*)                                         AS click_count,
    COUNT(DISTINCT pce.session_id)                   AS unique_sessions,
    ROUND(COUNT(*)::NUMERIC / SUM(COUNT(*)) OVER () * 100, 2) AS click_share_pct
FROM policy_click_events pce
LEFT JOIN log_policies lp ON pce.policy_id = lp.policy_id
WHERE pce.clicked_at >= NOW() - INTERVAL '30 days'
GROUP BY pce.policy_id, lp.policy_title, lp.category
ORDER BY click_count DESC
LIMIT 20;
