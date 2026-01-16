import streamlit as st
import requests

st.set_page_config(page_title='영화 리뷰 감성 분석', layout="wide")
BACKEND_URL = "http://localhost:8000"

st.title("🎬 영화 목록")
st.markdown("---")

# 1. 영화 목록 불러오기
try:
    response = requests.get(f"{BACKEND_URL}/movies")
    if response.status_code == 200:
        movies = response.json()
        
        # 3개의 컬럼 생성
        cols = st.columns(3)
        
        for i, movie in enumerate(movies):
            with cols[i % 3]:
                st.image(movie['poster_url'], use_container_width=True)
                st.subheader(movie['title'])
                st.write(f"**장르:** {movie['genre']}")
                st.write(f"**감독:** {movie['director']}")
                if st.button(f"상세보기", key=f"btn_{movie['id']}"):
                    st.write(f"상세보기 버튼 클릭됨: {movie['title']}")
    else:
        st.error("영화 목록을 불러오는 데 실패했습니다.")
except Exception as e:
    st.error(f"서버 연결 오류: {e}")
