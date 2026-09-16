from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import Employee
from app.schemas import EmployeeOut, LoginRequest, RegisterRequest, TokenResponse
from app.security import (
    create_access_token,
    get_current_employee,
    hash_password,
    verify_password,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(data: RegisterRequest, session: AsyncSession = Depends(get_session)):
    name = data.name.strip()
    exists = await session.scalar(select(Employee).where(Employee.name == name))
    if exists is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Сотрудник с таким именем уже зарегистрирован",
        )

    employee = Employee(name=name, password_hash=hash_password(data.password))
    session.add(employee)
    await session.commit()
    await session.refresh(employee)

    return TokenResponse(access_token=create_access_token(employee), name=employee.name)


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, session: AsyncSession = Depends(get_session)):
    employee = await session.scalar(
        select(Employee).where(Employee.name == data.name.strip())
    )
    if employee is None or not verify_password(data.password, employee.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверное имя или пароль"
        )

    return TokenResponse(access_token=create_access_token(employee), name=employee.name)


@router.get("/me", response_model=EmployeeOut)
async def me(employee: Employee = Depends(get_current_employee)):
    return employee
