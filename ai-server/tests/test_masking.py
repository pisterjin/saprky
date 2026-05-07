"""
shared/masking_cases.yaml 의 모든 케이스를 검증한다.
실행: pytest ai-server/tests/test_masking.py -v
"""
import os
import yaml
import pytest

from utils.masking import mask

YAML_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "shared", "masking_cases.yaml")


def load_cases():
    with open(YAML_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


cases = load_cases()


@pytest.mark.parametrize("case", cases.get("positive", []), ids=lambda c: c["id"])
def test_positive(case):
    result = mask(case["input"])
    assert result.hit == case["should_hit"], (
        f"[{case['id']}] hit 불일치: expected {case['should_hit']}, got {result.hit}"
    )
    assert result.masked == case["expected"], (
        f"[{case['id']}] 마스킹 결과 불일치\n  input:    {case['input']}\n"
        f"  expected: {case['expected']}\n  got:      {result.masked}"
    )


@pytest.mark.parametrize("case", cases.get("negative", []), ids=lambda c: c["id"])
def test_negative(case):
    result = mask(case["input"])
    assert result.hit == case["should_hit"], (
        f"[{case['id']}] false positive! 마스킹되지 않아야 하는 입력이 마스킹됨:\n"
        f"  input:  {case['input']}\n  output: {result.masked}"
    )
    assert result.masked == case["input"], (
        f"[{case['id']}] 텍스트가 변경됨 (마스킹 금지 대상)\n"
        f"  input:  {case['input']}\n  got:    {result.masked}"
    )
