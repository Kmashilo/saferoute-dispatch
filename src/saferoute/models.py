from dataclasses import dataclass, field
from enum import IntEnum


class EmptyDispatchError(Exception):
    """Raised when a dispatch is attempted with no routes."""


class VehicleNotFoundError(KeyError):
    """Raised when a vehicle is not found in the fleet."""


class InvalidIncidentError(ValueError):
    """Raised when an incident is invalid or cannot be processed."""


class Severity(IntEnum):
    """Enumeration for incident severity levels."""

    ROUTINE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Incident:
    """Represents an incoming emergency call logged by SafeRoute."""

    incident_id: str
    description: str
    location: str
    severity: Severity
    vehicle_registration: str | None = None

    def __post_init__(self) -> None:
        if not self.incident_id or not self.incident_id.strip():
            raise InvalidIncidentError("Incident ID cannot be empty.")
        if not isinstance(self.severity, Severity):
            raise InvalidIncidentError(
                f"Invalid severity '{self.severity}'. Must be a Severity value."
            )

    @property
    def suburb(self) -> str:
        return self.location


@dataclass
class Vehicle:
    """Represents a vehicle in the SafeRoute fleet."""

    registration: str
    vehicle_type: str
    crew: list[str] = field(default_factory=list)
    capacity: int = 1
    is_available: bool = True

    def __post_init__(self) -> None:
        if not self.registration or not self.registration.strip():
            raise ValueError("Vehicle registration cannot be empty.")
        if self.capacity <= 0:
            raise ValueError("Vehicle capacity must be a positive integer.")

    @property
    def unit_type(self) -> str:
        return self.vehicle_type

    @property
    def status(self) -> str:
        return "AVAILABLE" if self.is_available else "UNAVAILABLE"

    @status.setter
    def status(self, value: str) -> None:
        self.is_available = value.strip().upper() == "AVAILABLE"
