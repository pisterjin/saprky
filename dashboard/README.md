# SPARKY 대시보드

SPARKY 로그 DB(PostgreSQL)에 직접 쿼리해서 서비스 현황을 파악하는 SQL 대시보드입니다.

---

## 연결 정보

| 항목     | 값                                      |
| -------- | --------------------------------------- |
| Host     | `localhost`                             |
| Port     | `5433` (Docker 매핑)                    |
| DB       | `sparky`                                |
| User     | `postgres`                              |
| Password | `password` (`.env` 참고)                |

**접속 예시 (psql):**
```bash
psql -h localhost -p 5433 -U postgres -d sparky
```

**접속 예시 (DBeaver / DataGrip):** 위 정보를 그대로 입력.

---

## 테이블 구조

| 테이블                | 역할                                  | 주요 컬럼 |
| --------------------- | ------------------------------------- | --------- |
| `chat_logs`           | 채팅 턴별 로그 (질문·답변·도메인 등) | `session_id`, `domain`, `is_clarifying`, `response_time_ms`, `masking_hit` |
| `session_meta`        | 세션 단위 메타 (연령대·지역·턴 수)   | `session_id`, `age_group`, `gender`, `region`, `total_turns` |
| `log_policies`        | 응답에 포함된 정책 카드 목록          | `chat_log_id`, `policy_id`, `policy_title`, `category`, `rank_pos` |
| `policy_click_events` | 사용자가 클릭한 정책 카드 이벤트     | `session_id`, `policy_id`, `category`, `clicked_at` |

---

## SQL 파일 목록

| 파일 | 내용 | 주요 지표 |
| ---- | ---- | --------- |
| [01_daily_usage.sql](sql/01_daily_usage.sql) | 일별 사용량 | 세션 수, 질문 수, 평균 응답시간, clarifying 비율 |
| [02_domain_distribution.sql](sql/02_domain_distribution.sql) | 도메인별 질문 분포 | 주거/취업/금융/교육/복지별 질문 비율 |
| [03_user_profile_distribution.sql](sql/03_user_profile_distribution.sql) | 사용자 프로필 분포 | 연령대·성별·지역별 세션 수 |
| [04_top_clicked_policies.sql](sql/04_top_clicked_policies.sql) | 인기 정책 TOP 20 | 클릭 수, 클릭 세션 수, 클릭 점유율 |
| [05_response_time_stats.sql](sql/05_response_time_stats.sql) | 응답 시간 분포 | 평균·P50·P90·P95, 10초/30초 초과 건수 |
| [06_clarifying_and_retry.sql](sql/06_clarifying_and_retry.sql) | 재질문·재시도 현황 | RAG 품질 지표, 세션당 평균 대화 턴 |
| [07_masking_stats.sql](sql/07_masking_stats.sql) | 개인정보 마스킹 현황 | 마스킹 감지율, 소스별 빈도, 일별 추이 |

---

## 빠른 현황 확인 (원라이너)

```sql
-- 오늘 세션 수 / 질문 수
SELECT COUNT(DISTINCT session_id) AS sessions, COUNT(*) AS questions
FROM chat_logs WHERE DATE(created_at) = CURRENT_DATE;

-- 현재 clarifying 비율 (최근 7일)
SELECT ROUND(AVG(is_clarifying::int) * 100, 1) AS clarifying_pct
FROM chat_logs WHERE created_at >= NOW() - INTERVAL '7 days';

-- 가장 많이 클릭된 정책 (오늘)
SELECT policy_id, COUNT(*) AS clicks
FROM policy_click_events WHERE DATE(clicked_at) = CURRENT_DATE
GROUP BY policy_id ORDER BY clicks DESC LIMIT 5;
```

---

## 권장 모니터링 주기

| 지표 | 권장 주기 | 참고 쿼리 |
| ---- | --------- | --------- |
| 일별 사용량 | 매일 아침 | `01_daily_usage.sql` |
| 응답 시간 이상 | 실시간/1시간 | `05_response_time_stats.sql` |
| 인기 정책 | 주 1회 | `04_top_clicked_policies.sql` |
| 마스킹 감지율 급증 | 이상 시 | `07_masking_stats.sql` |
| 사용자 프로필 | 주 1회 | `03_user_profile_distribution.sql` |
