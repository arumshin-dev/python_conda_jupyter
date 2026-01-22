from sqlalchemy.orm import Session
import models, schemas

import os
import json
from sentiment import analyze_sentiment

from sqlalchemy import func

# Movie CRUD
def get_movies_all(db: Session):
    return db.query(models.Movie).all()
def get_movies(db: Session, skip: int = 0, limit: int = 100, 
               title: str = None, genre: str = None, 
               director: str = None, year: str = None):
    # 기본 쿼리: 영화 정보와 리뷰 평균 점수를 JOIN해서 가져옴
    # outerjoin을 써야 리뷰가 없는 영화도 나옵니다.
    query = db.query(
        models.Movie,
        func.avg(models.Review.rating).label("average_rating")
    ).outerjoin(models.Review).group_by(models.Movie.id)

    # SQL WHERE 필터링
    if title:
        query = query.filter(models.Movie.title.ilike(f"%{title.strip()}%"))
    if genre and genre != "전체":
        # query = query.filter(models.Movie.genre == genre)
        query = query.filter(models.Movie.genre.contains(genre))
    if director:
        query = query.filter(models.Movie.director.ilike(f"%{director.strip()}%"))
    if year and year != "전체":
        query = query.filter(models.Movie.release_date.startswith(year.strip()))

    results = query.offset(skip).limit(limit).all()
    
    # 결과를 Pydantic 모델에 맞게 변환 (평균 점수 주입)
    movies = []
    for movie_obj, avg_rating in results:
        # DB 객체에 동적으로 average_rating 속성 추가
        movie_obj.average_rating = round(avg_rating, 1) if avg_rating else 0.0
        movies.append(movie_obj)
        
    return movies

def get_movie(db: Session, movie_id: int):
    movie = db.query(models.Movie).filter(models.Movie.id == movie_id).first()
    if movie:
        # 상세 조회 시에도 평균 점수 계산 (SQL 1회 더 실행)
        avg = db.query(func.avg(models.Review.rating)).filter(models.Review.movie_id == movie_id).scalar()
        movie.average_rating = round(avg, 1) if avg else 0.0
    return movie

def create_movie(db: Session, movie: schemas.MovieCreate):
    db_movie = models.Movie(**movie.model_dump())
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)
    return db_movie

def update_movie(db: Session, movie_id: int, movie_data: schemas.MovieCreate):
    db_movie = db.query(models.Movie).filter(models.Movie.id == movie_id).first()
    if db_movie:
        for key, value in movie_data.model_dump().items():
            setattr(db_movie, key, value)
        db.commit()
        db.refresh(db_movie)
    return db_movie

def delete_movie(db: Session, movie_id: int):
    db_movie = db.query(models.Movie).filter(models.Movie.id == movie_id).first()
    if db_movie:
        db.delete(db_movie)
        db.commit()
        return True
    return False

# Review CRUD 추가
def get_reviews(db: Session, movie_id: int):
    return db.query(models.Review).filter(models.Review.movie_id == movie_id).all()

def create_review(db: Session, movie_id: int, review: schemas.ReviewCreate):
    sentiment = analyze_sentiment(review.content)
    db_review = models.Review(**review.model_dump(), movie_id=movie_id, sentiment=sentiment)
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review

def delete_review(db: Session, review_id: int):
    db_review = db.query(models.Review).filter(models.Review.id == review_id).first()
    if db_review:
        db.delete(db_review)
        db.commit()
        return True
    return False

def update_review(db: Session, review_id: int, review_data: schemas.ReviewCreate):
    db_review = db.query(models.Review).filter(models.Review.id == review_id).first()
    if db_review:
        # 내용이 바뀌면 감성 분석도 다시 수행
        if db_review.content != review_data.content:
            db_review.sentiment = analyze_sentiment(review_data.content)
            
        for key, value in review_data.model_dump().items():
            if key != "sentiment": # sentiment는 위에서 별도로 처리함
                setattr(db_review, key, value)
        db.commit()
        db.refresh(db_review)
    return db_review

def init_db(db: Session):
    if db.query(models.Movie).count() == 0:
        json_path = os.path.join(os.path.dirname(__file__), "movies.json")
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                movies_data = json.load(f)
            initial_movies = [
                models.Movie(**movie) for movie in movies_data
            ]
            db.add_all(initial_movies)
            db.commit()
        else:
            # Fallback to a small set if file doesn't exist
            fallback_movies = [
                models.Movie(title="타이타닉", director="제임스 카메론", genre="로맨스", poster_url="https://media.themoviedb.org/t/p/w300_and_h450_face/132KjhVrWUqKFVfMAKKNkherytA.jpg", release_date="1997-12-19"),
                models.Movie(title="해리포터와 마법사의 돌", director="크리스 콜럼버스", genre="판타지", poster_url="https://media.themoviedb.org/t/p/w300_and_h450_face/8YaP48tVfngbURGldWk1I5odsBK.jpg", release_date="2001-11-16"),
                models.Movie(title="인셉션", director="크리스토퍼 놀란", genre="SF", poster_url="https://media.themoviedb.org/t/p/w300_and_h450_face/zTgjeblxSLSvomt6F6UYtpiD4n7.jpg", release_date="2010-07-16")
            ]
            db.add_all(fallback_movies)
            db.commit()