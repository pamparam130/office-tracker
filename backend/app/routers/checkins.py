from datetime import UTC, datetime, time, timedelta
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.database import get_session
from app.models import CheckIn, Employee
from app.schemas import CheckInOut, CheckInStatus
from app.security import get_current_employee

router = APIRouter(prefix="/api/checkins", tags=["checkins"])


def office_day_bounds() -> tuple[datetime, datetime]:
    """Начало и конец текущих офисных суток в UTC."""
    tz = ZoneInfo(settings.office_tz)
    today = datetime.now(tz).date()
    start = datetime.combine(today, time.min, tzinfo=tz)
    return start.astimezone(UTC), (start + timedelta(days=1)).astimezone(UTC)


def to_out(checkin: CheckIn) -> CheckInOut:
    return CheckInOut(
        id=checkin.id, name=checkin.employee.name, arrived_at=checkin.arrived_at
    )


@router.post("", response_model=CheckInOut, status_code=status.HTTP_201_CREATED)
async def check_in(
    employee: Employee = Depends(get_current_employee),
    session: AsyncSession = Depends(get_session),
):
    """Отметиться: «пришёл в офис». Один раз за офисные сутки."""
    day_start, day_end = office_day_bounds()
    already = await session.scalar(
        select(CheckIn).where(
            CheckIn.employee_id == employee.id,
            CheckIn.arrived_at >= day_start,
            CheckIn.arrived_at < day_end,
        )
    )
    if already is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Сегодня вы уже отметились"
        )

    checkin = CheckIn(employee_id=employee.id, arrived_at=datetime.now(UTC))
    session.add(checkin)
    await session.commit()
    await session.refresh(checkin)

    return CheckInOut(id=checkin.id, name=employee.name, arrived_at=checkin.arrived_at)


@router.get("/me", response_model=CheckInStatus)
async def my_status(
    employee: Employee = Depends(get_current_employee),
    session: AsyncSession = Depends(get_session),
):
    day_start, day_end = office_day_bounds()
    today = await session.scalar(
        select(CheckIn).where(
            CheckIn.employee_id == employee.id,
            CheckIn.arrived_at >= day_start,
            CheckIn.arrived_at < day_end,
        )
    )
    last = await session.scalar(
        select(CheckIn)
        .where(CheckIn.employee_id == employee.id)
        .order_by(desc(CheckIn.arrived_at))
        .limit(1)
    )
    return CheckInStatus(
        checked_in_today=today is not None,
        last_arrival=last.arrived_at if last else None,
    )


@router.get("/today", response_model=list[CheckInOut])
async def today(
    _: Employee = Depends(get_current_employee),
    session: AsyncSession = Depends(get_session),
):
    """Кто уже в офисе сегодня."""
    day_start, day_end = office_day_bounds()
    rows = await session.scalars(
        select(CheckIn)
        .options(selectinload(CheckIn.employee))
        .where(CheckIn.arrived_at >= day_start, CheckIn.arrived_at < day_end)
        .order_by(CheckIn.arrived_at)
    )
    return [to_out(row) for row in rows]


@router.get("/history", response_model=list[CheckInOut])
async def history(
    employee: Employee = Depends(get_current_employee),
    session: AsyncSession = Depends(get_session),
    limit: int = 30,
):
    rows = await session.scalars(
        select(CheckIn)
        .options(selectinload(CheckIn.employee))
        .where(CheckIn.employee_id == employee.id)
        .order_by(desc(CheckIn.arrived_at))
        .limit(min(limit, 100))
    )
    return [to_out(row) for row in rows]
