# Ollama + GPT 둘 다 사용 가능함

import os, re
import traceback  # 예외(에러)가 발생했을 때 어디서 어떻게 났는지 자세히 출력해주는 도구로 파이썬 표준 라이브러리에 들어 있는 모듈
from cachetools import TTLCache
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from services.rag_service import get_context, get_context_for_condition_change
from langchain_core.messages import HumanMessage, AIMessage
from services.rag_service import classify_domain_simple

# 모듈 레벨 변수 (전역). 30분 TTL, 최대 1000개 세션
# 캐시 인스턴스 정의(조건 변경 지역 선택 후 도메인 다시 선택 시 문제 발생 해 캐시 정보 추가)
_session_profile_cache = TTLCache(maxsize=1000, ttl=1800)

# main.py 호환용 변수
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
#                             ↑ .env에서 읽어옴    ↑ .env에 없을 때 기본값
OLLAMA_MODEL    = os.getenv("OLLAMA_MODEL", "gemma3:4b") 
_BASE_HEADERS   = {
    "Content-Type": "application/json",
    "ngrok-skip-browser-warning": "true",
}

REGION_KR = {
    "seoul": "서울", "busan": "부산", "daegu": "대구",
    "incheon": "인천", "gwangju": "광주", "daejeon": "대전",
    "ulsan": "울산", "sejong": "세종", "gyeonggi": "경기",
    "gangwon": "강원", "chungbuk": "충북", "chungnam": "충남",
    "jeonbuk": "전북", "jeonnam": "전남", "gyeongbuk": "경북",
    "gyeongnam": "경남", "jeju": "제주"
}

GENDER_KR = {
    "male": "남성",
    "female": "여성",
    "none": "",          # "선택 안 함"일 경우
}

# ─── "마지막 답변 우선" 추출용 키워드 상수 ───
EMPLOYMENT_KEYWORDS = ["미취업", "재직", "구직", "이직"]

# 사용자 발화 키워드 — '전국'은 거주지가 아닌 검색 범위 의향이라 리스트에 포함
'''
용도: 사용자가 대화 중 입력한 지역 의향 감지
사용자 발화 키워드로 '전국'도 필요
예: 사용자가 "전국 정책도 봐주세요"라고 말하면 매칭
"전국"이 필요한 이유: 사용자는 거주 지역과 별개로 "전국 단위 정책"을 원한다고 표현할 수 있어요. 
이건 거주지가 아니라 검색 범위 의향이에요.
'''
# "이게 어떤 지역인가"를 직접 가리키는 단어
# _latest_user_value에서도 재사용 가능 (사용자의 마지막 지역 발화 추출)
REGION_KEYWORDS = [
    "서울", "부산", "대구", "인천", "광주", "대전",
    "울산", "세종", "경기", "강원", "충북", "충남",
    "전북", "전남", "경북", "경남", "제주", "전국",
]

# 두 곳에서 공유
INCOME_KEYWORDS = [
    "중위소득", "중위", "50%", "100%", "제한 없음", "이하", "모름",
    "중간", "저소득", "소득층", "무관", "모르", "중간 소득",
    "소득 무관", "잘 모",
]

INTEREST_KEYWORDS = [
    "주거", "금융", "교육", "취업", "일자리",
    "문화", "복지", "참여권리", "참여", "권리",
]

# ─── 조건 변경용 정규화 헬퍼 ───
# 텍스트에서 "재직"/"미취업" 카테고리를 추출. 모호하면 None.
def _normalize_employment(text: str) -> str | None:
    if not text:
        return None
    if "미취업" in text or "구직" in text:
        return "미취업"
    if "재직" in text or "근로 중" in text or "이직" in text:
        return "재직"
    return None

# 텍스트에서 소득 카테고리를 추출. "중위"만 있으면 None(모호) 반환.
def _normalize_income(text: str) -> str | None:
    if not text:
        return None
    if "무관" in text or "모름" in text or "모르" in text or "제한 없음" in text:
        return "무관"
    if "50%" in text or "50 %" in text or "저소득" in text:
        return "50%"
    if "100%" in text or "100 %" in text or "중간" in text:
        return "100%"
    return None

# 질문 재탐식 시 도메인 선택 후 조건 변경 하는 경우 관심 분야(도메인)은 최근 껄로 가져오기 위한 코드
# history에서 사용자가 가장 최근에 선택한 도메인(분야)을 반환. 없으면 None.
# classify_domain_simple은 이미 정의돼 있으므로 그대로 재사용.
def find_last_user_domain(history) -> str | None:
    """
    history에서 사용자가 가장 최근에 선택한 도메인(분야)을 반환.
    단, "조건 변경" 발화 이후의 사용자 메시지(예: "취업 상태", "재직 중")는
    조건 변경 흐름의 답변이지 도메인 선택이 아니므로 제외한다.
    """
    # 가장 최근의 "조건 변경" 사용자 발화 위치 찾기
    last_change_idx = -1
    for i, m in enumerate(history):
        if getattr(m, "role", "") == "user" and "조건 변경" in m.content:
            last_change_idx = i

    # "조건 변경" 이전까지의 메시지만 도메인 후보로 사용
    # (조건 변경이 없으면 전체 history 사용)
    search_history = history[:last_change_idx] if last_change_idx >= 0 else history

    for m in reversed(search_history):
        if getattr(m, "role", "") != "user":
            continue
        d = classify_domain_simple(m.content)
        if d:
            return d
    return None

def _latest_user_value(history, current_question: str, keywords: list[str]) -> str:
    """
    history(대화 이력) + current_question(현재 턴 입력)에서
    keywords와 매칭된 가장 최신 사용자 발화를 반환한다.
    매칭 없으면 빈 문자열.
    """
    msgs = [m.content for m in history
            if getattr(m, "role", "") == "user"] + [current_question]
    for content in reversed(msgs):
        if any(k in content for k in keywords):
            return content
    return ""

async def close_http_client():
    pass  # GPT 사용 시 별도 클라이언트 없으므로 빈 함수

# ========== 모델 설정 ==========
# GPT 모델
llm_gpt = ChatOpenAI(
    model="gpt-4o-mini",
    openai_api_key=os.getenv("GPT_API_KEY"),
    temperature=0
)


llm_ollama = ChatOllama(
    model=os.getenv("OLLAMA_MODEL", "gemma3:4b"),
    base_url=OLLAMA_BASE_URL,
    temperature=0
)

# .env의 USE_MODEL 값으로 선택 (기본값: gpt) / 어떤 모델 쓸지 환경변수로 선택
USE_MODEL = os.getenv("USE_MODEL", "gpt")
llm = llm_gpt if USE_MODEL == "gpt" else llm_ollama

# ========== 프롬프트 ==========
# 시스템 프롬프트 (prompt = ChatPromptTemplate.from_messages([...]))위치: llm_service.py 상단, 모듈 로드 시 한 번 정의
# 프롬프트 (청년 정책용)
prompt = ChatPromptTemplate.from_messages([
    ("system", """당신은 청년 정책 안내 챗봇입니다.

[사용자 기본 정보]
나이: {user_age}세, 지역: {user_region}, 성별: {user_gender}
위 기본 정보는 답변에서 다시 언급하지 마세요.

[최우선 규칙]
대화 기록({history})을 반드시 먼저 확인하세요.
이미 답한 정보는 절대 다시 묻지 마세요.

[탐색 규칙]
아래 정보를 모두 파악하기 전에는 절대로 정책을 안내하지 마세요.
반드시 한 가지씩만 질문하세요.
이미 말한 정보는 다시 묻지 마세요.
아직 파악되지 않은 정보만 질문하세요.
반드시 아래 공통 정보를 모두 파악한 후에만 추가 질문으로 넘어가세요.
공통 정보가 하나라도 없으면 추가 질문 절대 금지.
공통 정보 4가지(관심 분야/취업 상태/지역/소득)가 모두 확인되기 전에는
분야별 추가 질문(거주 형태, 이직 희망 등)을 절대 하지 마세요.
사용자가 "주거", "취업", "일자리", "금융", "교육", "복지", "문화" 같은 단일 단어를 답하면 해당 분야를 관심 분야로 확정하고
절대 관심 분야 질문을 다시 하지 마세요

공통 정보 (반드시 먼저 수집)

- 관심 분야: 이미 대화에서 언급된 경우 다시 묻지 마세요. 언급되지 않은 경우에만 다음 문장만 그대로 출력하세요. 앞뒤로 어떤 말도 추가하지 마세요.
  "주거/취업(일자리)/금융/교육/복지·문화·참여권리 중 어떤 분야에 관심 있으신가요?"

- 취업 상태: 다음 문장만 그대로 출력하세요.
  "정책별 자격조건 확인을 위해 현재 근로 상태를 알려주세요. 재직 중(이직 준비 포함) / 미취업(구직 중 포함)"

- 소득 수준: 반드시 다음 문장만 그대로 출력하세요.
  "정책에 따라 소득 기준이 적용됩니다. 현재 가구 소득이 어느 정도 되시나요?
  중위소득 50% 이하 (저소득층) /
  중위소득 100% 이하 (중간 소득층) /
  소득 무관 (소득 조건 없이 신청 원함 또는 모름)"

  사용자 답변 처리 규칙 (반드시 이 표대로만 행동, 표에 없는 행동은 모두 금지):
    - "50%" 또는 "저소득층" 포함 → 50% 이하로 인식, 다음 단계 진행
    - "100%" 또는 "중간 소득층" 포함 → 100% 이하로 인식, 다음 단계 진행
    - "소득 무관", "모름", "무관", "모르겠다" 중 하나 → 소득 무관으로 인식, 다음 단계 진행
    - "중위" 또는 "중위소득"만 단독 입력 → 다음 문장만 출력하고 멈춤: "중위소득 50% 이하 또는 중위소득 100% 이하 중 하나를 선택해 주세요."
    - 위 케이스에 모두 해당 안 됨 → 다음 문장만 출력: "중위소득 50% 이하 / 중위소득 100% 이하 / 소득 무관 중 하나로 답해 주세요."

  사용자 의도를 추측하거나 확인 질문을 던지는 행동은 금지합니다.

[관심 분야 확정 후 안내 규칙]
대화 전체에서 단 한 번만 출력하세요. 이미 안내했다면 절대 반복 금지.
사용자 답변이 "문화" 또는 "참여" 또는 "참여권리"를 포함한 경우, 다음 공통 정보 질문(취업 상태)을 출력하기 직전에 아래 안내 문장을 먼저 한 줄 출력하세요.
  - "문화" 포함 시: "문화 분야는 '복지·문화·참여권리' 카테고리에 포함돼요. 관련 정책으로 찾아드릴게요!"
  - "참여" 또는 "참여권리" 포함 시: "참여권리 분야는 '복지·문화·참여권리' 카테고리에 포함돼요. 관련 정책으로 찾아드릴게요!"
안내 문장 출력 후 줄바꿈을 한 번 넣고, 곧바로 취업 상태 질문 문장을 이어서 출력하세요.
사용자 답변이 "주거", "취업", "일자리", "금융", "교육", "복지" 중 하나만 포함한 경우에는 안내 없이 바로 다음 질문으로 넘어가세요.

공통 정보 모두 수집 완료 후에만 아래 추가 질문 진행
관심 분야가 주거인 경우 추가 질문
- "현재 거주 형태가 전세/월세/자가 중 어떻게 되시나요?" 라고만 질문하세요
- "주택을 소유하고 계신가요? (있음/없음)" 라고만 질문하세요
- "현재 대출이 있으신가요? (있음/없음)" 라고만 질문하세요

관심 분야가 금융인 경우 추가 질문
- "월 저축 가능 금액이 어떻게 되시나요?" 라고만 질문하세요

관심 분야가 취업인 경우 추가 질문
- 미취업인 경우: "취업 준비를 시작한 지 얼마나 되셨나요? (6개월 미만/6개월 이상/1년 이상)" 라고만 질문하세요
- 재직 중인 경우: "현재 이직을 희망하시나요? (네/아니오)" 라고만 질문하세요

관심 분야가 복지·문화·참여권리인 경우 추가 질문
- "어떤 분야가 궁금하신가요? (건강·의료 / 문화·여가 / 심리상담 / 사회참여 중 선택)" 라고만 질문하세요

[답변 규칙]
모든 정보 확인 후 참고 자료 기반으로만 답변하세요.
참고 자료 개수를 내부적으로 파악하세요. (이용자에게 개수 언급 금지)
반드시 이용자가 선택한 관심 분야와 관련된 정책만 안내하세요.
관심 분야와 무관한 정책은 절대 안내하지 마세요.

참고 자료 5개 이상:
  "조건에 맞는 정책 중 가장 적합한 정책을 안내해드리겠습니다." 안내 후
  사용자 조건(나이/지역/소득/관심 분야)에 가장 적합한 정책 최대 5개를
  적합도 기준(참고 자료 순서 아님)으로 선별해서 추천하세요.
  적합한 정책이 적으면 적은 수만 출력해도 됩니다.

참고 자료 1~4개: 바로 추천 (적합한 것만, 무관한 정책 제외)
참고 자료 0개 또는 관심 분야와 무관한 정책만 있는 경우: "조건에 맞는 정책을 찾지 못했습니다." 안내 후 아래 순서로 조건 완화 질문
  → 지역 조건 있으면: "전국 정책도 포함해서 찾아볼까요?"
  → 소득 조건 있으면: "소득 조건을 넓혀서 찾아볼까요?"
  → 그래도 없으면: "다른 분야도 함께 찾아볼까요?"
  → 동의하면 조건 완화 후 재검색, 거절하면 대화 종료
  
정책의 "분류" 필드는 "대분류 > 소분류" 형식입니다. 
대분류에는 여러 도메인이 묶여 있을 수 있으므로 (예: "금융･복지･문화"),
실제 도메인 판단은 반드시 다음 둘을 함께 봐야 합니다:
  1) 소분류 (>의 오른쪽). 예: "예술인지원" → 문화/예술
  2) 정책명·지원내용·설명에 사용된 핵심 어휘
대분류에 사용자 관심 분야 단어가 포함돼 있더라도, 소분류와 본문이 다른 도메인을 가리키면 추천에서 제외하세요.
판단이 모호하면 추천에서 제외하세요. 잘못된 추천을 하느니 적게 추천하는 편이 낫습니다.

예시:
- 분류 "금융･복지･문화 > 예술인지원" + 본문에 "문화예술", "문화창작" 
  → 사용자가 "금융" 선택했으면 제외
- 분류 "금융･복지･문화 > 취약계층 및 금융지원" + 본문에 "자산 형성", "재정 교육"
  → 사용자가 "금융" 선택했으면 추천  
  
[정책 추천 출력 형식]
정책 추천은 [참고 자료]에 실제로 들어온 정책에 한해서만 가능합니다.
참고 자료가 비어있거나 관심 분야와 관련된 정책이 없을 때는 "조건에 맞는 정책을 찾지 못했습니다." 한 문장만 출력하고, [답변 규칙]의 조건 완화 질문 단계로 넘어가세요. 이 경우 정책명을 만들어내거나 추측해서 출력하지 마세요.

참고 자료에 관심 분야 정책이 있는 경우에만 다음 형식으로 답변하세요.

  정책명: <정책명1>
  정책명: <정책명2>
  [RECOMMEND: <정책ID1>, <정책ID2>, <정책ID3>]
  
  다른 분야 정책이 궁금하시면 "다른 정책 추천"이라고 말씀해 주세요.

[RECOMMEND]와 안내 문구 사이에는 정확히 빈 줄 하나만 두세요. 그 외 위치엔 빈 줄을 추가하지 마세요.

위 <...> 표기는 자리 표시자입니다. 출력에는 <...> 그대로가 아니라 참고 자료의 실제 정책명·정책ID 값으로 치환해서 채워야 합니다.
"정책ID1", "정책ID2", "(정책명만)" 같은 자리 표시 문구가 출력에 그대로 등장하면 형식 오류로 간주됩니다.


[정책명 정확 복사 규칙 — 매우 중요]
정책명은 [참고 자료]의 "정책명: ..." 라인에서 한 글자도 빠짐없이 그대로 복사해야 합니다.
다음 행위는 절대 금지:
- "(1차)", "(2차)" 같은 차수 접두사 생략 금지
  잘못된 예: "2026 광주청년 구직활동수당 및 활동지원사업"
  올바른 예: "(1차) 2026 광주청년 구직활동수당 및 활동지원사업"
- 띄어쓰기·기호·숫자 변형 금지 (예: "2026" ↔ "2026년", "[남구]" 생략 등)
- 비슷한 정책 여러 개를 하나로 통합·요약 금지
- 정책명 일부만 추출·축약 금지
같은 사업의 차수가 여러 개(1차/2차/3차/4차)면 사용자에게 추천하고 싶은 차수를 각각 별도 줄로 출력하세요.
참고 자료의 정책명을 그대로 복사하는 것이 핵심이며, LLM의 자체 판단으로 정리하지 마세요.

[지역 정책 안내 규칙]
사용자 거주지({user_region})는 첫 단계에서 이미 수집되었습니다.
거주지를 골랐다는 것은 곧 그 지역 정책을 원한다는 의사 표시로 간주하세요.
"지역 정책을 원하시나요, 아니면 전국 정책도 괜찮으신가요?" 같은 별도 확인 질문은 절대 던지지 마세요.

기본 동작:
→ 참고 자료에 {user_region} 정책이 1개 이상 있으면, 그 지역 정책을 즉시 [정책 추천 출력 형식]으로 안내하세요.
→ 참고 자료에 {user_region} 정책이 0개일 때만, [답변 규칙]의 조건 완화 단계로 넘어가
   "{user_region} 지역 정책 정보가 없습니다. 전국 정책도 포함해서 찾아볼까요?" 질문하세요.

이미 정책 추천을 마친 뒤, 사용자가 직접 "전국 정책도 보여줘", "다른 지역도 알려줘" 같이
명시적으로 확장 의사를 밝히면 그때 전국 정책을 포함해 안내하세요.

[대화 재시작 및 재질문 처리]
이미 한 번 정책 추천을 완료한 후, 사용자가 새 분야(주거/취업/금융/교육/복지·문화·참여권리)를 언급하며 다른 정책을 요청하면:
→ 취업 상태/지역/소득/관심 분야를 절대 다시 묻지 마세요.
→ 기존 대화에서 이미 수집된 프로필을 그대로 재사용해서 바로 [정책 추천 출력 형식]으로 답하세요.
→ 관련 분야가 대화에 명시되지 않은 경우에만 "다른 정책이 궁금하신가요? 주거/취업(일자리)/금융/교육/복지·문화·참여권리 중 말씀 부탁드립니다." 라고 한 번만 물어보세요.

"처음부터", "다시", "리셋" 같은 명시적 초기화 요청이 있을 때만
→ "네, 다른 정책을 찾아드릴게요." 안내 후 처음부터 다시 질문.

[절대 금지]
질문 앞에 "관심 분야:", "취업 상태:", "소득 수준:" 등 레이블 붙이기 금지
번호목록 사용 금지
숫자 번호(1. 2. 3.) 사용 금지
마크다운/번호목록/이모지 사용 금지
URL 임의 생성 또는 수정 금지
참고 자료에 없는 내용 추가 금지
추가 설명 금지
URL을 텍스트 답변에 절대 출력하지 마세요. URL은 카드 UI에서 따로 표시됩니다.
"신청 URL", "지원 내용", "신청 방법", "신청 기한" 등 정책명 외 어떤 항목도 텍스트에 포함하지 마세요.
참고 자료가 몇 개든 반드시 최대 5개만 선택해서 추천하세요.
절대로 5개를 초과해서 출력하지 마세요.

[참고 자료]
{context}
위 참고 자료를 답변에 그대로 출력하지 마세요.
참고 자료가 비어있으면 [정책 추천 출력 형식]에 따라 "조건에 맞는 정책을 찾지 못했습니다." 한 문장만 출력하세요.
참고 자료에 정책이 있을 때는 [정책 추천 출력 형식]의 출력 형식에 따라 답변하세요.
    """),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{question}"),
])

# ========== 대화 기록 ==========
store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

# ========== chain 구성 헬퍼 함수 ==========
def get_question(x):
    return x["question"]

def get_history(x):
    return x.get("history", []) # 없으면 [] 빈 리스트 (대화 기록용)
# ㄴ 대화 기록이 없으면 빈 리스트로 시작

# get_user_age가 현재 "youth_35_up" 문자열을 그대로 반환해서, 
# 프롬프트에 나이에 youth_35_up세 같은 이상한 문자열이 들어가 작업
AGE_KR = {
    "youth_19_24": "19~24세",
    "youth_25_29": "25~29세",
    "youth_30_34": "30~34세",
    "youth_35_up": "35세 이상",
}

def get_user_age(x):
    return x.get("user_age", "") # 없으면 빈 문자열 "" (텍스트 정보용)
  
def get_user_region(x):
    region = x.get("user_region", "")
    return REGION_KR.get(region, region)  # 한글로 변환

def get_user_gender(x):
    gender = x.get("user_gender", "")
    return gender if gender else "미입력"  # 없으면 "미입력"

# ========== chain 구성 ==========
chain = (
    {   
        "context":     RunnablePassthrough(), 
        "question":    RunnableLambda(get_question),  
        "history":     RunnableLambda(get_history),     
        "user_age":    RunnableLambda(get_user_age), 
        "user_region": RunnableLambda(get_user_region),  
        "user_gender": RunnableLambda(get_user_gender)  
    }   
    | prompt  
    | llm   
    | StrOutputParser()  
)

conversational_chain = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="question",
    history_messages_key="history"
)

# ========== chat.py 호환용 함수 ==========
async def classify_domain(question: str):
    """chat.py 호환 - 키워드 방식"""
    from models.schemas import PolicyDomain
    domain_str = classify_domain_simple(question)
    mapping = {
        "주거": PolicyDomain.housing,
        "취업": PolicyDomain.employment,
        "금융": PolicyDomain.finance,
        "교육": PolicyDomain.education,
        "복지": PolicyDomain.welfare,
    }
    return mapping.get(domain_str, PolicyDomain.unknown)

async def expand_query(question: str, history=None) -> str:
    """chat.py 호환 - 쿼리 확장 (본인 방식은 history_text 누적)"""
    if not history:
        return question
    history_text = " ".join([m.content for m in history if m.role == "user"])
    return history_text + " " + question

async def generate_answer(
    question: str,
    context_docs: list,
    conversation_history: list,
    user_profile,
    domain,
    total_count: int = 0,
    turn_count: int = 1,
    session_id: str | None = None,    
) -> tuple[str, bool, str | None]:
  
    print(f"🔍 [LLM] generate_answer 시작")
    
    if session_id:
        cached = _session_profile_cache.get(session_id, {})
        if "region" in cached:
            user_profile.region = cached["region"]
            print(f"🔄 [세션] region 복원: {cached['region']}")
    # ─── 신규 끝 ───
    
    print(f"🔍 [LLM] history 개수: {len(conversation_history)}개")
    
    print(f"🔍 [LLM] history 내용: {[m.content for m in conversation_history]}")
    print(f"🔍 [LLM] history 전체내용: {[m.content for m in conversation_history]}")
       
    # history_text 직접 구성
    history_text = " ".join([
        m.content for m in conversation_history
    ]) if conversation_history else ""

    full_text = history_text + " " + question
  
    # get_context 직접 호출(정상 흐름: 5개 정보 모은 후 첫 추천)
    context = get_context({
        "question":    question,
        "user_region": user_profile.region,
        "user_age":    user_profile.ageGroup,
        "full_text":   full_text,
        "history":     conversation_history,
    })  
    print(f"🔍 [LLM] context 길이: {len(context)}")
    print(f"🔍 [LLM] context 전체:\n{context}\n{'='*60}") 


    # 환각 방지 안전장치 포함(할루시네이션) 
    # 공통 정보 4가지 다 수집됐는데 매칭 정책 0건 → LLM에 그대로 넘기면 정책을 지어내는 환각 발생
    # my_dict.get(찾고 싶은 키, 못 찾았을 때 쓸 기본값)
    user_region_kr = REGION_KR.get(user_profile.region, user_profile.region)
    

    user_only_text = " ".join(
        [m.content for m in conversation_history
         if getattr(m, "role", "") == "user"]
        + [question]
    )

    last_bot_msg = ""     # 빈 문자열로 초기화
    for m in reversed(conversation_history):    # 대화 기록을 뒤에서부터 순회
        if getattr(m, "role", "") == "assistant":   # 봇(assistant) 메시지 발견하면
            last_bot_msg = m.content    # 그 내용을 저장하고
            break     # 즉시 종료
        
    # ─── 소득 단계 한정: 사용자가 의미를 모른다/설명 요청 시 풀어서 안내 ───
    INCOME_HELP_KEYWORDS = [
        # "뭐?" 류 의미 질문
        "뭐예요", "뭔가요", "뭔지", "뭐지", "뭐야", "뭔데",
        "무슨 뜻", "무슨 의미", "무슨 말", "무슨 소리",
        "어떤 의미", "어떤 뜻", "뜻이",
        "처음 들", "들어본 적",
        # "모르겠다" 류
        "잘 모르", "모르겠", "이해 안", "이해가 안", "이해 못",
        "감이 안", "감 안",
        # "어렵다" 류
        "어렵", "복잡", "헷갈",
        # "설명해줘" 류
        "설명", "알려줘", "알려주세", "알려 주세",
    ]
    # 직전 봇 메시지가 소득 질문이었을 때만 발동 (다른 턴에서 오발동 방지)
    asking_income_just_before = any(k in last_bot_msg for k in [
        "중위소득 50%", "중위소득 100%", "소득 무관", "소득 기준이 적용",
    ])
    user_confused = any(k in question for k in INCOME_HELP_KEYWORDS)
    
    # 직전 봇 메시지가 소득 질문 + 사용자가 헷갈려할 때 → 즉시 설명
    if asking_income_just_before and user_confused:
        return (
            "중위소득 기준을 풀어서 설명드릴게요.\n\n"
            "• 중위소득 50% 이하 — 월 소득 약 110만원 이하 (1인 가구 기준). "
            "저소득층 대상 정책이 해당돼요.\n"
            "• 중위소득 100% 이하 — 월 소득 약 220만원 이하 (1인 가구 기준). "
            "중간 소득층까지 지원받는 정책이 해당돼요.\n"
            "• 소득 무관 — 소득 조건 없이 누구나 신청 가능한 정책이에요.\n\n"
            "이 중 어디에 해당하시나요? "
            "정확히 모르겠다면 '소득 무관'을 선택해도 괜찮아요.",
            True,
            None,
        )    
    
    # ========== (개인 수정 예정) 종료 의사 감지 ==========

    has_employment = any(k in user_only_text for k in EMPLOYMENT_KEYWORDS)
    has_interest   = any(k in user_only_text for k in INTEREST_KEYWORDS)

    has_region = bool(user_profile.region) or any(
        k in user_only_text for k in
        REGION_KEYWORDS + ["지역", "원해", "어디나", "상관없",
                        user_profile.region, user_region_kr]
    )
        
    has_income     = any(k in user_only_text for k in INCOME_KEYWORDS)
    all_info_collected = has_employment and has_interest and has_region and has_income
    

    # 정보 수집 단계: LLM 없이 즉시 반환 (속도 최적화) # 여기서부터 추가
    if not all_info_collected:
        # last_bot_msg는 함수 상단에서 이미 계산됨 (중복 제거)

        if not has_interest: 
            return (
                "어떤 분야 정책을 추천해드릴까요?\n"
                "주거 / 취업(일자리) / 금융 / 교육 / 복지·문화·참여권리 중 하나를 알려주세요.",
                True,
                None,
            )
        # 관심 분야 안내 (문화/참여권리) - 아직 취업상태 미수집 시 함께 출력
        interest_notice = ""
        if "문화" in question and "문화 분야는" not in last_bot_msg:
            interest_notice = "문화 분야는 '복지·문화·참여권리' 카테고리에 포함돼요. 관련 정책으로 찾아드릴게요!\n"
        elif any(k in question for k in ["참여권리", "참여", "권리"]) and "참여권리 분야는" not in last_bot_msg:
            interest_notice = "참여권리 분야는 '복지·문화·참여권리' 카테고리에 포함돼요. 관련 정책으로 찾아드릴게요!\n"
        
        if not has_employment:
            return (
                interest_notice + "정책별 자격조건 확인을 위해 현재 근로 상태를 알려주세요.",
                True,
                "employment"
            )
        if not has_region:
            region_display = REGION_KR.get(user_profile.region, user_profile.region) or "거주 지역"
            return (
                f"{region_display} 지역 정책을 원하시나요, 아니면 전국 정책도 괜찮으신가요?",
                True,
                None,
            )
        if not has_income:
            
            # 표준 소득 질문 
            return (
                "정책에 따라 소득 기준이 적용됩니다. 현재 가구 소득이 어느 정도 되시나요?\n"
                "중위소득 50% 이하 (저소득층) /\n"
                "중위소득 100% 이하 (중간 소득층) /\n"
                "소득 무관 (소득 조건 없이 신청 원함 또는 모름)",
                True,
                None,
            )
     
    # ========== 재질문 감지 (정보 수집 완료 후 새 도메인 요청) ==========
    if all_info_collected:
        prev_was_recommendation = any(k in last_bot_msg for k in [
            "정책명:", "[RECOMMEND:", "조건에 맞는 정책 중 가장 적합한"
        ])
        # 직전 봇이 "어떤 분야?" 묻는 중인지 (다른 정책 → 분야 재질문 → 사용자 답변 케이스)
        prev_was_domain_ask = any(k in last_bot_msg for k in [
            "어떤 분야에 관심",
            "어떤 분야 정책을", 
            "주거/취업(일자리)/금융/교육/복지·문화·참여권리 중",
            "주거 / 취업(일자리) / 금융 / 교육 / 복지·문화·참여권리 중",
        ])
        # 히스토리 어딘가에 과거 추천이 있었는지 (2-turn 이상 떨어져도 잡기)
        any_past_recommendation = any(
            any(k in m.content for k in ["정책명:", "[RECOMMEND:"])
            for m in conversation_history
            if getattr(m, "role", "") == "assistant"
        )
        # 1) 조건 변경 의도 우선 감지
        wants_condition_change = any(k in question for k in [
            "조건 변경", "조건 바꿔", "조건 바꾸", "조건 다시", "조건 수정",
            "다시 입력", "조건 고치"
        ])
        if prev_was_recommendation and wants_condition_change:
            print("🔄 [LLM] 조건 변경 요청 감지")
            return (
                "어떤 조건을 바꾸고 싶으세요?\n"
                "취업 상태 / 소득 / 지역 / 관심 분야 중 말씀해 주세요.",
                True,
                None,
            )
        
        # 1-A) ""어떤 조건을 바꾸고 싶으세요?" 답변 감지 → 새 값 요청
        prev_asked_which_condition = "어떤 조건을 바꾸고 싶으세요" in last_bot_msg
        if prev_asked_which_condition:
            if any(k in question for k in ["취업", "근로", "재직", "구직"]):
        # 이전 취업 상태를 추출해서 안내문에 명시
                prior_emp_text = _latest_user_value(
                    conversation_history, "", EMPLOYMENT_KEYWORDS)
                prior_emp = _normalize_employment(prior_emp_text)
                if prior_emp == "재직":
                    msg = (
                        "현재는 '재직 중 (이직 준비 포함)'으로 설정되어 있어요.\n"
                        "새로운 취업 상태를 선택해 주세요."
                    )
                elif prior_emp == "미취업":
                    msg = (
                        "현재는 '미취업 (구직 중 포함)'으로 설정되어 있어요.\n"
                        "새로운 취업 상태를 선택해 주세요."
                    )
                else:
                    msg = (
                        "새로운 취업 상태를 알려주세요.\n"
                        "재직 중 (이직 준비 포함) / 미취업 (구직 중 포함)"
                    )
                print(f"🔧 [LLM] 조건 변경 - 취업상태 (이전: {prior_emp})")
                return (msg, True, "employment")
            if "소득" in question:
                # 이전 소득 값을 추출해서 안내문에 명시
                prior_income_text = _latest_user_value(
                    conversation_history, "", INCOME_KEYWORDS)
                prior_income = _normalize_income(prior_income_text)
                prior_label_map = {
                    "50%": "중위소득 50% 이하 (저소득층)",
                    "100%": "중위소득 100% 이하 (중간 소득층)",
                    "무관": "소득 무관",
                }
                if prior_income in prior_label_map:
                    head = (
                        f"현재는 '{prior_label_map[prior_income]}'으로 설정되어 있어요.\n"
                        "새로운 가구 소득을 선택해 주세요."
                    )
                else:
                    head = "새로운 가구 소득을 알려주세요."
                msg = (
                    f"{head}\n"
                    "중위소득 50% 이하 (저소득층) / 중위소득 100% 이하 (중간 소득층) / 소득 무관"
                )
                print(f"🔧 [LLM] 조건 변경 - 소득 (이전: {prior_income})")
                return (msg, True, None)
            if any(k in question for k in ["지역", "거주", "사는"]):
                print("🔧 [LLM] 조건 변경 - 지역")
                return (
                    "새로운 거주 지역을 알려주세요.\n"
                    "(서울 / 경기 / 부산 / 인천 / 대구 / 광주 / 대전 / 울산 / 세종 / 강원 / "
                    "충북 / 충남 / 전북 / 전남 / 경북 / 경남 / 제주 중 하나)",
                    True,
                    None,
                )
            if any(k in question for k in ["관심", "분야"]):
                print("🔧 [LLM] 조건 변경 - 관심 분야")
                return (
                    "새로운 관심 분야를 알려주세요.\n"
                    "주거 / 취업(일자리) / 금융 / 교육 / 복지·문화·참여권리 중 하나",
                    True,
                    None,
                )
            # 위 4개 어디에도 안 걸리면 안내 다시
            print("⚠️ [LLM] 조건 변경 - 인식 못함")
            return (
                "어떤 조건을 바꾸고 싶으세요? 취업 상태 / 소득 / 지역 / 관심 분야 중 하나로 말씀해 주세요.",
                True,
                None,
            )
        
        condition_just_changed = False
        
        prev_asked_new_value = any(k in last_bot_msg for k in [
            "새로운 취업 상태를", "새로운 가구 소득을",
            "새로운 거주 지역을", "새로운 관심 분야를",
        ])
        prev_asked_new_value = prev_asked_new_value or (
            "새로운 취업 상태를 선택해 주세요" in last_bot_msg
            or "새로운 가구 소득을 선택해 주세요" in last_bot_msg
        )
        if prev_asked_new_value:
            asked_for_employment = (
                "새로운 취업 상태를" in last_bot_msg
                or "취업 상태를 선택해" in last_bot_msg
            )
            asked_for_income = (
                "새로운 가구 소득을" in last_bot_msg
                or "가구 소득을 선택해" in last_bot_msg
            )

            # 검증: 소득
            if asked_for_income:
                new_income = _normalize_income(question)
                if new_income is None:
                    print("⚠️ [LLM] 소득 모호 → 재질문")
                    return (
                        "조금 더 구체적으로 알려주세요.\n"
                        "중위소득 50% 이하 (저소득층) / 중위소득 100% 이하 (중간 소득층) / 소득 무관 "
                        "중 하나로 말씀해 주세요.",
                        True,
                        None,
                    )

            # 검증: 취업 상태
            if asked_for_employment:
                new_emp = _normalize_employment(question)
                if new_emp is None:
                    print("⚠️ [LLM] 취업상태 모호 → 재질문")
                    return (
                        "조금 더 구체적으로 알려주세요.\n"
                        "재직 중 (이직 준비 포함) / 미취업 (구직 중 포함) 중 선택해 주세요.",
                        True,
                        "employment",
                    )
            
            # 검증 + 갱신: 지역
            asked_for_region = (
                "새로운 거주 지역을" in last_bot_msg
                or "거주 지역을 알려주세요" in last_bot_msg
            )
            # 검증 + 갱신: 관심 분야 (신규 추가)
            asked_for_interest = (
                "새로운 관심 분야를" in last_bot_msg
                or "관심 분야를 알려주세요" in last_bot_msg
            )
            
            # 관심 분야 변경 처리 (지역 처리보다 먼저 또는 나중 어느 쪽이든 OK)
            if asked_for_interest:
                # 사용자 입력에서 도메인 키워드 추출
                new_domain = classify_domain_simple(question)
                if new_domain:
                    print(f"🔧 [LLM] 관심 분야 업데이트: {new_domain}")
                    # question을 새 도메인으로 덮어써서 이후 흐름이 새 도메인으로 처리되게 함
                    question = new_domain
                    condition_just_changed = True
                    # last_domain 검색을 우회하고 직접 새 도메인 사용
                else:
                    print("⚠️ [LLM] 관심 분야 모호 → 재질문")
                    return (
                        "분야를 인식하지 못했어요.\n"
                        "주거 / 취업(일자리) / 금융 / 교육 / 복지·문화·참여권리 중 하나로 입력해 주세요.",
                        True,
                        None,
                    )
            if asked_for_region:
                # REGION_KR을 순회하면서 사용자 입력에 한국어 지역명이 있는지 검사
                # 한글 지명을 영문 코드로 변환
                new_region_code = None
                for code, kr_name in REGION_KR.items():  
                    if kr_name in question:   
                        new_region_code = code  
                        break
                    
                # 프로필에 영어 코드로 저장 ("seoul")
                if new_region_code:
                    user_profile.region = new_region_code   # 프로필 갱신 (핵심)
                    print(f"🔧 [LLM] 지역 업데이트: {new_region_code}")                  
                    # 새 지역으로 context 재계산(조건 변경 전용 함수 사용 → 옛 컨텍스트 차단)
                    
                    # ─── 조건 변경 시 지역 선택 후 도메인 재선택하면 기존 지역의 도메인으로 나와 추가한 코드 
                    # 신규: 세션 캐시에 저장 (다음 요청에서 복원 가능하게) ───
                    # 캐시 저장 로직
                    if session_id:
                        if session_id not in _session_profile_cache:
                            _session_profile_cache[session_id] = {}
                        _session_profile_cache[session_id]["region"] = new_region_code
                        print(f"💾 [세션] region 캐시 저장: {new_region_code}")
                    
                    # 조건 변경용 (검증 스킵 + 깨끗한 쿼리 검색)
                    # _search_and_filter_policies는 get_context와 get_context_for_condition_change 둘이 공유하는 검색 엔진
                    context = get_context_for_condition_change({
                        "question": question,
                        "user_region": user_profile.region, # 새로 업데이트된 값
                        "user_age": user_profile.ageGroup,
                        "history": conversation_history, 
                        # full_text는 의도적으로 안 넘김 (옛 답변이 FAISS 쿼리에 섞이지 않도록)
                    })
                    print(f"🔄 [LLM] 새 지역({new_region_code})으로 context 재계산 완료, 길이: {len(context)}")
                else:
                    print("⚠️ [LLM] 지역 모호 → 재질문")
                    return (
                        "지역을 인식하지 못했어요.\n"
                        "서울 / 경기 / 부산 / 인천 / 대구 / 광주 / 대전 / 울산 / 세종 / "
                        "강원 / 충북 / 충남 / 전북 / 전남 / 경북 / 경남 / 제주 중 하나로 입력해 주세요.",
                        True,
                        None,
                    )                
            
            # 관심 분야 변경(asked_for_interest)으로 이미 처리됐으면 last_domain 검색 우회
            # (이미 question이 새 도메인으로 설정됐으므로 또 덮어쓰지 않음)
            if asked_for_interest and condition_just_changed:
                print(f"✅ [LLM] 새 관심 분야({question})로 즉시 재추천")
                # question은 이미 위에서 새 도메인으로 설정됨, 그대로 사용
            else:
                last_domain = find_last_user_domain(conversation_history)

                if last_domain:
                    print(f"✅ [LLM] 새 조건 값 수신 → 기존 분야({last_domain})로 즉시 재추천")
                    question = last_domain
                    condition_just_changed = True 
                else:
                    print("✅ [LLM] 새 조건 값 수신 → 분야 재질문 (이전 분야 없음)")
                    return (
                        "조건이 업데이트되었어요. 어떤 분야 정책을 추천해드릴까요?\n"
                        "주거 / 취업(일자리) / 금융 / 교육 / 복지·문화·참여권리 중 하나를 알려주세요.",
                        True,
                        None,
                    )
        
        current_domain_kw = classify_domain_simple(question)
        restart_signal = (
            prev_was_recommendation or prev_was_domain_ask or any_past_recommendation
        )
        
        # 추가 정책 추천 요청 시 "다른 정책/분야" 요청인데 도메인 키워드는 없음 → 분야 되묻기
        wants_other = any(k in question for k in [
            "다른 정책", "다른 분야", "다른 거", "다른 것", "또 다른", "다른 추천"
        ])
        if restart_signal and wants_other and not current_domain_kw:
            print("🔀 [LLM] 다른 분야 요청 감지 → 분야 재질문")
            return (
                "어떤 분야 정책을 추천해드릴까요?\n"
                "주거 / 취업(일자리) / 금융 / 교육 / 복지·문화·참여권리 중 하나를 알려주세요.",
                True,
                None,
            )
                           
        if restart_signal and current_domain_kw:
            print(f"🔁 [LLM] 재질문 감지 → 새 도메인({current_domain_kw}) 고지 후 즉시 추천")
            
            # "마지막 답변 우선"으로 최신 프로필 추출
            latest_employment = _latest_user_value(
                conversation_history, question, EMPLOYMENT_KEYWORDS)
            latest_region = _latest_user_value(
                conversation_history, question, REGION_KEYWORDS)
            latest_income = _latest_user_value(
                conversation_history, question, INCOME_KEYWORDS)
            
            # 사용자 프로필 요약 (이용자에게 보여줄 문자열)
            age_kr = AGE_KR.get(user_profile.ageGroup, "")
            region_kr = REGION_KR.get(user_profile.region, user_profile.region)
            gender_kr = GENDER_KR.get(user_profile.gender, "")
            emp_text = latest_employment or ""
            income_text = latest_income or ""
           
            # REGION_KEYWORDS 중 latest_region에 들어간 키워드만 뽑기
            # 새 지역 발화 우선
            # 사용자 발화 전체 문장("부산으로 바꿀게요" 여기서 부산만 추출되게 
            # display_region = latest_region or region_kr  => 이러면 지역명 다 들어가므로
            # 순수 지역명만 추출되게 
            display_region = next(
                (k for k in REGION_KEYWORDS if k in latest_region),
                region_kr,   # 못 찾으면 기본값
            )
            
            # 새 도메인으로는 매칭 정책이 0건인 경우 → 안내 멘트 + 전국 확대 제안을 함께 출력
            if not context.strip():
                print(f"⚠️ [LLM] 재질문({current_domain_kw}) 시 매칭 0건 → 안내 + 전국 확대 제안")
                return (
                    f"기존과 동일한 조건으로 {current_domain_kw} 정책을 찾아드릴게요. "
                    f"조건 변경을 원하시면 \"조건 변경\"이라고 말씀해 주세요.\n\n"
                    f"다만 현재 조건({REGION_KR.get(user_profile.region, user_profile.region)})에서는 "
                    f"맞는 {current_domain_kw} 정책을 찾지 못했어요. "
                    f"전국 정책도 포함해서 찾아볼까요? (네/아니오)",
                    False,
                    None,
                )
            
            # 정책 추가 추천 요청 시 조건 변경이냐 동일 조건이냐에 따라 멘트 상이하게끔 처리
            # 조건 변경 직후면 "변경된 조건으로...", 아니면 "기존과 동일한 조건으로..."
            intro_msg = (
                f"변경된 조건으로 {current_domain_kw} 정책을 찾아드릴게요. "
                if condition_just_changed
                else f"기존과 동일한 조건으로 {current_domain_kw} 정책을 찾아드릴게요. "
            )
            
            # 추천 정책 재질문시 동일한 조건을 요약 상태로 열거하는 방식으로 한다면 필요            
            # profile_parts = [p for p in [age_kr, gender_kr, display_region,  # region_kr → display_region 으로 변경
            #                              emp_text, income_text] if p]
            # profile_summary = ", ".join(profile_parts) if profile_parts else "기존 조건"
            
            # LLM에게 고지 문구 + 추천 + [RECOMMEND:] 태그 의무화
            # 동적 프롬프트 (question = (f"[시스템 지시]..."))
            # 역할: 특수 상황의 추가 지시
            question = (
                f"[시스템 지시]\n"
                f"이전 대화에서 이미 수집된 프로필을 그대로 재사용하세요.\n"
                f"취업 상태/지역/소득/관심 분야를 절대 다시 묻지 마세요.\n"
                # ★★★ 다음 줄들 추가 / 조건 변경 지역 선택 시 환각 증성 방지 위함 ★★★
                f"\n⚠️ 중요: 이전 대화에 등장한 정책명은 모두 무시하세요.\n"
                f"오직 [참고 자료]에 새로 제공된 정책만 사용해서 답변하세요.\n"
                f"참고 자료에 없는 정책명을 절대 만들거나 가져오지 마세요.\n\n"
                f"참고 자료에 정책이 1~2개뿐이라도 그것만 출력하세요.\n\n"
                # ── 변경: 라벨 제거하고 출력 형식만 명시 ──
                # 추천 정책 재질문시 동일한 조건을 요약 상태로 열거하는 방식으로 한다면 필요
                # f"현재 조건({profile_summary})으로 {current_domain_kw} 정책을 찾아드릴게요. "
                f"답변은 다음 형식 그대로 출력하세요. 라벨이나 머리표는 절대 포함하지 마세요:\n\n"
                f"{intro_msg}"   # 조건 변경 여부에 따라 intro_msg라는 변수에 분기된 메시지를 담아둠
                f"조건 변경을 원하시면 \"조건 변경\"이라고 말씀해 주세요.\n\n"
                f"정책명: <정책명1>\n"
                f"정책명: <정책명2>\n"
                f"[RECOMMEND: <정책ID1>, <정책ID2>, ...]\n\n"
                f"원래 사용자 질문: {question}"
                f"위 형식 외 어떤 안내 문장도 출력하지 마세요. "
                f"특히 끝부분에 \"다른 분야 정책이 궁금하시면 '다른 정책 추천'이라고 말씀해 주세요\" 같은 꼬리 안내는 이번 응답에서 절대 추가하지 마세요. "
                f"이미 첫 줄에 '조건 변경' 안내가 있어 중복입니다.\n\n"
            )
    
    if not context.strip() and all_info_collected:

        user_agreed = any(k in question for k in ["네", "좋아요", "그래", "응", "예", "포함"])
        offered_expand_region = "전국 정책도 포함해서 찾아볼까요" in last_bot_msg
        offered_expand_domain = "다른 분야도 함께 찾아볼까요"    in last_bot_msg
        user_declined = any(k in question for k in ["아니오", "아냐", "싫어", "됐어", "괜찮", "노"])
        if offered_expand_region and user_declined:
            return (
                "알겠어요. 다른 분야나 조건으로 다시 시도해보시겠어요?",
                False,
                None,
            )
        elif offered_expand_region and user_agreed:
            # 1차 완화: 지역 필터 해제 후 재조회
            print("🔄 [LLM] 전국 확대 동의 감지 → 지역 필터 해제 후 재조회")
            context = get_context({
                "question":    question,
                "user_region": "",
                "user_age":    user_profile.ageGroup,
                "full_text":   full_text,
                "history":     conversation_history,
            })
            print(f"🔍 [LLM] 재조회 context 길이: {len(context)}")

            # 환각, hallucination 방어 코드 
            if not context.strip():
                print("⚠️ [LLM] 전국 확대 후에도 0건")
                if user_profile.ageGroup == "youth_35_up":
                    return (
                        "선택하신 조건에 맞는 청년정책을 찾지 못했어요. "
                        "청년정책 대부분이 만 19~34세로 한정되어 있어 35세 이상에 "
                        "해당하는 정책이 제한적입니다. 관심 분야를 바꿔보시거나 "
                        "일반 복지정책 안내를 원하시면 말씀해 주세요.",
                        False,
                        None,
                    )
                return (
                    "전국 정책에서도 조건에 맞는 정책을 찾지 못했어요. 다른 분야도 함께 찾아볼까요? (네/아니오)",
                    False,
                    None,
                )
                
            # 정책 추천 재요청 시 
            domain_for_msg = current_domain_kw or "맞춤"
            question = (
                f"[시스템 지시]\n"
                f"이전 대화에서 이미 수집된 프로필을 그대로 재사용하세요.\n"
                f"취업 상태/소득/관심 분야를 절대 다시 묻지 마세요.\n"
                f"답변은 다음 형식 그대로 출력하세요. \"[블록1: ...]\", \"[블록2: ...]\" 같은 메타 라벨이나 머리표는 절대 포함하지 마세요.\n\n"
                f"전국으로 범위를 넓혀서 {domain_for_msg} 정책을 찾았어요. "
                f"조건 변경을 원하시면 \"조건 변경\"이라고 말씀해 주세요.\n\n"
                f"정책명: <정책명1>\n"
                f"정책명: <정책명2>\n"
                f"[RECOMMEND: <정책ID1>, <정책ID2>, ...]\n\n"
                f"원래 사용자 질문: 전국 확대해서 추천해줘"
            )          

        elif offered_expand_domain and user_agreed:
            print("⚠️ [LLM] 분야 확대 동의 → 재시작 안내")
            return (
                "죄송해요, 조건에 맞는 정책을 찾지 못했어요. 페이지를 새로고침해서 다른 조건으로 다시 시도해 주세요.",
                False,
                None,
            )
        
        else:
            print("⚠️ [LLM] 환각 방지: context 비어있고 4가지 정보 수집 완료 → 전국 확대 제안")
            return (
                "조건에 맞는 정책을 찾지 못했어요. 전국 정책도 포함해서 찾아볼까요? (네/아니오)",
                False,
                None,
            )
            
    # lc_history = LangChain 형식으로 변환된 대화 기록 (변환 후)
    lc_history = []   # lc = LangChain
    for m in conversation_history:
        if m.role == "user":
            lc_history.append(HumanMessage(content=m.content)) # SPARKY → LangChain
        elif m.role == "assistant":
            lc_history.append(AIMessage(content=m.content))  # SPARKY → LangChain
    
    # 조건 변경 직후엔 history 초기화
    if condition_just_changed:
        lc_history = []
        print("🧹 [LLM] 조건 변경 직후 → history 비움 (옛 정책 환각 방지)")
    
    full_response = ""
    try:
      
        async for chunk in chain.astream(  
            {
                "question":    question,
                "user_age":    AGE_KR.get(user_profile.ageGroup, ""),
                "user_region": REGION_KR.get(user_profile.region, user_profile.region),
                "user_gender": GENDER_KR.get(user_profile.gender, ""),
                "history":     lc_history,  # 직접 변환한 history
                "context":     context,  # 직접 구성한 context 전달
            },
        ):
            full_response += chunk
            print(f"🔍 chunk: {chunk}")
    except Exception as e:
        print(f"❌ [LLM] astream 오류: {type(e).__name__}: {e}")   
        traceback.print_exc()  
    
        return "오류가 발생했습니다.", False, None 
           
    full_response = re.sub(r'[ \t]+\n', '\n', full_response)   
    full_response = re.sub(r'\n{3,}', '\n\n', full_response)   
    
    print(f"✅ [LLM] 전체 응답: {full_response[:100]}")
    is_clarifying = "[CLARIFYING]" in full_response
    full_response = full_response.replace("[CLARIFYING]", "").strip()

    # ========== 정책명-ID 매칭 검증/복구 ==========
    
    if "정책명:" in full_response and context.strip():
        policy_names = re.findall(r"정책명:\s*([^\n\r]+)", full_response)
        context_blocks = context.split("\n\n")
        matched_ids: list[str] = []
        seen_ids: set[str] = set()
        for raw_name in policy_names[:5]:
            name_clean = raw_name.strip().rstrip(".").rstrip(",")
            raw_name.strip().rstrip(".,")
            if not name_clean:
                continue
            # 정규화 함수: 비교 전에 양쪽을 다 가공해서 사소한 차이 무시
            # LLM이 차수 누락하거나 "2026" → "2026년"으로 살짝 바꿔도 매칭이 되게끔
            def _normalize_name(s: str) -> str:
                """정책명 비교용 정규화. 공백·기호·연도 표기 등 사소한 차이 무시."""
                import re as _re
                # 모든 공백 제거
                s = _re.sub(r"\s+", "", s)
                # 괄호와 그 안의 차수 표시는 유지(중요한 정보)
                # "2026년" → "2026" 통일
                s = s.replace("년", "")
                # 모든 특수문자(괄호 제외) 제거
                s = _re.sub(r"[^\w가-힣()]", "", s)
                return s.lower()
            
            for block in context_blocks:
                # "정책명: XYZ" 라인을 우선 정확 매칭, 실패 시 부분 매칭으로 폴백    
                # 1차: 정확 매칭 ("정책명: " + name 통째 검사)
                # 2차: 부분 매칭 (name이 block 안에 있냐)    
                if f"정책명: {name_clean}" in block or name_clean in block:
                    id_match = re.search(r"\[ID:\s*([^\]\s]+)\s*\]", block)
                    if id_match:
                        pid = id_match.group(1).strip()
                        if pid and pid not in seen_ids:
                            matched_ids.append(pid)
                            seen_ids.add(pid)
                        break
                # 3차 (신규): 정규화 매칭 — 띄어쓰기·"년" 같은 사소한 차이 무시
                block_name_match = re.search(r"정책명:\s*([^\n\r]+)", block)
                if block_name_match:
                    block_name = block_name_match.group(1).strip()
                    norm_input = _normalize_name(name_clean)
                    norm_block = _normalize_name(block_name)
                    # LLM이 차수 빼먹은 경우: 정규화한 input이 정규화한 block_name에 포함되거나 그 반대
                    if norm_input and (norm_input in norm_block or norm_block in norm_input):
                        id_match = re.search(r"\[ID:\s*([^\]\s]+)\s*\]", block)
                        if id_match:
                            pid = id_match.group(1).strip()
                            if pid and pid not in seen_ids:
                                matched_ids.append(pid)
                                seen_ids.add(pid)
                                print(f"🔧 [LLM] 정규화 매칭으로 ID 발견: {block_name}")
                            break    
          
        # 정답 id를 찾았을 때 분기
        if matched_ids:
            if "[RECOMMEND:" in full_response:   # 태그 있는 경우
                # 기존 RECOMMEND 태그 ID를 검증된 ID로 덮어쓰기
                # ─── 케이스 A: 태그 있음 + 정답 ID도 있음
                #     → 기존 ID와 비교, 다르면 교정 후 덮어쓰기(re.sub으로 덮어쓰기)
                old_match = re.search(r"\[RECOMMEND:[^\]]*\]", full_response)
                old_ids = re.findall(r"20\d{18}", old_match.group(0)) if old_match else []
                if old_ids != matched_ids:
                    print(f"🔧 [LLM] RECOMMEND ID 불일치 감지 → 정책명 매칭으로 교정")
                    print(f"   LLM 출력: {old_ids}")
                    print(f"   정정 후:  {matched_ids}")
                full_response = re.sub(
                    r"\[RECOMMEND:[^\]]*\]",
                    f"[RECOMMEND: {', '.join(matched_ids)}]",
                    full_response,
                )
            else:   # 태그가 없는 경우
                # ─── 케이스 B: 태그 없음 + 정답 ID 있음
                #     → 자동 복원해서 태그 부착
                print("🔧 [LLM] RECOMMEND 태그 누락 → 자동 복원")
                full_response = full_response.rstrip() + f"\n[RECOMMEND: {', '.join(matched_ids)}]"
            print(f"✅ [LLM] 검증된 ID: {matched_ids}")
        else:
            # ─── 케이스 C: 정답 ID 산출 실패
            #     → 손대지 않음 (LLM 출력 그대로 유지)
            # "LLM이 출력한 정책명을 context 블록에서 찾지 못한 경우
            # 1. LLM이 정책명 자체를 환각한 경우
            # ㄴ context에는 드림For 청년통장만 있는데 LLM이 청년월세지원사업 이라고 답함 → 어떤 블록에도 없음 → 매칭 0건
            # 2. LLM이 정책명을 너무 많이 변형한 경우
            # ㄴ context는 청년내일저축계좌 인데 LLM이 청년 내일 저축 계좌 처럼 띄어쓰기 다르게 출력 → 부분 매칭(폴백)도 실패
            # 3. context는 정상인데 매칭 로직 자체가 못 잡는 엣지 케이스
            # "정책이 없을 때(검색 결과 0개)" 는 그 위쪽 단계에서 이미 걸러져서 여기까지 안 옴. 
            # 여기는 "LLM 출력 vs context 비교가 실패" 한 경우임
            print("⚠️ [LLM] 정책명-context 매칭 실패 (LLM ID 그대로 사용)")
        
    # RECOMMEND 태그 없이 물음표로 끝나는 응답은 추가 질문으로 판단
    if not is_clarifying and "[RECOMMEND:" not in full_response:
        stripped = full_response.rstrip()
        if stripped.endswith("?") or stripped.endswith("?)") or "?" in stripped[-80:]:
            is_clarifying = True
    return full_response, is_clarifying, None
