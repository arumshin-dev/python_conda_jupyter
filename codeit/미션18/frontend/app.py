import streamlit as st
import requests
import os
import datetime
import socket

# --- Configuration ---
st.set_page_config(page_title='영화 리뷰 홈', layout="wide", page_icon="🍿")

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")
hostname = socket.gethostname()

# --- Functions ---
def get_movies_all():
    try:
        res = requests.get(f"{BACKEND_URL}/movies_all", timeout=5)
        return res.json() if res.status_code == 200 else []
    except:
        return []

def get_movies():
    try:
        res = requests.get(f"{BACKEND_URL}/movies", timeout=5)
        return res.json() if res.status_code == 200 else []
    except:
        return []

def get_movie_detail(movie_id):
    try:
        res = requests.get(f"{BACKEND_URL}/movies/{movie_id}", timeout=5)
        return res.json() if res.status_code == 200 else None
    except:
        return None

# --- Main Logic ---
st.title("🍿 영화 감상 및 리뷰 홈")

# --- [페이지 1] 영화 감상 및 리뷰 ---
def show_home():
    # --- 상세 보기 모드 ---
    params = st.query_params
    selected_id = int(params["movie_id"]) if "movie_id" in params else None

    if selected_id:
        movie = get_movie_detail(selected_id)
        if movie:
            col_img, col_txt = st.columns([1, 2])
            with col_img:
                if movie.get('poster_url'):
                    try:
                        resp = requests.get(movie['poster_url'])
                        if resp.status_code == 200: 
                            st.image(resp.content, use_container_width=True)
                        else: st.warning("이미지 오류")
                    except: st.warning("이미지 없음")
            with col_txt:
                st.header(movie['title'])
                st.subheader(f"⭐ {movie.get('average_rating', 0.0)} | 🎬 {movie['director']} | 🎭 {movie['genre']}")
                st.caption(f"개봉일: {movie.get('release_date', '미정')}")
                if st.button("⬅️ 목록으로"):
                    st.query_params.clear()
                    st.rerun()

            st.divider()
            st.subheader(f"💬 리뷰 ({len(movie.get('reviews', []))})")
            
            with st.expander("✍️ 리뷰 남기기"):
                with st.form("add_review"):
                    auth = st.text_input("작성자")
                    cont = st.text_area("내용")
                    rate = st.slider("평점", 0.0, 10.0, 8.0, 0.5)
                    if st.form_submit_button("등록"):
                        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                        requests.post(f"{BACKEND_URL}/movies/{selected_id}/reviews", 
                                      json={"author": auth, "content": cont, "rating": rate, "created_at": now})
                        st.rerun()

            for rev in reversed(movie.get('reviews', [])):
                with st.container(border=True):
                    r1, r2, r3 = st.columns([1, 4, 1])
                    r1.write(f"**{rev['author']}**")
                    r1.caption(rev['created_at'])
                    color = "green" if "긍정" in rev.get('sentiment', '') else ("red" if "부정" in rev.get('sentiment', '') else "gray")
                    r2.write(rev['content'])
                    r2.markdown(f"⭐ {rev['rating']} | <span style='color:{color}'>AI: {rev['sentiment']}</span>", unsafe_allow_html=True)
                    with r3:
                        if st.button("🗑️", key=f"del_{rev['id']}"):
                            requests.delete(f"{BACKEND_URL}/reviews/{rev['id']}")
                            st.rerun()
                        if st.toggle("✏️", key=f"ed_{rev['id']}"):
                            with st.form(f"f_{rev['id']}"):
                                n_auth = st.text_input("작성자", value=rev['author'])
                                n_cont = st.text_area("내용", value=rev['content'])
                                n_rate = st.slider("평점", 0.0, 10.0, float(rev['rating']), 0.5)
                                if st.form_submit_button("수정"):
                                    requests.put(f"{BACKEND_URL}/reviews/{rev['id']}", 
                                                 json={"author": n_auth, "content": n_cont, "rating": n_rate, "created_at": rev['created_at']})
                                    st.rerun()
    else:
        # --- [목록 페이지] ---
        st.header("🍿 영화 감상실")
        
        # 1. 사이드바나 상단에서 모든 영화 정보 미리 가져오기 (필터 옵션용)
        raw_movies = get_movies_all() # raw_movies: 영화 데이터 리스트
        # st.write(f"총 영화: {len(raw_movies)}")
        genres = set()  # 중복 제거를 위해 set 사용

        for m in raw_movies:
            if m.get('genre'):
                # 콤마로 분리 후 strip()으로 공백 제거
                for g in m['genre'].split(','):
                    genres.add(g.strip())

        # 최종적으로 정렬된 리스트
        genres = sorted(genres)

        years = sorted(list(set(m['release_date'][:4] for m in raw_movies if m.get('release_date'))), reverse=True)

        # 2. 검색 UI
        with st.expander("🔍 상세 검색 및 필터", expanded=True):
            c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
            s_title = c1.text_input("영화 제목")
            s_genre = c2.selectbox("장르", ["전체"] + genres)
            s_director = c3.text_input("감독명")
            s_year = c4.selectbox("개봉년도", ["전체"] + years)

        # 3. 페이징 상태 및 필터 변경 감지
        if 'page' not in st.session_state: st.session_state.page = 1
        
        # 필터 변경 시 페이지 리셋
        filter_state = f"{s_title}_{s_genre}_{s_director}_{s_year}"
        if 'last_filter' not in st.session_state:
            st.session_state.last_filter = filter_state
        
        if st.session_state.last_filter != filter_state:
            st.session_state.page = 1
            st.session_state.last_filter = filter_state

        limit = 10
        skip = (st.session_state.page - 1) * limit

        # 4. API로 필터링된 데이터만 가져오기
        params = {"skip": skip, "limit": limit, "title": s_title, "genre": s_genre, "director": s_director, "year": s_year}
        res = requests.get(f"{BACKEND_URL}/movies", params=params)
        current_movies = res.json() if res.status_code == 200 else []
        if not current_movies:
            st.info("조건에 맞는 영화가 없습니다.")
        else:
            # 영화 그리드
            cols = st.columns(5)
            for idx, m in enumerate(current_movies):
                with cols[idx % 5]:
                    if m.get('poster_url'):
                        try: 
                            resp = requests.get(m['poster_url'])
                            if resp.status_code == 200: 
                                st.image(resp.content, use_container_width=True)
                            else: st.warning("이미지 오류")
                        except: st.warning("이미지 오류")
                    # st.markdown(f"⭐ **{m.get('average_rating', 0.0)}** | {m.get('release_date', '미정')[:4]}")
                    st.markdown(f"⭐ **{m.get('average_rating', 0.0)}** | {m.get('release_date', '미정')}")
                    st.subheader(m['title'])
                    if st.button("상세보기", key=f"v_{m['id']}", use_container_width=True):
                        st.query_params["movie_id"] = m['id']
                        st.rerun()

            # 5. 페이징 버튼 UI
            st.divider()
            col_b1, col_page, col_b2 = st.columns([1, 2, 1])
            with col_b1:
                if st.button("⬅️ 이전 페이지", disabled=st.session_state.page <= 1, use_container_width=True):
                    st.session_state.page -= 1
                    st.rerun()
            with col_page:
                st.markdown(f"<center><b>{st.session_state.page} 페이지</b></center>", unsafe_allow_html=True)
            with col_b2:
                # 다음 페이지 데이터가 있는지 확인용 (간단히 현재 데이터가 limit만큼 있으면 다음이 있다고 가정)
                if st.button("다음 페이지 ➡️", disabled=len(current_movies) < limit, use_container_width=True):
                    st.session_state.page += 1
                    st.rerun()

# 실행
if __name__ == "__main__":
    show_home()
