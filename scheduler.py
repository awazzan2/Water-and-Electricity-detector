import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database import POLL_INTERVAL_SECONDS, AsyncSessionLocal
from crud import (
    WATER_LEVELS,
    close_open_electricity_record,
    close_open_water_record,
    create_electricity_record,
    create_water_record,
)
from sensors import elec_status, water_status
from sse_manager import sse_manager

logger = logging.getLogger(__name__)

previous_water_state: int = 0
previous_elec_state: bool = False

scheduler = AsyncIOScheduler()


def init_sensor_states() -> None:
    global previous_water_state, previous_elec_state
    previous_water_state = water_status()
    previous_elec_state = elec_status()
    logger.info(
        "Initial sensor states — water=%s, electricity=%s",
        previous_water_state,
        previous_elec_state,
    )


async def _handle_water_change(new_state: int) -> None:
    if new_state == 0:
        async with AsyncSessionLocal() as session:
            await close_open_water_record(session)
        await sse_manager.broadcast({"type": "water", "active": False})
        return

    level = WATER_LEVELS[new_state]
    async with AsyncSessionLocal() as session:
        await close_open_water_record(session)
        await create_water_record(session, level=level)
    await sse_manager.broadcast({"type": "water", "active": True})


async def _handle_electricity_change(new_state: bool) -> None:
    if not new_state:
        async with AsyncSessionLocal() as session:
            await close_open_electricity_record(session)
        await sse_manager.broadcast({"type": "electricity", "active": False})
        return

    async with AsyncSessionLocal() as session:
        await create_electricity_record(session)
    await sse_manager.broadcast({"type": "electricity", "active": True})


async def poll_sensors() -> None:
    global previous_water_state, previous_elec_state

    current_water = water_status()
    if current_water != previous_water_state:
        logger.info("Water state changed: %s -> %s", previous_water_state, current_water)
        await _handle_water_change(current_water)
        previous_water_state = current_water

    current_elec = elec_status()
    if current_elec != previous_elec_state:
        logger.info("Electricity state changed: %s -> %s", previous_elec_state, current_elec)
        await _handle_electricity_change(current_elec)
        previous_elec_state = current_elec


def start_scheduler() -> None:
    scheduler.add_job(
        poll_sensors,
        "interval",
        seconds=POLL_INTERVAL_SECONDS,
        id="sensor_poll",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Scheduler started (interval=%ss)", POLL_INTERVAL_SECONDS)


def stop_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)
