from pydantic import BaseModel, ConfigDict
from typing import List, Optional

class MovieBase(BaseModel):
    title: str
    director: str
    genre: str
    poster_url: str

class MovieCreate(MovieBase):
    pass

class Movie(MovieBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)
