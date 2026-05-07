"""
Phase 1 진단 스크립트 — 코드 수정 없음, 읽기 전용
D3: 인덱스 지역/도메인 분포 + 서울+주거 교집합 확인
D5: 특정 ID 메타데이터 덤프
"""
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from collections import Counter
from services.rag_service import load_vectorstore

vs = load_vectorstore()
if vs is None:
    print("❌ 벡터스토어 로드 실패")
    sys.exit(1)

docs = list(vs.docstore._dict.values())
print(f"\n📦 총 문서 수: {len(docs)}")

# 지역 분포
regions = Counter(d.metadata.get("region", "?") for d in docs)
print("\n🗺️  지역 분포 (상위 20):")
for r, cnt in regions.most_common(20):
    print(f"  {r:20s} : {cnt}개")

# 도메인 분포
domains = Counter(d.metadata.get("domain", "?") for d in docs)
print("\n🏷️  도메인 분포:")
for dom, cnt in domains.most_common():
    print(f"  {dom:20s} : {cnt}개")

# 서울+주거 교집합
seoul_housing = [
    d for d in docs
    if d.metadata.get("region") == "seoul"
    and d.metadata.get("domain") in ("주거", "housing")
]
print(f"\n🏠 서울+주거 정책: {len(seoul_housing)}개")
for d in seoul_housing[:5]:
    title = d.page_content.split("\n")[0]
    print(f"  - {title} | {d.metadata}")

# central로 등록된 지역 정책 의심 샘플 (연령 제한 있는데 central인 것)
suspicious = [
    d for d in docs
    if d.metadata.get("region") == "central"
    and (d.metadata.get("min_age", 0) > 0 or d.metadata.get("max_age", 0) > 0)
]
print(f"\n⚠️  central인데 연령제한 있는 문서 (지역 오분류 의심): {len(suspicious)}개")
for d in suspicious[:5]:
    title = d.page_content.split("\n")[0]
    print(f"  - {title} | {d.metadata}")

# D5: 특정 ID 덤프
TARGET_IDS = ['20250903005400211614', '20250716005400211289', '20250502005400210772']
print(f"\n🔎 D5 특정 ID 메타데이터:")
found = 0
for d in docs:
    if d.metadata.get("id") in TARGET_IDS:
        print(f"\n  ID: {d.metadata.get('id')}")
        print(f"  metadata: {d.metadata}")
        print(f"  content[:200]: {d.page_content[:200]}")
        print("  ---")
        found += 1
if found == 0:
    print("  (해당 ID 없음 — 인덱스가 다른 데이터로 구성됨)")
