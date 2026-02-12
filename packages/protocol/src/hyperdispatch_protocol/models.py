from enum import Enum
from pydantic import BaseModel, Field


class DriverStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    MATCHED = "MATCHED"
    ON_TRIP = "ON_TRIP"


class RiderStatus(str, Enum):
    WAITING = "WAITING"
    MATCHED = "MATCHED"
    PICKED_UP = "PICKED_UP"
    DROPPED_OFF = "DROPPED_OFF"


class TripStatus(str, Enum):
    MATCHED = "MATCHED"
    ON_TRIP = "ON_TRIP"
    COMPLETED = "COMPLETED"


class LatLng(BaseModel):
    lat: float = Field(ge=-90, le=90)
    lng: float = Field(ge=-180, le=180)


class Driver(BaseModel):
    id: str
    location: LatLng
    heading_deg: float
    speed_mps: float
    status: DriverStatus
    last_update_ms: int


class Rider(BaseModel):
    id: str
    location: LatLng
    status: RiderStatus
    requested_at_ms: int


class Trip(BaseModel):
    id: str
    rider_id: str
    driver_id: str
    status: TripStatus
    pickup: LatLng
    dropoff: LatLng
    created_at_ms: int


class MatchRequest(BaseModel):
    rider_id: str
    pickup: LatLng
    dropoff: LatLng
    constraints: dict[str, str | int | float | bool] = Field(default_factory=dict)


class MatchDecision(BaseModel):
    trip_id: str
    driver_id: str
    rider_id: str
    pickup_eta_s: float
    distance_m: float
    trace_id: str


class TraceSpan(BaseModel):
    trace_id: str
    span_id: str
    parent_id: str | None = None
    name: str
    start_ms: int
    end_ms: int
    attrs: dict[str, str | int | float | bool] = Field(default_factory=dict)


class WorldMetrics(BaseModel):
    matches_per_min: float
    avg_pickup_eta_s: float
    waiting_riders: int
    available_drivers: int
    match_failures: int
    retries: int


class WorldSnapshot(BaseModel):
    ts_ms: int
    drivers: list[Driver]
    riders: list[Rider]
    trips: list[Trip]
    metrics: WorldMetrics
