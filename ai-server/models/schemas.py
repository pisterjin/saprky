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
    candidateIds: List[str] = []  # 이전 턴 후보 풀 (AND 누적 필터링용)

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
    endDate:  Optional[str] = None  # raw bizPrdEndYmd (D-day 계산용)

class ChatResponse(BaseModel):
    answer:        str
    policyIds:     List[str]
    domain:        PolicyDomain
    cards:         List[PolicyCard]
    is_clarifying: bool = False
    candidateIds:  List[str] = []  # 현재 턴 후보 풀 → 다음 턴 요청에 그대로 전달
    chips:         Optional[str] = None  # "employment" | "income" | None
