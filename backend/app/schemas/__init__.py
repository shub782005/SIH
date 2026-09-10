from app.schemas.user import UserResponse, UserCreate, DriverProfileResponse
from app.schemas.auth import UserLogin, Token
from app.schemas.collection_point import (
    CollectionPointBase,
    CollectionPointCreate,
    CollectionPointUpdate,
    CollectionPointResponse,
)
from app.schemas.vehicle import VehicleBase, VehicleCreate, VehicleUpdate, VehicleResponse
from app.schemas.driver import DriverBase, DriverCreate, DriverUpdate, DriverResponse
from app.schemas.routing import (
    LocationInput,
    MatrixRequest,
    MatrixResponse,
    RouteGeometryRequest,
    RouteGeometryResponse,
)
from app.schemas.route import (
    RouteStopResponse,
    RouteResponse,
    RouteSummaryResponse,
    RouteStatusUpdateRequest,
    RouteAssignRequest,
)
from app.schemas.optimization import (
    OptimizationGenerateRequest,
    OptimizationRunSummaryResponse,
    OptimizationRunDetailResponse,
    ReoptimizeRequest,
)
from app.schemas.collection import (
    CollectionCreateRequest,
    CollectionFailRequest,
    CollectionResponse,
    ProofUploadResponse,
)
from app.schemas.analytics import (
    DailyWasteTrendItem,
    WasteByTypeItem,
    VehicleUtilizationItem,
    CollectionStats,
    RouteStats,
    OptimizationImpact,
    AnalyticsOverviewResponse,
)

__all__ = [
    "UserResponse",
    "UserCreate",
    "DriverProfileResponse",
    "UserLogin",
    "Token",
    "CollectionPointBase",
    "CollectionPointCreate",
    "CollectionPointUpdate",
    "CollectionPointResponse",
    "VehicleBase",
    "VehicleCreate",
    "VehicleUpdate",
    "VehicleResponse",
    "DriverBase",
    "DriverCreate",
    "DriverUpdate",
    "DriverResponse",
    "LocationInput",
    "MatrixRequest",
    "MatrixResponse",
    "RouteGeometryRequest",
    "RouteGeometryResponse",
    "RouteStopResponse",
    "RouteResponse",
    "RouteSummaryResponse",
    "RouteStatusUpdateRequest",
    "RouteAssignRequest",
    "OptimizationGenerateRequest",
    "OptimizationRunSummaryResponse",
    "OptimizationRunDetailResponse",
    "ReoptimizeRequest",
    "CollectionCreateRequest",
    "CollectionFailRequest",
    "CollectionResponse",
    "ProofUploadResponse",
    "DailyWasteTrendItem",
    "WasteByTypeItem",
    "VehicleUtilizationItem",
    "CollectionStats",
    "RouteStats",
    "OptimizationImpact",
    "AnalyticsOverviewResponse",
]




