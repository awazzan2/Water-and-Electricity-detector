# Mutable state for sensor values (updated by device)
_water_status: int = 0
_water_description: str = "Off"
_elec_status: bool = False
_elec_description: str = "Off"


def set_sensor_status(
    water_status: int,
    water_description: str,
    elec_status: bool,
    elec_description: str,
) -> None:
    """Update sensor status from device."""
    global _water_status, _water_description, _elec_status, _elec_description
    _water_status = water_status
    _water_description = water_description
    _elec_status = elec_status
    _elec_description = elec_description


def water_status() -> int:
    """Returns 0 = off, 1 = low, 2 = medium, 3 = high."""
    # TODO: Replace with real sensor logic
    return _water_status


def elec_status() -> bool:
    """Returns True = electricity ON, False = electricity OFF."""
   
    return _elec_status
