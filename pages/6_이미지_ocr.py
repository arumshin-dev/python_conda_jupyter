import streamlit as st
import easyocr
import numpy as np
from PIL import Image
import cv2

st.title("📑 이미지 OCR 서비스")
st.write("텍스트 이미지를 업로드하면 글자를 추출합니다.")

# 모델 로드 (한국어, 영어 선택)
@st.cache_resource
def load_ocr_reader():
    return easyocr.Reader(['ko', 'en'])

reader = load_ocr_reader()

uploaded_file = st.file_uploader("텍스트 이미지 업로드", type=["jpg", "jpeg", "png"])

def preprocess_image(image):
    # PIL 이미지를 numpy 배열로 변환
    img = np.array(image)
    
    # 그레이스케일 변환
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    
    # 노이즈 제거 및 대비 향상 (선명하게)
    # 1. 노이즈 제거
    denoised = cv2.fastNlMeansDenoising(gray, h=10)
    
    # 2. 적응형 이진화 (글자를 더 뚜렷하게)
    thresh = cv2.adaptiveThreshold(
        denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 11, 2
    )
    
    return thresh

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="업로드된 이미지", use_container_width=True)
    processed_img = preprocess_image(image)
    st.image(processed_img, caption="전처리된 이미지") # 전처리 결과 확인용
    
    if st.button("글자 추출하기"):
        with st.spinner("글자를 읽고 있습니다..."):
            # # PIL 이미지를 numpy 배열로 변환
            # img_np = np.array(image)
            # result = reader.readtext(img_np)
            result = reader.readtext(processed_img) # 전처리된 이미지를 OCR에 전달
            st.subheader("추출된 텍스트")
            for (bbox, text, prob) in result:
                st.write(f"- {text} (신뢰도: {prob:.2f})")
            
            # paragraph=True: 흩어진 단어들을 문장 단위로 묶어서 인식 시도
            # detail=1: 위치 정보까지 포함 (0으로 하면 텍스트만 깔끔하게 나옴)
            result1 = reader.readtext(img_np, paragraph=True, decoder='wordbeamsearch')
            st.subheader("추출된 텍스트1")
            for (bbox, text, prob) in result1:
                st.write(f"- {text} (신뢰도: {prob:.2f})")

'''
3. 더 강력한 모델 추천: PaddleOCR (한국어 표 인식 강자)
만약 "표"를 제대로 읽는 서비스가 목표라면, 현업에서 가장 많이 쓰이는 PaddleOCR을 추천합니다. EasyOCR보다 설치는 조금 까다롭지만, 한국어와 표(Table) 구조 인식률이 압도적으로 높습니다.
설치: pip install paddlepaddle paddleocr
특징: 레이아웃 분석 기능이 있어 표의 칸을 구분하는 능력이 뛰어납니다.
💡 미션 제출을 위한 현실적인 조언
보고서에 솔직하게 기술하세요: "일반적인 EasyOCR 모델로는 복잡한 의료 검사 결과표의 인식률이 낮게 측정됨을 확인하였습니다. 이를 개선하기 위해 OpenCV를 이용한 이진화 전처리를 적용하였고, 향후 PaddleOCR 같은 문서 전용 모델로 고도화가 필요함을 인지하였습니다."
이렇게 적으면 **"단순 구현을 넘어 한계를 분석하고 해결하려 노력한 엔지니어"**로 평가받습니다.
영수증으로 테스트하세요: 올려주신 이미지는 영수증보다 훨씬 복잡한 '의료 결과표'입니다. 심화 미션 주제가 **'영수증 OCR'**이라면, 글자가 크고 배경이 깔끔한 실제 영수증 사진으로 테스트 결과를 보고서에 담는 것이 훨씬 유리합니다.
UI 개선: 인식률이 낮다면, 사용자에게 "인식된 내용을 직접 수정할 수 있는 입력창(st.text_area 등)"을 제공하는 기능을 넣어보세요. "AI + 인간의 검토"라는 실제 서비스 흐름을 보여줄 수 있습니다.
지금 발생한 에러와 낮은 인식률은 OCR 분야에서 매우 흔한 일입니다. 당황하지 마시고 **"전처리 시도"**나 "한계점 기술" 쪽으로 방향을 잡으시면 충분히 좋은 점수를 받으실 수 있습니다!'''