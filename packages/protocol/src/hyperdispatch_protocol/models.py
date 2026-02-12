from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class DriverStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    ENROUTE = "ENROUTE"
    ON_TRIP = "ON_TRIP"
    OFFLINE = "OFFLINE"


class RiderStatus(str, Enum):
    WAITING = "WAITING"
    MATCHED = "MATCHED"
    PICKED_UP = "PICKED_UP"
    DROPPED_OFF = "DROPPED_OFF"
    CANCELED = "CANCELED"


class DispatchEventType(str, Enum):
    DRIVER_UPDATE = "DRIVER_UPDATE"
    RIDER_REQUEST = "RIDER_REQUEST"
    MATCHED = "MATCHED"
    CANCELED = "CANCELED"
    PICKUP = "PICKUP"
    DROPOFF = "DROPOFF"
    ANOMALY = "ANOMALY"


@dataclass(slots=True)
class SimBounds:
    min_lat: float
    min_lon: float
    max_lat: float
    max_lon: float


@dataclass(slots=True)
class City:
    id: str
    name: str
    center_lat: float
    center_lon: float
    sim_bounds: SimBounds


@dataclass(slots=True)
class Driver:
    id: str
    status: DriverStatus
    lat: float
    lon: float
    heading: float
    speed_mps: float
    last_update_ts: int
    city_id: str
    idle_since_ts: int = 0


@dataclass(slots=True)
class Rider:
    id: str
    status: RiderStatus
    lat: float
    lon: float
    request_ts: int
    city_id: str


@dataclass(slots=True)
class RidePreferences:
    quiet_mode: bool = False
    accessibility: bool = False


@dataclass(slots=True)
class RideRequest:
    id: str
    rider_id: str
    created_ts: int
    max_pickup_km: float
    preferences: RidePreferences
    city_id: str
    pickup_lat: float
    pickup_lon: float
    dropoff_lat: float
    dropoff_lon: float


@dataclass(slots=True)
class MatchDecision:
    request_id: str
    driver_id: str
    score: float
    reasons: list[str]
    candidate_count: int
    pickup_eta_s: float


@dataclass(slots=True)
class DispatchEvent:
    ts: int
    type: DispatchEventType
    city_id: str
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class TraceSpan:
    trace_id: str
    span_id: str
    parent_span_id: str | None
    name: str
    start_ns: int
    end_ns: int
    tags: dict[str, Any] = field(default_factory=dict)
    logs: list[str] = field(default_factory=list)


@dataclass(slots=True)
class WorldSnapshot:
    ts: int
    drivers: list[Driver]
    riders: list[Rider]
    requests: list[RideRequest]


def to_dict(value: Any) -> Any:
    if hasattr(value, "__dataclass_fields__"):
        return asdict(value)
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, list):
        return [to_dict(v) for v in value]
    if isinstance(value, dict):
        return {k: to_dict(v) for k, v in value.items()}
    return value
