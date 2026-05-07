"""
resource.json → PostgreSQL 데이터 적재 스크립트

사용법:
    python scripts/seed_db.py
    python scripts/seed_db.py --file ../resource.json
"""

import os
import sys
import json
import argparse
import asyncio
from datetime import datetime
import asyncpg
from dotenv import load_dotenv

# ai-server 루트를 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

DATABASE_URL  = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/sparky")
DEFAULT_FILE  = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "resource.json")

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


async def seed(file_path: str):
    print(f"📂 파일 로드 중: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    policies = data.get("result", {}).get("youthPolicyList", [])
    print(f"📦 총 {len(policies)}개 정책 발견")

    conn = await asyncpg.connect(DATABASE_URL)
    try:
        rows = [_row(p) for p in policies if p.get("plcyNo")]
        skipped = len(policies) - len(rows)
        if skipped:
            print(f"⚠️  plcyNo 없는 항목 {skipped}개 스킵")

        # executemany로 일괄 처리
        await conn.executemany(INSERT_SQL, rows)
        print(f"✅ {len(rows)}개 정책 적재 완료 (upsert — 중복 시 업데이트)")
    finally:
        await conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="resource.json → PostgreSQL 적재")
    parser.add_argument("--file", default=DEFAULT_FILE, help="resource.json 경로")
    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"❌ 파일 없음: {args.file}")
        sys.exit(1)

    asyncio.run(seed(args.file))
