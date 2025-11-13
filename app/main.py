from fastapi import FastAPI
from .database import engine
from . import models
from .routers import library

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Library Service",
    description="Микросервис для управления личной библиотекой",
    version="1.0.0"
)

app.include_router(library.router, prefix="/api/v1/library", tags=["library"])

@app.get("/")
def read_root():
    return {"message": "Library Service is running!"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "library"}