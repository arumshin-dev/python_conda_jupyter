from pydantic import BaseModel, ConfigDict
from typing import List, Optional

# --- Review Schemas ---
class ReviewBase(BaseModel):
    author: str
    content: str
    rating: float
    created_at: str

class ReviewCreate(ReviewBase):
    pass

class Review(ReviewBase):
    id: int
    movie_id: int
    sentiment: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

# --- Movie Schemas ---
class MovieBase(BaseModel):
    title: str
    director: str
    genre: str
    poster_url: str
    release_date: Optional[str] = None

class MovieCreate(MovieBase):
    pass

class Movie(MovieBase):
    id: int
    reviews: List[Review] = []
    average_rating: float = 0.0
    
    model_config = ConfigDict(from_attributes=True)
