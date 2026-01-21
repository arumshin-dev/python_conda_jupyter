import streamlit as st
import requests
import os
import datetime

st.set_page_config(page_title='영화 관리자', layout="wide", page_icon="⚙️")

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")

def get_movies():
    try:
        res = requests.get(f"{BACKEND_URL}/movies", timeout=5)
        return res.json() if res.status_code == 200 else []
    except:
        return []

st.title("⚙️ 영화 데이터 관리자")

tab1, tab2 = st.tabs(["📋 영화 목록 관리", "➕ 새 영화 등록"])

with tab1:
    movies = get_movies()
    if not movies:
        st.info("등록된 영화가 없습니다.")
    else:
        for m in movies:
            with st.expander(f"🎬 {m['title']} (ID: {m['id']})"):
                with st.form(f"admin_edit_{m['id']}"):
                    u_title = st.text_input("제목", value=m['title'])
                    u_dir = st.text_input("감독", value=m['director'])
                    u_genre = st.text_input("장르", value=m['genre'])
                    u_url = st.text_input("포스터 URL", value=m['poster_url'])
                    u_date = st.text_input("개봉일 (YYYY-MM-DD)", value=m.get('release_date', ''))
                    
                    if st.form_submit_button("💾 정보 수정"):
                        requests.put(f"{BACKEND_URL}/movies/{m['id']}", 
                                     json={"title": u_title, "director": u_dir, "genre": u_genre, "poster_url": u_url, "release_date": u_date})
                        st.success("수정 완료!")
                        st.rerun()
                
                if st.button("🗑️ 영화 완전 삭제", key=f"admin_del_{m['id']}", type="primary"):
                    requests.delete(f"{BACKEND_URL}/movies/{m['id']}")
                    st.success("삭제 완료!")
                    st.rerun()

with tab2:
    with st.form("admin_add"):
        st.subheader("새 영화 추가")
        n_title = st.text_input("제목 (필수)")
        n_dir = st.text_input("감독")
        n_genre = st.text_input("장르")
        n_url = st.text_input("포스터 URL")
        n_date = st.text_input("개봉일 (YYYY-MM-DD)", value=datetime.date.today().strftime("%Y-%m-%d"))
        
        if st.form_submit_button("🚀 등록하기"):
            if n_title:
                requests.post(f"{BACKEND_URL}/movies", 
                              json={"title": n_title, "director": n_dir, "genre": n_genre, "poster_url": n_url, "release_date": n_date})
                st.success("등록 완료!")
                st.rerun()
            else:
                st.error("제목을 입력해주세요.")
