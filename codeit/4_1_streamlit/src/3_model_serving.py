import streamlit as st
# HuggingFace Transformers (설치 필요)
from transformers import pipeline
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification

st.title("🧠 AI 감성 분석기 (모델 캐싱 실습)")

# [Caching] 모델 로딩 함수 최적화 
# 이 데코레이터가 있으면 함수 결과를 캐시에 저장하여, 
# 두 번째 실행부터는 모델을 다시 로드하지 않고 캐시된 모델을 사용합니다.
# @st.cache_resource
# def load_model():
#     # 감성 분석 모델 다운로드 (최초 1회만 실행됨)
#     return pipeline("sentiment-analysis")

# "monologg/kobert" → 한국어 BERT 기반 모델 (다만 직접 fine-tuning된 감성 분석 버전은 따로 필요할 수 있음)
# "nlptown/bert-base-multilingual-uncased-sentiment" → 다국어 지원, 한국어 포함
# "j-hartmann/emotion-english-distilroberta-base" 같은 모델은 영어 전용이라 한국어에는 적합하지 않음
@st.cache_resource
def load_model():
    # 한국어/다국어 감성 분석 모델 지정
    # return pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment")
    models = { 
        "영어 기본": pipeline("sentiment-analysis"), 
        "다국어 BERT": pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment"), 
        # "KoBERT": pipeline("sentiment-analysis", model="monologg/kobert") 
        } 
    return models

# 스피너로 로딩 상태 표시 
with st.spinner("AI 모델을 로딩 중입니다..."):
    # classifier = load_model()
    classifiers = load_model()
# st.write(classifiers)
st.write("영어 문장을 입력하면 긍정(Positive)인지 부정(Negative)인지 분석합니다.")

# 사용자 입력 받기 
user_input = st.text_area("분석할 텍스트 입력", "나는 AI 엔지니어과정이 재밌습니다.")
if st.button("분석하기"):
    if user_input.strip():
        print("clf exists:", "clf" in globals())

        cols = st.columns(len(classifiers))
        for i, (name, clf) in enumerate(classifiers.items()):
            result = clf(user_input)[0]
            label = result['label']
            score = result['score']
            
            with cols[i]:
                st.subheader(name)
                st.metric("감성 결과", label)
                st.metric("확신도", f"{score:.2%}")
                st.progress(score)
    else:
        st.warning("분석할 텍스트를 입력해주세요!")
'''
if st.button("분석하기"): 
    if user_input.strip():
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
            st.progress(score) # progress bar 시각화
            
        # 임계값 설정
        if score < 0.7:
            # st.warning("확신도가 낮습니다. 다른 문장으로 재시도해주세요.")
            st.info("🤔 AI가 확신하지 못하는 문장입니다.")
        else:
            if label == 'POSITIVE':
                st.success("긍정적인 문장입니다! 😊")
            else:
                st.error("부정적인 문장입니다. 😞")
    else:
        st.warning("분석할 텍스트를 입력해주세요!")  # 빈 입력값 방지
'''
