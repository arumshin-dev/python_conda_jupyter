from fastapi import FastAPI, HTTPException, Depends 
from pydantic import BaseModel
from typing import List
import os
import uvicorn

app = FastAPI()



@app.get("/")
def read_root():
    return {"status": "ok"}

# 영화 등록 요청 데이터 모델
class MovieCreate(BaseModel):
    title: str
    director: str
    genre: str
    poster_url: str

# 영화 데이터 모델
class Movie(BaseModel):
    id: int
    title: str
    director: str
    genre: str
    poster_url: str

    class Config:
        from_attributes = True # ✅ Pydantic V2 방식

# 초기 영화 데이터
MOVIES_DB = [
    {
        "id": 1,
        "title": "타이타닉",
        "director": "제임스 카메론",
        "genre": "로맨스",
        "poster_url": "https://media.themoviedb.org/t/p/w300_and_h450_face/132KjhVrWUqKFVfMAKKNkherytA.jpg"
    },
    {
        "id": 2,
        "title": "해리포터와 마법사의 돌",
        "director": "크리스 콜럼버스",
        "genre": "판타지",
        "poster_url": "https://media.themoviedb.org/t/p/w300_and_h450_face/8YaP48tVfngbURGldWk1I5odsBK.jpg"
    },
    {
        "id": 3,
        "title": "인셉션",
        "director": "크리스토퍼 놀란",
        "genre": "SF",
        "poster_url": "https://media.themoviedb.org/t/p/w300_and_h450_face/zTgjeblxSLSvomt6F6UYtpiD4n7.jpg"
    }
]

# 영화 목록 조회
@app.get("/movies", response_model=List[Movie])
def get_movies():
    return MOVIES_DB

# 영화 상세 조회
@app.get("/movies/{movie_id}", response_model=Movie)
def get_movie(movie_id: int):
    movie = next((m for m in MOVIES_DB if m["id"] == movie_id), None)
    if movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie

# 영화 등록
@app.post("/movies", response_model=Movie)
def add_movie(movie: MovieCreate):
    new_id = max([m["id"] for m in MOVIES_DB]) + 1 if MOVIES_DB else 1
    new_movie = {"id": new_id, **movie.dict()}
    MOVIES_DB.append(new_movie)
    return new_movie

# 영화 수정
@app.put("/movies/{movie_id}", response_model=Movie)
def update_movie(movie_id: int, movie_data: MovieCreate):
    for i, m in enumerate(MOVIES_DB):
        if m["id"] == movie_id:
            updated_movie = {"id": movie_id, **movie_data.dict()}
            MOVIES_DB[i] = updated_movie
            return updated_movie
    raise HTTPException(status_code=404, detail="Movie not found")

# 영화 삭제
@app.delete("/movies/{movie_id}")
def delete_movie(movie_id: int):
    global MOVIES_DB
    MOVIES_DB = [m for m in MOVIES_DB if m["id"] != movie_id]
    return {"message": "Movie deleted successfully"}

# uvicorn codeit.미션18.backend.main:app --host 0.0.0.0 --port $PORT
if __name__ == "__main__":
    uvicorn.run(
        "codeit.미션18.backend.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000))
    )
# python codeit/미션18/backend/main.py
