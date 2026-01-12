import streamlit as st
from PIL import Image
from utils import load_model, classify_and_show

st.title("📸 카메라 이미지 분류")

model = load_model()

camera_file = st.camera_input("사진 찍기")

if camera_file:
    image = Image.open(camera_file)
    st.image(image, caption="찍은 사진", width="stretch")

    if st.button("분류하기"):
        classify_and_show(image, model, title=camera_file.name)
        # results = classifier(image)
        # st.subheader("🔎 결과")
        # for result in results:
        #     st.metric(result["label"], f"{result['score']:.2f}")
        # # 상위 1개 결과 강조
        # top_result = results[0]
        # st.metric(label="가장 유력한 결과", value=f"{top_result['label']}")
        
        # st.write("---")
        
        # # 전체 순위 및 확률 시각화
        # for res in results:
        #     label = res['label']
        #     score = res['score']
            
        #     # 라벨과 퍼센트 표시
        #     st.write(f"**{label}** ({score*100:.1f}%)")
        #     # 프로그레스 바(진행바)로 확률 시각화
        #     st.progress(score)

        # import altair as alt
        # import pandas as pd

        # df = pd.DataFrame(results)

        # chart = alt.Chart(df).mark_bar().encode(
        #     x="label",
        #     y="score"
        # ).properties(title="Top-5 Classification Results")

        # st.altair_chart(chart, width="stretch")
