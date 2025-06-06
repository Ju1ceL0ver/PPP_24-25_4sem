from sqlalchemy.orm import Session
from fastapi import HTTPException
import models
import schemas


def get_authors(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Author).offset(skip).limit(limit).all()


def create_author(db: Session, author: schemas.AuthorCreate):
    db_author = models.Author(name=author.name)
    db.add(db_author)
    db.commit()
    db.refresh(db_author)
    return db_author


def get_author(db: Session, author_id: int):
    return db.query(models.Author).filter(models.Author.id == author_id).first()


def update_author(db: Session, author_id: int, author: schemas.AuthorCreate):
    db_author = get_author(db, author_id)
    if not db_author:
        raise HTTPException(status_code=404, detail="Author not found")
    db_author.name = author.name
    db.commit()
    db.refresh(db_author)
    return db_author


def delete_author(db: Session, author_id: int):
    db_author = get_author(db, author_id)
    if not db_author:
        raise HTTPException(status_code=404, detail="Author not found")
    db.delete(db_author)
    db.commit()


def get_books(db: Session, author_id: int = None, skip: int = 0, limit: int = 10):
    query = db.query(models.Book)
    if author_id:
        query = query.filter(models.Book.author_id == author_id)
    return query.offset(skip).limit(limit).all()


def create_book(db: Session, book: schemas.BookCreate):
    author = get_author(db, book.author_id)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    db_book = models.Book(**book.dict())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book
