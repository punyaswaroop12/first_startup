from pydantic import BaseModel, EmailStr

from app.schemas.user import UserResponse


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class AuthProviderStatus(BaseModel):
    key: str
    label: str
    enabled: bool


class AuthProvidersResponse(BaseModel):
    providers: list[AuthProviderStatus]
