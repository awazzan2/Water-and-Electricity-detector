from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from crud import get_latest_water_record, get_water_records
from database import get_db
from schemas import PaginatedResponse, WaterRecord, WaterStatusResponse
from sensors import water_status

router = APIRouter()


@router.get("/records", response_model=PaginatedResponse[WaterRecord])
async def list_water_records(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    items, total = await get_water_records(db, page=page, size=size)
    return PaginatedResponse(items=items, page=page, size=size, total=total)


@router.get("/records/latest", response_model=WaterRecord)
async def latest_water_record(db: AsyncSession = Depends(get_db)):
    record = await get_latest_water_record(db)
    if record is None:
        raise HTTPException(status_code=404, detail="No water records found")
    return record


@router.get("/status", response_model=WaterStatusResponse)
async def water_status_endpoint():
    return WaterStatusResponse(status=water_status())
