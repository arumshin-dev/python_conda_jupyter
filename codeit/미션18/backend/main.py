from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
import os
import uvicorn

# DB 관련 임포트 
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# DB 연결
SQLALCHEMY_DATABASE_URL = "sqlite:///./movies.db"  # 예시: SQLite 사용
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# Base 클래스 선언
Base = declarative_base()

# 세션 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
from sqlalchemy import Column, Integer, String, Float, ForeignKey,Date

class MovieModel(Base):
    __tablename__ = "movies"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    director = Column(String)
    genre = Column(String)
    poster_url = Column(String)

# DB 테이블 생성
Base.metadata.create_all(bind=engine)

app = FastAPI()

# DB 세션 의존성
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic 모델
class MovieCreate(BaseModel):
    title: str
    director: str
    genre: str
    poster_url: str

class Movie(BaseModel):
    id: int
    title: str
    director: str
    genre: str
    poster_url: str

    class Config:
        from_attributes = True

@app.get("/")
def read_root():
    return {"status": "ok", "mode": "database"}

initial_movies = [
    MovieModel(title="타이타닉", director="제임스 카메론", genre="로맨스", poster_url="https://media.themoviedb.org/t/p/w300_and_h450_face/132KjhVrWUqKFVfMAKKNkherytA.jpg"),
    MovieModel(title="해리포터와 마법사의 돌", director="크리스 콜럼버스", genre="판타지", poster_url="https://media.themoviedb.org/t/p/w300_and_h450_face/8YaP48tVfngbURGldWk1I5odsBK.jpg"),
    MovieModel(title="인셉션", director="크리스토퍼 놀란", genre="SF", poster_url="https://media.themoviedb.org/t/p/w300_and_h450_face/zTgjeblxSLSvomt6F6UYtpiD4n7.jpg")
]
# 초기 데이터 삽입 (DB가 비어있을 때만)
@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    if db.query(MovieModel).count() == 0:
        db.add_all(initial_movies)
        db.commit()
    db.close()
@app.post("/set3movies")
def set3movies(db: Session = Depends(get_db)):
    db.add_all(initial_movies)
    db.commit()
    return {"message": "3 movies set successfully"}

# 영화 목록 조회
@app.get("/movies", response_model=List[Movie])
def get_movies(db: Session = Depends(get_db)):
    return db.query(MovieModel).all()

# 영화 상세 조회
@app.get("/movies/{movie_id}", response_model=Movie)
def get_movie(movie_id: int, db: Session = Depends(get_db)):
    movie = db.query(MovieModel).filter(MovieModel.id == movie_id).first()
    if movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie

# 영화 등록
@app.post("/movies", response_model=Movie)
def add_movie(movie: MovieCreate, db: Session = Depends(get_db)):
    new_movie = MovieModel(**movie.dict())
    db.add(new_movie)
    db.commit()
    db.refresh(new_movie)
    return new_movie

# 영화 수정
@app.put("/movies/{movie_id}", response_model=Movie)
def update_movie(movie_id: int, movie_data: MovieCreate, db: Session = Depends(get_db)):
    db_movie = db.query(MovieModel).filter(MovieModel.id == movie_id).first()
    if not db_movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    for key, value in movie_data.dict().items():
        setattr(db_movie, key, value)
    
    db.commit()
    db.refresh(db_movie)
    return db_movie

# 영화 삭제
@app.delete("/movies/{movie_id}")
def delete_movie(movie_id: int, db: Session = Depends(get_db)):
    db_movie = db.query(MovieModel).filter(MovieModel.id == movie_id).first()
    if not db_movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    db.delete(db_movie)
    db.commit()
    return {"message": "Movie deleted successfully"}

if __name__ == "__main__":
    uvicorn.run("codeit.미션18.backend.main:app", host="0.0.0.0", port=8000, reload=True)
# python codeit/미션18/backend/main.py
# uvicorn codeit.미션18.backend.main:app --reload --port 8000