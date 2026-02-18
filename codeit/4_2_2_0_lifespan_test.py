"""
🎯 FastAPI 실습: Lifespan 
1. Lifespan을 활용한 서버 시작/종료 시 리소스 관리
2. ML 모델을 서버 시작 시 1회만 로딩하는 패턴 이해
3. 전역 저장소를 활용한 모델 공유 방식 학습

📌 실행 방법:
uvicorn lab0.lifespan_test:app --reload
"""

# https://fastapi.tiangolo.com/advanced/events/
from fastapi import FastAPI
from contextlib import asynccontextmanager
import time

# ===============================
# Fake model loader
# ===============================
def load_model():
    time.sleep(3)
    return {"model": "fake-ml-model"}

# ===============================
# 전역 모델 저장소
# ===============================
ml_models = {}  # global dict

# ===============================
# Lifespan: 서버 시작/종료 시 리소스 관리
# ===============================
@asynccontextmanager                # ① 비동기 컨텍스트 매니저로 만들어주는 데코레이터
async def lifespan(app: FastAPI):
    # ② 서버 시작 시 실행되는 부분 (startup)
    print("====== 모델로딩중...")
    ml_models["sentiment"] = load_model()   # 모델을 메모리에 올림
    print("✅ 모델 로딩 완료")

    # ③ 여기서 "일시정지" → 서버가 요청을 받기 시작
    yield

    # ④ 서버 종료 시 실행되는 부분 (shutdown)
    print("🧹 모델 메모리 정리")
    ml_models.clear()


app = FastAPI(lifespan=lifespan)


# ===============================
# API Endpoints
# ===============================
@app.get("/predict")
def predict(text: str):
    model = ml_models["sentiment"]
    return {
        "input": text,
        "prediction": "positive",
        "model": model["model"]
    }

@app.get("/bad")
def bad_example(text: str):
    print("- 모델 매번 로딩 X")
    model = load_model()
    return {
        "input": text,
        "result": "느림",
        "model": model["model"]
    }
