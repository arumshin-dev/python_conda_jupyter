"""
🎯 FastAPI 실습: OpenAI GPT API를 활용한 텍스트 요약
1. OpenAI AsyncClient를 사용한 비동기 API 호출
2. 프롬프트 엔지니어링을 통한 역할 부여 (신문사 편집장)
3. dotenv를 활용한 API 키 환경변수 관리
4. 로컬 모델 로딩 없이 외부 API 서빙하는 패턴 이해

📌 사전 준비:
1. pip install openai python-dotenv
2. .env 파일 생성 후 OPENAI_API_KEY=sk-xxx 추가

📌 실행 방법:
python ./lab1/openai_summary.py

📌 사전 준비:
pip install gunicorn
🚀 운영 환경 실행(배포용, Gunicorn):
gunicorn lab1.openai_summary:app \
  -k uvicorn.workers.UvicornWorker \
  -w 2 \
  -b 0.0.0.0:8000
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import AsyncOpenAI
import os
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

app = FastAPI()

# OpenAI 설정
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY")) 

class ArticleRequest(BaseModel):
    text: str
    min_length: int = 30        # 최소 길이 설정 가능
    max_length: int = 200       # 최대 길이 설정 가능

@app.post("/summarize-gpt")
async def summarize_gpt(request: ArticleRequest):
    if len(request.text) < 50:
        raise HTTPException(status_code=400, details="요약할  텍스트가 없습니다.")
    
    # 모델을 로딩하지 않고 API 사용하여 GPT에게 역할을 부여하는 프롬프트 (가장 큰 차이점!)
    system_instruction = """
    너는 신문사 편집장이야. 
    사용자가 입력한 기사를 읽고, 가장 중요한 핵심 내용을 '3줄 요약' 형태로 깔끔하게 정리해줘.
    """

    try:
        # OpenAI API 비동기 호출
        # response = await client.chat.completions.create(
        #     model="gpt-4o-mini",
        #     messages = [
        #         {"role":"system", "content": system_instruction},
        #         {"role": "user", "content": request.text}
        #     ],
        #     temperature=0.3
        # )
        response = await client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": request.text}
            ],
            # max_tokens=request.max_length,
            temperature=1,
            # top_p=1,
            # frequency_penalty=0,
            # presence_penalty=0
        )
        
        # 결과 추출
        summary = response.choices[0].message.content
        return {"summary": summary}
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="OpenAI API 호출중 오류 발생")
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)