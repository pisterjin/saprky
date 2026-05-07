import os
import html
import re
from datetime import date
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import Document
from models.schemas import PolicyDomain, UserProfile
          
# ========== 설정값 ==========
EMBEDDING_MODEL      = os.getenv("EMBEDDING_MODEL", "snunlp/KR-SBERT-V40K-klueNLI-augSTS")
FAISS_INDEX_PATH     = os.getenv("FAISS_INDEX_PATH", "./data/faiss_index")
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "1.5"))

AGE_RANGE = {
    "youth_19_24": (19, 24),
    "youth_25_29": (25, 29),
    "youth_30_34": (30, 34),
    "youth_35_up": (35, 39),   # 청년 상한이 보통 39세까지라 39로 설정
} 

# Phase 2 패치: threshold 상한 캡
# 2.0을 초과해서 완화하면 무관한 정책까지 포함됨
# 청년 나이 기준(443개 중에서 나이 조건으로 필터링)
# 결과 수 기반 동적 임계값 완화 단계
# 결과가 RELAX_MIN 미만이면 threshold를 RELAX_STEP씩 올려 RELAX_MAX까지 재시도
# Phase 2 패치: threshold 상한 캡
# 2.0을 초과해서 완화하면 무관한 정책까지 포함됨
YOUTH_MIN_AGE = 19
YOUTH_MAX_AGE = 34
MAX_THRESHOLD    = 1.8  # 절대 이 값을 초과하지 않음
RELAX_STEP       = 0.2
TARGET_RESULTS   = 3   # 이상적인 결과 수 (못 채워도 포기)
MIN_RESULTS_ACCEPT = 1 # 이 개수 이상이면 "충분"으로 판단

_embeddings  = None
_vectorstore = None

# ========== 도메인 키워드 ==========
DOMAIN_KEYWORDS = {
    "주거": ["주거", "집", "전세", "월세", "주택"],
    "취업": ["취업", "일자리", "채용", "구직", "창업"],  
    "금융": ["금융", "대출", "적금", "저축", "지원금"],
    "교육": ["교육", "학교", "장학금", "자격증", "훈련"],
    "복지": ["복지", "의료", "건강", "문화", "심리", "참여"],  
}

# ========== 텍스트 변환 ==========
def youth_policy_to_text(policy):
    text = f"""
[청년 정책]
정책명: {policy.get('plcyNm', '')}
분류: {policy.get('lclsfNm', '')} > {policy.get('mclsfNm', '')}
키워드: {policy.get('plcyKywdNm', '')}
설명: {policy.get('plcyExplnCn', '')}
지원 내용: {policy.get('plcySprtCn', '')}
대상 나이: {policy.get('sprtTrgtMinAge', '')}세 ~ {policy.get('sprtTrgtMaxAge', '')}세
신청 방법: {policy.get('plcyAplyMthdCn', '')}
주관 기관: {policy.get('sprvsnInstCdNm', '')}
신청 URL: {policy.get('aplyUrlAddr', '')}
""".strip()
    return html.unescape(text)

def gov24_to_text(service):
    text = f"""
[정부24 혜택]
서비스명: {service.get('서비스명', '')}
서비스 목적: {service.get('서비스목적요약', '')}
지원 대상: {service.get('지원대상', '')}
선정 기준: {service.get('선정기준', '')}
지원 내용: {service.get('지원내용', '')}
신청 기한: {service.get('신청기한', '')}
신청 방법: {service.get('신청방법', '')}
소관 기관: {service.get('소관기관명', '')}
신청 URL: {service.get('상세조회URL', '')}
""".strip()
    return html.unescape(text)

# ========== 도메인 분류 ==========
EMPLOYMENT_STATUS_WORDS = ["미취업", "재직 중", "재직중", "재직", "구직 중", "구직중", "구직", "이직 중", "이직중", "이직"]

# 다른 도메인 정책 추천 시 최근 키워드 우선으로 진행
def classify_domain_simple(question):
    """
    키워드 기반 도메인 분류.
    한국어 부분매칭 함정("취업" in "미취업" == True)을 피하기 위해,
    고용 상태 답변 단어를 먼저 제거한 뒤 검사한다.
    누적 텍스트("금융 ... 교육")가 들어와도 가장 뒤(=가장 최근)에
    등장한 도메인 키워드를 우선으로 한다.
    """
    cleaned = question
    for w in EMPLOYMENT_STATUS_WORDS:
        cleaned = cleaned.replace(w, " ")

    # 텍스트 내 위치(rfind)를 비교해 가장 뒤쪽 도메인 키워드를 선택
    best_domain = None
    best_pos = -1
    for domain, keywords in DOMAIN_KEYWORDS.items():
        for kw in keywords:
            pos = cleaned.rfind(kw)
            if pos > best_pos:
                best_pos = pos
                best_domain = domain
    return best_domain

# ========== FAISS 로드 ==========
def load_embeddings():
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True}
        )
    return _embeddings

def reload_vectorstore():
    """FAISS 인덱스를 디스크에서 다시 읽어 메모리에 반영한다."""
    global _vectorstore
    _vectorstore = None
    load_vectorstore()
    print("🔄 [RAG] 벡터스토어 핫리로드 완료")

def hot_swap_vectorstore(new_vs) -> None:
    """이미 로드된 FAISS 인스턴스를 무중단으로 교체한다.
    빌드가 완료된 vs 객체를 받아 참조만 교체하므로 None 구간이 없다."""
    global _vectorstore
    _vectorstore = new_vs
    print("🔄 [RAG] 벡터스토어 핫스왑 완료")

# FAISS 재사용
def load_vectorstore():
    global _vectorstore
    if _vectorstore is None:  # 처음 한 번만 로드 
        print("🧠 [RAG] 임베딩 모델 로드 중...")
        emb = load_embeddings()    
        idx = os.path.join(FAISS_INDEX_PATH, "index.faiss")
        if os.path.exists(idx): 
            print(f"📂 [RAG] FAISS 인덱스 로드 중: {FAISS_INDEX_PATH}")
            _vectorstore = FAISS.load_local(
                FAISS_INDEX_PATH, emb,
                allow_dangerous_deserialization=True
            )
        else:
            print(f"⚠️ [RAG] FAISS 인덱스 파일을 찾을 수 없습니다: {idx}")
    return _vectorstore  # 이후엔 캐시된 것 재사용

# ========== Python 필터 ==========
def _apply_python_filters(
    docs_scores: list,
    user_profile: UserProfile,
    # user_age: int,
    u_min: int,
    u_max: int,
    threshold: float,
    today_str: str,
    today_ym: str,
    include_expired: bool,
    top_k: int,
) -> list[Document]:
    filtered: list[Document] = []
    for doc, score in docs_scores:
        meta     = doc.metadata
        mn = int(meta.get("min_age") or 0)
        mx = int(meta.get("max_age") or 0)
        age_ok = (mn == 0 and mx == 0) or not (mx < u_min or mn > u_max)  # 구간 겹침
        score_ok = score <= threshold
        region_ok = meta.get("region") in [user_profile.region, "central"]
        end_date = meta.get("end_date", "")
        if include_expired or not end_date:
            date_ok = True
        elif len(end_date) <= 6 and end_date.isdigit():
            date_ok = end_date >= today_ym
        else:
            date_ok = end_date >= today_str
        if region_ok and age_ok and score_ok and date_ok:
            filtered.append(doc)
        if len(filtered) >= top_k * 3:
            break
    return filtered

# 조건 변경 시 지역을 요청했을 때 
# 기존 답변으로 인해 오염되지 않기 위해 _search_and_filter_policies 함수 생성
# 기존의 get_context(x) 함수에서 일부만 수정
def _search_and_filter_policies(
    query: str,
    domain: str | None,
    user_region: str,
    user_age_code: str,
    wants_national: bool,
) -> str:
    """FAISS 검색 + 모든 필터 + 상위 20개 포맷까지 담당하는 내부 헬퍼.
    검증 로직은 호출자가 책임지고, 이 함수는 '깨끗한 입력'만 받는다고 가정한다.
    """
    from services.llm_service import REGION_KR  # user_region_kr 만들 때 필요
    user_region_kr = REGION_KR.get(user_region, user_region)
    
    vs = load_vectorstore()
    if vs is None:
        return ""
    
    # 도메인이 잡혀 있을 때를 대비해 회수량을 충분히 확보 (k=500)
    # FAISS의 as_retriever().invoke(query) 는 벡터 유사도 점수가 높은 순(코사인 거리 가까운 순)으로 정렬된 리스트를 반환.
    # 가장 적합한 정책이 docs[0], 그 다음이 docs[1]... 식으로 들어옴
    # get_context() 함수에서 복붙해올 때
    docs = vs.as_retriever(search_kwargs={"k": 500}).invoke(query)
 
    # 도메인 메타필터: 인덱스에는 한국어 값("금융"/"주거"/"취업"/"교육"/"복지")으로 저장됨.
    # 메타데이터 기준으로 필터링
    # domain 매칭 결과가 0개면 필터를 풀고 원본을 유지한다 (안전장치).
    if domain:
        domain_docs = [d for d in docs if d.metadata.get("domain") == domain]   # 도메인 1차 필터 (EXCLUSION 적용 전)
        # ---- 결합 분류로 인한 오분류 방어 (블랙리스트) ----
        # 원본 데이터의 "금융･복지･문화 > 예술인지원"처럼 대분류에 여러 도메인이 묶인
        # 정책은 domain 메타가 부정확할 수 있음. 본문에 다른 도메인 키워드가 강하게
        # 드러나면 현재 도메인 추천에서 제외.  
        EXCLUSION_KEYWORDS = {
            "금융": [
                # 기존 (문화예술 거점/창작 관련)
                "문화예술", "문화창작", "예술인지원", "공연", "전시", "예술 거점", "창작 공간",
                # 추가: 결혼·만남·생활지원 계열 (금융과 무관)
                "미혼", "만남", "결혼", "이어드림", "맞선", "이성교제",
                # 추가: 소분류 자체 차단
                "문화활동 및 생활지원",
            ],
            "주거": ["문화창작", "예술인지원", "재정 교육", "자산 형성",
                    "미혼", "만남", "결혼", "이어드림"],
            "교육": ["문화예술 거점", "공연장", "전시장",
                    "미혼", "만남", "결혼", "이어드림"],
            "취업": ["미혼", "만남", "결혼", "이어드림",
                    "문화창작", "예술인지원"],   # 취업 도메인도 보호
            "복지": ["문화창작 거점", "예술 거점"],   # 복지/문화 도메인은 만남정책이 진짜 들어갈 수도 있어서 보수적으로 유지
            # 소분류 필요에 따라 추가 예정
        }
        
        # EXCLUSION 필터 
        excl = EXCLUSION_KEYWORDS.get(domain, [])
        if excl:
            before = len(domain_docs)
            domain_docs = [                               # domain_docs는 새로 필터됨 (예: 30 → 28)
                d for d in domain_docs
                if not any(k in d.page_content for k in excl)
            ]
            if before != len(domain_docs):
                print(f"🔍 [get_context] 결합분류 방어 필터로 {before - len(domain_docs)}개 제외 (domain={domain})")

        if domain_docs:
            docs = domain_docs
            print(f"🔍 [get_context] 도메인 필터 적용 후 docs 개수: {len(docs)} (domain={domain})")
        else:
            print(f"⚠️ [get_context] 도메인({domain}) 매칭 정책 0개 → 도메인 필터 해제")
    
    # 연령 구간 필터
    if user_age_code in AGE_RANGE:
        u_min, u_max = AGE_RANGE[user_age_code]
  
        def _age_overlap(d):
            mn = int(d.metadata.get("min_age") or 0) # 정책의 최소 나이
            mx = int(d.metadata.get("max_age") or 0) # 정책의 최대 나이
            if mn == 0 and mx == 0:
                return True                       # "전 연령"은 통과 (정책 결정에 따라 False도 가능)
             # ㄴ 나이 정보 없는 "전 연령" 정책은 통과
            return not (mx < u_min or mn > u_max)  # 구간 겹치면 통과
        docs = [d for d in docs if _age_overlap(d)]

    # 만료 정책 제외 (메타데이터의 end_date 기준)
    today_str = date.today().strftime("%Y%m%d")  # 8자리(년월일까지) 가져옴
    today_ym  = today_str[:6]  #6자리(월까지) 가져옴
       
    # 마감 필터(end_date 외에도 period 필드 추가해 버그 수정)
    # 연령 필터 → 도메인 필터 → 마감 필터 → 지역 필터 순서
    def _is_active(doc):
        end_date = doc.metadata.get("end_date", "")
        # 1) end_date 메타가 있으면 우선 사용
        if end_date:
            if len(end_date) <= 6 and end_date.isdigit():
                return end_date >= today_ym # 연월 비교 (6자리)
            digits = re.sub(r"\D", "", end_date)[:8]
            if len(digits) == 8:
                return digits >= today_str   # 연월일 비교 (8자리)
            if len(digits) >= 6:
                return digits[:6] >= today_ym
            return True  # 이상한 포맷이면 일단 통과

        # 2) fallback: period 텍스트에서 "~" 뒤의 종료 연월/연월일을 파싱
        period = doc.metadata.get("period", "")
        if period and period.strip() != "상시":
            after = period.split("~")[-1] if "~" in period else period
            digits = re.sub(r"\D", "", after)[:8]
            if len(digits) == 8:
                return digits >= today_str
            if len(digits) >= 6:
                return digits[:6] >= today_ym
        # 정말 정보 없으면 상시 정책으로 간주
        return True
    docs = [d for d in docs if _is_active(d)]
    print(f"🔍 [get_context] 마감 정책 제외 후 docs 개수: {len(docs)}")    

    # 지역 필터
    # user_region이 이미 프로필에 있으니, 전국 요청만 아니면 기본적으로 지역 필터 적용
    wants_local = (not wants_national) and bool(user_region_kr)
 
    if wants_local:
        # 사용자가 명시적으로 지역 선택하면 central(전국) 제외.
        # 서울 전용 정책이 0개라도 그대로 둠 (사용자 의도 존중).
        # 사용자가 다음 턴에 "전국도 괜찮아요"라고 답하면 wants_local=False
        # 자동으로 전국 정책까지 검색 범위에 들어옴.
        docs = [
            d for d in docs
            if d.metadata.get("region") == user_region
        ]
        print(f"🔍 [get_context] 지역 전용 정책: {len(docs)}개 (region={user_region})")
        
    docs = docs[:20]  # LLM에 최대 20개만 전달
    
    # return "\n\n".join(doc.page_content for doc in docs)  
    result = "\n\n".join(
    f"[ID: {doc.metadata.get('id', '')}]\n{doc.page_content}"
    for doc in docs
    )
    print(f"🔍 [get_context] 반환 docs 개수: {len(docs)}")
    print(f"🔍 [get_context] 반환 context 길이: {len(result)}")
    return result

# ========== 대화 맥락 기반 context 생성 ==========
def get_context(x):
   # 함수 안에서만 import / llm_service.py 파일과 순환 문제로 임포트를 여기에 
    from services.llm_service import REGION_KR  
    print(f"🔍 [get_context] 호출됨!")
    question = x["question"]
    user_region = x.get("user_region", "")
    user_age_code = x.get("user_age", "")
    
    # full_text 직접 받기(봇 + 사용자 누적)
    full_text = x.get("full_text", "")
    history = x.get("history", [])   # 항상 먼저 가져오기 (한 줄로 통합)
    if not full_text:
        history_text = " ".join([m.content for m in history]) if history else ""
        full_text = history_text + " " + question

    # user_only_text는 사용자가 한 말만 모은 텍스트(봇 질문 제외)
    # 메시지 객체는 .role 속성 
    # 도메인 분류 + 지역 필터(wants_national 판단) 둘 다에서 공유 사용함
    # "조건 변경" 발화 이후의 사용자 메시지는 도메인 분류에서 제외
    # (예: "취업 상태", "재직 중"은 조건 변경 흐름의 답변이지 도메인 선택이 아니므로)
    last_change_idx = -1
    for i, m in enumerate(history):
        if getattr(m, "role", "") == "user" and "조건 변경" in m.content:
            last_change_idx = i
    
    history_for_domain = history[:last_change_idx] if last_change_idx >= 0 else history
    
    user_msgs = [
        m.content for m in history_for_domain
        if getattr(m, "role", "") == "user"
    ]
    user_only_text = " ".join(user_msgs + [question])

    print(f"🔍 [get_context] full_text 길이: {len(full_text)}")
    print(f"🔍 [get_context] user_only_text: {user_only_text}")

    # 도메인은 user_only_text로 분류 (봇 질문 오염 방지 + 누적 답변에서 키워드 탐색)
    # 도메인 필터와 도메인 분류는 다른 것으로 여기서는 필터 역할이 아닌 도메인 분류만 진행함
    # 사용자 발화(user_only_text)에서 키워드 매칭으로 사용자가 원하는 도메인이 뭔지 판단
    # 결과를 domain 변수에 담음 (예: "주거" 라는 문자열)
    # domain 변수에 사용자 의도를 저장만 함
    domain = classify_domain_simple(user_only_text)
    print(f"🔍 [get_context] domain: {domain}")
    
    # has_* 플래그는 반드시 user_only_text 기반으로 검사할 것.
    # full_text에는 봇 질문("재직 중/미취업", "복지·문화·참여권리..." 등)이 포함돼
    # 이용자가 답하지 않은 항목도 True로 오판정되어 full_text -> user_only_text로 수정
    has_employment = any(k in user_only_text for k in ["미취업", "재직", "구직", "이직"])
    has_interest = any(k in user_only_text for k in 
    ["주거", "금융", "교육", "취업", "일자리", "문화", "복지", "참여권리", "참여", "권리"])
    user_region_kr = REGION_KR.get(user_region, user_region)
    has_region     = any(k in user_only_text for k in
        ["지역", "전국", "원해", "괜찮", "네", "아니오",
         "원합니다", "좋아요", "어디나", "상관없", user_region, user_region_kr])
    has_age = bool(user_age_code) or any(k in user_only_text for k in
        ["19~24", "25~29", "30~34", "35세", "19세", "20대", "30대", "이상"])
    has_income     = any(k in user_only_text for k in
        ["중위소득", "중위", "50%", "100%", "제한 없음", "이하", "모름",
         "중간", "저소득", "소득층", "무관", "모르",
         "중간 소득", "소득 무관", "잘 모"])

    print(f"🔍 has_employment: {has_employment}")  
    print(f"🔍 has_interest: {has_interest}")     
    print(f"🔍 has_region: {has_region}")         
    print(f"🔍 has_income: {has_income}")          
    
    # 4개 정보(취업상태/관심분야/지역/소득)가 모두 모여야 RAG 진행
    if not (has_age and has_employment and has_interest and has_region and has_income):
        return ""
    
    # 최초 정책 추천+ 조건 변경 시 지역을 선택하는 경우 답변 오염 방지 
    # 거의 발생할 수 없는 케이스(domain도 None이고 region도 빈 문자열)에 대비. 
    wants_national = any(k in user_only_text for k in 
        ["전국", "어디든", "어디나", "상관없", "아무데나", "전국 정책", "전국도"])
    
    # 깨끗한 쿼리 조립: 지역명 + 도메인 (둘 다 없을 가능성은 거의 없음 — 검증 통과했으니)
    # 그래도 안전장치: 둘 다 비어있으면 fallback으로 user_only_text 사용
    clean_query_parts = []
    if user_region_kr and not wants_national:
        clean_query_parts.append(user_region_kr)
    if domain:
        clean_query_parts.append(domain)
    clean_query = " ".join(clean_query_parts) if clean_query_parts else user_only_text
    
    
    print(f"🔍 [get_context] clean_query: {clean_query}")
    
    return _search_and_filter_policies(
        query=clean_query,
        domain=domain,
        user_region=user_region,
        user_age_code=user_age_code,
        wants_national=wants_national,
    )
 

# ========== 조건 변경 직후 전용 context 생성 ==========
def get_context_for_condition_change(x):
    """조건 변경(지역/소득/취업/관심) 직후에만 호출.
    
    정상 흐름의 get_context와 달리:
      - 5개 정보 검증 스킵 (이미 모여있다고 가정)
      - 쿼리를 누적된 user_only_text가 아니라
        '현재 question + 현재 프로필 값 + 이전 도메인'으로 깨끗하게 새로 조립
      - 옛 답변(예: 직전 지역명)이 FAISS 쿼리에 섞이지 않음
      - 이전 도메인은 history에서 lookup만 하고, 쿼리 본문에는 history 텍스트가 안 섞임
    """
    from services.llm_service import REGION_KR, find_last_user_domain
    print(f"🔄 [get_context_for_condition_change] 호출됨!")
    
    # 사용자가 방금 입력한 답변이 question 
    question = x["question"]  # 사용자가 방금 친 한 줄 (예: "서울")
    user_region = x.get("user_region", "")  # 프로필에 저장된 지역 코드 (예: "seoul")
    user_age_code = x.get("user_age", "")  
    # 조건 변경 시 지역 변경 했더니 기존 도메인 정보를 끌고 오지 않아 추가됨
    history = x.get("history", [])  # 이전 도메인 lookup용 (쿼리 텍스트로는 안 씀)
    
    # 도메인은 history에서 사용자가 직전에 선택한 분야 우선
    # 예: 사용자가 "취업"을 골라서 추천받은 후 지역만 바꾸는 흐름이면 "취업" 유지
    # history에서 못 찾으면 question에서 분류 시도 (방어적 fallback)
    # find_last_user_domain(history) 로 이전 도메인 찾기
    prior_domain = find_last_user_domain(history) if history else None
    domain = prior_domain or classify_domain_simple(question)
    
    # 도메인은 question만으로 분류
    # wants_national은 question만으로 판단 
    # 사용자가 새로 "전국"을 선택했으면 True, 아니면 False
    wants_national = any(k in question for k in 
        ["전국", "어디든", "어디나", "상관없", "아무데나", "전국 정책", "전국도"])
    
    # 깨끗한 쿼리 조립: 현재 질문 + 중복 단어 방지
    user_region_kr = REGION_KR.get(user_region, user_region)  # 지역 코드를 한국어로 변환 (예: "서울")
    clean_query_parts = [question]   # ["서울"]
    if user_region_kr and user_region_kr not in question and not wants_national:
        clean_query_parts.append(user_region_kr)  # "서울"이 question에 없는 경우만 더함
    if domain and domain not in question:
        clean_query_parts.append(domain)   # "취업"이 question에 없으면 더함
    clean_query = " ".join(clean_query_parts) # "서울 취업"
    
    print(f"🔄 [condition_change] clean_query: {clean_query}")
    print(f"🔄 [condition_change] prior_domain: {prior_domain}, final domain: {domain}, wants_national: {wants_national}")
        
    return _search_and_filter_policies(
        query=clean_query,
        domain=domain,
        user_region=user_region,
        user_age_code=user_age_code,
        wants_national=wants_national,
    )

# ========== FastAPI용 검색 함수 ==========
def search_policies(
    query: str,
    user_profile: UserProfile,
    domain: PolicyDomain,
    top_k: int = 50,
    candidate_ids: list[str] | None = None,
    include_expired: bool = False,
) -> tuple[list[Document], bool]:
    """
    정책을 검색하고 (결과 목록, insufficient 여부)를 반환.
    """
    vs = load_vectorstore()
    if vs is None:
        print("⚠️ [RAG] 벡터스토어가 로드되지 않아 검색을 건너뜁니다.")
        return [], True

    try:
        if user_profile.ageGroup == "youth_15_18":
            print("🚫 [RAG] 15-18세 연령대 요청 - 서비스 제외 대상")
            return [], True

        u_min, u_max = AGE_RANGE.get(user_profile.ageGroup, (19, 34))

        today_str = date.today().strftime("%Y%m%d")
        today_ym  = today_str[:6]

        print(f"🔍 [RAG] 검색 시작 | 쿼리: '{query[:60]}'")

        has_domain = domain != PolicyDomain.unknown
        if has_domain:
            search_filter = lambda metadata: (
                metadata.get("region") in [user_profile.region, "central"]
                and metadata.get("domain") == domain.value
            )
        else:
            search_filter = lambda metadata: (
                metadata.get("region") in [user_profile.region, "central"]
            )

        docs_scores = vs.similarity_search_with_score(query, k=200, filter=search_filter)

        # ── Python-side 필터 + threshold 동적 완화 ────────
        # Phase 2 패치: 상한을 MAX_THRESHOLD(1.8)로 캡

        threshold = SIMILARITY_THRESHOLD
        filtered  = _apply_python_filters(
            docs_scores, user_profile, u_min, u_max,
            threshold, today_str, today_ym, include_expired, top_k,
        )

        while len(filtered) < TARGET_RESULTS and threshold < MAX_THRESHOLD:
            threshold = min(round(threshold + RELAX_STEP, 2), MAX_THRESHOLD)
            print(f"📈 [RAG] 결과 {len(filtered)}개 부족 → threshold 완화: {threshold:.1f}")

            filtered = _apply_python_filters(
                docs_scores, user_profile, u_min, u_max,
                threshold, today_str, today_ym, include_expired, top_k,
            )

        # Phase 2 패치: 상한 도달 후 결과 부족 시 솔직하게 insufficient 반환
        # (이전: 임계값 완전 무시 fallback으로 무관한 정책 강제 반환 → 제거)
        if len(filtered) < MIN_RESULTS_ACCEPT:
            print(f"⚠️ [RAG] 관련 정책 부족 (threshold={threshold:.1f}, 결과={len(filtered)}개) → insufficient")
            return filtered, True

        # ── 도메인 릴렉싱 (도메인 필터 결과가 0개일 때만) ──
        # Phase 2 패치: 기존 < 5 → == 0 으로 강화 (1개 이상이면 릴렉싱 안 함)
        if has_domain and len(filtered) == 0:
            print(f"🔄 [RAG] 도메인 필터 결과 0개 → 도메인 제약 해제 후 재검색")
            no_domain_filter = lambda metadata: metadata.get("region") in [user_profile.region, "central"]
            docs_scores_nd   = vs.similarity_search_with_score(query, k=200, filter=no_domain_filter)
            filtered_nd      = _apply_python_filters(
                docs_scores_nd, user_profile, u_min, u_max,
                threshold, today_str, today_ym, include_expired, top_k,
            )
            if len(filtered_nd) == 0:
                print(f"   도메인 릴렉싱 후에도 0개 → insufficient")
                return [], True

            existing_ids = {d.metadata.get("id") for d in filtered}
            extras       = [d for d in filtered_nd if d.metadata.get("id") not in existing_ids]
            filtered     = filtered + extras

        # 지역 필터링 추가
        user_region = user_profile.region
        wants_national_meta = domain == PolicyDomain.unknown
        if not wants_national_meta:
            region_filtered = [
                d for d in filtered
                if d.metadata.get("region") in [user_region, "central"]
            ]
            if region_filtered:
                filtered = region_filtered

        if candidate_ids:
            prev_set = set(candidate_ids)
            filtered = [d for d in filtered if d.metadata.get("id") in prev_set]

        filtered = filtered[:top_k]

        if not filtered and candidate_ids:
            filtered = _apply_python_filters(
                docs_scores, user_profile, u_min, u_max,
                threshold, today_str, today_ym, include_expired, top_k,
            )[:top_k]

        insufficient = len(filtered) < MIN_RESULTS_ACCEPT
        print(f"✅ [RAG] 최종 후보: {len(filtered)}개 (threshold={threshold:.1f}, insufficient={insufficient})")
        return filtered, insufficient

    except Exception as e:
        print(f"❌ [RAG] 검색 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return [], True
