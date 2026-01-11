import streamlit as st
from transformers import pipeline
from PIL import Image

# 페이지 설정
st.set_page_config(page_title="이미지 분류 App", layout="centered", page_icon="🖼️")

# 제목
st.title("🖼️ 이미지 분류 앱")

# 모델 로드 (캐싱으로 속도 최적화)
@st.cache_resource
def load_model():
    # Hugging Face의 pipeline을 사용하여 모델 로드
    return pipeline("image-classification", model="google/vit-base-patch16-224")

classifier = load_model()

# UI 레이아웃
st.write("이미지를 업로드하면 AI가 무엇인지 분석해줍니다.")
# 파일 업로드
uploaded_file = st.file_uploader("이미지 파일을 선택하세요", type=["jpg", "jpeg", "png"])

# 카메라 입력
camera_file = st.camera_input("카메라로 사진 찍기")

# 업로드 또는 카메라 입력된 이미지 선택
image_source = uploaded_file if uploaded_file else camera_file

if image_source is not None:
    # 이미지 표시 (use_column_width 대신 width 사용)
    image = Image.open(image_source)
# if uploaded_file is not None:
#     # 이미지 표시
#     image = Image.open(uploaded_file)
    st.image(image, caption="업로드된 이미지", use_container_width=True)
    st.write("")
    # 분류 실행 버튼
    if st.button("분류하기"):
        with st.spinner("AI가 이미지를 분석 중입니다..."):
            # 모델 추론
            results = classifier(image)

        # 결과 출력
        st.subheader("🔎 분류 결과")
        # for result in results:
        #     st.metric(label=result["label"], value=f"{result['score']:.2f}")

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
