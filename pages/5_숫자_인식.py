import streamlit as st
from streamlit_drawable_canvas import st_canvas
import onnxruntime as ort
import numpy as np
from PIL import Image
import requests
import os
import pandas as pd

# 1. 페이지 설정
st.set_page_config(page_title="MNIST 손글씨 인식기", layout="wide")
st.title("🖋️ MNIST 손글씨 숫자 인식 서비스")

# 2. 모델 다운로드 및 로드 (캐싱)
MODEL_URL = "https://github.com/onnx/models/raw/main/validated/vision/classification/mnist/model/mnist-8.onnx"
MODEL_PATH = "mnist.onnx"

@st.cache_resource
def load_onnx_model():
    if not os.path.exists(MODEL_PATH):
        with st.spinner("모델 다운로드 중..."):
            response = requests.get(MODEL_URL)
            with open(MODEL_PATH, "wb") as f:
                f.write(response.content)
    return ort.InferenceSession(MODEL_PATH)

session = load_onnx_model()

# 세션 상태 초기화 (이미지 저장소용)
if "history" not in st.session_state:
    st.session_state.history = []

# 레이아웃 나누기
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. 숫자 그리기")
    # 3. 입력 캔버스 (280x280 크기, 배경은 검정, 선은 흰색)
    canvas_result = st_canvas(
        fill_color="rgba(255, 255, 255, 1)",
        stroke_width=20,
        stroke_color="#FFFFFF",
        background_color="#000000",
        update_streamlit=True,
        height=280,
        width=280,
        drawing_mode="freedraw",
        key="canvas",
    )

with col2:
    if canvas_result.image_data is not None:
        st.subheader("2. 전처리 이미지")
        
        # 4. 이미지 전처리
        # RGBA -> Gray -> Resize(28x28) -> Normalize
        img = Image.fromarray(canvas_result.image_data.astype('uint8')).convert('L')
        img_resized = img.resize((28, 28))
        st.image(img_resized, width=100) # 전처리 결과 표시
        
        # 모델 입력 형식으로 변환 (1, 1, 28, 28)
        img_array = np.array(img_resized).astype('float32')
        img_array = img_array.reshape(1, 1, 28, 28)
        img_array /= 255.0  # 정규화
        
        # 5. 모델 추론
        input_name = session.get_inputs()[0].name
        outputs = session.run(None, {input_name: img_array})
        probabilities = np.exp(outputs[0][0]) / np.sum(np.exp(outputs[0][0])) # Softmax
        
        # 결과 표시
        st.subheader("3. 모델 추론 결과")
        prediction = np.argmax(probabilities)
        st.write(f"### 예측 결과: **{prediction}**")
        
        # 막대 차트 시각화
        chart_data = pd.DataFrame(probabilities, columns=["Probability"])
        st.bar_chart(chart_data)

        # 저장 버튼
        if st.button("결과 저장하기"):
            st.session_state.history.append({
                "image": img_resized,
                "label": prediction,
                "prob": probabilities[prediction]
            })

# 6. 이미지 저장소 (하단)
st.write("---")
st.subheader("📂 이미지 저장소")
if st.session_state.history:
    cols = st.columns(5)
    for i, item in enumerate(reversed(st.session_state.history)):
        with cols[i % 5]:
            st.image(item["image"], caption=f"예측: {item['label']} ({item['prob']*100:.1f}%)")
else:
    st.write("저장된 결과가 없습니다.")