"""
SPARKY 테스트 공통 픽스처
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from fastapi.testclient import TestClient
from main import app

# ── 공통 픽스처 ──────────────────────────────────────────────

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def user_seoul_25():
    return {
        "ageGroup": "youth_25_29",
        "gender": "male",
        "region": "seoul",
        "uuid": "test-uuid-1234"
    }

@pytest.fixture
def user_busan_22():
    return {
        "ageGroup": "youth_19_24",
        "gender": "female",
        "region": "busan",
        "uuid": "test-uuid-5678"
    }

@pytest.fixture
def welcome_msg():
    return {
        "id": "welcome",
        "role": "assistant",
        "content": "안녕하세요! 저는 SPARKY예요 :)",
        "timestamp": 1700000000
    }

def make_user_msg(content: str, idx: int = 1):
    return {"id": f"u_{idx}", "role": "user", "content": content, "timestamp": 1700000000 + idx}

def make_ai_msg(content: str, idx: int = 2):
    return {"id": f"a_{idx}", "role": "assistant", "content": content, "timestamp": 1700000000 + idx}
