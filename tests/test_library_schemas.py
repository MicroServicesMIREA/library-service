import uuid
from uuid import UUID

from app.schemas import (
    BookCreate,
    UserBookUpdate,
)


def test_book_create_valid_data():
    book = BookCreate(
        title="Clean Code",
        author="Robert C. Martin",
        genre="programming",
    )

    assert book.title == "Clean Code"
    assert book.author == "Robert C. Martin"
    assert book.genre == "programming"


def test_user_book_update_partial_data():
    update = UserBookUpdate(
        reading_status="reading",
    )

    assert update.reading_status == "reading"
    assert update.progress_page is None
