from sqlalchemy.orm import Session
import models, schemas

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) if api_key else None

def analyze_sentiment(content: str):
    """AI를 사용한 감성 분석 (OpenAI 사용, 없으면 간단한 로직으로 대체)"""
    if not client:
        # API 키가 없을 때의 간단한 휴리스틱 분석
        pos_words = ["좋아", "최고", "감동", "재밌", "훌륭", "추천"]
        neg_words = ["노잼", "별로", "최악", "지루", "망작", "비추"]
        
        pos_count = sum(1 for word in pos_words if word in content)
        neg_count = sum(1 for word in neg_words if word in content)
        
        if pos_count > neg_count: return "긍정 (Heuristic)"
        elif neg_count > pos_count: return "부정 (Heuristic)"
        else: return "중립 (Heuristic)"

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "너는 영화 리뷰 감성 분석가야. 리뷰 내용을 보고 '긍정', '부정', '중립' 중 하나로만 대답해."},
                {"role": "user", "content": content}
            ],
            max_tokens=10
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"분석 오류 ({str(e)})"

# Movie CRUD (기존 유지)
def get_movie(db: Session, movie_id: int):
    return db.query(models.Movie).filter(models.Movie.id == movie_id).first()

def get_movies(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Movie).offset(skip).limit(limit).all()

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
            setattr(db_review, key, value)
        db.commit()
        db.refresh(db_review)
    return db_review

def init_db(db: Session):
    if db.query(models.Movie).count() == 0:
        initial_movies = [
            models.Movie(title="타이타닉", director="제임스 카메론", genre="로맨스", poster_url="https://media.themoviedb.org/t/p/w300_and_h450_face/132KjhVrWUqKFVfMAKKNkherytA.jpg"),
            models.Movie(title="해리포터와 마법사의 돌", director="크리스 콜럼버스", genre="판타지", poster_url="https://media.themoviedb.org/t/p/w300_and_h450_face/8YaP48tVfngbURGldWk1I5odsBK.jpg"),
            models.Movie(title="인셉션", director="크리스토퍼 놀란", genre="SF", poster_url="https://media.themoviedb.org/t/p/w300_and_h450_face/zTgjeblxSLSvomt6F6UYtpiD4n7.jpg")
        ]
        db.add_all(initial_movies)
        db.commit()
