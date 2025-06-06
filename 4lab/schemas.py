from pydantic import BaseModel, Field, validator
from datetime import datetime

class AuthorBase(BaseModel):
    name: str = Field(..., min_length=1)

class AuthorCreate(AuthorBase):
    pass

class AuthorOut(AuthorBase):
    id: int
    class Config:
        orm_mode = True

class BookBase(BaseModel):
    title: str = Field(..., min_length=1)
    year: int
    author_id: int

    @validator("year")
    def year_not_in_future(cls, v):
        current_year = datetime.now().year
        if v > current_year:
            raise ValueError("Year must not be in the future")
        return v

class BookCreate(BookBase):
    pass

class BookOut(BookBase):
    id: int
    class Config:
        orm_mode = True
