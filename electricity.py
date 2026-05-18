from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from crud import get_electricity_records, get_latest_electricity_record
from database import get_db
from schemas import ElectricityRecord, ElectricityStatusResponse, PaginatedResponse
from sensors import elec_status

router = APIRouter()


@router.get("/records", response_model=PaginatedResponse[ElectricityRecord])
async def list_electricity_records(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    items, total = await get_electricity_records(db, page=page, size=size)
    return PaginatedResponse(items=items, page=page, size=size, total=total)


@router.get("/records/latest", response_model=ElectricityRecord)
async def latest_electricity_record(db: AsyncSession = Depends(get_db)):
    record = await get_latest_electricity_record(db)
    if record is None:
        raise HTTPException(status_code=404, detail="No electricity records found")
    return record


@router.get("/status", response_model=ElectricityStatusResponse)
async def electricity_status_endpoint():
    return ElectricityStatusResponse(status=elec_status())
