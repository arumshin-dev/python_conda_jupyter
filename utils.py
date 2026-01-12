from transformers import pipeline
import streamlit as st
import pandas as pd
import plotly.express as px

@st.cache_resource
def load_model():
    return pipeline(
        "image-classification", 
        model="google/vit-base-patch16-224"
        )
def classify_and_show(image, model, title="결과"):
    results = model(image)
    st.subheader("🔎 분류 결과")
    # 상위 1개 결과 강조
    top_result = results[0]
    st.metric(label="가장 유력한 결과", value=f"{top_result['label']}")
    
    st.write("---")
    
    # 전체 순위 및 확률 시각화
    for res in results:
        label = res['label']
        score = res['score']
        
        # 라벨과 퍼센트 표시
        st.write(f"**{label}** ({score*100:.1f}%)")
        # 프로그레스 바(진행바)로 확률 시각화
        st.progress(score)
    top5 = results[:5]
    df = pd.DataFrame(top5)
    # st.subheader(f"🔎 {title}")
    # st.write(df)
    fig = px.bar(df, x="label", y="score", title=f"{title} Top-5 결과")
    st.plotly_chart(fig, key=title)
    return results

def classify_image(image, model, top_k=5):
    results = model(image)
    top5 = results[:top_k]
    df = pd.DataFrame(top5)
    return df

def s_show(idx, file_name, image, df):
    st.image(image, caption=file_name, width=400)
    st.dataframe(df)

    fig = px.bar(
        df,
        x="label",
        y="score",
        title=f"{file_name} Top-5 결과"
    )
    st.plotly_chart(fig, key=f"chart_{idx}")

