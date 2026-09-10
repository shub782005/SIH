import enum

class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    DRIVER = "DRIVER"
    MANAGER = "MANAGER"

class DriverStatus(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    ON_ROUTE = "ON_ROUTE"
    OFF_DUTY = "OFF_DUTY"
    INACTIVE = "INACTIVE"

class VehicleStatus(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    ON_ROUTE = "ON_ROUTE"
    OFF_DUTY = "OFF_DUTY"
    INACTIVE = "INACTIVE"

class WasteType(str, enum.Enum):
    PET = "PET"
    HDPE = "HDPE"
    LDPE = "LDPE"
    PP = "PP"
    OTHER_RECYCLABLE_PLASTIC = "OTHER_RECYCLABLE_PLASTIC"
    MIXED_PLASTIC = "MIXED_PLASTIC"

class PriorityLevel(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class RouteStatus(str, enum.Enum):
    PLANNED = "PLANNED"
    ASSIGNED = "ASSIGNED"
    STARTED = "STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class StopStatus(str, enum.Enum):
    PENDING = "PENDING"
    ARRIVED = "ARRIVED"
    COLLECTED = "COLLECTED"
    SKIPPED = "SKIPPED"
    FAILED = "FAILED"

class OptimizationStatus(str, enum.Enum):
    SUCCESS = "SUCCESS"
    PARTIAL_SUCCESS = "PARTIAL_SUCCESS"
    FAILED = "FAILED"
    INFEASIBLE = "INFEASIBLE"

class FailureReason(str, enum.Enum):
    NO_WASTE = "NO_WASTE"
    LOCATION_INACCESSIBLE = "LOCATION_INACCESSIBLE"
    VEHICLE_ISSUE = "VEHICLE_ISSUE"
    COLLECTION_POINT_CLOSED = "COLLECTION_POINT_CLOSED"
    EXCESSIVE_WASTE = "EXCESSIVE_WASTE"
    OTHER = "OTHER"
