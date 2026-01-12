import streamlit as st
from utils import load_model1, run_inference
from PIL import Image
import pandas as pd

# 페이지 설정
st.set_page_config(page_title="이미지 분류 App", layout="centered", page_icon="🖼️")

# 제목
st.title("🖼️ 이미지 분류 모델 비교")

MODEL_CANDIDATES = {
    #Transformer 계열
    "ViT": "google/vit-base-patch16-224",# 기본값
    "Swin": "microsoft/swin-base-patch4-window7-224",# Swin 모델(고급 느림)
    "DeiT": "facebook/deit-base-distilled-patch16-224",# DeiT 모델(효율적 트랜스포머)
    # CNN 계열
    "ResNet50": "microsoft/resnet-50",# ResNet50 모델(빠르고 가벼움)
    "EfficientNet": "google/efficientnet-b0",# EfficientNet 모델(성능+속도 균형)
    "ConvNeXt": "facebook/convnext-base-224",# ConvNeXt 모델(최신 아키텍처CNN)

    # "clip": "openai/clip-vit-base-patch32" # CLIP 모델(멀티모달)-LABEL_0, LABEL_1 → 다른 모델과 직접 비교 불가
}
with st.sidebar:
    selected_models = st.multiselect(
        "비교할 모델 선택",
        options=list(MODEL_CANDIDATES.keys()),
        default=["ViT", "ResNet50"],
        max_selections=6
    )

    uploaded_file = st.file_uploader("이미지 업로드")
    run = st.button("비교 실행")

if uploaded_file and run:
    image = Image.open(uploaded_file)
    st.image(image, caption=f"업로드된 이미지{uploaded_file.name}", width='stretch')
    # cols = st.columns(len(selected_models))
    # cols = st.columns(3)
    # for col, model_key in zip(cols, selected_models):
    #     model_name = MODEL_CANDIDATES[model_key]

    #     with col:
    #         model = load_model1(model_name)
    #         df, elapsed = run_inference(image, model)

    #         st.subheader(f"🔎 {model_name} 결과")
    #         st.metric("⏱ 시간", f"{elapsed:.3f}s")
    #         st.success(df.iloc[0]["label"])
    #         st.bar_chart(df.set_index("label")["score"])

    summary_rows = []
    detail_results = []

    for model_key in selected_models:
        model_name = MODEL_CANDIDATES[model_key]
        model = load_model1(model_name)
        df, elapsed = run_inference(image, model)

        summary_rows.append({
            "모델": model_key,
            "Top-1": df.iloc[0]["label"],
            "확률": round(df.iloc[0]["score"], 3),
            "추론시간(s)": round(elapsed, 3),
        })
        detail_results.append((model_key, model_name, df, elapsed))
    
    summary_df = pd.DataFrame(summary_rows)
    st.subheader("📋 모델별 요약 비교")
    st.dataframe(summary_df)

    for model_key, model_name, df, elapsed in detail_results:
        with st.expander(f"🔍 {model_key} 상세 결과"):
            st.subheader(f"🔎 {model_name} 결과")
            st.metric("⏱ 시간", f"{elapsed:.3f}s")
            st.success(df.iloc[0]["label"])
            st.bar_chart(df.set_index("label")["score"])





# classifier = load_model()

# # UI 레이아웃
# st.write("이미지를 업로드하면 AI가 무엇인지 분석해줍니다.")
# # 파일 업로드
# uploaded_file = st.file_uploader("이미지 파일을 선택하세요", type=["jpg", "jpeg", "png"])

# # 카메라 입력
# camera_file = st.camera_input("카메라로 사진 찍기")

# # 업로드 또는 카메라 입력된 이미지 선택
# image_source = uploaded_file if uploaded_file else camera_file

# if image_source is not None:
#     # 이미지 표시 (use_column_width 대신 width 사용)
#     image = Image.open(image_source)
# # if uploaded_file is not None:
# #     # 이미지 표시
# #     image = Image.open(uploaded_file)
#     st.image(image, caption="업로드된 이미지", use_container_width=True)
#     st.write("")
#     # 분류 실행 버튼
#     if st.button("분류하기"):
#         with st.spinner("AI가 이미지를 분석 중입니다..."):
#             # 모델 추론
#             results = classifier(image)

#         # 결과 출력
#         st.subheader("🔎 분류 결과")
#         # for result in results:
#         #     st.metric(label=result["label"], value=f"{result['score']:.2f}")

#         # 상위 1개 결과 강조
#         top_result = results[0]
#         st.metric(label="가장 유력한 결과", value=f"{top_result['label']}")
        
#         st.write("---")
        
#         # 전체 순위 및 확률 시각화
#         for res in results:
#             label = res['label']
#             score = res['score']
            
#             # 라벨과 퍼센트 표시
#             st.write(f"**{label}** ({score*100:.1f}%)")
#             # 프로그레스 바(진행바)로 확률 시각화
#             st.progress(score)
