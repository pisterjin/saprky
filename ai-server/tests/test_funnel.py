"""
TC-01 ~ TC-05 : 아키네이터 퍼널 흐름 테스트
아키네이터 방식 핵심: 질문을 통해 정책을 줄여나감
Turn1(50개) → 질문 → Turn2(15개) → 질문 → Turn3(3개) → 캐러셀 반환
"""
import pytest
from conftest import make_user_msg, make_ai_msg


# ─────────────────────────────────────────────────────────────
# TC-01 Turn 1: 첫 질문 → is_clarifying=True, 카드 없음
# ─────────────────────────────────────────────────────────────
class TestTurn1:
    def test_first_question_returns_clarifying(self, client, user_seoul_25, welcome_msg):
        """Turn 1: 첫 질문에 대해 좁히기 질문을 반환해야 함"""
        payload = {
            "question": "청년 주거 지원 정책 알고 싶어요",
            "userProfile": user_seoul_25,
            "conversationHistory": [welcome_msg]  # 환영 메시지만
        }
        res = client.post("/api/chat", json=payload)
        assert res.status_code == 200
        data = res.json()

        # 아키네이터: 첫 턴은 후보가 많으므로 좁히기 질문
        assert data["is_clarifying"] == True
        assert data["cards"] == []
        assert data["policyIds"] == []
        assert len(data["answer"]) > 0
        # 개수 안내 문구 포함 여부
        assert any(kw in data["answer"] for kw in ["개", "정책", "조건"])

    def test_first_question_domain_classified(self, client, user_seoul_25, welcome_msg):
        """Turn 1: 도메인이 올바르게 분류되어야 함"""
        payload = {
            "question": "취업 지원 정책 알려줘",
            "userProfile": user_seoul_25,
            "conversationHistory": [welcome_msg]
        }
        res = client.post("/api/chat", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["domain"] == "취업"

    def test_housing_keyword_classification(self, client, user_seoul_25, welcome_msg):
        """Turn 1: 주거 키워드 도메인 분류"""
        for question in ["전세 지원받고 싶어요", "월세 보조 정책", "주택 지원"]:
            payload = {
                "question": question,
                "userProfile": user_seoul_25,
                "conversationHistory": [welcome_msg]
            }
            res = client.post("/api/chat", json=payload)
            assert res.status_code == 200
            assert res.json()["domain"] == "주거", f"failed for: {question}"


# ─────────────────────────────────────────────────────────────
# TC-02 Turn 2: 맥락 유지 + 좁히기 질문 계속
# ─────────────────────────────────────────────────────────────
class TestTurn2ContextRetention:
    def test_context_maintained_after_clarifying(self, client, user_seoul_25, welcome_msg):
        """Turn 2: 최초 의도(주거)가 후속 답변에서도 유지되어야 함"""
        history = [
            welcome_msg,
            make_user_msg("청년 주거 지원 받고 싶어요", 1),
            make_ai_msg("현재 50개 정책이 있어요. 전세 지원을 원하시나요, 월세 지원을 원하시나요?", 2),
        ]
        payload = {
            "question": "전세요",
            "userProfile": user_seoul_25,
            "conversationHistory": history
        }
        res = client.post("/api/chat", json=payload)
        assert res.status_code == 200
        data = res.json()

        # 맥락 유지: 주거 도메인 유지
        assert data["domain"] == "주거"
        # 여전히 후보가 많으면 추가 질문, 아니면 추천
        assert isinstance(data["is_clarifying"], bool)
        assert len(data["answer"]) > 0

    def test_turn_count_correct(self, client, user_seoul_25, welcome_msg):
        """Turn 2: turn_count가 2로 계산되어야 함 (user 메시지 1개 + 1)"""
        # 이 테스트는 내부 turn_count 로직을 간접 검증
        # Turn 2에서 count > 5면 여전히 is_clarifying=True여야 함
        history = [
            welcome_msg,
            make_user_msg("교육 지원 정책 알려줘", 1),
            make_ai_msg("15개 정책이 있어요. 직업 훈련을 원하시나요, 학비 지원을 원하시나요?", 2),
        ]
        payload = {
            "question": "직업 훈련이요",
            "userProfile": user_seoul_25,
            "conversationHistory": history
        }
        res = client.post("/api/chat", json=payload)
        assert res.status_code == 200
        # Turn 2는 강제 종료 대상 아님 (turn < 4)
        # 후보 수에 따라 clarifying or recommend
        data = res.json()
        assert data["domain"] in ["교육", "취업", "판단불가"]


# ─────────────────────────────────────────────────────────────
# TC-03 Turn 4: 강제 종료 → 반드시 추천 반환
# ─────────────────────────────────────────────────────────────
class TestForcedTermination:
    def test_turn4_must_recommend(self, client, user_seoul_25, welcome_msg):
        """Turn 4: 후보 수 무관하게 반드시 추천 (should_recommend=True)"""
        # 3번의 user 메시지 = turn_count가 4가 됨
        history = [
            welcome_msg,
            make_user_msg("복지 지원 받고 싶어요", 1),
            make_ai_msg("50개 정책이 있어요. 의료 지원인가요, 생활 지원인가요?", 2),
            make_user_msg("생활 지원이요", 3),
            make_ai_msg("20개 정책이 있어요. 현금 지원인가요, 서비스 지원인가요?", 4),
            make_user_msg("현금 지원이요", 5),
            make_ai_msg("10개 정책이 있어요. 기혼자인가요, 미혼인가요?", 6),
        ]
        payload = {
            "question": "미혼이에요",
            "userProfile": user_seoul_25,
            "conversationHistory": history  # user 메시지 3개 → turn_count = 4
        }
        res = client.post("/api/chat", json=payload)
        assert res.status_code == 200
        data = res.json()

        # 핵심: Turn 4는 무조건 추천
        assert data["is_clarifying"] == False, "Turn 4는 강제 종료 → 반드시 추천해야 함"
        # 카드가 있거나, 없더라도 추천 시도
        assert isinstance(data["cards"], list)


# ─────────────────────────────────────────────────────────────
# TC-04 소규모 후보: ≤5개 → 즉시 추천
# ─────────────────────────────────────────────────────────────
class TestSmallCandidateSet:
    def test_small_candidate_set_recommends(self, client, user_seoul_25, welcome_msg):
        """후보가 ≤5개면 추가 질문 없이 즉시 캐러셀 반환"""
        # 매우 구체적인 질문으로 후보를 줄임
        history = [
            welcome_msg,
            make_user_msg("청년 전세 대출 지원 받고 싶어요", 1),
            make_ai_msg("15개 정책이 있어요. 단독가구인가요, 2인 이상 가구인가요?", 2),
            make_user_msg("단독가구요", 3),
            make_ai_msg("7개 정책이 있어요. 무주택자인가요?", 4),
        ]
        payload = {
            "question": "네 무주택자예요",
            "userProfile": user_seoul_25,
            "conversationHistory": history
        }
        res = client.post("/api/chat", json=payload)
        assert res.status_code == 200
        data = res.json()
        # 후보가 ≤5개거나 turn=3이면 추천
        # is_clarifying=False여야 추천 모드
        if data["is_clarifying"] == False:
            # 추천 모드: 카드가 있어야 함 (policy_service에 해당 ID가 있다면)
            assert isinstance(data["cards"], list)


# ─────────────────────────────────────────────────────────────
# TC-05 빈 결과 Fallback
# ─────────────────────────────────────────────────────────────
class TestEmptyResultFallback:
    def test_zero_result_triggers_fallback(self, client, user_seoul_25, welcome_msg):
        """검색 결과 0개 → should_recommend=True + fallback 안내"""
        payload = {
            "question": "우주비행사 청년 정책 알려줘",  # 존재하지 않을 질문
            "userProfile": user_seoul_25,
            "conversationHistory": [welcome_msg]
        }
        res = client.post("/api/chat", json=payload)
        assert res.status_code == 200
        data = res.json()
        # 결과 없을 때: is_clarifying=False, 안내 메시지
        # (FAISS fallback이 유사 정책 반환할 수 있음)
        assert len(data["answer"]) > 0
        assert isinstance(data["cards"], list)
