import re
from fastapi import APIRouter, HTTPException
from models.schemas import ChatRequest, ChatResponse, PolicyDomain
from services.llm_service import classify_domain, generate_answer
from services.policy_service import fetch_policies_by_ids, filter_valid_ids

# 라우터 객체 생성
router = APIRouter(prefix="/api", tags=["chat"])

_PAST_KEYWORDS = ["지난", "예전", "작년", "마감", "종료", "과거", "이전에", "끝난", "만료", "지났"]

# 정책 부족 시 사용자에게 보여줄 안내 문구 (도메인별 맞춤)
_CLARIFY_TEMPLATES = {
    "주거": "현재 {region} 지역의 주거지원 정책을 정확히 찾지 못했어요. "
            "혹시 월세 지원, 전세자금 대출, 청년 임대주택 중 어떤 유형이 궁금하신가요?",
    "취업": "현재 {region} 지역의 취업 지원 정책이 충분하지 않아요. "
            "정규직 취업, 인턴십, 직업훈련 중 어떤 쪽이 필요하신가요?",
    "금융": "현재 {region} 지역의 금융 지원 정책을 찾지 못했어요. "
            "대출, 저축, 신용 지원 중 어떤 쪽이 궁금하신가요?",
    "교육": "현재 {region} 지역의 교육 지원 정책이 부족해요. "
            "장학금, 직업훈련, 자격증 취득 중 어떤 쪽이 필요하신가요?",
    "복지": "현재 {region} 지역의 복지 지원 정책을 찾지 못했어요. "
            "의료, 문화, 심리상담 중 어떤 쪽이 궁금하신가요?",
    "default": "현재 조건에 맞는 정책을 정확히 찾지 못했어요. "
               "조건을 조금 더 구체적으로 말씀해 주시면 다시 찾아볼게요!",
}

# 지역 코드 → 한국어 표시 이름
_REGION_LABELS = {
    "seoul": "서울", "busan": "부산", "daegu": "대구", "incheon": "인천",
    "gwangju": "광주", "daejeon": "대전", "ulsan": "울산", "sejong": "세종",
    "gyeonggi": "경기", "gangwon": "강원", "chungbuk": "충북", "chungnam": "충남",
    "jeonbuk": "전북", "jeonnam": "전남", "gyeongbuk": "경북", "gyeongnam": "경남",
    "jeju": "제주",
}


def _is_past_query(question: str, history) -> bool:
    text = question + " ".join(m.content for m in history if m.role == "user")
    return any(kw in text for kw in _PAST_KEYWORDS)


def _insufficient_reply(domain: PolicyDomain, region_code: str) -> str:
    """정책 부족 시 도메인에 맞는 안내 문구를 반환한다."""
    region_label = _REGION_LABELS.get(region_code, region_code)
    template = _CLARIFY_TEMPLATES.get(domain.value, _CLARIFY_TEMPLATES["default"])
    return template.format(region=region_label)


# POST 요청을 받는 엔드포인트
@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """
    RAG 파이프라인
    1. 도메인 분류
    2. 턴 계산
    3. generate_answer() → get_context() → FAISS 검색
    4. ID 파싱 → PolicyCard 조회
    """
    
    print(f"\n💬 [API] 요청 수신 (UUID: {req.userProfile.uuid}) | '{req.question}'")
    try:
        # 0. 연령 기반 조기 차단 (15-18세 제외)
        if req.userProfile.ageGroup == "youth_15_18":
            return ChatResponse(
                answer="죄송합니다. SPARKY는 현재 만 19세 이상의 청년 정책을 전문적으로 안내해 드리고 있습니다. 향후 서비스 대상을 확대할 예정이니 양해 부탁드립니다.",
                policyIds=[],
                domain=PolicyDomain.unknown,
                cards=[],
                is_clarifying=False
            )

        # 1. 도메인 분류 + 과거 정책 조회 의도 감지
        domain = await classify_domain(req.question)
        include_expired = _is_past_query(req.question, req.conversationHistory)
        if include_expired:
            print("📅 [API] 과거 정책 조회 의도 감지 → 만료 필터 해제")

        # 2. 턴 계산
        turn_count = len([m for m in req.conversationHistory if m.role == "user"]) + 1

        # 3. 답변 생성
        answer, is_clarifying, chips = await generate_answer(
            req.question,
            [],  # get_context()가 내부에서 처리하므로 빈 리스트
            req.conversationHistory,
            req.userProfile,
            domain,
            total_count=0,
            turn_count=turn_count,
            session_id=req.userProfile.uuid, # 세션 캐시 호출부
            # ㄴ 콘솔 로그에서 보이던 UUID는 **req.userProfile.uuid**에서 나오고 있어요. 즉 사용자 프로필 객체 안에 uuid가 있고, 매 요청마다 같은 사용자는 같은 UUID로 들어옴.
            # ㄴ 이게 세션 식별자 역할을 하니까 캐시 키로 사용 가능(실제로 UUID를 들고 있는 변수명)
        )

        # 4. 답변에서 추천 ID 파싱 → 카드 조회
        cards = []
        ids = []
        if not is_clarifying:
            # 1순위: 정식 [RECOMMEND: ID1, ID2, ...] 태그
            # .*?는 비탐욕적 매칭이라 줄바꿈이 있으면 ID를 못 찾을 수 있음
            # re.DOTALL 추가하면 줄바꿈 포함해서 매칭됨
            '''
            비탐욕적 매칭(Non-greedy matching)
            정규식에서 .*와 .*?의 차이입니다:
           text = "[RECOMMEND: ID1, ID2, ID3]"

            # 탐욕적 (.*) - 가능한 한 많이 매칭
            re.search(r"\[RECOMMEND:\s*(.*)\]", text)
            → "ID1, ID2, ID3" ✅

            # 비탐욕적 (.*?) - 가능한 한 적게 매칭
            re.search(r"\[RECOMMEND:\s*(.*?)\]", text)
            → "ID1, ID2, ID3" ✅ (한 줄이면 같음)
            그런데 줄바꿈이 있으면:
            text = "[RECOMMEND:\nID1,\nID2,\nID3]"

            # 비탐욕적 (.*?) - 줄바꿈 못 넘어감
            → "" ❌ (못 찾음)

            # re.DOTALL 추가하면 줄바꿈도 매칭
            re.search(r"\[RECOMMEND:\s*(.*?)\]", text, re.DOTALL)
            → "ID1,\nID2,\nID3" ✅
            그래서 re.DOTALL 추가가 필요합니다! 😊
            '''
            # 매칭 데이터 텍스트 읽기
            recommend_match = re.search(r"\[RECOMMEND:\s*(.*?)\]", answer, re.DOTALL)
            if recommend_match:
                raw_ids = re.split(r"[,\s]+", recommend_match.group(1))
                # ID만 빼서 별도 변수에 저
                ids = [i.strip() for i in raw_ids if i.strip()]
                print(f"🔍 [API] 파싱된 IDs: {ids}")  # 디버깅용
                # answer = re.sub(r"\[RECOMMEND:.*?\]", "", answer).strip()
                # ㄴ 텍스트만 골라서 지움 → 그 자리에 줄바꿈이 남아 빈 줄이 됨
            # [RECOMMEND: ...] 태그 + 그 줄 전체(앞 줄바꿈까지) 제거
            # 그래야 빈 줄이 안 남음
            # 같은 텍스트에서 [RECOMMEND] 태그 제거
                answer = re.sub(r"\n*\[RECOMMEND:.*?\]\n*", "\n\n", answer).strip()
                # ㄴ \n*는 "줄바꿈이 0개 이상"이라는 뜻이에요. 앞뒤로 줄바꿈이 몇 개가 있든 다 잡아서 통째로 제거하고, 
                # 깔끔한 줄바꿈 1개("\n")로 대체.
            # re.sub(r"\n*\[RECOMMEND:.*?\]\n*", "\n\n", answer)
            #        └───── 잡는 범위 ───────┘      └─┘
            #                                       └ 이걸로 대체
            # 즉 "잡은 부분을 지우고 그 자리에 깔끔한 줄바꿈 2개를 새로 넣는" 동작이에요. 
            # 결과적으로 정책명 줄과 안내 줄이 줄바꿈 2개 차이로 붙어있게 됩니다 (= 빈 줄 0개).
            
            else:
                # 2순위: 텍스트 내 ID 패턴 추출
                ids = re.findall(r"\b(20\d{18})\b", answer)
                if ids:
                    print(f"⚠️ [API] RECOMMEND 태그 없음 → ID fallback 추출: {ids}")

            if ids:
                valid_ids = set(await filter_valid_ids(ids, include_expired=include_expired))
                ids = [i for i in ids if i in valid_ids]
                print(f"🎯 [API] 최종 추천 ID: {ids}")
                cards = await fetch_policies_by_ids(ids, include_expired=include_expired)
            else:
                print("⚠️ [API] 추천 ID 없음 (카드 0장)")
        else:
            print("💬 [API] 추가 질문 모드 → 카드 미렌더링")

        print(f"✅ [API] 완료 | 카드: {len(cards)}개 | is_clarifying: {is_clarifying}")
        return ChatResponse(
            answer=answer,
            policyIds=[c.id for c in cards],
            domain=domain,
            cards=cards,
            is_clarifying=is_clarifying,
            candidateIds=[],
            chips=chips,
        )
        
    except Exception as e:
        print(f"❌ [API] 치명적 오류: {e}")
        import traceback; traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# 서버 상태 확인용 엔드포인트
@router.get("/health")
async def health():
    return {"status": "ok", "service": "SPARKY AI Server"}
