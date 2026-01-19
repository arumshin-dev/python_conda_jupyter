from sqlalchemy.orm import Session
from . import models, schemas

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

def init_db(db: Session):
    if db.query(models.Movie).count() == 0:
        initial_movies = [
            models.Movie(title="타이타닉", director="제임스 카메론", genre="로맨스", poster_url="https://media.themoviedb.org/t/p/w300_and_h450_face/132KjhVrWUqKFVfMAKKNkherytA.jpg"),
            models.Movie(title="해리포터와 마법사의 돌", director="크리스 콜럼버스", genre="판타지", poster_url="https://media.themoviedb.org/t/p/w300_and_h450_face/8YaP48tVfngbURGldWk1I5odsBK.jpg"),
            models.Movie(title="인셉션", director="크리스토퍼 놀란", genre="SF", poster_url="https://media.themoviedb.org/t/p/w300_and_h450_face/zTgjeblxSLSvomt6F6UYtpiD4n7.jpg")
        ]
        db.add_all(initial_movies)
        db.commit()
