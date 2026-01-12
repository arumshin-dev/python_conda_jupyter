import streamlit as st
from PIL import Image
from utils import load_model, classify_and_show

model = load_model()

# --- 파일 업로드 방식 ---
st.header("📂 파일 업로드로 분류하기")
uploaded_file = st.file_uploader("이미지를 업로드하세요", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="업로드된 이미지")

    if st.button("업로드 이미지 분류하기"):
        with st.spinner("이미지를 분석 중입니다..."):
            # classify_and_show(image, model, title="결과")
            classify_and_show(image, model, title=uploaded_file.name)

        # st.subheader("🔎 분류 결과")
#         for result in results:
#             st.metric(label=result["label"], value=f"{result['score']:.2f}")