from sqlalchemy import Column, Integer, String, Float, ForeignKey,Date
from database import Base

from sqlalchemy.orm import relationship

class Movie(Base):
    __tablename__ = "movies"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    director = Column(String)
    genre = Column(String)
    poster_url = Column(String)
    release_date = Column(String, nullable=True) # YYYY-MM-DD 형식

    # 1:N 관계 (영화 하나에 리뷰 여러 개)
    reviews = relationship("Review", back_populates="movie", cascade="all, delete-orphan")

class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, index=True)
    movie_id = Column(Integer, ForeignKey("movies.id"))
    author = Column(String)
    content = Column(String)
    rating = Column(Float)
    sentiment = Column(String, nullable=True) 
    created_at = Column(String)

    # N:1 관계 (리뷰는 한 영화에 속함)
    movie = relationship("Movie", back_populates="reviews")
