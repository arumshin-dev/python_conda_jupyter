from transformers import pipeline
import streamlit as st
import pandas as pd
import plotly.express as px
import time

# 기본 모델 설정
DEFAULT_MODEL = "google/vit-base-patch16-224"

@st.cache_resource
def get_image_classifier(model_name=DEFAULT_MODEL):
    """이미지 분류 모델을 로드하고 캐싱합니다."""
    return pipeline("image-classification", model=model_name)

@st.cache_resource
def get_emoji_pipeline():
    """텍스트를 이모지로 변환하는 모델을 로드하고 캐싱합니다."""
    return pipeline("text2text-generation", model="google/flan-t5-small")

def get_emoji_from_labels(labels):
    # 1. 자주 나오는 핵심 키워드 매핑 (ImageNet 기반)
    EMOJI_KEYWORD_MAP = {
        # 동물
        "cat": "🐱", "dog": "🐶", "bird": "🐦", "fish": "🐟", "insect": "🦋",
        "rabbit": "🐰", "mouse": "🐭", "horse": "🐎", "cow": "🐮", "goat": "🐐",
        "sheep": "🐑", "pig": "🐖", "chicken": "🐔", "duck": "🦆", "owl": "🦉",
        "snake": "🐍", "lizard": "🦎", "frog": "🐸", "turtle": "🐢", "bear": "🐻",
        "elephant": "🐘", "giraffe": "🦒", "rhino": "🦏", "hippopotamus": "🦛",
        "monkey": "🐒", "ape": "猿", "gorilla": "🦍", "chimpanzee": "chimp",
        "panda": "🐼", "koala": "🐨", "kangaroo": "🦘", "platypus": "🦴",
        "crocodile": "🐊", "snake": "🐍", "lizard": "🦎", "frog": "🐸", "turtle": "🐢",
        # 풍경/자연
        "mountain": "⛰️", "alp": "🏔️", "valley": "🏞️", "ocean": "🌊", "sea": "🌊", 
        "beach": "🏖️", "sand": "🏖️", "forest": "🌳", "wood": "🌳", "tree": "🌲", 
        "lake": "💧", "river": "🛶", "grass": "🌱", "field": "🌻", "garden": "🏡",
        "desert": "🌵", "snow": "❄️", "ice": "🧊", "sky": "☁️", "cloud": "☁️",
        # 장소/건물
        "house": "🏠", "building": "🏢", "city": "🏙️", "street": "🛣️", "bridge": "🌉", "castle": "🏰", "church": "⛪",
        # 사물/음식
        "car": "🚗", "bus": "🚌", "train": "🚂", "motorcycle": "🏍️", "bicycle": "🚲",
        "vehicle": "🚲", "food": "🍔", "fruit": "🍎", "bread": "🍞",
        "flower": "🌸", "tree": "🌳", "person": "👤", "man": "👨", "woman": "👩",
        "computer": "💻", "phone": "📱", "book": "📚", "clock": "⏰", "shirt": "👕",
        # LLM 카테고리용 (추가)
        "animal": "🐾", "nature": "🌲", "scenery": "🖼️", "transport": "🚀", "furniture": "🪑"
    }
    
    label_text = ", ".join(labels).lower()
    
    # 2. 키워드 기반 즉시 매핑 (가장 정확하고 빠름)
    for keyword, emoji in EMOJI_KEYWORD_MAP.items():
        if keyword in label_text:
            return emoji

    # 3. 키워드가 없을 때만 LLM(flan-t5-small)에게 "단어"를 물어본 뒤 변환
    # 이모지 대신 "animal" 같은 단어를 뱉으라고 시키는 게 T5에게는 훨씬 쉽습니다.
    pipe = get_emoji_pipeline()
    prompt = (
        "Classify the following items into one simple category word (e.g., animal, vehicle, food, tool, nature, building, person, or object).\n"
        f"Items: {label_text}\n"
        "Category:"
    )
    
    out = pipe(prompt, max_new_tokens=5)[0]["generated_text"].lower().strip()
    
    # 모델이 뱉은 카테고리 단어를 다시 이모지로 변환
    return EMOJI_KEYWORD_MAP.get(out, "🖼️") 

def run_inference(image, model):
    """이미지 분류를 수행하고 결과와 소요 시간을 반환합니다."""
    start = time.time()
    results = model(image)
    elapsed = time.time() - start

    df = pd.DataFrame(results[:5])
    return df, elapsed, results

def classify_and_show(image, model, title="결과"):
    """상세한 분류 결과와 시각화 차트를 출력합니다."""
    df, elapsed, results = run_inference(image, model)
    
    st.subheader("🔎 분류 결과")
    
    # 상위 1개 결과 강조
    top_result = results[0]
    prediction = top_result['label']
    
    # 이모지 변환 
    # emoji = get_emoji_from_text(prediction)
    labels = [r["label"] for r in results[:5]]
    emoji = get_emoji_from_labels(labels)

    st.metric(label="가장 유력한 결과", value=f"{emoji} {prediction}")
    st.write(f"⏱ 추론 시간: {elapsed:.3f}초")
    
    st.write("---")
    
    # 전체 순위 및 확률 시각화
    for res in results[:5]:
        label = res['label']
        score = res['score']
        st.write(f"**{label}** ({score*100:.1f}%)")
        st.progress(score)

    fig = px.bar(df, x="label", y="score", title=f"{title} Top-5 결과")
    st.plotly_chart(fig, key=title)
    return results

def classify_image(image, model, top_k=5):
    """이미지 분류 후 결과 DataFrame만 반환합니다."""
    df, _, _ = run_inference(image, model)
    return df.head(top_k)

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

