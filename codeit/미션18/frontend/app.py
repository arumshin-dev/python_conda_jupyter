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
# st.title("🍿 영화 감상 및 리뷰 홈")

# --- [페이지 1] 영화 감상 및 리뷰 ---
def show_movie_detail(movie_id):
    st.markdown("### 🎬 영화 상세 정보")
    movie = get_movie_detail(movie_id) # Changed from get_movie to get_movie_detail
    if not movie:
        st.error("영화 정보를 찾을 수 없습니다.")
        if st.button("목록으로"):
            del st.query_params["movie_id"]
            st.rerun()
        return

    # 좌측 포스터 / 우측 상세 정보 (컴팩트 레이아웃)
    col1, col2 = st.columns([1, 2])
    with col1:
        if movie.get('poster_url'):
            try:
                resp = requests.get(movie['poster_url'], timeout=3)
                if resp.status_code == 200:
                    st.image(resp.content, use_container_width=True)
            except:
                st.warning("이미지 로드 실패")
    
    with col2:
        st.subheader(movie['title'])
        st.markdown(f"**감독**: {movie.get('director', '-')}")
        st.markdown(f"**장르**: {movie.get('genre', '-')}")
        st.markdown(f"**개봉**: {movie.get('release_date', '-')}")
        st.markdown(f"#### ⭐ **{movie.get('average_rating', 0.0)}** / 10.0")
        if st.button("⬅️ 목록으로", use_container_width=True):
            del st.query_params["movie_id"]
            st.rerun()

    st.divider()
    
    # 리뷰 섹션 (최대한 세로 길이를 압축)
    reviews = movie.get('reviews', [])
    st.markdown(f"#### 💬 리뷰 ({len(reviews)})")
    
    with st.expander("➕ 새 리뷰 작성"):
        with st.form("review_form", clear_on_submit=True):
            author = st.text_input("닉네임", "익명")
            content = st.text_area("내용")
            rating = st.slider("평점", 0.0, 10.0, 8.0, step=0.5)
            if st.form_submit_button("등록"): # Changed from st.form_submit_url_button to st.form_submit_button
                if content:
                    res = requests.post(f"{BACKEND_URL}/movies/{movie_id}/reviews", 
                                     json={"author": author, "content": content, "rating": rating, "created_at": ""})
                    if res.status_code == 200:
                        st.success("리뷰 등록 완료!")
                        st.rerun()
                else: st.warning("내용을 입력하세요")

    # 리뷰 리스트 (카드 스타일로 압축)
    for r in reversed(reviews):
        sentiment_color = "blue" if r['sentiment'] == "긍정" else "red" if r['sentiment'] == "부정" else "gray"
        with st.container(border=True):
            c1, c2 = st.columns([4, 1])
            with c1:
                st.markdown(f"**{r['author']}** <small>({r['created_at'][:10]})</small>", unsafe_allow_html=True)
                st.markdown(f"{r['content']}")
            with c2:
                st.markdown(f"⭐ {r['rating']}")
                st.markdown(f"<span style='color:{sentiment_color}; font-weight:bold;'>{r['sentiment']}</span>", unsafe_allow_html=True)

def show_home():
    # --- 상세 보기 모드 ---
    params = st.query_params
    selected_id = int(params["movie_id"]) if "movie_id" in params else None

    if selected_id:
        show_movie_detail(selected_id)
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
