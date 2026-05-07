# Python 3.11 slim image 사용
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 의존성 설치 (FAISS 등을 위해 필요할 수 있음)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# requirements.txt 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 임베딩 모델 미리 다운로드 (선택 사항, 시작 속도 향상용)
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('snunlp/KR-SBERT-V40K-klueNLI-augSTS')"

# 소스 코드 복사
COPY . .

# 데이터 및 모델 폴더 생성 (인덱스 저장용)
RUN mkdir -p data/faiss_index

# 실행 권한 부여
RUN chmod +x init.sh

# FastAPI 서버 실행 (uvicorn)
# --host 0.0.0.0 필수 (컨테이너 외부 노출용)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
