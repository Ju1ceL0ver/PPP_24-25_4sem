from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.db import get_db
from app.cruds.user import get_user_by_email, create_user, authenticate_user
from app.schemas.user import UserCreate, UserResponse
from app.services.auth import create_access_token, get_current_user
from app.schemas.graph import Graph, PathResult
from app.services.tsp import solve_tsp

router = APIRouter()

@router.post("/sign-up/", response_model=UserResponse)
def sign_up(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = create_user(db, user.email, user.password)
    token = create_access_token({"sub": new_user.email})
    return {"id": new_user.id, "email": new_user.email, "token": token}

@router.post("/login/", response_model=UserResponse)
def login(user: UserCreate, db: Session = Depends(get_db)):
    authenticated_user = authenticate_user(db, user.email, user.password)
    if not authenticated_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": authenticated_user.email})
    return {"id": authenticated_user.id, "email": authenticated_user.email, "token": token}

@router.get("/users/me/", response_model=UserResponse)
def get_me(authorization: str = Header(...), db: Session = Depends(get_db)):
    token = authorization.split("Bearer ")[1] if "Bearer " in authorization else authorization
    user = get_current_user(token, db)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return {"id": user.id, "email": user.email, "token": token}

@router.post("/shortest-path/", response_model=PathResult)
def shortest_path(graph: Graph):
    result = solve_tsp(graph)
    return result