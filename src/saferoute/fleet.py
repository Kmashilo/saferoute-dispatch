from saferoute.models import Vehicle, VehicleNotFoundError


class FleetRegistry:
    """Hash-table-backed registry for O(1) average-case vehicle and crew lookup."""

    def __init__(self) -> None:
        self._vehicles: dict[str, Vehicle] = {}

    @staticmethod
    def _normalize_key(fleet_number: str) -> str:
        if not fleet_number or not fleet_number.strip():
            raise VehicleNotFoundError("Fleet/registration number cannot be empty.")
        return fleet_number.strip().upper()

    def register_vehicle(self, vehicle: Vehicle) -> None:
        """Insert or update a vehicle record in O(1) average time."""
        key = self._normalize_key(vehicle.registration)
        vehicle.registration = key
        self._vehicles[key] = vehicle

    def get_vehicle(self, fleet_number: str) -> Vehicle:
        """Retrieve a vehicle record by fleet/registration number in O(1) average time."""
        key = self._normalize_key(fleet_number)
        try:
            return self._vehicles[key]
        except KeyError as exc:
            raise VehicleNotFoundError(
                f"Vehicle with fleet/registration '{key}' was not found."
            ) from exc

    def update_status(self, fleet_number: str, new_status: str) -> None:
        """Update the operational status of an existing vehicle."""
        vehicle = self.get_vehicle(fleet_number)
        vehicle.status = new_status.strip().upper()

    def __len__(self) -> int:
        return len(self._vehicles)