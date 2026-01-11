import streamlit as st
from transformers import pipeline
from PIL import Image

# st.set_page_config(page_title="Image Classification App", layout="centered")
# st.title("🖼️ 이미지 분류 앱")

@st.cache_resource
def load_model():
    return pipeline("image-classification", model="google/vit-base-patch16-224")

classifier = load_model()

# --- 파일 업로드 방식 ---
st.header("📂 파일 업로드로 분류하기")
uploaded_file = st.file_uploader("이미지를 업로드하세요", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="업로드된 이미지")

    if st.button("업로드 이미지 분류하기"):
        with st.spinner("이미지를 분석 중입니다..."):
            results = classifier(image)
        st.subheader("🔎 분류 결과")
#         for result in results:
#             st.metric(label=result["label"], value=f"{result['score']:.2f}")
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

        import plotly.express as px
        # DataFrame 변환
        import pandas as pd
        df = pd.DataFrame(results)

        # 막대 차트
        fig = px.bar(df, x="label", y="score", title="Top-5 Classification Results")
        st.plotly_chart(fig)


# # --- 카메라 입력 방식 ---
# st.header("📸 카메라로 사진 찍어 분류하기")
# camera_file = st.camera_input("사진 찍기")

# if camera_file is not None:
#     image = Image.open(camera_file)
#     st.image(image, caption="찍은 사진")

#     if st.button("카메라 이미지 분류하기"):
#         with st.spinner("이미지를 분석 중입니다..."):
#             results = classifier(image)
#         st.subheader("🔎 분류 결과")
#         for result in results:
#             st.metric(label=result["label"], value=f"{result['score']:.2f}")