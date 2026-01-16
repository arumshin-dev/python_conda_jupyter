from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI()

# 영화 데이터 모델
class Movie(BaseModel):
    id: int
    title: str
    director: str
    genre: str
    poster_url: str

# 인메모리 데이터 (초기 영화 3개)
movies_db = [
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

@app.get("/movies", response_model=List[Movie])
def get_movies():
    return movies_db

@app.get("/movies/{movie_id}", response_model=Movie)
def get_movie(movie_id: int):
    movie = next((m for m in movies_db if m["id"] == movie_id), None)
    if movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie
