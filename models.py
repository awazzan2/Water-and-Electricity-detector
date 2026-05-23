from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from database import Base


class WaterRecord(Base):
    __tablename__ = "water_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    time_on: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    time_off: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    level: Mapped[str] = mapped_column(String, nullable=False)


class ElectricityRecord(Base):
    __tablename__ = "electricity_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    time_on: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    time_off: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
