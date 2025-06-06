from fastapi import FastAPI, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from database import SessionLocal, engine, Base
import models, schemas, crud

Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/authors", response_model=List[schemas.AuthorOut])
def get_authors(skip: int = 0, limit: int = Query(10, le=100), db: Session = Depends(get_db)):
    return crud.get_authors(db, skip=skip, limit=limit)


@app.post("/authors", response_model=schemas.AuthorOut, status_code=201)
def create_author(author: schemas.AuthorCreate, db: Session = Depends(get_db)):
    return crud.create_author(db, author)

@app.get("/authors/{author_id}", response_model=schemas.AuthorOut)
def get_author(author_id: int, db: Session = Depends(get_db)):
    db_author = crud.get_author(db, author_id)
    if not db_author:
        raise HTTPException(status_code=404, detail="Author not found")
    return db_author

@app.put("/authors/{author_id}", response_model=schemas.AuthorOut)
def update_author(author_id: int, author: schemas.AuthorCreate, db: Session = Depends(get_db)):
    return crud.update_author(db, author_id, author)

@app.delete("/authors/{author_id}", status_code=204)
def delete_author(author_id: int, db: Session = Depends(get_db)):
    crud.delete_author(db, author_id)
    return

@app.get("/books", response_model=List[schemas.BookOut])
def get_books(
    author_id: Optional[int] = Query(None),
    skip: int = 0,
    limit: int = Query(10, le=100),
    db: Session = Depends(get_db),
):
    return crud.get_books(db, author_id=author_id, skip=skip, limit=limit)


@app.post("/books", response_model=schemas.BookOut, status_code=201)
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db)):
    return crud.create_book(db, book)

@app.post("/populate")
def populate(db: Session = Depends(get_db)):
    from random import randint

    authors = ["Лев Толстой", "А.С. Пушкин", "Ф.М. Достоевский"]
    for name in authors:
        author = crud.create_author(db, schemas.AuthorCreate(name=name))
        for i in range(3):  # по 3 книги на автора
            crud.create_book(db, schemas.BookCreate(
                title=f"Книга {i+1} от {name}",
                year=randint(1800, 2024),
                author_id=author.id
            ))
    return {"status": "ok"}
