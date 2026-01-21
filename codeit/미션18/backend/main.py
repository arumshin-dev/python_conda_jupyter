from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
import uvicorn
from contextlib import asynccontextmanager

import database, models, schemas, crud

# DB 테이블 생성
models.Base.metadata.create_all(bind=database.engine)

# Lifespan 관리 (startup/shutdown)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 앱 시작 시 초기 데이터 확인
    db = database.SessionLocal()
    try:
        crud.init_db(db)
    finally:
        db.close()
    yield

app = FastAPI(lifespan=lifespan)

# DB 세션 의존성
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"status": "ok", "mode": "database_refactored"}

# 초기화 수동 트리거 (기존 기능 유지)
@app.post("/set3movies")
def set3movies(db: Session = Depends(get_db)):
    crud.init_db(db)
    return {"message": "3 movies set successfully or already exist"}

# 영화 목록 조회
@app.get("/movies_all", response_model=List[schemas.Movie])
def get_movies_all(db: Session = Depends(get_db)):
    return crud.get_movies_all(db)

@app.get("/movies", response_model=List[schemas.Movie])
def get_movies(
    skip: int = 0, 
    limit: int = 100, 
    title: str = None, 
    genre: str = None, 
    director: str = None, 
    year: str = None,
    db: Session = Depends(get_db)
):
    return crud.get_movies(db, skip=skip, limit=limit, title=title, genre=genre, director=director, year=year)

# 영화 상세 조회
@app.get("/movies/{movie_id}", response_model=schemas.Movie)
def get_movie(movie_id: int, db: Session = Depends(get_db)):
    movie = crud.get_movie(db, movie_id)
    if movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie

# 영화 등록
@app.post("/movies", response_model=schemas.Movie)
def add_movie(movie: schemas.MovieCreate, db: Session = Depends(get_db)):
    return crud.create_movie(db, movie)

# 영화 수정
@app.put("/movies/{movie_id}", response_model=schemas.Movie)
def update_movie(movie_id: int, movie_data: schemas.MovieCreate, db: Session = Depends(get_db)):
    movie = crud.update_movie(db, movie_id, movie_data)
    if movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie

# 영화 삭제
@app.delete("/movies/{movie_id}")
def delete_movie(movie_id: int, db: Session = Depends(get_db)):
    success = crud.delete_movie(db, movie_id)
    if not success:
        raise HTTPException(status_code=404, detail="Movie not found")
    return {"message": "Movie deleted successfully"}

# 리뷰 등록
@app.post("/movies/{movie_id}/reviews", response_model=schemas.Review)
def add_review(movie_id: int, review: schemas.ReviewCreate, db: Session = Depends(get_db)):
    return crud.create_review(db, movie_id, review)

# 리뷰 삭제
@app.delete("/reviews/{review_id}")
def delete_review(review_id: int, db: Session = Depends(get_db)):
    success = crud.delete_review(db, review_id)
    if not success:
        raise HTTPException(status_code=404, detail="Review not found")
    return {"message": "Review deleted successfully"}

# 리뷰 수정
@app.put("/reviews/{review_id}", response_model=schemas.Review)
def update_review(review_id: int, review: schemas.ReviewCreate, db: Session = Depends(get_db)):
    updated_review = crud.update_review(db, review_id, review)
    if updated_review is None:
        raise HTTPException(status_code=404, detail="Review not found")
    return updated_review

if __name__ == "__main__":
    uvicorn.run("codeit.미션18.backend.main:app", host="0.0.0.0", port=8000, reload=True)
# python codeit/미션18/backend/main.py
# uvicorn codeit.미션18.backend.main:app --reload --port 8000