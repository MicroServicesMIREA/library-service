from pydantic import BaseModel
from uuid import UUID
from typing import Optional

class BookBase(BaseModel):
    title: str
    author: str
    genre: Optional[str] = None

class BookCreate(BookBase):
    pass

class BookResponse(BookBase):
    book_id: UUID

    class Config:
        from_attributes = True

class UserBookCreate(BaseModel):
    reading_status: str = "want_to_read"
    progress_page: int = 0

class UserBookResponse(BaseModel):
    user_book_id: UUID
    user_id: UUID
    book_id: UUID
    reading_status: str
    progress_page: int

    class Config:
        from_attributes = True

class UserBookUpdate(BaseModel):
    reading_status: Optional[str] = None
    progress_page: Optional[int] = None