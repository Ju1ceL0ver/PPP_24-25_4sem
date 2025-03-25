from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    token: str

    class Config:
        orm_mode = True

class Token(BaseModel):
    token: str