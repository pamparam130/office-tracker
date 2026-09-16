from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    password: str = Field(min_length=6, max_length=72)


class LoginRequest(BaseModel):
    name: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    name: str


class EmployeeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class CheckInOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    arrived_at: datetime


class CheckInStatus(BaseModel):
    checked_in_today: bool
    last_arrival: datetime | None = None
