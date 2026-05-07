import os
import asyncpg
from models.schemas import PolicyCard
from services.utils import map_domain, build_period

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5433/sparky")

_pool: asyncpg.Pool | None = None

_FETCH_COLUMNS = """
    "plcyNo", "plcyNm", "plcyExplnCn", "plcySprtCn",
    "lclsfNm", "mclsfNm",
    "sprtTrgtMinAge", "sprtTrgtMaxAge",
    "bizPrdBgngYmd", "bizPrdEndYmd", "bizPrdEtcCn",
    "aplyUrlAddr", "refUrlAddr1"
"""


async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=5)
    return _pool


async def close_pool():
    global _pool
    if _pool:
        await _pool.close()
        _pool = None


def _build_target(row: asyncpg.Record) -> str:
    try:
        mn = int(row["sprtTrgtMinAge"] or 0)
        mx = int(row["sprtTrgtMaxAge"] or 0)
    except (ValueError, TypeError):
        mn, mx = 0, 0
    if mn == 0 and mx == 0:
        return "전 연령 청년"
    return f"만 {mn}~{mx}세"


def _get_url(row: asyncpg.Record) -> str:
    return (
        (row["aplyUrlAddr"] or "").strip()
        or (row["refUrlAddr1"] or "").strip()
        or "https://www.youthcenter.go.kr"
    )


_DATE_FILTER = """AND (
    "bizPrdEndYmd" IS NULL
    OR "bizPrdEndYmd" = ''
    OR (LENGTH("bizPrdEndYmd") <= 6 AND "bizPrdEndYmd" >= TO_CHAR(CURRENT_DATE, 'YYYYMM'))
    OR (LENGTH("bizPrdEndYmd") > 6 AND "bizPrdEndYmd" >= TO_CHAR(CURRENT_DATE, 'YYYYMMDD'))
)"""


async def find_ids_by_name(names: list[str], include_expired: bool = False) -> list[str]:
    """정책명으로 DB에서 plcyNo를 조회한다 (LLM이 RECOMMEND 태그를 누락했을 때 fallback)."""
    if not names:
        return []
    date_clause = "" if include_expired else _DATE_FILTER
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            result = []
            for name in names:
                name = name.strip()
                if not name:
                    continue
                rows = await conn.fetch(
                    f'SELECT "plcyNo" FROM youth_policies WHERE "plcyNm" = $1 {date_clause} LIMIT 1',
                    name,
                )
                result.extend(row["plcyNo"] for row in rows)
            return result
    except Exception as e:
        print(f"❌ [DB] 정책명 검색 오류: {e}")
        return []


async def filter_valid_ids(ids: list[str], include_expired: bool = False) -> list[str]:
    """DB에 실제 존재하는 ID만 반환. include_expired=False면 만료 정책도 제외."""
    if not ids:
        return []
    date_clause = "" if include_expired else _DATE_FILTER
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                f'SELECT "plcyNo" FROM youth_policies WHERE "plcyNo" = ANY($1::text[]) {date_clause}',
                ids,
            )
        valid = {row["plcyNo"] for row in rows}
        return [i for i in ids if i in valid]
    except Exception as e:
        print(f"❌ [DB] ID 검증 오류: {e}")
        return ids


async def fetch_policies_by_ids(ids: list[str], include_expired: bool = False) -> list[PolicyCard]:
    if not ids:
        return []

    date_clause = "" if include_expired else _DATE_FILTER
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                f'SELECT {_FETCH_COLUMNS} FROM youth_policies WHERE "plcyNo" = ANY($1::text[]) {date_clause}',
                ids,
            )
    except Exception as e:
        print(f"❌ [DB] 정책 조회 오류: {e}")
        return []

    row_map = {row["plcyNo"]: row for row in rows}
    cards = []
    for pid in ids:
        row = row_map.get(pid)
        if not row:
            print(f"⚠️ [DB] ID 없음: {pid}")
            continue
        try:
            domain = map_domain(row["lclsfNm"] or "", row["mclsfNm"] or "")
            cards.append(PolicyCard(
                id       = pid,
                title    = row["plcyNm"] or "정책명 없음",
                summary  = (row["plcyExplnCn"] or "")[:300],
                domain   = domain,
                target   = _build_target(row),
                benefit  = (row["plcySprtCn"] or "상세 내용 참조")[:80],
                period   = build_period(row),
                applyUrl = _get_url(row),
                source   = "youth",
                endDate  = (row["bizPrdEndYmd"] or "").strip() or None,
            ))
        except Exception as e:
            print(f"⚠️ [DB] 카드 생성 오류 ({pid}): {e}")

    return cards
