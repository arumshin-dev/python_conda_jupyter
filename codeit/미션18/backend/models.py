from sqlalchemy import Column, Integer, String, Float, ForeignKey,Date
from database import Base

class Movie(Base):
    __tablename__ = "movies"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    director = Column(String)
    genre = Column(String)
    poster_url = Column(String)
