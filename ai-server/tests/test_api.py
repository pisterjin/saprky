"""
TC-20 ~ TC-25 : API 엔드포인트 통합 테스트
health check, CORS, 15-18세 차단, 스키마 검증 등
"""
import pytest
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


class TestHealthCheck:
    def test_health_endpoint(self, client):
        """GET /api/health → 200"""
        res = client.get("/api/health")
        assert res.status_code == 200
        assert res.json()["status"] == "ok"
        assert res.json()["service"] == "SPARKY AI Server"


class TestSchemaValidation:
    def test_missing_question_field(self, client, user_seoul_25):
        """question 필드 누락 → 422"""
        payload = {
            "userProfile": user_seoul_25,
            "conversationHistory": []
        }
        res = client.post("/api/chat", json=payload)
        assert res.status_code == 422

    def test_missing_user_profile(self, client):
        """userProfile 필드 누락 → 422"""
        payload = {"question": "테스트", "conversationHistory": []}
        res = client.post("/api/chat", json=payload)
        assert res.status_code == 422

    def test_response_schema(self, client, user_seoul_25, welcome_msg):
        """응답 스키마 필수 필드 검증"""
        payload = {
            "question": "취업 지원 알려줘",
            "userProfile": user_seoul_25,
            "conversationHistory": [welcome_msg]
        }
        res = client.post("/api/chat", json=payload)
        assert res.status_code == 200
        data = res.json()

        # 필수 필드 존재 확인
        assert "answer" in data
        assert "policyIds" in data
        assert "domain" in data
        assert "cards" in data
        assert "is_clarifying" in data

        # 타입 검증
        assert isinstance(data["answer"], str)
        assert isinstance(data["policyIds"], list)
        assert isinstance(data["cards"], list)
        assert isinstance(data["is_clarifying"], bool)

    def test_domain_values(self, client, user_seoul_25, welcome_msg):
        """domain 값이 유효한 Enum 값이어야 함"""
        VALID_DOMAINS = {"취업", "주거", "금융", "교육", "복지", "판단불가"}
        payload = {
            "question": "청년 정책 알려줘",
            "userProfile": user_seoul_25,
            "conversationHistory": [welcome_msg]
        }
        res = client.post("/api/chat", json=payload)
        assert res.status_code == 200
        assert res.json()["domain"] in VALID_DOMAINS


class TestAgeGroupBlocking:
    def test_15_18_blocked(self, client, welcome_msg):
        """15-18세 연령대 → 서비스 대상 외 안내"""
        payload = {
            "question": "청년 정책 알려줘",
            "userProfile": {
                "ageGroup": "youth_15_18",
                "gender": "male",
                "region": "seoul",
                "uuid": "test-uuid"
            },
            "conversationHistory": [welcome_msg]
        }
        res = client.post("/api/chat", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["is_clarifying"] == False
        assert data["cards"] == []
        # 안내 메시지 포함 여부
        assert any(kw in data["answer"] for kw in ["19세", "만 19", "서비스", "대상"])

    def test_19_24_not_blocked(self, client, welcome_msg):
        """19-24세 → 정상 처리"""
        payload = {
            "question": "취업 정책 알려줘",
            "userProfile": {
                "ageGroup": "youth_19_24",
                "gender": "female",
                "region": "busan",
                "uuid": "test-uuid"
            },
            "conversationHistory": [welcome_msg]
        }
        res = client.post("/api/chat", json=payload)
        assert res.status_code == 200
        # 정상 처리 (answer가 차단 메시지가 아님)
        data = res.json()
        block_keywords = ["19세 이상", "만 19세", "서비스 대상"]
        is_blocked = any(kw in data["answer"] for kw in block_keywords)
        assert not is_blocked, "19-24세가 차단되어선 안 됨"


class TestIsClarifyingLogic:
    def test_is_clarifying_true_has_no_cards(self, client, user_seoul_25, welcome_msg):
        """is_clarifying=True 응답에는 cards=[] 이어야 함"""
        payload = {
            "question": "청년 지원 정책 알려줘",
            "userProfile": user_seoul_25,
            "conversationHistory": [welcome_msg]
        }
        res = client.post("/api/chat", json=payload)
        assert res.status_code == 200
        data = res.json()

        if data["is_clarifying"]:
            assert data["cards"] == [], "is_clarifying=True일 때 cards는 비어 있어야 함"
            assert data["policyIds"] == [], "is_clarifying=True일 때 policyIds는 비어 있어야 함"

    def test_is_clarifying_false_may_have_cards(self, client, user_seoul_25):
        """is_clarifying=False인 최종 추천에는 cards가 있을 수 있음"""
        # Turn 4 강제 종료 시나리오
        from conftest import make_user_msg, make_ai_msg
        history = [
            {"id": "welcome", "role": "assistant", "content": "안녕하세요", "timestamp": 1},
            {"id": "u1", "role": "user", "content": "취업 정책 알려줘", "timestamp": 2},
            {"id": "a1", "role": "assistant", "content": "어떤 취업 형태인가요?", "timestamp": 3},
            {"id": "u2", "role": "user", "content": "중소기업이요", "timestamp": 4},
            {"id": "a2", "role": "assistant", "content": "경력자인가요?", "timestamp": 5},
            {"id": "u3", "role": "user", "content": "신입이에요", "timestamp": 6},
            {"id": "a3", "role": "assistant", "content": "지원금 유형을 알려주세요", "timestamp": 7},
        ]
        payload = {
            "question": "취업 장려금이요",
            "userProfile": user_seoul_25,
            "conversationHistory": history
        }
        res = client.post("/api/chat", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["is_clarifying"] == False  # Turn 4 강제 종료
