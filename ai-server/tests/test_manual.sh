#!/bin/bash
# ============================================================
# SPARKY 수동 테스트 스크립트 (curl)
# 실행: cd ai-server && bash tests/test_manual.sh
# 서버가 localhost:8000에서 실행 중이어야 함
# ============================================================

BASE="http://localhost:8000"
PASS=0
FAIL=0

check() {
  local desc="$1"
  local result="$2"
  local expect="$3"
  if echo "$result" | grep -q "$expect"; then
    echo "  ✅ PASS: $desc"
    ((PASS++))
  else
    echo "  ❌ FAIL: $desc"
    echo "     응답: $(echo $result | head -c 200)"
    ((FAIL++))
  fi
}

echo ""
echo "========================================"
echo "  SPARKY 수동 테스트 시작"
echo "  서버: $BASE"
echo "========================================"


# ──────────────────────────────────────────
# TC-20 헬스체크
echo ""
echo "[ TC-20 헬스체크 ]"
RES=$(curl -s "$BASE/api/health")
check "health endpoint" "$RES" '"status":"ok"'


# ──────────────────────────────────────────
# TC-01 Turn 1: 첫 질문 → is_clarifying=true
echo ""
echo "[ TC-01 Turn 1: 주거 첫 질문 ]"
RES=$(curl -s -X POST "$BASE/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "청년 주거 지원 정책 알고 싶어요",
    "userProfile": {"ageGroup":"youth_25_29","gender":"male","region":"seoul","uuid":"test-t1"},
    "conversationHistory": [{"id":"welcome","role":"assistant","content":"안녕하세요 SPARKY입니다","timestamp":1}]
  }')
check "is_clarifying=true" "$RES" '"is_clarifying":true'
check "cards=[]" "$RES" '"cards":\[\]'
check "domain=주거" "$RES" '"domain":"주거"'


# ──────────────────────────────────────────
# TC-02 Turn 2: 맥락 유지 (IT → 전세 조건 추가)
echo ""
echo "[ TC-02 Turn 2: 맥락 유지 (IT + 전세) ]"
RES=$(curl -s -X POST "$BASE/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "전세요",
    "userProfile": {"ageGroup":"youth_25_29","gender":"male","region":"seoul","uuid":"test-t2"},
    "conversationHistory": [
      {"id":"welcome","role":"assistant","content":"안녕하세요 SPARKY입니다","timestamp":1},
      {"id":"u1","role":"user","content":"IT 청년정책 알고 싶어요","timestamp":2},
      {"id":"a1","role":"assistant","content":"50개 정책이 있어요. 전세 지원인가요, 월세 지원인가요?","timestamp":3}
    ]
  }')
check "응답 있음" "$RES" '"answer":'
check "domain 분류됨" "$RES" '"domain":'
echo "  📌 expand_query IT 맥락 유지 확인 (서버 로그 참고)"


# ──────────────────────────────────────────
# TC-03 Turn 4: 강제 종료 → is_clarifying=false
echo ""
echo "[ TC-03 Turn 4: 강제 종료 ]"
RES=$(curl -s -X POST "$BASE/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "미혼이에요",
    "userProfile": {"ageGroup":"youth_19_24","gender":"female","region":"busan","uuid":"test-t4"},
    "conversationHistory": [
      {"id":"welcome","role":"assistant","content":"안녕하세요","timestamp":1},
      {"id":"u1","role":"user","content":"복지 지원 정책 알려줘","timestamp":2},
      {"id":"a1","role":"assistant","content":"의료 지원인가요, 생활 지원인가요?","timestamp":3},
      {"id":"u2","role":"user","content":"생활 지원이요","timestamp":4},
      {"id":"a2","role":"assistant","content":"현금 지원인가요?","timestamp":5},
      {"id":"u3","role":"user","content":"네 현금이요","timestamp":6},
      {"id":"a3","role":"assistant","content":"기혼인가요, 미혼인가요?","timestamp":7}
    ]
  }')
check "Turn4 강제종료 is_clarifying=false" "$RES" '"is_clarifying":false'


# ──────────────────────────────────────────
# TC-21 15-18세 차단
echo ""
echo "[ TC-21 15-18세 차단 ]"
RES=$(curl -s -X POST "$BASE/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "청년 정책 알려줘",
    "userProfile": {"ageGroup":"youth_15_18","gender":"male","region":"seoul","uuid":"test-age"},
    "conversationHistory": []
  }')
check "15-18세 cards=[]" "$RES" '"cards":\[\]'
check "15-18세 is_clarifying=false" "$RES" '"is_clarifying":false'


# ──────────────────────────────────────────
# TC-22 도메인 분류 키워드 매칭
echo ""
echo "[ TC-22 도메인 분류 ]"
for Q in "취업하고 싶어요:취업" "전세 지원 받고 싶어요:주거" "적금 들고 싶어요:금융" "장학금 받고 싶어요:교육" "의료 지원 받고 싶어요:복지"; do
  QUESTION="${Q%%:*}"
  EXPECTED="${Q##*:}"
  RES=$(curl -s -X POST "$BASE/api/chat" \
    -H "Content-Type: application/json" \
    -d "{
      \"question\": \"$QUESTION\",
      \"userProfile\": {\"ageGroup\":\"youth_25_29\",\"gender\":\"male\",\"region\":\"seoul\",\"uuid\":\"test-domain\"},
      \"conversationHistory\": []
    }")
  check "도메인 분류: '$QUESTION' → $EXPECTED" "$RES" "\"domain\":\"$EXPECTED\""
done


# ──────────────────────────────────────────
# TC-23 스키마 검증
echo ""
echo "[ TC-23 스키마 검증 ]"
RES=$(curl -s -X POST "$BASE/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"userProfile": {"ageGroup":"youth_25_29","gender":"male","region":"seoul","uuid":"test"}}')
check "question 필드 누락 → 422" "$RES" '"detail"'

RES=$(curl -s -X POST "$BASE/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"question": "테스트"}')
check "userProfile 필드 누락 → 422" "$RES" '"detail"'


# ──────────────────────────────────────────
# TC-24 아키네이터 전체 시나리오 (주거: 전세 → 단독가구)
echo ""
echo "[ TC-24 아키네이터 전체 시나리오: 주거 퍼널 ]"
echo "  Step 1/3: 첫 질문..."
S1=$(curl -s -X POST "$BASE/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "청년 전세 지원 정책 알고 싶어요",
    "userProfile": {"ageGroup":"youth_25_29","gender":"male","region":"seoul","uuid":"scenario-1"},
    "conversationHistory": [{"id":"welcome","role":"assistant","content":"안녕하세요","timestamp":1}]
  }')
check "Step1 is_clarifying=true" "$S1" '"is_clarifying":true'
A1=$(echo $S1 | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('answer','')[:80])" 2>/dev/null)
echo "  📣 AI 답변: $A1"

echo "  Step 2/3: '단독가구요' 답변..."
S2=$(curl -s -X POST "$BASE/api/chat" \
  -H "Content-Type: application/json" \
  -d "{
    \"question\": \"단독가구요\",
    \"userProfile\": {\"ageGroup\":\"youth_25_29\",\"gender\":\"male\",\"region\":\"seoul\",\"uuid\":\"scenario-1\"},
    \"conversationHistory\": [
      {\"id\":\"welcome\",\"role\":\"assistant\",\"content\":\"안녕하세요\",\"timestamp\":1},
      {\"id\":\"u1\",\"role\":\"user\",\"content\":\"청년 전세 지원 정책 알고 싶어요\",\"timestamp\":2},
      {\"id\":\"a1\",\"role\":\"assistant\",\"content\":\"$A1\",\"timestamp\":3}
    ]
  }")
check "Step2 응답 있음" "$S2" '"answer":'
A2=$(echo $S2 | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('answer','')[:80])" 2>/dev/null)
echo "  📣 AI 답변: $A2"
echo "  is_clarifying: $(echo $S2 | python3 -c "import json,sys; print(json.load(sys.stdin).get('is_clarifying'))" 2>/dev/null)"
echo "  카드 수: $(echo $S2 | python3 -c "import json,sys; print(len(json.load(sys.stdin).get('cards',[])))" 2>/dev/null)"


# ──────────────────────────────────────────
# 결과 요약
echo ""
echo "========================================"
echo "  테스트 결과: PASS=$PASS, FAIL=$FAIL"
if [ $FAIL -eq 0 ]; then
  echo "  🎉 모든 테스트 통과!"
else
  echo "  ⚠️  $FAIL개 실패 — 서버 로그 확인 필요"
fi
echo "========================================"
