"""
TC-10 ~ TC-19 : 유닛 테스트
도메인 분류, 맥락 유지, 마스킹, 필드 매핑 등
"""
import pytest
import asyncio
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


# ─────────────────────────────────────────────────────────────
# TC-10 : 도메인 분류 (키워드 매칭)
# ─────────────────────────────────────────────────────────────
class TestDomainClassification:
    @pytest.mark.asyncio
    async def test_employment_keywords(self):
        from services.llm_service import classify_domain
        from models.schemas import PolicyDomain
        cases = ["취업하고 싶어요", "일자리 지원", "채용 정보", "인턴십 알려줘", "구직 중이에요"]
        for q in cases:
            result = await classify_domain(q)
            assert result == PolicyDomain.employment, f"'{q}' → {result} (expected 취업)"

    @pytest.mark.asyncio
    async def test_housing_keywords(self):
        from services.llm_service import classify_domain
        from models.schemas import PolicyDomain
        cases = ["전세 지원", "월세 보조", "주거 정책", "주택 지원", "임대 아파트"]
        for q in cases:
            result = await classify_domain(q)
            assert result == PolicyDomain.housing, f"'{q}' → {result} (expected 주거)"

    @pytest.mark.asyncio
    async def test_finance_keywords(self):
        from services.llm_service import classify_domain
        from models.schemas import PolicyDomain
        cases = ["대출 받고 싶어요", "적금 지원", "청년 자산 형성", "저축 정책"]
        for q in cases:
            result = await classify_domain(q)
            assert result == PolicyDomain.finance, f"'{q}' → {result} (expected 금융)"

    @pytest.mark.asyncio
    async def test_education_keywords(self):
        from services.llm_service import classify_domain
        from models.schemas import PolicyDomain
        cases = ["장학금 받고 싶어요", "직업 훈련", "자격증 취득", "학비 지원"]
        for q in cases:
            result = await classify_domain(q)
            assert result == PolicyDomain.education, f"'{q}' → {result} (expected 교육)"

    @pytest.mark.asyncio
    async def test_welfare_keywords(self):
        from services.llm_service import classify_domain
        from models.schemas import PolicyDomain
        cases = ["의료 지원", "건강 보험", "복지 서비스", "심리 상담"]
        for q in cases:
            result = await classify_domain(q)
            assert result == PolicyDomain.welfare, f"'{q}' → {result} (expected 복지)"


# ─────────────────────────────────────────────────────────────
# TC-11 : expand_query 맥락 유지 검증
# ─────────────────────────────────────────────────────────────
class TestExpandQueryContextRetention:
    @pytest.mark.asyncio
    async def test_first_intent_preserved_turn2(self):
        """Turn 2에서 최초 의도(IT) 키워드가 쿼리에 유지되어야 함"""
        from services.llm_service import expand_query
        from conftest import make_user_msg, make_ai_msg

        history = [
            {"id": "welcome", "role": "assistant", "content": "안녕하세요 SPARKY입니다", "timestamp": 1},
            {"id": "u1", "role": "user", "content": "IT 청년정책 알고 싶어요", "timestamp": 2},
            {"id": "a1", "role": "assistant", "content": "50개 정책이 있어요. 취업 지원인가요, 교육 지원인가요?", "timestamp": 3},
        ]

        # ChatMessage 객체로 변환
        from models.schemas import ChatMessage
        history_objs = [ChatMessage(**m) for m in history]

        result = await expand_query("취업 지원이요", history_objs)

        # 최초 의도 IT가 확장 쿼리에 포함되어야 함
        it_related = any(kw in result for kw in ["IT", "소프트웨어", "SW", "디지털", "개발", "기술"])
        assert it_related, f"IT 맥락이 쿼리에서 누락됨: '{result}'"

    @pytest.mark.asyncio
    async def test_welcome_message_not_treated_as_first_intent(self):
        """환영 메시지가 최초 요청으로 사용되지 않아야 함"""
        from services.llm_service import expand_query
        from models.schemas import ChatMessage

        history = [
            ChatMessage(id="welcome", role="assistant", content="안녕하세요! 저는 SPARKY예요 :)", timestamp=1),
        ]

        result = await expand_query("주거 지원 알려줘", history)
        # 환영 메시지 내용이 쿼리로 잡히면 안 됨
        assert "SPARKY" not in result
        assert "안녕하세요" not in result

    @pytest.mark.asyncio
    async def test_conditions_accumulate_across_turns(self):
        """Turn 3에서 Turn 1, 2 조건이 누적되어야 함"""
        from services.llm_service import expand_query
        from models.schemas import ChatMessage

        history = [
            ChatMessage(id="welcome", role="assistant", content="안녕하세요", timestamp=1),
            ChatMessage(id="u1", role="user", content="청년 주거 지원 받고 싶어요", timestamp=2),
            ChatMessage(id="a1", role="assistant", content="전세 지원인가요, 월세 지원인가요?", timestamp=3),
            ChatMessage(id="u2", role="user", content="전세요", timestamp=4),
            ChatMessage(id="a2", role="assistant", content="단독가구인가요, 가족과 함께인가요?", timestamp=5),
        ]

        result = await expand_query("단독가구요", history)
        # 주거 + 전세 조건이 쿼리에 포함되어야 함
        housing_related = any(kw in result for kw in ["주거", "전세", "주택", "임대"])
        assert housing_related, f"주거/전세 조건이 누락됨: '{result}'"


# ─────────────────────────────────────────────────────────────
# TC-12 : policy_service 필드 매핑 검증
# ─────────────────────────────────────────────────────────────
class TestPolicyServiceFieldMapping:
    @pytest.mark.asyncio
    async def test_policies_loaded(self):
        """resource.json 로드 확인"""
        from services.policy_service import load_policies, _policy_dict
        load_policies()
        assert len(_policy_dict) > 0, "정책 데이터가 로드되지 않음"

    @pytest.mark.asyncio
    async def test_fetch_by_valid_id(self):
        """유효한 ID로 PolicyCard 반환"""
        from services.policy_service import load_policies, fetch_policies_by_ids, _policy_dict
        load_policies()

        # 실제 존재하는 ID 하나 가져오기
        if not _policy_dict:
            pytest.skip("resource.json 없음")

        sample_id = list(_policy_dict.keys())[0]
        cards = await fetch_policies_by_ids([sample_id])

        assert len(cards) == 1
        card = cards[0]
        assert card.id == sample_id
        assert card.title and len(card.title) > 0
        assert card.domain is not None
        assert card.applyUrl and card.applyUrl.startswith("http")

    @pytest.mark.asyncio
    async def test_invalid_id_returns_empty(self):
        """존재하지 않는 ID → 빈 리스트 반환"""
        from services.policy_service import fetch_policies_by_ids
        cards = await fetch_policies_by_ids(["NONEXISTENT_ID_999"])
        assert cards == []

    @pytest.mark.asyncio
    async def test_target_field_not_none(self):
        """sprtTrgtCn 없는 필드 → '만 N~M세' 형식으로 대체"""
        from services.policy_service import load_policies, fetch_policies_by_ids, _policy_dict
        load_policies()
        if not _policy_dict:
            pytest.skip("resource.json 없음")

        sample_ids = list(_policy_dict.keys())[:10]
        cards = await fetch_policies_by_ids(sample_ids)
        for card in cards:
            assert card.target is not None
            assert "None" not in card.target
            assert len(card.target) > 0

    @pytest.mark.asyncio
    async def test_period_field_not_none(self):
        """rqutPrdCn 없는 필드 → bizPrdEtcCn / 상시 fallback"""
        from services.policy_service import load_policies, fetch_policies_by_ids, _policy_dict
        load_policies()
        if not _policy_dict:
            pytest.skip("resource.json 없음")

        sample_ids = list(_policy_dict.keys())[:10]
        cards = await fetch_policies_by_ids(sample_ids)
        for card in cards:
            assert card.period is not None
            assert "None" not in card.period


# ─────────────────────────────────────────────────────────────
# TC-13 : 민감정보 마스킹
# ─────────────────────────────────────────────────────────────
class TestMasking:
    def test_rrn_masked(self):
        """주민번호 마스킹"""
        from utils.masking import mask_sensitive
        result = mask_sensitive("제 주민번호는 901225-1234567 입니다")
        assert "901225-1234567" not in result
        assert "[주민번호 마스킹]" in result

    def test_phone_masked(self):
        """전화번호 마스킹"""
        from utils.masking import mask_sensitive
        cases = ["010-1234-5678", "01012345678", "010 1234 5678"]
        for phone in cases:
            result = mask_sensitive(f"연락처: {phone}")
            assert phone not in result
            assert "[전화번호 마스킹]" in result, f"전화번호 마스킹 실패: {phone}"

    def test_account_masked(self):
        """계좌번호 마스킹"""
        from utils.masking import mask_sensitive
        result = mask_sensitive("계좌번호: 110-123456-78901")
        assert "110-123456-78901" not in result
        assert "[계좌번호 마스킹]" in result

    def test_email_masked(self):
        """이메일 마스킹"""
        from utils.masking import mask_sensitive
        result = mask_sensitive("이메일은 sparky@test.com 입니다")
        assert "sparky@test.com" not in result
        assert "[이메일 마스킹]" in result

    def test_normal_text_unchanged(self):
        """민감정보 없는 일반 텍스트는 변경 없음"""
        from utils.masking import mask_sensitive
        text = "청년 전세 대출 지원 정책을 알고 싶어요"
        assert mask_sensitive(text) == text

    def test_multiple_patterns_in_one_text(self):
        """여러 민감정보 동시 마스킹"""
        from utils.masking import mask_sensitive
        text = "주민번호 901225-1234567, 전화 010-9876-5432, 계좌 110-123456-78901"
        result = mask_sensitive(text)
        assert "901225-1234567" not in result
        assert "010-9876-5432" not in result
        assert "110-123456-78901" not in result


# ─────────────────────────────────────────────────────────────
# TC-14 : 도메인 매핑 (utils.py)
# ─────────────────────────────────────────────────────────────
class TestDomainMapping:
    def test_employment_mapping(self):
        from services.utils import map_domain
        from models.schemas import PolicyDomain
        assert map_domain("일자리", "취업") == PolicyDomain.employment
        assert map_domain("", "창업") == PolicyDomain.employment

    def test_housing_mapping(self):
        from services.utils import map_domain
        from models.schemas import PolicyDomain
        assert map_domain("주거", "주택 및 거주지") == PolicyDomain.housing
        assert map_domain("", "전월세 및 주거급여 지원") == PolicyDomain.housing

    def test_finance_mapping(self):
        from services.utils import map_domain
        from models.schemas import PolicyDomain
        assert map_domain("금융·복지·문화", "") == PolicyDomain.finance

    def test_education_mapping(self):
        from services.utils import map_domain
        from models.schemas import PolicyDomain
        assert map_domain("교육·직업훈련", "") == PolicyDomain.education
        assert map_domain("교육", "미래역량강화") == PolicyDomain.education

    def test_welfare_mapping(self):
        from services.utils import map_domain
        from models.schemas import PolicyDomain
        assert map_domain("복지문화", "건강") == PolicyDomain.welfare
        assert map_domain("참여권리", "청년참여") == PolicyDomain.welfare


# ─────────────────────────────────────────────────────────────
# TC-15 : 지역 매핑 (build_index.py)
# ─────────────────────────────────────────────────────────────
class TestRegionMapping:
    def test_major_cities(self):
        from scripts.build_index import map_region
        assert map_region("서울특별시") == "seoul"
        assert map_region("부산광역시") == "busan"
        assert map_region("인천광역시 청년정책담당관") == "incheon"
        assert map_region("울산광역시") == "ulsan"
        assert map_region("광주시청") == "gwangju"

    def test_province_full_names(self):
        """충청북도 등 전체 도명 매핑 (이전 버그: central로 빠지던 문제)"""
        from scripts.build_index import map_region
        assert map_region("충청북도") == "chungbuk", "충청북도가 central로 매핑되는 버그"
        assert map_region("충청남도") == "chungnam"
        assert map_region("전라남도") == "jeonnam"
        assert map_region("경상북도") == "gyeongbuk"
        assert map_region("경상남도") == "gyeongnam"

    def test_central_government(self):
        """중앙부처 → central"""
        from scripts.build_index import map_region
        assert map_region("고용노동부") == "central"
        assert map_region("중소벤처기업부") == "central"
        assert map_region("교육부") == "central"
        assert map_region("청년정책담당관") == "central"

    def test_empty_region(self):
        """빈 값 → central"""
        from scripts.build_index import map_region
        assert map_region("") == "central"
        assert map_region(None) == "central"
