import os
import re
import torch
import json
from openai import OpenAI
from dotenv import load_dotenv
from transformers import pipeline

# .env 파일 로드
env_path = os.path.join(os.path.dirname(__file__), ".env")
if not os.path.exists(env_path):
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")

load_dotenv(dotenv_path=env_path)
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) if api_key else None

# --- [로컬 모델 캐싱 및 로드] ---
_sentiment_pipeline = None

def get_ml_pipeline():
    global _sentiment_pipeline
    if _sentiment_pipeline is None:
        try:
            device = 0 if torch.cuda.is_available() else -1
            print(f"Loading sentiment model on device: {'GPU' if device == 0 else 'CPU'}...")
            _sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model="nlptown/bert-base-multilingual-uncased-sentiment",
                device=device
            )
            print("Model loaded successfully.")
        except Exception as e:
            print(f"로컬 모델 로드 실패: {e}")
    return _sentiment_pipeline

def ml_sentiment(text: str):
    """
    로컬 모델 분석 (BERT 1-5성 -> 긍정/부정/중립 변환)
    사용자 0-10점 체계 대응:
    - 4-5성 (긍정): 약 7-10점에 해당
    - 3성 (중립): 약 5-6점에 해당
    - 1-2성 (부정): 약 0-4점에 해당
    """
    pipe = get_ml_pipeline()
    if not pipe:
        return "중립", 0.0
    
    try:
        result = pipe(text)[0]
        label = result['label']  # '1 star' ~ '5 stars'
        score = result['score']  # 신뢰도

        stars = int(label.split()[0])
        if stars >= 4: return "긍정", score
        elif stars == 3: return "중립", score
        else: return "부정", score
    except:
        return "중립", 0.0

def analyze_sentiment(content: str):
    """Hybrid 감성 분석: 로컬 모델 + GPT-5-mini 보조"""
    
    # 1. 로컬 모델로 먼저 분석
    ml_label, ml_score = ml_sentiment(content)

    # 2. 신뢰도가 낮거나 부정확할 가능성이 있을 때만 GPT 호출
    if (ml_score < 0.85 or ml_label == "부정") and client:
        try:
            prompt = f"영화 리뷰 감성 분석. 무조건 '긍정', '부정', '중립' 중 하나만 출력.\n\n리뷰: {content}\n결과:"
            
            # gpt-5-mini 전용 호출
            response = client.responses.create(
                model="gpt-5-mini",
                input=prompt,
                max_output_tokens=256
            )

            # [핵심] 모든 output 항목을 훑어서 텍스트를 추출합니다.
            output = getattr(response, "output", [])
            for item in output:
                # 'output_text' 타입을 우선적으로 찾습니다.
                if getattr(item, 'type', '') == 'output_text':
                    con_list = getattr(item, 'content', [])
                    for c in con_list:
                        raw = getattr(c, 'text', '')
                        if raw:
                            match = re.search(r"(긍정|부정|중립)", raw)
                            if match:
                                return match.group(1)
            
            # 차선책: 전체 텍스트 필드 확인
            raw_text = getattr(response, "output_text", "")
            if raw_text:
                match = re.search(r"(긍정|부정|중립)", raw_text)
                if match:
                    return match.group(1)

        except Exception as e:
            print(f"GPT 분석 오류: {e}")
            pass 

    return ml_label
