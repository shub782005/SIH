# System Architecture & Technical Specification

## Plastic Waste Collection Optimization Platform

### Logical Architecture Overview

```text
React 18 Frontend (Vite + Tailwind CSS + Leaflet)
                      │
                   REST API (JWT Bearer Auth)
                      │
             FastAPI Backend (Python)
          ┌───────────┴───────────┐
          │                       │
 PostgreSQL / SQLite         Services Layer
                          ┌───────┴───────┐
                          │               │
                     OR-Tools          OSRM Service
                   (CVRP Engine)     (Distance Matrix &
                                      Road Polylines)
```

### Module Breakdown

1. **Frontend**:
   - Single Page Application built with React 18, Vite, React Router v7, and Tailwind CSS.
   - Map Rendering via Leaflet and React-Leaflet.
   - Analytics Visualization via Recharts.

2. **Backend**:
   - Async REST API using FastAPI.
   - Pydantic models for request payload validation.
   - SQLAlchemy 2.0 ORM with SQLite fallback for seamless zero-setup development and PostgreSQL for production.

3. **Optimization Engine**:
   - Formulated as a Capacitated Vehicle Routing Problem (CVRP).
   - Solved using Google OR-Tools.
   - Considers depot start/end, vehicle capacities, waste demand, and node priority scores.

4. **Routing Engine**:
   - OpenStreetMap OSRM API integration for real road distances, travel durations, and road geometry polylines.
