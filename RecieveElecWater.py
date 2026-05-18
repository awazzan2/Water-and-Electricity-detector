from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from sensors import set_sensor_status


class SensorData(BaseModel):
    water_status: int = Field(..., ge=0, le=3, description="Water status: 0=off, 1=low, 2=medium, 3=high")
    water_description: str = Field(..., description="Description of water status")
    elec_status: bool = Field(..., description="Electricity status: true=on, false=off")
    elec_description: str = Field(..., description="Description of electricity status")


router = APIRouter(prefix="/receive")


@router.post("/WaterandElectricity")
async def receive_water_and_electricity(data: SensorData):
    """Receive sensor data from device and update internal state."""
    try:
        set_sensor_status(
            water_status=data.water_status,
            water_description=data.water_description,
            elec_status=data.elec_status,
            elec_description=data.elec_description,
        )
        return {
            "status": "success",
            "message": "Sensor data received and updated",
            "data": data.dict(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating sensor status: {str(e)}")