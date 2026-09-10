import os
import requests
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.config import settings
from app.database.session import get_db, engine
from app.database.base import Base

# Ensure upload directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

# Create database tables if using SQLite / initial setup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Smart Waste Management, CVRP Route Optimization, and Geospatial Collection Platform Backend",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.api.endpoints import (
    auth,
    collection_points,
    vehicles,
    drivers,
    users,
    routing,
    optimization,
    routes,
    collections,
    analytics,
)

# Static files for image uploads
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Include API endpoints
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(collection_points.router, prefix="/api")
app.include_router(vehicles.router, prefix="/api")
app.include_router(drivers.router, prefix="/api")
app.include_router(routing.router, prefix="/api")
app.include_router(optimization.router, prefix="/api")
app.include_router(routes.router, prefix="/api")
app.include_router(collections.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")





@app.get("/")
def root():
    return {
        "name": settings.PROJECT_NAME,
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs"
    }

@app.get("/api/health")
def health_check(db: Session = Depends(get_db)):
    # Check Database connection
    db_status = "healthy"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    # Check OSRM Routing Engine status
    osrm_status = "reachable"
    try:
        response = requests.get(f"{settings.OSRM_SERVER_URL}/nearest/v1/driving/73.7868,18.5590", timeout=3)
        if response.status_code != 200:
            osrm_status = f"warning: HTTP {response.status_code}"
    except Exception as e:
        osrm_status = f"unreachable: {str(e)}"

    # Query database stats
    stats = {}
    try:
        from app.models import CollectionPoint, Vehicle, Driver, Depot
        stats = {
            "collection_points": db.query(CollectionPoint).count(),
            "vehicles": db.query(Vehicle).count(),
            "drivers": db.query(Driver).count(),
            "depots": db.query(Depot).count(),
        }
    except Exception:
        pass

    return {
        "status": "ok",
        "database": db_status,
        "osrm_routing_service": osrm_status,
        "stats": stats,
        "version": "1.0.0"
    }
