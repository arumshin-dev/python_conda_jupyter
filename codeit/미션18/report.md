# 영화 리뷰 및 하이브리드 감성 분석 서비스 보고서

## 1. 서비스 개요
본 서비스는 사용자가 영화 정보를 확인하고 리뷰를 남기면, AI가 실시간으로 리뷰의 감성(긍정/부정/중립)을 분석해주는 플랫폼입니다. 특히 **로컬 GPU를 활용한 소형 언어 모델(SLM)**과 **최신 LLM(GPT-5)**을 결합한 하이브리드 아키텍처를 통해 비용 효율성과 정확도를 동시에 달성했습니다.

## 2. 서비스 구조도 (Architecture)
서비스는 다음과 같은 최신 기술 스택으로 구성되어 있습니다:
- **Frontend**: Streamlit (인터랙티브 웹 UI)
- **Backend**: FastAPI (고성능 REST API)
- **Database**: SQLite (SQLAlchemy ORM 활용)
- **AI Model Serving**:
    - **Primary (GPU)**: `bert-base-multilingual-uncased-sentiment` 모델이 NVIDIA L4 GPU에서 구동되어 0.1초 내외로 1차 분석을 수행합니다.
    - **Secondary (LLM)**: 로컬 모델의 신뢰도가 낮을 경우(score < 0.8), OpenAI의 **GPT-5-mini** 모델이 정밀 분석을 수행하여 보완합니다.

## 3. 데이터베이스 구조 (ERD)
데이터베이스는 영화 정보를 담는 `Movie` 테이블과 리뷰 및 분석 결과를 담는 `Review` 테이블로 구성되며, 1:N 관계를 가집니다.

- **Movie**: id, title, director, genre, poster_url, release_date
- **Review**: id, movie_id, content, rating, sentiment (AI 분석 결과 저장)

## 4. AI 모델 서빙 상세 (심화)
- **GPU 가속**: 컨테이너 내부에서 NVIDIA L4 GPU를 직접 호출하여 연산 성능을 극대화했습니다.
- **하이브리드 로직**: 
    1. 로컬 모델 연산 (비용 0원, 최고 속도)
    2. 신뢰도 체크 (Confidence Score > 0.8? -> 즉시 반환)
    3. LLM Fallback (낮은 신뢰도 시 GPT-5 호출하여 정확도 보충)

## 5. 서비스 동작 확인
- **데이터 등록 현황**: 50개 이상의 영화 데이터가 등록되어 있으며, 주요 영화 3종에 대해 각각 10개 이상의 풍부한 리뷰 데이터가 AI 분석과 함께 저장되어 있습니다.
- **분석 결과 예시**:
    - "정말 감동적인 영화였습니다." -> **긍정** (Local BERT 분석)
    - "조금 지루했지만 볼만했어요." -> **중립** (Local BERT 분석)
    - "생각보다 별로였습니다." -> **부정** (GPT-5 보조 분석 가능성)
