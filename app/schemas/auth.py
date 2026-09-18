from pydantic import BaseModel, ConfigDict, EmailStr


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in_minutes: int 


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    role: str

    model_config = ConfigDict(from_attributes=True)


class MessageResponse(BaseModel):
    message: str
