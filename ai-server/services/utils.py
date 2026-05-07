from models.schemas import PolicyDomain

REGION_MAP = {
    # ── 광역시·도 풀네임 (우선 매칭) ─────────────────────────────
    "서울특별시": "seoul",    "부산광역시": "busan",
    "대구광역시": "daegu",    "인천광역시": "incheon",
    "광주광역시": "gwangju",  "대전광역시": "daejeon",
    "울산광역시": "ulsan",    "세종특별자치시": "sejong",
    "경기도": "gyeonggi",
    "강원특별자치도": "gangwon",
    "충청북도": "chungbuk",   "충청남도": "chungnam",
    "전북특별자치도": "jeonbuk", "전라북도": "jeonbuk",
    "전라남도": "jeonnam",
    "경상북도": "gyeongbuk",  "경상남도": "gyeongnam",
    "제주특별자치도": "jeju",
    # ── 광역시·도 약칭 ────────────────────────────────────────────
    "서울": "seoul",   "부산": "busan",   "대구": "daegu",
    "인천": "incheon", "광주": "gwangju", "대전": "daejeon",
    "울산": "ulsan",   "세종": "sejong",
    "경기": "gyeonggi",
    "강원": "gangwon",
    "충북": "chungbuk",  "충청북": "chungbuk",
    "충남": "chungnam",  "충청남": "chungnam",
    "전북": "jeonbuk",   "전라북": "jeonbuk",  "전북특별": "jeonbuk",
    "전남": "jeonnam",   "전라남": "jeonnam",
    "경북": "gyeongbuk", "경상북": "gyeongbuk",
    "경남": "gyeongnam", "경상남": "gyeongnam",
    "제주": "jeju",
    # ── 도 prefix 없는 시·군 단독 표기 ───────────────────────────
    # 제주
    "서귀포시": "jeju",
    # 경기
    "부천시": "gyeonggi", "광명시": "gyeonggi", "시흥시": "gyeonggi",
    "의왕시": "gyeonggi", "가평군": "gyeonggi",
    # 강원
    "동해시": "gangwon", "강릉시": "gangwon", "속초시": "gangwon",
    "원주시": "gangwon",
    # 충북
    "청주시": "chungbuk", "충주시": "chungbuk", "제천시": "chungbuk",
    "음성군": "chungbuk", "괴산군": "chungbuk",
    # 충남
    "서산시": "chungnam",
    # 전북
    "전주시": "jeonbuk", "군산시": "jeonbuk", "익산시": "jeonbuk",
    "순창군": "jeonbuk", "장수군": "jeonbuk",
    # 전남
    "순천시": "jeonnam", "해남군": "jeonnam", "완도군": "jeonnam",
    "영암군": "jeonnam",
    # 경남
    "창원시": "gyeongnam", "김해시": "gyeongnam", "통영시": "gyeongnam",
    # 경북
    "영양군": "gyeongbuk", "예천군": "gyeongbuk",
    # 부산 구
    "부산진구": "busan", "사상구": "busan", "영도구": "busan",
    "연제구": "busan",
}


def map_domain(lclsf: str, mclsf: str) -> PolicyDomain:
    target = (lclsf or "") + (mclsf or "")
    if any(kw in target for kw in ["일자리", "취업", "창업", "고용", "재직"]):
        return PolicyDomain.employment
    if any(kw in target for kw in ["주거", "주택", "월세", "전세", "거주"]):
        return PolicyDomain.housing
    if any(kw in target for kw in ["금융", "대출", "자산", "저축", "적금", "금융·복지", "금융･복지"]):
        return PolicyDomain.finance
    if any(kw in target for kw in ["교육", "학교", "장학", "학비", "직업훈련", "역량"]):
        return PolicyDomain.education
    if any(kw in target for kw in ["복지", "건강", "문화", "생활", "참여", "기반", "심리", "의료", "예술"]):
        return PolicyDomain.welfare
    return PolicyDomain.unknown


def map_region(inst_nm: str) -> str:
    if not inst_nm:
        return "central"
    for kor in sorted(REGION_MAP, key=len, reverse=True):
        if kor in inst_nm:
            return REGION_MAP[kor]
    return "central"


# 행정구역코드 2자리 prefix → region 코드
# (우편번호가 아닌 행정표준코드 — 같은 도 내 시군구는 같은 prefix 공유)
_ZIP_PREFIX_MAP: dict[str, str] = {
    "11": "seoul",    "26": "busan",    "27": "daegu",    "28": "incheon",
    "29": "gwangju",  "30": "daejeon",  "31": "ulsan",    "36": "sejong",
    "41": "gyeonggi", "42": "gangwon",  "43": "chungbuk", "44": "chungnam",
    "45": "jeonbuk",  "46": "jeonnam",  "47": "gyeongbuk","48": "gyeongnam",
    "50": "jeju",     "51": "gangwon",  "52": "jeonbuk",
}
_NATIONAL_THRESHOLD = 10  # 이 수 이상의 시/도를 포함하면 전국형으로 간주


def map_region_by_zip(zip_str: str, inst_nm: str = "") -> str:
    """
    zipCd(행정구역코드) 기반으로 region을 결정한다.
    - 단일 시/도 → 해당 region
    - 전국(≥10개 시/도) → 'central'
    - 2~9개 시/도 혼합 → 기관명 fallback, 실패 시 'central'
    - zipCd 없거나 미인식 → 기관명 fallback
    """
    if not zip_str or not zip_str.strip():
        return map_region(inst_nm)

    codes = [z.strip() for z in zip_str.split(",") if z.strip()]
    regions: set[str] = set()
    for code in codes:
        r = _ZIP_PREFIX_MAP.get(code[:2])
        if r:
            regions.add(r)

    if not regions:
        return map_region(inst_nm)
    if len(regions) >= _NATIONAL_THRESHOLD:
        return "central"
    if len(regions) == 1:
        return next(iter(regions))
    # 2~9개 시/도에 걸친 정책 → 기관명으로 재시도
    inst_result = map_region(inst_nm)
    if inst_result != "central":
        return inst_result
    # 기관명도 실패 → zipCd에서 나온 첫 번째 지역 반환 (오분류보다 나음)
    return sorted(regions)[0]


def build_period(p) -> str:
    bgn = (p.get("bizPrdBgngYmd") or "").strip()
    end = (p.get("bizPrdEndYmd") or "").strip()
    etc = (p.get("bizPrdEtcCn") or "").strip()
    if bgn and end:
        return f"{bgn[:10]} ~ {end[:10]}"
    if etc and etc not in ("기타", ""):
        return etc
    return "상시"
