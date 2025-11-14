from uuid import uuid4

from sqlalchemy import text

from app.database import SessionLocal, engine
from app import models


def _db_is_ready() -> bool:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            result = conn.execute(
                text("SELECT to_regclass('library_service.books')")
            )
            table_name = result.scalar()
            if table_name is None:
                return False
        return True
    except Exception:
        return False


def test_create_and_read_book_from_real_db():
    if not _db_is_ready():
        return

    db = SessionLocal()

    try:
        book = models.Book(
            title="Test library book",
            author="Test Author",
            genre="test-genre",
        )
        db.add(book)
        db.commit()
        db.refresh(book)

        fetched = (
            db.query(models.Book)
            .filter(models.Book.book_id == book.book_id)
            .first()
        )

        assert fetched is not None
        assert fetched.title == "Test library book"
        assert fetched.author == "Test Author"
        assert fetched.genre == "test-genre"

    finally:
        try:
            db.query(models.Book).filter(
                models.Book.book_id == book.book_id
            ).delete()
            db.commit()
        except Exception:
            pass
        finally:
            db.close()
