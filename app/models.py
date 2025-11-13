from sqlalchemy import Column, String, Integer, UUID, ForeignKey
from sqlalchemy.sql import func
import uuid
from .database import Base

class Book(Base):
    __tablename__ = "books"
    __table_args__ = {'schema': 'library_service'}

    book_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    author = Column(String(255), nullable=False)
    genre = Column(String(100))

class UserBook(Base):
    __tablename__ = "user_books"
    __table_args__ = {'schema': 'library_service'}

    user_book_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False) # Внешний ключ на user_service.users
    book_id = Column(UUID(as_uuid=True), ForeignKey('library_service.books.book_id'), nullable=False)
    reading_status = Column(String(50), default='want_to_read')
    progress_page = Column(Integer, default=0)