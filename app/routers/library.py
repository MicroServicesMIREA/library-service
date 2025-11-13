from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas
from uuid import UUID

router = APIRouter()

# === CRUD для книг (Book) ===

# CREATE - Добавление новой книги в каталог
@router.post("/books/", response_model=schemas.BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db)):
    db_book = models.Book(
        title=book.title,
        author=book.author,
        genre=book.genre
    )
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

# READ - Получение всех книг из каталога
@router.get("/books/", response_model=list[schemas.BookResponse])
def get_all_books(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    books = db.query(models.Book).offset(skip).limit(limit).all()
    return books

# READ - Получение книги по ID
@router.get("/books/{book_id}", response_model=schemas.BookResponse)
def get_book(book_id: str, db: Session = Depends(get_db)):
    try:
        book_uuid = UUID(book_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid book ID format")
    
    book = db.query(models.Book).filter(models.Book.book_id == book_uuid).first()
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

# UPDATE - Обновление книги
@router.put("/books/{book_id}", response_model=schemas.BookResponse)
def update_book(book_id: str, book_update: schemas.BookCreate, db: Session = Depends(get_db)):
    try:
        book_uuid = UUID(book_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid book ID format")
    
    db_book = db.query(models.Book).filter(models.Book.book_id == book_uuid).first()
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    
    db_book.title = book_update.title
    db_book.author = book_update.author
    db_book.genre = book_update.genre
    
    db.commit()
    db.refresh(db_book)
    return db_book

# DELETE - Удаление книги из каталога
@router.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: str, db: Session = Depends(get_db)):
    try:
        book_uuid = UUID(book_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid book ID format")
    
    db_book = db.query(models.Book).filter(models.Book.book_id == book_uuid).first()
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    
    db.delete(db_book)
    db.commit()
    return None

# === CRUD для личной библиотеки пользователя (UserBook) ===

# CREATE - Добавление книги в личную библиотеку пользователя
@router.post("/{user_id}/books/{book_id}", response_model=schemas.UserBookResponse)
def add_book_to_library(
    user_id: str,
    book_id: str,
    library_data: schemas.UserBookCreate,
    db: Session = Depends(get_db)
):
    try:
        user_uuid = UUID(user_id)
        book_uuid = UUID(book_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ID format")
    
    # Проверяем, есть ли уже такая книга у пользователя
    existing_entry = db.query(models.UserBook).filter(
        models.UserBook.user_id == user_uuid,
        models.UserBook.book_id == book_uuid
    ).first()
    if existing_entry:
        raise HTTPException(status_code=400, detail="Book already in library")
    
    # Проверяем существование книги
    db_book = db.query(models.Book).filter(models.Book.book_id == book_uuid).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found in catalog")
    
    # Добавляем книгу в библиотеку пользователя
    db_user_book = models.UserBook(
        user_id=user_uuid,
        book_id=book_uuid,
        reading_status=library_data.reading_status,
        progress_page=library_data.progress_page
    )
    db.add(db_user_book)
    db.commit()
    db.refresh(db_user_book)
    return db_user_book

# READ - Получение всех книг пользователя
@router.get("/{user_id}/books", response_model=list[schemas.UserBookResponse])
def get_user_books(user_id: str, db: Session = Depends(get_db)):
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    
    books = db.query(models.UserBook).filter(models.UserBook.user_id == user_uuid).all()
    return books

# UPDATE - Обновление статуса чтения или прогресса
@router.put("/{user_id}/books/{book_id}", response_model=schemas.UserBookResponse)
def update_user_book(
    user_id: str,
    book_id: str,
    update_data: schemas.UserBookUpdate,
    db: Session = Depends(get_db)
):
    try:
        user_uuid = UUID(user_id)
        book_uuid = UUID(book_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ID format")
    
    user_book = db.query(models.UserBook).filter(
        models.UserBook.user_id == user_uuid,
        models.UserBook.book_id == book_uuid
    ).first()
    
    if not user_book:
        raise HTTPException(status_code=404, detail="Book not found in user library")
    
    # Обновляем только переданные поля
    update_fields = update_data.dict(exclude_unset=True)
    for field, value in update_fields.items():
        setattr(user_book, field, value)
    
    db.commit()
    db.refresh(user_book)
    return user_book

# DELETE - Удаление книги из личной библиотеки пользователя
@router.delete("/{user_id}/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_book_from_library(user_id: str, book_id: str, db: Session = Depends(get_db)):
    try:
        user_uuid = UUID(user_id)
        book_uuid = UUID(book_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ID format")
    
    user_book = db.query(models.UserBook).filter(
        models.UserBook.user_id == user_uuid,
        models.UserBook.book_id == book_uuid
    ).first()
    
    if not user_book:
        raise HTTPException(status_code=404, detail="Book not found in user library")
    
    db.delete(user_book)
    db.commit()
    return None

# Тестовый эндпоинт
@router.get("/test")
def test_endpoint():
    return {"message": "Library router is working!"}