import re
from typing import NamedTuple


class MaskingResult(NamedTuple):
    masked: str
    hit: bool


_PATTERNS: list[tuple] = [
    # R1: 주민등록번호
    (re.compile(r"\b(\d{6})-([1-4]\d{6})\b"), lambda m: "######-*******"),
    # R2: 카드번호
    (re.compile(r"\b(\d{4})[-.\s](\d{4})[-.\s](\d{4})[-.\s](\d{4})\b"), "****-****-****-****"),
    # R3: 휴대폰 번호
    (re.compile(r"\b(01[016789])[-.\s]?(\d{3,4})[-.\s]?(\d{4})\b"),
     lambda m: f"{m.group(1)}-****-****"),
    # R4: 계좌번호 (키워드 뒤에 오는 경우만)
    (re.compile(r"(?:계좌|account|acnt)\s*[번호:：]?\s*(\d[\d\-]{9,17})"),
     lambda m: m.group(0).replace(m.group(1), "[계좌번호]")),
    # R5: 이메일
    (re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b"), "[이메일]"),
]


def mask(text: str) -> MaskingResult:
    if not text:
        return MaskingResult(text, False)
    hit = False
    result = text
    for pattern, repl in _PATTERNS:
        new_result = pattern.sub(repl, result)
        if new_result != result:
            hit = True
            result = new_result
    return MaskingResult(result, hit)


def mask_sensitive(text: str) -> str:
    return mask(text).masked
