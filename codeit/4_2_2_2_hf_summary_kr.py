"""
🎯 FastAPI 실습: HuggingFace 요약 모델 서빙
1. Lifespan을 활용한 HuggingFace Transformers 모델 로딩
2. Pydantic BaseModel을 사용한 요청 데이터 검증
3. POST 요청으로 텍스트 요약 API 구현
4. HTTPException을 활용한 에러 처리

📌 실행 방법: 8001 포트 사용 (새로운 터미널 열어서 가상환경 설정후 실행)
python ./lab1/hf_summary_kr.py
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager
from transformers import pipeline

ml_models = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("한국어 요약 모델(KoBART) 로딩 중...")
    
    # 파이프라인 생성 (모델 이름만 한국어 모델로 교체)
    # gogamza/kobart-summarization: 한국어 뉴스/문서 요약에 특화된 유명한 모델
    ml_models["ko_summarizer"] = pipeline("summarization", model="gogamza/kobart-summarization")
    
    print("✅ 모델 로딩 완료!")
    yield
    ml_models.clear()

app = FastAPI(lifespan=lifespan)

class ArticleRequest(BaseModel):
    text: str
    min_length: int = 30        # 최소 길이 설정 가능
    max_length: int = 200       # 최대 길이 설정 가능

@app.post("/summarize-korean-simple")
def summarize_korean_simple(request: ArticleRequest):
    summarizer = ml_models.get("ko_summarizer")
    
    if len(request.text) < 50:
        raise HTTPException(status_code=400, detail="텍스트가 너무 짧습니다.")

    try:
        # 파이프라인 실행
        result = summarizer(
            request.text, 
            max_length=128,  # 요약문의 최대 길이
            min_length=32   # 요약문의 최소 길이
        )
        return {"summary": result[0]['summary_text']}
        
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="요약 실패")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)