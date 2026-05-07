#!/bin/bash
# ============================================================
# SPARKY - AI 서버 초기화 스크립트 (Python 3.13 & FAISS 호환 수정본)
# FastAPI + LangChain + FAISS + Ollama (EXAONE 3.5 7.8B)
# 실행: cd ai-server && bash init.sh
# ============================================================

set -e

# 스크립트 파일이 있는 폴더(ai-server/)로 자동 이동
cd "$(dirname "$0")"

echo ""
echo "🤖 SPARKY AI 서버 초기화 시작..."
echo "📂 실행 위치: $(pwd)"
echo "=============================================="

# ── 1. Python 가상환경 ─────────────────────────────────────────
echo ""
echo "🐍 [1/5] Python 가상환경 생성 중..."
python -m venv venv
# OS별 가상환경 활성화 대응
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# pip 최신화 (Python 3.13에서는 필수적입니다)
python -m pip install --upgrade pip

# ── 2. 폴더 구조 생성 ─────────────────────────────────────────
echo ""
echo "📁 [2/5] 폴더 구조 생성 중..."
mkdir -p routers services models utils data/faiss_index scripts
touch routers/__init__.py services/__init__.py models/__init__.py utils/__init__.py

# ── 3. requirements.txt ───────────────────────────────────────
echo ""
echo "📦 [3/5] requirements.txt 생성 및 패키지 설치 중..."

# Python 3.13 호환을 위해 fastapi, pydantic 버전을 상향 조정했습니다.
cat > requirements.txt << 'EOF'
fastapi~=0.115.0
uvicorn[standard]~=0.30.0
python-dotenv==1.0.1
pydantic~=2.9.0
langchain~=0.3.0
langchain-community~=0.3.0
langchain-huggingface~=0.1.0
faiss-cpu>=1.9.0
sentence-transformers~=3.3.0
httpx~=0.28.1
cachetools~=5.5.0
requests==2.32.3
EOF

pip install -r requirements.txt
echo "   ✅ 패키지 설치 완료"

# ── 4. 소스 파일 생성 ─────────────────────────────────────────
echo ""
echo "📝 [4/5] 소스 파일 생성 중..."

# ─────────────── models/schemas.py ────────────────────────────
cat > models/schemas.py << 'PYEOF'
from pydantic import BaseModel
from typing import Optional, List
from enum import Enum

class PolicyDomain(str, Enum):
    employment = "취업"
    housing    = "주거"
    finance    = "금융"
    education  = "교육"
    welfare    = "복지"
    unknown    = "판단불가"

class UserProfile(BaseModel):
    ageGroup: str   # youth_19_24 | youth_25_29 | youth_30_34
    gender:   str   # male | female
    region:   str   # seoul | busan | ...
    uuid:     str

class ChatMessage(BaseModel):
    id:       str
    role:     str    # user | assistant
    content:  str
    timestamp: int

class ChatRequest(BaseModel):
    question: str
    userProfile: UserProfile
    conversationHistory: List[ChatMessage] = []

class PolicyCard(BaseModel):
    id:       str
    title:    str
    summary:  str
    domain:   PolicyDomain
    target:   str
    benefit:  str
    period:   str
    applyUrl: str
    source:   str    # youth | subsidy

class ChatResponse(BaseModel):
    answer:    str
    policyIds: List[str]
    domain:    PolicyDomain
    cards:     List[PolicyCard]
PYEOF

# ─────────────── utils/masking.py ─────────────────────────────
cat > utils/masking.py << 'PYEOF'
import re

RRN_PATTERN     = re.compile(r'\d{6}-[1-4]\d{6}')
PHONE_PATTERN   = re.compile(r'01[016789]-?\d{3,4}-?\d{4}')
ACCOUNT_PATTERN = re.compile(r'\d{3,6}-\d{2,6}-\d{4,8}')
EMAIL_PATTERN   = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')

def mask_sensitive(text: str) -> str:
    """채팅 텍스트에서 민감정보 마스킹"""
    text = RRN_PATTERN.sub('[주민번호 마스킹]', text)
    text = PHONE_PATTERN.sub('[전화번호 마스킹]', text)
    text = ACCOUNT_PATTERN.sub('[계좌번호 마스킹]', text)
    text = EMAIL_PATTERN.sub('[이메일 마스킹]', text)
    return text
PYEOF

# ─────────────── services/policy_service.py ───────────────────
cat > services/policy_service.py << 'PYEOF'
import os
import httpx
from cachetools import TTLCache
from models.schemas import PolicyCard, PolicyDomain

_cache: TTLCache = TTLCache(maxsize=512, ttl=86400)  # TTL 1일

YOUTH_API_URL   = os.getenv("YOUTH_API_URL", "")
SUBSIDY_API_URL = os.getenv("SUBSIDY_API_URL", "")

async def fetch_policies(domain: PolicyDomain, age_group: str, gender: str, region: str) -> list[PolicyCard]:
    """온통청년 API + 보조금24 API 호출 (TTL 1일 캐싱)"""
    cache_key = f"{domain}:{age_group}:{gender}:{region}"
    if cache_key in _cache:
        return _cache[cache_key]

    mock_cards = _get_mock_cards(domain, region)
    _cache[cache_key] = mock_cards
    return mock_cards

def _get_mock_cards(domain: PolicyDomain, region: str) -> list[PolicyCard]:
    return [
        PolicyCard(
            id=f"mock_{domain.value}_001",
            title=f"[{domain.value}] 청년 지원 정책 예시 1",
            summary=f"{region} 거주 청년을 위한 {domain.value} 분야 지원 정책입니다.",
            domain=domain,
            target="만 19~34세 청년",
            benefit="최대 300만 원 지원",
            period="2024.01.01 ~ 2024.12.31",
            applyUrl="https://www.youthcenter.go.kr",
            source="youth",
        ),
        PolicyCard(
            id=f"mock_{domain.value}_002",
            title=f"[{domain.value}] 청년 지원 정책 예시 2",
            summary=f"중앙정부 {domain.value} 분야 청년 정책입니다.",
            domain=domain,
            target="만 18~34세 청년",
            benefit="월 50만 원 지원",
            period="상시",
            applyUrl="https://www.bokjiro.go.kr",
            source="subsidy",
        ),
    ]
PYEOF

# ─────────────── services/rag_service.py ──────────────────────
cat > services/rag_service.py << 'PYEOF'
import os
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import Document
from models.schemas import PolicyDomain, UserProfile

EMBEDDING_MODEL      = os.getenv("EMBEDDING_MODEL", "snunlp/KR-SBERT-V40K-klueNLI-augSTS")
FAISS_INDEX_PATH     = os.getenv("FAISS_INDEX_PATH", "./data/faiss_index")
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.5"))

_embeddings   = None
_vectorstore  = None

def _load_embeddings():
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"},
        )
    return _embeddings

def _load_vectorstore():
    global _vectorstore
    if _vectorstore is None:
        emb = _load_embeddings()
        idx = os.path.join(FAISS_INDEX_PATH, "index.faiss")
        if os.path.exists(idx):
            _vectorstore = FAISS.load_local(FAISS_INDEX_PATH, emb, allow_dangerous_deserialization=True)
    return _vectorstore

def search_policies(query: str, user_profile: UserProfile, domain: PolicyDomain, top_k: int = 5) -> list[Document]:
    vs = _load_vectorstore()
    if vs is None: return []
    try:
        filter_dict = {"domain": domain.value}
        docs_scores = vs.similarity_search_with_score(query, k=top_k, filter=filter_dict)
        return [doc for doc, score in docs_scores if score >= SIMILARITY_THRESHOLD]
    except Exception as e:
        print(f"[RAG] 검색 오류: {e}")
        return []
PYEOF

# ─────────────── services/llm_service.py ──────────────────────
cat > services/llm_service.py << 'PYEOF'
import os
import httpx
from models.schemas import PolicyDomain, ChatMessage, UserProfile

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL    = os.getenv("OLLAMA_MODEL", "exaone3.5:7.8b")

DOMAIN_KEYWORDS = {
    PolicyDomain.employment: ["취업", "일자리", "채용", "직업", "알바", "인턴", "구직"],
    PolicyDomain.housing:    ["주거", "집", "전세", "월세", "주택", "아파트", "숙소"],
    PolicyDomain.finance:    ["금융", "대출", "적금", "저축", "신용", "부채", "지원금"],
    PolicyDomain.education:  ["교육", "학교", "대학", "장학금", "학비", "자격증", "훈련"],
    PolicyDomain.welfare:    ["복지", "의료", "건강", "지원", "바우처", "수당", "혜택"],
}

async def classify_domain(question: str) -> PolicyDomain:
    for domain, keywords in DOMAIN_KEYWORDS.items():
        if any(kw in question for kw in keywords):
            return domain
    return PolicyDomain.unknown

async def generate_answer(question: str, context_docs: list, conversation_history: list, user_profile: UserProfile, domain: PolicyDomain) -> str:
    context = "\n\n".join(context_docs) if context_docs else "관련 정책 정보 없음"
    system_prompt = f"당신은 청년 정책 전문 AI SPARKY입니다. 사용자 지역: {user_profile.region}"
    
    messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": f"컨텍스트: {context}\n질문: {question}"}]

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(f"{OLLAMA_BASE_URL}/api/chat", json={"model": OLLAMA_MODEL, "messages": messages, "stream": False})
            return resp.json()["message"]["content"]
    except Exception as e:
        return f"AI 서비스 오류가 발생했습니다: {str(e)}"
PYEOF

# ─────────────── routers/chat.py ──────────────────────────────
cat > routers/chat.py << 'PYEOF'
from fastapi import APIRouter, HTTPException
from models.schemas import ChatRequest, ChatResponse
from services.rag_service import search_policies
from services.llm_service import classify_domain, generate_answer
from services.policy_service import fetch_policies

router = APIRouter(prefix="/api", tags=["chat"])

@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    try:
        domain = await classify_domain(req.question)
        rag_docs = search_policies(req.question, req.userProfile, domain)
        context = [doc.page_content for doc in rag_docs]
        cards = await fetch_policies(domain, req.userProfile.ageGroup, req.userProfile.gender, req.userProfile.region)
        answer = await generate_answer(req.question, context, req.conversationHistory, req.userProfile, domain)
        return ChatResponse(answer=answer, policyIds=[c.id for c in cards], domain=domain, cards=cards)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
PYEOF

# ─────────────── scripts/build_index.py ───────────────────────
cat > scripts/build_index.py << 'PYEOF'
import os, sys, json

# Windows 콘솔에서 유니코드(이모지 등) 출력을 위한 설정
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import Document
from models.schemas import PolicyDomain

EMBEDDING_MODEL  = os.getenv("EMBEDDING_MODEL", "snunlp/KR-SBERT-V40K-klueNLI-augSTS")
FAISS_INDEX_PATH = "./data/faiss_index"
RESOURCE_FILE    = "../resource.json"

def map_domain(lclsf, mclsf):
    target = (lclsf or "") + (mclsf or "")
    if any(kw in target for kw in ["일자리", "취업", "창업", "고용"]):
        return PolicyDomain.employment.value
    if any(kw in target for kw in ["주거", "주택", "월세", "전세"]):
        return PolicyDomain.housing.value
    if any(kw in target for kw in ["금융", "대출", "자산", "저축", "적금"]):
        return PolicyDomain.finance.value
    if any(kw in target for kw in ["교육", "대학", "학교", "장학", "학비", "기술학습"]):
        return PolicyDomain.education.value
    if any(kw in target for kw in ["복지", "건강", "문화", "생활", "참여", "기반", "심리", "의료"]):
        return PolicyDomain.welfare.value
    return PolicyDomain.unknown.value

def build():
    print(f"📂 {RESOURCE_FILE} 로드 중...")
    try:
        with open(RESOURCE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ 파일 로드 실패: {e}")
        return

    policies = data.get("result", {}).get("youthPolicyList", [])
    print(f"📦 총 {len(policies)}개의 정책 데이터를 파싱합니다.")

    docs = []
    for p in policies:
        content = f"정책명: {p.get('plcyNm')}\n설명: {p.get('plcyExplnCn')}\n지원내용: {p.get('plcySprtCn')}"
        domain = map_domain(p.get("lclsfNm"), p.get("mclsfNm"))
        docs.append(Document(
            page_content=content,
            metadata={
                "domain": domain,
                "id": p.get("plcyNo")
            }
        ))

    print("🧠 임베딩 생성 및 FAISS 인덱스 빌드 중...")
    emb = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL, model_kwargs={"device": "cpu"})
    vs = FAISS.from_documents(docs, emb)
    os.makedirs(FAISS_INDEX_PATH, exist_ok=True)
    vs.save_local(FAISS_INDEX_PATH)
    print(f"✅ FAISS 인덱스 생성 완료: {FAISS_INDEX_PATH} (총 {len(docs)}개 문서)")

if __name__ == "__main__":
    build()
PYEOF

# ─────────────── main.py ──────────────────────────────────────
cat > main.py << 'PYEOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.chat import router as chat_router
from dotenv import load_dotenv
import os

load_dotenv()
app = FastAPI(title="SPARKY AI Server")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.include_router(chat_router)

@app.on_event("startup")
async def startup_event():
    print("🚀 SPARKY AI Server 준비 완료")
PYEOF

# ── 5. 완료 ────────────────────────────────────────────────────
# .env 파일 생성 등 마무리 로직...
cat > .env << 'EOF'
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=exaone3.5:7.8b
EMBEDDING_MODEL=snunlp/KR-SBERT-V40K-klueNLI-augSTS
EOF

echo ""
echo "=============================================="
echo "✅ [5/5] AI 서버 초기화 완료!"
echo "=============================================="