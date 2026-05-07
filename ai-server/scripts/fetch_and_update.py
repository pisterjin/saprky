"""
온통청년 API → PostgreSQL 갱신 + FAISS 재빌드

사용법:
    python scripts/fetch_and_update.py           # 변경분 동기화
    python scripts/fetch_and_update.py --dry-run # 변경 수만 확인 (DB/FAISS 미수정)
"""

import os
import sys
import shutil
import asyncio
import argparse
from datetime import datetime

import asyncpg
import httpx
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from services.utils import map_domain, map_region_by_zip, build_period
from services.rag_service import load_embeddings, FAISS_INDEX_PATH

DATABASE_URL  = os.getenv("DATABASE_URL", "postgresql://sparky:sparky1234@localhost:5433/sparky")
ONTONG_API_KEY = os.getenv("ONTONG_API_KEY", "")
API_BASE_URL  = "https://www.youthcenter.go.kr/go/ythip/getPlcy"
PAGE_SIZE     = 100

INSERT_SQL = """
INSERT INTO youth_policies (
    "plcyNo", "plcyNm", "plcyExplnCn", "plcySprtCn", "plcyKywdNm",
    "lclsfNm", "mclsfNm",
    "sprtTrgtMinAge", "sprtTrgtMaxAge", "sprtTrgtAgeLmtYn",
    "bizPrdBgngYmd", "bizPrdEndYmd", "bizPrdEtcCn",
    "aplyUrlAddr", "refUrlAddr1", "refUrlAddr2",
    "sprvsnInstCdNm", "operInstCdNm",
    "plcyAplyMthdCn", "mrgSttsCd", "earnCndSeCd",
    "earnMinAmt", "earnMaxAmt",
    "frstRegDt", "lastMdfcnDt"
) VALUES (
    $1,  $2,  $3,  $4,  $5,
    $6,  $7,
    $8,  $9,  $10,
    $11, $12, $13,
    $14, $15, $16,
    $17, $18,
    $19, $20, $21,
    $22, $23,
    $24, $25
)
ON CONFLICT ("plcyNo") DO UPDATE SET
    "plcyNm"         = EXCLUDED."plcyNm",
    "plcyExplnCn"    = EXCLUDED."plcyExplnCn",
    "plcySprtCn"     = EXCLUDED."plcySprtCn",
    "plcyKywdNm"     = EXCLUDED."plcyKywdNm",
    "lclsfNm"        = EXCLUDED."lclsfNm",
    "mclsfNm"        = EXCLUDED."mclsfNm",
    "sprtTrgtMinAge" = EXCLUDED."sprtTrgtMinAge",
    "sprtTrgtMaxAge" = EXCLUDED."sprtTrgtMaxAge",
    "bizPrdBgngYmd"  = EXCLUDED."bizPrdBgngYmd",
    "bizPrdEndYmd"   = EXCLUDED."bizPrdEndYmd",
    "bizPrdEtcCn"    = EXCLUDED."bizPrdEtcCn",
    "aplyUrlAddr"    = EXCLUDED."aplyUrlAddr",
    "refUrlAddr1"    = EXCLUDED."refUrlAddr1",
    "sprvsnInstCdNm" = EXCLUDED."sprvsnInstCdNm",
    "lastMdfcnDt"    = EXCLUDED."lastMdfcnDt"
"""


def _parse_timestamp(val: str | None):
    if not val or not val.strip():
        return None
    try:
        return datetime.strptime(val.strip()[:19], "%Y-%m-%d %H:%M:%S")
    except Exception:
        return None


def _row(p: dict) -> tuple:
    return (
        p.get("plcyNo"),
        p.get("plcyNm"),
        p.get("plcyExplnCn"),
        p.get("plcySprtCn"),
        p.get("plcyKywdNm"),
        p.get("lclsfNm"),
        p.get("mclsfNm"),
        p.get("sprtTrgtMinAge"),
        p.get("sprtTrgtMaxAge"),
        p.get("sprtTrgtAgeLmtYn"),
        (p.get("bizPrdBgngYmd") or "").strip() or None,
        (p.get("bizPrdEndYmd") or "").strip() or None,
        p.get("bizPrdEtcCn"),
        p.get("aplyUrlAddr"),
        p.get("refUrlAddr1"),
        p.get("refUrlAddr2"),
        p.get("sprvsnInstCdNm"),
        p.get("operInstCdNm"),
        p.get("plcyAplyMthdCn"),
        p.get("mrgSttsCd"),
        p.get("earnCndSeCd"),
        p.get("earnMinAmt"),
        p.get("earnMaxAmt"),
        _parse_timestamp(p.get("frstRegDt")),
        _parse_timestamp(p.get("lastMdfcnDt")),
    )


async def fetch_all_from_api() -> list[dict]:
    """온통청년 API에서 전체 정책을 페이징으로 가져온다."""
    if not ONTONG_API_KEY:
        raise RuntimeError("ONTONG_API_KEY가 설정되지 않았습니다. .env를 확인하세요.")

    policies: list[dict] = []
    page = 1
    tot  = 0
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        while True:
            params = {
                "apiKeyNm": ONTONG_API_KEY,
                "pageSize": PAGE_SIZE,
                "pageNum":  page,
                "rtnType":  "json",
            }
            # 500 에러 시 최대 3회 재시도
            for attempt in range(3):
                try:
                    resp = await client.get(API_BASE_URL, params=params)
                    resp.raise_for_status()
                    break
                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 500 and attempt < 2:
                        print(f"   ⚠️  {page}페이지 서버 에러, {attempt+1}회 재시도...")
                        await asyncio.sleep(2)
                    else:
                        raise
            data  = resp.json()
            if page == 1:
                top_keys = list(data.keys()) if isinstance(data, dict) else type(data).__name__
                print(f"   🔑 응답 최상위 키: {top_keys}")
            batch = data.get("youthPolicyList") or data.get("result", {}).get("youthPolicyList", [])
            if page == 1:
                raw_tot = data.get("totalCnt") or data.get("result", {}).get("pagging", {}).get("totCount") or 0
                tot = int(raw_tot) if str(raw_tot).isdigit() else 0
            policies.extend(batch)
            print(f"   📄 {page}페이지: {len(batch)}개 수신 (누적 {len(policies)}/{tot})")
            if len(policies) >= tot or not batch:
                break
            page += 1
            await asyncio.sleep(0.3)
    return policies


async def find_changed(conn: asyncpg.Connection, api_policies: list[dict]) -> list[dict]:
    """API 결과 중 DB와 비교해 신규·변경된 정책만 반환한다."""
    rows = await conn.fetch('SELECT "plcyNo", "lastMdfcnDt" FROM youth_policies')
    existing: dict[str, datetime | None] = {r["plcyNo"]: r["lastMdfcnDt"] for r in rows}

    changed = []
    for p in api_policies:
        pid = p.get("plcyNo")
        if not pid:
            continue
        new_dt = _parse_timestamp(p.get("lastMdfcnDt"))
        if pid not in existing or existing[pid] != new_dt:
            changed.append(p)
    return changed


def _policy_to_doc(p: dict) -> Document | None:
    pid = p.get("plcyNo") or p.get("plcy_no")
    if not pid:
        return None
    try:
        min_age = int(p.get("sprtTrgtMinAge") or p.get("sprt_trgt_min_age") or 0)
        max_age = int(p.get("sprtTrgtMaxAge") or p.get("sprt_trgt_max_age") or 0)
    except (ValueError, TypeError):
        min_age, max_age = 0, 0

    region  = map_region_by_zip(
        p.get("zipCd", "") or "",
        p.get("sprvsnInstCdNm", "") or p.get("sprvsn_inst_cd_nm", "") or "",
    )
    domain  = map_domain(
        p.get("lclsfNm", "") or p.get("lclsf_nm", ""),
        p.get("mclsfNm", "") or p.get("mclsf_nm", ""),
    )
    period  = build_period(p)
    age_str = "전 연령" if (min_age == 0 and max_age == 0) else f"만 {min_age}~{max_age}세"
    content = (
        f"정책명: {p.get('plcyNm') or p.get('plcy_nm', '')}\n"
        f"지원내용: {(p.get('plcySprtCn') or p.get('plcy_sprt_cn') or '')[:300]}\n"
        f"설명: {(p.get('plcyExplnCn') or p.get('plcy_expln_cn') or '')[:300]}\n"
        f"키워드: {p.get('plcyKywdNm') or p.get('plcy_kywd_nm', '')}\n"
        f"분류: {p.get('lclsfNm') or p.get('lclsf_nm', '')} > {p.get('mclsfNm') or p.get('mclsf_nm', '')}\n"
        f"대상: {age_str} / 지역: {p.get('sprvsnInstCdNm') or p.get('sprvsn_inst_cd_nm', '')}"
    ).strip()

    return Document(
        page_content=content,
        metadata={
            "id":       pid,
            "domain":   domain.value,
            "region":   region,
            "min_age":  min_age,
            "max_age":  max_age,
            "period":   period,
            "end_date": (p.get("bizPrdEndYmd") or p.get("biz_prd_end_ymd") or "").strip(),
        },
    )


async def rebuild_faiss(conn: asyncpg.Connection) -> int:
    """DB 전체 데이터로 FAISS 인덱스를 무중단 재빌드한다.

    흐름:
      1. 임시 경로(faiss_index_new)에 빌드 → 서비스 중단 없음
      2. 메모리 핫스왑 → None 구간 없이 즉시 교체
      3. 디렉토리 교체 → 재시작 후에도 새 인덱스 사용
    """
    FAISS_INDEX_NEW = FAISS_INDEX_PATH + "_new"
    FAISS_INDEX_OLD = FAISS_INDEX_PATH + "_old"

    print("🗄️  DB에서 전체 정책 로드 중...")
    rows = await conn.fetch("SELECT * FROM youth_policies")

    docs = []
    for row in rows:
        doc = _policy_to_doc(dict(row))
        if doc:
            docs.append(doc)
    print(f"📦 총 {len(docs)}개 문서 준비")

    # 1단계: 임시 경로에 빌드 (서비스는 기존 인덱스로 계속 운영)
    print(f"🧠 FAISS 인덱스 재빌드 중 → {FAISS_INDEX_NEW} (수 분 소요, 서비스 무중단)")
    emb = load_embeddings()
    vs  = FAISS.from_documents(docs, emb)
    if os.path.exists(FAISS_INDEX_NEW):
        shutil.rmtree(FAISS_INDEX_NEW)
    os.makedirs(FAISS_INDEX_NEW, exist_ok=True)
    vs.save_local(FAISS_INDEX_NEW)
    print(f"✅ FAISS 임시 저장 완료: {FAISS_INDEX_NEW}")

    # 2단계: 이미 로드된 vs 객체를 메모리에 원자적으로 교체 (None 구간 없음)
    from services.rag_service import hot_swap_vectorstore
    hot_swap_vectorstore(vs)

    # 3단계: 디렉토리 교체 (서버 재시작 후에도 새 인덱스 유지)
    if os.path.exists(FAISS_INDEX_OLD):
        shutil.rmtree(FAISS_INDEX_OLD)
    if os.path.exists(FAISS_INDEX_PATH):
        os.rename(FAISS_INDEX_PATH, FAISS_INDEX_OLD)
    os.rename(FAISS_INDEX_NEW, FAISS_INDEX_PATH)
    if os.path.exists(FAISS_INDEX_OLD):
        shutil.rmtree(FAISS_INDEX_OLD)
    print(f"✅ 디렉토리 교체 완료: {FAISS_INDEX_PATH}")

    return len(docs)


async def run_update(dry_run: bool = False):
    print(f"\n{'='*55}")
    print(f"🔄 온통청년 API 동기화 시작 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
    print(f"{'='*55}")

    print("🌐 온통청년 API 전체 정책 수신 중...")
    api_policies = await fetch_all_from_api()
    print(f"✅ API 수신 완료: 총 {len(api_policies)}개")

    conn = await asyncpg.connect(DATABASE_URL)
    try:
        changed = await find_changed(conn, api_policies)
        print(f"📊 변경/신규: {len(changed)}개 (전체 {len(api_policies)}개 중)")

        if dry_run:
            print("🔍 [dry-run] DB/FAISS 미수정")
            return

        if not changed:
            print("✅ 갱신 없음 — 종료")
            return

        rows = [_row(p) for p in changed if p.get("plcyNo")]
        await conn.executemany(INSERT_SQL, rows)
        print(f"✅ DB upsert 완료: {len(rows)}개")

        await rebuild_faiss(conn)

    finally:
        await conn.close()

    print(f"✅ 동기화 완료 ({datetime.now().strftime('%H:%M:%S')})\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="온통청년 API → DB/FAISS 갱신")
    parser.add_argument("--dry-run", action="store_true", help="변경사항만 확인, DB/FAISS 수정 안 함")
    args = parser.parse_args()
    asyncio.run(run_update(dry_run=args.dry_run))
