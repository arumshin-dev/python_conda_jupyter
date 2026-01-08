import streamlit as st
# HuggingFace Transformers (설치 필요)
from transformers import pipeline

st.title("🧠 AI 감성 분석기 (모델 캐싱 실습)")

# [Caching] 모델 로딩 함수 최적화 
# 이 데코레이터가 있으면 함수 결과를 캐시에 저장하여, 
# 두 번째 실행부터는 모델을 다시 로드하지 않고 캐시된 모델을 사용합니다.
@st.cache_resource
def load_model():
    # 감성 분석 모델 다운로드 (최초 1회만 실행됨)
    return pipeline("sentiment-analysis")

# 스피너로 로딩 상태 표시 
with st.spinner("AI 모델을 로딩 중입니다..."):
    classifier = load_model()

st.write("영어 문장을 입력하면 긍정(Positive)인지 부정(Negative)인지 분석합니다.")

# 사용자 입력 받기 
user_input = st.text_area("분석할 텍스트 입력", "나는 AI 엔지니어과정이 재밌습니다.")

if st.button("분석하기"): 
    if user_input:
        # 예측 수행 
        result = classifier(user_input)[0]
        label = result['label']
        score = result['score']
        
        # 결과 시각화
        col1, col2 = st.columns(2)
        with col1:
            st.metric("감성 결과", label)
        with col2:
            st.metric("확신도 (Score)", f"{score:.2%}")
            
        if label == 'POSITIVE':
            st.success("긍정적인 문장입니다! 😊")
        else:
            st.error("부정적인 문장입니다. 😞")