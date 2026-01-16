import streamlit as st
import requests
import socket

# 페이지 설정 (항상 최상단에 위치)
st.set_page_config(page_title='영화 리뷰 감성 분석', layout="wide")

# 현재 실행 환경의 호스트 이름 가져오기
hostname = socket.gethostname()
st.write(hostname)
# 로컬 실행 여부 판단
if "local" in hostname.lower() or hostname.startswith("DESKTOP") or hostname.startswith("MacBook"):
    BACKEND_URL = "http://localhost:8000"
else:
    BACKEND_URL = "https://python-conda-jupyter.onrender.com/"

st.title("Streamlit Redirect Example")
st.write(f"현재 BACKEND_URL: `{BACKEND_URL}`")

# 백엔드로 이동 버튼 (JS 실행)
if st.button("백엔드로 이동"):
    # st.markdown(f'<meta http-equiv="refresh" content="0; url={BACKEND_URL}">'# 외부 URL 강제 이동 → <meta refresh> 태그 활용
    #     ,unsafe_allow_html=True
    # )
    # streamlit 에서 script 안됨
    # st.markdown(
    #     f"""
    #     <script>
    #     console.log("백엔드로 이동",{BACKEND_URL});
    #         window.location.href = "{BACKEND_URL}";
    #     </script>
    #     """,
    #     unsafe_allow_html=True
    # )
    st.markdown(
    f'<a href="{BACKEND_URL}/docs" target="_blank">👉 백엔드로 새창에서 열기-swagger</a>',
    unsafe_allow_html=True
    )
    st.markdown(f"[👉 백엔드로 이동하기-redoc]({BACKEND_URL}/redoc)", unsafe_allow_html=True)

# URL 파라미터 읽기
params = st.query_params
selected_id = int(params["movie_id"]) if "movie_id" in params else None

if selected_id:
    st.title("🎬 영화 상세")
    # 상세 페이지
    try:
        response = requests.get(f"{BACKEND_URL}/movies/{selected_id}", timeout=5)
        if response.status_code == 200:
            movie = response.json()
            st.image(movie['poster_url'], use_container_width=True)
            st.title(movie['title'])
            st.write(f"**장르:** {movie['genre']}")
            st.write(f"**감독:** {movie['director']}")
            # 목록으로 돌아가기 버튼
            if st.button("⬅️ 목록으로 돌아가기"):
                st.query_params.clear()
                st.rerun()
        else:
            st.error("영화 상세 정보를 불러올 수 없습니다.")
    except requests.exceptions.RequestException as e:
        st.error(f"백엔드 요청 실패: {e}")
else:
    st.title("🎬 영화 목록")
    try:
        response = requests.get(f"{BACKEND_URL}/movies", timeout=5)
        if response.status_code == 200:
            movies = response.json()
            cols = st.columns(3)
            for i, movie in enumerate(movies):
                with cols[i % 3]:
                    st.image(movie['poster_url'], use_container_width=True)
                    st.subheader(movie['title'])
                    st.write(f"**장르:** {movie['genre']}")
                    st.write(f"**감독:** {movie['director']}")
                    if st.button("상세보기", key=f"btn_{movie['id']}"):
                        st.query_params["movie_id"] = movie['id']
                        st.rerun()
        else:
            st.error("영화 목록을 불러올 수 없습니다.")
    except requests.exceptions.RequestException as e:
        st.error(f"백엔드 요청 실패: {e}")
