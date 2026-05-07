from dotenv import load_dotenv

load_dotenv()

import asyncio
import httpx
# build__index.py 파일 대신 fetch_and_update.py 파일 사용 + 자동 갱신 24시간 코드 대신 10시마다 데이터 갱신하는 코드로 변경 돼 주석 처리
# import json 
import os
import services.rag_service as rag
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from routers.chat import router as chat_router
from services.llm_service import OLLAMA_BASE_URL, OLLAMA_MODEL, close_http_client, _BASE_HEADERS
from services.rag_service import load_vectorstore
from services.policy_service import get_pool, close_pool
# build__index.py 파일 대신 fetch_and_update.py 파일 사용 + 자동 갱신 24시간 코드 대신 10시마다 데이터 갱신하는 코드로 변경 돼 주석 처리
# from scripts.seed_db import seed

# build__index.py 파일 대신 fetch_and_update.py 파일 사용 + 자동 갱신 24시간 코드 대신 10시마다 데이터 갱신하는 코드로 변경 돼 주석 처리        
# from scripts.build_index import build    

# build__index.py 파일 대신 fetch_and_update.py 파일 사용 + 자동 갱신 24시간 코드 대신 10시마다 데이터 갱신하는 코드로 변경 돼 주석 처리
# from data_loader import get_youth_service_list, get_gov24_service_list  

app = FastAPI(title="SPARKY AI Server")
_scheduler = AsyncIOScheduler(timezone="Asia/Seoul")

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)
app.include_router(chat_router)

# _scheduled_update()가 매일 오전 10시에 fetch_and_update.py의 run_update()를 호출해서 
# 동일한 작업을 하기 때문에 auto_refresh_task()는 필요 없어 주석 처리
# async def auto_refresh_task():
#     """24시간마다 데이터 자동 갱신"""
#     while True:
#         await asyncio.sleep(86400)  # 24시간 대기
#         print("🔄 데이터 자동 갱신 시작...")
#         try:
#             # 0. API에서 최신 데이터 가져오기 ← 추가
#             youth_raw = get_youth_service_list(os.getenv("ONTONG_API_KEY"))
#             resource_file = os.path.join(
#                 os.path.dirname(os.path.dirname(__file__)), "resource.json"
#             )
#             with open(resource_file, "w", encoding="utf-8") as f:
#                 json.dump(youth_raw, f, ensure_ascii=False)

#             gov_raw = get_gov24_service_list(os.getenv("GOV_API_KEY"))
#             gov_file = os.path.join(
#                 os.path.dirname(os.path.dirname(__file__)), "data", "gov24_data.json"
#             )
#             with open(gov_file, "w", encoding="utf-8") as f:
#                 json.dump(gov_raw, f, ensure_ascii=False)

#             # 1. seed_db.py 실행
#             await seed(resource_file)

#             # (2. build_index.py 실행 - 삭제)
#             # await asyncio.to_thread(build) 
#             # ㄴ fetch_and_update.py로 데이터 갱신하고 build_index.py 파일은 버릴 예정이므로 주석 처리    

#             # 2. FAISS 인덱스 새로고침 
#             rag._vectorstore = None  # 모듈 변수를 직접 수정 / 캐시 초기화 → 다음 요청 시 새로 로드
#             await asyncio.to_thread(load_vectorstore)

#             print("✅ 데이터 자동 갱신 완료!")
#         except Exception as e:
#             print(f"❌ 데이터 갱신 실패: {e}")

async def _init_faiss():
    print("🔍 FAISS 데이터 인덱스 로딩 중...")
    await asyncio.to_thread(load_vectorstore)
    print("✅ FAISS 인덱스 로드 완료! (RAG 준비됨)")

async def _init_db():
    await get_pool()
    print("✅ PostgreSQL 연결 풀 준비 완료!")

async def _scheduled_update():
    try:
        from scripts.fetch_and_update import run_update
        await run_update()
    except Exception as e:
        print(f"❌ [스케줄] 온통청년 API 동기화 실패: {e}")

@app.on_event("startup")
async def startup_event():
    print("🚀 SPARKY AI Server 준비 완료")
    # USE_MODEL이 ollama일 때만 Ollama 연결 확인
    if os.getenv("USE_MODEL", "gpt") == "ollama":
        await check_ollama_status()

    results = await asyncio.gather(_init_faiss(), _init_db(), return_exceptions=True)
    for r in results:
        if isinstance(r, Exception):
            print(f"❌ 초기화 실패: {r}")
            
    # 자동 갱신 태스크 시작
    # _scheduled_update()가 매일 오전 10시에 fetch_and_update.py의 run_update()를 호출해서 
    # 동일한 작업을 하기 때문에 auto_refresh_task()는 필요 없어 주석 처리
    # asyncio.create_task(auto_refresh_task())
    # print("⏰ 데이터 자동 갱신 스케줄러 시작 (24시간 주기)")

    _scheduler.add_job(_scheduled_update, "cron", hour=10, minute=0, id="ontong_sync")
    _scheduler.start()
    print("⏰ 온통청년 API 동기화 스케줄 등록 완료 (매일 10:00 KST)")

@app.on_event("shutdown")
async def shutdown_event():
    _scheduler.shutdown(wait=False)
    await asyncio.gather(close_pool(), close_http_client())
    print("👋 SPARKY AI Server 종료")

async def check_ollama_status():
    print(f"📡 Ollama 연결 확인 중... (모델: {OLLAMA_MODEL}, URL: {OLLAMA_BASE_URL})")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(
                f"{OLLAMA_BASE_URL}/api/tags",
                headers=_BASE_HEADERS,  # ← ngrok 헤더 추가
            )
            if resp.status_code == 200:
                models = [m["name"] for m in resp.json().get("models", [])]
                if any(OLLAMA_MODEL in m for m in models):
                    print(f"✅ Ollama 연결 성공! 모델 '{OLLAMA_MODEL}' 확인됨")
                else:
                    print(f"⚠️ Ollama 연결됨, 모델 '{OLLAMA_MODEL}' 없음. 설치된 모델: {models}")
                    print(f"   → 실행: ollama pull {OLLAMA_MODEL}")
            else:
                print(f"⚠️ Ollama 응답 이상: {resp.status_code}")
    except Exception as e:
        print(f"❌ Ollama 연결 실패: {e}")
        print(f"   → Ollama가 실행 중인지 확인하세요: ollama serve")
