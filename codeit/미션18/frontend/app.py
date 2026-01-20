import streamlit as st
import requests
import socket

# 페이지 설정 (항상 최상단에 위치)
st.set_page_config(page_title='영화 리뷰 감성 분석', layout="wide")

# 현재 실행 환경의 호스트 이름 가져오기
hostname = socket.gethostname()
st.write(f"현재 호스트: {hostname}")# streamlit cloud:localhost

# 로컬/클라우드 환경 구분
import os
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")
BACKEND_URL_BROWSER = os.getenv("BACKEND_URL_BROWSER", "http://localhost:8000")

st.title("🎬 영화 리뷰 감성 분석")
st.write(f"현재 BACKEND_URL: `{BACKEND_URL}`")

# 백엔드로 이동 버튼 (JS 실행)
if st.button("백엔드로 이동"):
    st.markdown(
    f'<a href="{BACKEND_URL_BROWSER}/docs" target="_blank">👉 백엔드로 새창에서 열기-swagger</a>',
    unsafe_allow_html=True
    )
    st.markdown(f"[👉 백엔드로 이동하기-redoc]({BACKEND_URL_BROWSER}/redoc)", unsafe_allow_html=True)


# URL 파라미터 읽기
params = st.query_params
selected_id = int(params["movie_id"]) if "movie_id" in params else None

if selected_id:
    st.title("🎬 영화 상세 및 수정")
    try:
        response = requests.get(f"{BACKEND_URL}/movies/{selected_id}", timeout=5)
        if response.status_code == 200:
            movie = response.json()
            
            col1, col2 = st.columns([1, 2])
            with col1:
                if movie['poster_url'] and movie['poster_url'].startswith(('http', 'https')):
                    st.image(movie['poster_url'], width='stretch')
                else:
                    st.warning("유효하지 않은 포스터 URL입니다.")
            
            with col2:
                # 수정 폼
                with st.form("update_movie_form"):
                    st.subheader("정보 수정")
                    edit_title = st.text_input("제목", value=movie['title'])
                    edit_director = st.text_input("감독", value=movie['director'])
                    edit_genre = st.text_input("장르", value=movie['genre'])
                    edit_poster = st.text_input("포스터 URL", value=movie['poster_url'])
                    
                    update_submitted = st.form_submit_button("변경사항 저장")
                    if update_submitted:
                        updated_data = {
                            "title": edit_title,
                            "director": edit_director,
                            "genre": edit_genre,
                            "poster_url": edit_poster
                        }
                        upd_res = requests.put(f"{BACKEND_URL}/movies/{selected_id}", json=updated_data, timeout=5)
                        if upd_res.status_code == 200:
                            st.success("수정되었습니다!")
                            st.rerun()
                        else:
                            st.error("수정 실패")

            # 버튼들 (목록으로, 삭제)
            col_b1, col_b2 = st.columns([1, 1])
            with col_b1:
                if st.button("⬅️ 목록으로 돌아가기"):
                    st.query_params.clear()
                    st.rerun()
            with col_b2:
                if st.button("🗑️ 영화 삭제", type="primary"):
                    del_res = requests.delete(f"{BACKEND_URL}/movies/{selected_id}", timeout=5)
                    if del_res.status_code == 200:
                        st.success("삭제되었습니다!")
                        st.query_params.clear()
                        st.rerun()
                    else:
                        st.error("삭제 실패")
        else:
            st.error("영화 상세 정보를 불러올 수 없습니다.")
    except requests.exceptions.RequestException as e:
        st.error(f"백엔드 요청 실패: {e}")

else:
    # 1. 등록 폼 (목록 상단)
    with st.form("add_movie_form"): 
        st.subheader("새 영화 등록") 
        title = st.text_input("제목") 
        director = st.text_input("감독") 
        genre = st.text_input("장르") 
        poster_url = st.text_input("포스터 URL") 
        submitted = st.form_submit_button("등록") 
        if submitted: 
            new_movie = { 
                "title": title, 
                "director": director, 
                "genre": genre, 
                "poster_url": poster_url 
                } 
            try: 
                response = requests.post(f"{BACKEND_URL}/movies", json=new_movie, timeout=5)
                if response.status_code == 200: 
                    st.success("영화가 등록되었습니다!") 
                    st.rerun() 
                else: st.error("등록 실패") 
            except requests.exceptions.RequestException as e: 
                st.error(f"백엔드 요청 실패: {e}")

    # 2. 영화 목록
    st.title("🎬 영화 목록")
    try:
        response = requests.get(f"{BACKEND_URL}/movies", timeout=5)
        if response.status_code == 200:
            movies = response.json()
            st.write(f"전체 영화 수: {len(movies)}개")
            cols = st.columns(3)
            for i, movie in enumerate(movies):
                with cols[i % 3]:
                    if movie['poster_url'] and movie['poster_url'].startswith(('http', 'https')):
                        st.image(movie['poster_url'], width='stretch')
                    else:
                        st.info("포스터 없음")
                    st.subheader(movie['title'])
                    st.write(f"**장르:** {movie['genre']}")
                    st.write(f"**감독:** {movie['director']}")
                    if st.button("상세보기/수정", key=f"btn_{movie['id']}"):
                        st.query_params["movie_id"] = movie['id']
                        st.rerun()
                    if st.button("🗑️ 영화 삭제", type="primary", key=f"del_{movie['id']}"):
                        del_res = requests.delete(f"{BACKEND_URL}/movies/{movie['id']}", timeout=5)
                        if del_res.status_code == 200:
                            st.success("삭제되었습니다!")
                            st.rerun()
                        else:
                            st.error("삭제 실패")
        else:
            st.error("영화 목록을 불러올 수 없습니다.")
    except requests.exceptions.RequestException as e:
        st.error(f"백엔드 요청 실패: {e}")
