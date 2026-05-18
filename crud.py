from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models import ElectricityRecord, WaterRecord

WATER_LEVELS = {1: "low", 2: "medium", 3: "high"}


def utc_now() -> datetime:
    return datetime.now(UTC)


async def get_open_water_record(session: AsyncSession) -> WaterRecord | None:
    result = await session.execute(
        select(WaterRecord)
        .where(WaterRecord.time_off.is_(None))
        .order_by(WaterRecord.id.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def close_open_water_record(session: AsyncSession, at: datetime | None = None) -> WaterRecord | None:
    record = await get_open_water_record(session)
    if record is None:
        return None
    record.time_off = at or utc_now()
    await session.commit()
    await session.refresh(record)
    return record


async def create_water_record(session: AsyncSession, level: str, at: datetime | None = None) -> WaterRecord:
    record = WaterRecord(time_on=at or utc_now(), time_off=None, level=level)
    session.add(record)
    await session.commit()
    await session.refresh(record)
    return record


async def get_water_records(
    session: AsyncSession, page: int = 1, size: int = 50
) -> tuple[list[WaterRecord], int]:
    offset = (page - 1) * size
    total_result = await session.execute(select(func.count()).select_from(WaterRecord))
    total = total_result.scalar_one()
    result = await session.execute(
        select(WaterRecord).order_by(WaterRecord.id.desc()).offset(offset).limit(size)
    )
    return list(result.scalars().all()), total


async def get_latest_water_record(session: AsyncSession) -> WaterRecord | None:
    result = await session.execute(
        select(WaterRecord).order_by(WaterRecord.id.desc()).limit(1)
    )
    return result.scalar_one_or_none()


async def get_open_electricity_record(session: AsyncSession) -> ElectricityRecord | None:
    result = await session.execute(
        select(ElectricityRecord)
        .where(ElectricityRecord.time_off.is_(None))
        .order_by(ElectricityRecord.id.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def close_open_electricity_record(
    session: AsyncSession, at: datetime | None = None
) -> ElectricityRecord | None:
    record = await get_open_electricity_record(session)
    if record is None:
        return None
    record.time_off = at or utc_now()
    await session.commit()
    await session.refresh(record)
    return record


async def create_electricity_record(
    session: AsyncSession, at: datetime | None = None
) -> ElectricityRecord:
    record = ElectricityRecord(time_on=at or utc_now(), time_off=None)
    session.add(record)
    await session.commit()
    await session.refresh(record)
    return record


async def get_electricity_records(
    session: AsyncSession, page: int = 1, size: int = 50
) -> tuple[list[ElectricityRecord], int]:
    offset = (page - 1) * size
    total_result = await session.execute(select(func.count()).select_from(ElectricityRecord))
    total = total_result.scalar_one()
    result = await session.execute(
        select(ElectricityRecord).order_by(ElectricityRecord.id.desc()).offset(offset).limit(size)
    )
    return list(result.scalars().all()), total


async def get_latest_electricity_record(session: AsyncSession) -> ElectricityRecord | None:
    result = await session.execute(
        select(ElectricityRecord).order_by(ElectricityRecord.id.desc()).limit(1)
    )
    return result.scalar_one_or_none()
