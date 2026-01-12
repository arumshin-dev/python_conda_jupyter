import streamlit as st
from PIL import Image
from utils import load_model, classify_image, s_show

st.title("📂 여러 이미지 한 번에 분류")

model = load_model()

# session_state 초기화
if "results" not in st.session_state:
    st.session_state.results = []

# 🔎 결과 먼저 출력
if st.session_state.results:
    st.subheader("🔎 분석 결과")
    for idx, (file_name, image, df) in enumerate(st.session_state.results):
        s_show(idx, file_name, image, df)

# # 여러 파일 업로드 허용
# uploaded_files = st.file_uploader(
#     "이미지를 여러 장 업로드하세요",
#     type=["jpg", "jpeg", "png"],
#     accept_multiple_files=True
# )
with st.sidebar:
    st.header("📤 이미지 업로드")

    uploaded_files = st.file_uploader(
        "이미지를 여러 장 업로드하세요",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True
    )

    classify_clicked = st.button("분류하기")

# if uploaded_files and st.button("분류하기"):
if uploaded_files and classify_clicked:
    # st.session_state.results = []  # 이전 결과 초기화

    for file in uploaded_files:
        image = Image.open(file)
        df = classify_image(image, model)

        st.session_state.results.append(
            (file.name, image, df)
        )

#     st.rerun()  # ✅ 최신 API
