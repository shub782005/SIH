from pydantic import BaseModel, EmailStr
from app.schemas.user import UserResponse

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
