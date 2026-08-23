# Plastic Waste Collection Optimization Platform

## 1. Project Overview

### Project Name

**Plastic Waste Collection Optimization Platform**

### Project Type

Smart Waste Management + Route Optimization + Geospatial Web Platform

### Problem Statement

Develop a route-optimization system for collecting recyclable plastic from multiple collection points.

The system should help waste-management authorities or recycling organizations efficiently collect recyclable plastic from multiple geographically distributed collection points by:

- Tracking collection points
- Recording estimated plastic quantities
- Managing collection vehicles and their capacities
- Assigning collection points to suitable vehicles
- Generating optimized collection routes
- Considering vehicle capacity constraints
- Considering collection priority
- Minimizing travel distance and time
- Visualizing routes on an interactive map
- Tracking collection progress
- Recording actual collected quantities
- Providing operational analytics

The primary objective is:

> **Collect maximum recyclable plastic using minimum operational resources such as distance, time, and vehicle capacity.**

---

# 2. Product Vision

The platform should transform plastic waste collection from a mostly manual process into a data-driven optimization workflow.

### Current/manual process

```text
Collection Points
       ↓
Manual Planning
       ↓
Driver Assignment
       ↓
Manual Route Selection
       ↓
Waste Collection
       ↓
Manual Reporting
```

### Proposed system

```text
Collection Data
       ↓
Priority Calculation
       ↓
Road Distance Calculation
       ↓
Route Optimization
       ↓
Vehicle Assignment
       ↓
Optimized Routes
       ↓
Driver Navigation
       ↓
Collection Verification
       ↓
Analytics
       ↓
Continuous Re-optimization
```

---

# 3. Primary Users

The system should support three primary user roles.

## 3.1 Administrator

The administrator manages the entire collection operation.

Responsibilities:

- Manage collection points
- Manage vehicles
- Manage drivers
- View waste information
- Generate optimized routes
- Monitor active routes
- View collection progress
- View analytics
- Re-optimize routes
- Manage system configuration

---

## 3.2 Driver

The driver receives an assigned route.

Responsibilities:

- View assigned route
- View collection points
- Navigate to collection points
- Mark arrival
- Record collected quantity
- Upload optional collection proof
- Mark collection completed
- Report issues
- Continue to next collection point

---

## 3.3 Operations Manager

Optional role for future expansion.

Responsibilities:

- Monitor multiple vehicles
- Monitor collection performance
- Review route efficiency
- Review operational analytics
- Handle exceptions
- Approve/reassign routes

For the MVP, Administrator and Operations Manager can be combined.

---

# 4. Core System Modules

The system should contain the following modules:

1. Authentication and Role Management
2. Dashboard
3. Collection Point Management
4. Vehicle Management
5. Driver Management
6. Waste Data Management
7. Priority Calculation
8. Distance/Travel-Time Engine
9. Route Optimization Engine
10. Route Management
11. Driver Collection Interface
12. Collection Verification
13. Analytics
14. Notifications
15. System Settings

---

# 5. MVP Scope

The first working version MUST focus on the following.

## Must Have

- Admin login
- Collection point CRUD
- Vehicle CRUD
- Driver CRUD
- Depot configuration
- Waste quantity management
- Collection point priority
- Interactive map
- Road distance calculation
- Multi-vehicle route optimization
- Vehicle capacity constraints
- Route visualization
- Route assignment
- Driver route interface
- Collection status
- Collected quantity recording
- Basic analytics

## Should Have

- Priority scoring
- Before-vs-after route comparison
- Route efficiency score
- Vehicle utilization
- Estimated fuel savings
- Route re-optimization
- Collection proof image
- Notifications

## Future Features

Do not implement these until the core MVP works:

- AI-based plastic classification
- Waste quantity prediction
- Traffic prediction
- IoT smart bins
- Dynamic GPS tracking
- Predictive collection
- Advanced machine learning
- Multi-depot optimization
- Carbon-emission optimization

---

# 6. High-Level System Architecture

Use the following architecture:

```text
                    ┌───────────────────────┐
                    │       ADMIN           │
                    └───────────┬───────────┘
                                │
                    ┌───────────▼───────────┐
                    │     React Frontend    │
                    │                       │
                    │ Dashboard             │
                    │ Maps                  │
                    │ Routes                │
                    │ Vehicles              │
                    │ Collection Points     │
                    └───────────┬───────────┘
                                │
                           REST API
                                │
                    ┌───────────▼───────────┐
                    │       FastAPI         │
                    │       Backend         │
                    └───────────┬───────────┘
                                │
              ┌─────────────────┼─────────────────┐
              │                 │                 │
              ▼                 ▼                 ▼
        PostgreSQL          OR-Tools            OSRM
         Database        Optimization       Routing Engine
              │                 │                 │
              └─────────────────┼─────────────────┘
                                │
                                ▼
                     Optimized Route Data
                                │
                    ┌───────────▼───────────┐
                    │    Driver Interface   │
                    └───────────────────────┘
```

---

# 7. Recommended Technology Stack

## Frontend

Use:

- React.js
- Vite
- Tailwind CSS
- React Router
- Axios
- Leaflet
- React-Leaflet
- Recharts

Purpose:

```text
React
→ UI

Leaflet
→ Maps

Recharts
→ Analytics
```

---

# 8. Backend

Use:

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- PostgreSQL
- JWT authentication

FastAPI should expose REST APIs.

---

# 9. Optimization

Use:

**Google OR-Tools**

The optimization engine should solve a:

> Capacitated Vehicle Routing Problem (CVRP)

with additional priority-based weighting.

Potential future constraints:

- Time windows
- Maximum route duration
- Vehicle availability
- Waste priority
- Multi-depot routing

---

# 10. Routing

Use:

**OpenStreetMap + OSRM**

OSRM should provide:

- Road distance
- Estimated travel duration
- Route geometry

Do NOT use straight-line geographic distance for actual route optimization when road routing is available.

---

# 11. Database

Use:

**PostgreSQL**

Recommended tables:

```text
users
drivers
vehicles
depots
collection_points
waste_records
routes
route_stops
collections
notifications
optimization_runs
```

---

# 12. Database Design

## users

```text
id
name
email
password_hash
role
created_at
updated_at
```

Roles:

```text
ADMIN
DRIVER
MANAGER
```

---

## drivers

```text
id
user_id
license_number
phone
status
created_at
```

Status:

```text
AVAILABLE
ON_ROUTE
OFF_DUTY
INACTIVE
```

---

## vehicles

```text
id
vehicle_number
vehicle_type
capacity_kg
driver_id
status
current_latitude
current_longitude
created_at
updated_at
```

---

## depots

```text
id
name
latitude
longitude
address
created_at
```

The MVP can support one depot.

---

## collection_points

```text
id
name
address
latitude
longitude
estimated_waste_kg
waste_type
priority
last_collection_date
overflow_status
status
created_at
updated_at
```

Waste types:

```text
PET
HDPE
LDPE
PP
OTHER_RECYCLABLE_PLASTIC
MIXED_PLASTIC
```

Priority:

```text
LOW
MEDIUM
HIGH
CRITICAL
```

---

## waste_records

```text
id
collection_point_id
estimated_quantity_kg
actual_quantity_kg
recorded_at
source
```

---

## routes

```text
id
route_date
vehicle_id
total_distance_km
estimated_duration_minutes
total_waste_kg
utilization_percentage
status
optimization_run_id
created_at
updated_at
```

Status:

```text
PLANNED
ASSIGNED
STARTED
IN_PROGRESS
COMPLETED
CANCELLED
```

---

## route_stops

```text
id
route_id
collection_point_id
sequence_number
estimated_arrival_time
actual_arrival_time
status
```

Status:

```text
PENDING
ARRIVED
COLLECTED
SKIPPED
FAILED
```

---

## collections

```text
id
route_stop_id
expected_quantity_kg
actual_quantity_kg
collection_time
verification_status
proof_image_url
remarks
```

---

## optimization_runs

```text
id
created_at
number_of_vehicles
number_of_collection_points
total_distance_before
total_distance_after
total_duration_before
total_duration_after
waste_collected
distance_saved_percentage
time_saved_percentage
status
```

---

# 13. Collection Point Workflow

Administrator creates a collection point.

Example:

```text
Name:
Baner Plastic Collection Point

Latitude:
18.5590

Longitude:
73.7868

Estimated Waste:
250 kg

Waste Type:
PET

Priority:
HIGH

Last Collection:
2026-08-20
```

The system stores the point.

It should appear on the map.

---

# 14. Vehicle Workflow

Administrator creates:

```text
Vehicle:
MH12-AB-1234

Capacity:
500 kg

Driver:
Rahul

Status:
AVAILABLE
```

The vehicle becomes available for optimization.

---

# 15. Priority Calculation

The system should calculate a collection priority score.

A conceptual formula:

```text
Priority Score =
Waste Quantity Score
+
Days Since Last Collection Score
+
Overflow Risk Score
+
Urgency Score
```

Normalize the score to:

```text
0 – 100
```

Example:

```text
0–30   → LOW
31–60  → MEDIUM
61–80  → HIGH
81–100 → CRITICAL
```

The exact weights should be configurable.

Example:

```text
Waste Quantity       40%
Days Since Collection 25%
Overflow Risk         25%
Urgency               10%
```

---

# 16. Route Optimization Workflow

This is the most important workflow.

## Input

The optimizer receives:

```text
Depot
Vehicles
Vehicle capacities
Available collection points
Waste quantities
Priority values
GPS coordinates
Road distance matrix
Travel-time matrix
```

---

## Step 1 — Validate Data

Check:

```text
No missing coordinates
No negative waste quantity
Vehicle capacity > 0
At least one vehicle available
At least one collection point
```

---

## Step 2 — Build Distance Matrix

Example:

```text
             Depot  CP1  CP2  CP3  CP4

Depot          0    4    7    5    9
CP1            4    0    3    6    8
CP2            7    3    0    4    5
CP3            5    6    4    0    3
CP4            9    8    5    3    0
```

The matrix should preferably use road distance from OSRM.

---

# 17. CVRP Model

Each collection point represents a demand.

Example:

```text
CP1 = 100 kg
CP2 = 200 kg
CP3 = 150 kg
CP4 = 250 kg
```

Vehicles:

```text
V1 = 500 kg
V2 = 500 kg
```

The optimizer must satisfy:

```text
Total waste assigned to V1 <= 500 kg

Total waste assigned to V2 <= 500 kg
```

---

# 18. Optimization Objective

Primary objective:

```text
Minimize total travel distance
```

Secondary considerations:

```text
Minimize travel time
Maximize waste collected
Prioritize high-priority points
Maximize vehicle utilization
```

A conceptual objective:

```text
Total Cost =

α × Distance

+ β × Travel Time

+ γ × Uncollected Waste

+ δ × Priority Penalty
```

The weights should be configurable.

---

# 19. Important Optimization Rule

The optimizer MUST NEVER assign more waste to a vehicle than its capacity.

Example:

```text
Vehicle capacity = 500 kg

Assigned:
CP1 = 200
CP2 = 150
CP3 = 150

Total = 500 kg ✓
```

Invalid:

```text
CP1 = 200
CP2 = 150
CP3 = 250

Total = 600 kg ✗
```

---

# 20. Route Output

The optimizer should return:

```json
{
  "vehicle_id": "V001",
  "route": [
    "DEPOT",
    "CP03",
    "CP01",
    "CP04",
    "DEPOT"
  ],
  "total_distance_km": 28.4,
  "estimated_duration_minutes": 62,
  "total_waste_kg": 500,
  "utilization_percentage": 100
}
```

---

# 21. Route Generation API

Endpoint:

```text
POST /api/optimization/generate
```

Request:

```json
{
  "depot_id": 1,
  "vehicle_ids": [1, 2, 3],
  "collection_point_ids": [1, 2, 3, 4, 5]
}
```

Response:

```json
{
  "optimization_id": 101,
  "status": "SUCCESS",
  "routes": []
}
```

---

# 22. Route Visualization

The frontend should display:

```text
Depot
  ↓
Collection Point 3
  ↓
Collection Point 7
  ↓
Collection Point 2
  ↓
Collection Point 8
  ↓
Depot
```

The actual road route should be rendered on the map.

Each vehicle should have a distinguishable route.

---

# 23. Driver Workflow

Driver logs in.

Dashboard:

```text
Vehicle:
MH12-AB-1234

Today's Route:
8 Collection Points

Estimated Distance:
31.4 km

Estimated Duration:
74 min
```

Driver presses:

```text
START ROUTE
```

The first collection point becomes active.

---

# 24. Collection Workflow

At each point:

```text
ARRIVE
```

Then:

```text
Expected:
150 kg

Actual:
142 kg
```

Driver can optionally:

```text
Upload Photo
Add Remarks
```

Then:

```text
CONFIRM COLLECTION
```

The stop becomes:

```text
COLLECTED ✓
```

The system proceeds to the next stop.

---

# 25. Failed Collection

If collection cannot happen:

```text
REPORT ISSUE
```

Reasons:

```text
NO WASTE
LOCATION INACCESSIBLE
VEHICLE ISSUE
COLLECTION POINT CLOSED
EXCESSIVE WASTE
OTHER
```

The system records the reason.

The point remains uncollected.

---

# 26. Dynamic Re-optimization

If a route changes during operation:

Example:

```text
Vehicle V001

Current:
CP1 ✓
CP2 ✓

Remaining:
CP3
CP4
CP5
```

New high-priority collection point:

```text
CP9 = 300 kg
```

The administrator can press:

```text
RE-OPTIMIZE ROUTE
```

The optimizer considers:

```text
Current vehicle location
Remaining collection points
Vehicle remaining capacity
New collection point
```

and generates a new route.

---

# 27. Dashboard Requirements

Dashboard must display:

### KPI Cards

```text
Total Waste Collected
Active Vehicles
Pending Collections
Completed Collections
Total Distance
Distance Saved
Estimated Fuel Saved
Vehicle Utilization
```

---

# 28. Map Dashboard

The map should show:

```text
Depot
Collection Points
Vehicle locations
Active routes
Completed points
Pending points
High-priority points
```

Clicking a collection point should show:

```text
Name
Address
Estimated waste
Priority
Last collection
Assigned vehicle
Status
```

---

# 29. Analytics

The analytics module should provide:

### Collection Analytics

```text
Total waste collected
Average collection per point
Daily collection
Weekly collection
Monthly collection
```

### Route Analytics

```text
Total distance
Average route distance
Average route duration
Vehicle utilization
```

### Optimization Impact

Compare:

```text
Before Optimization
vs
After Optimization
```

Metrics:

```text
Distance
Time
Fuel
Waste collected
Vehicle utilization
```

---

# 30. Fuel Saving Estimation

Fuel savings can be estimated using:

```text
Fuel Consumed =
Distance / Vehicle Efficiency
```

Example:

```text
Vehicle efficiency = 8 km/L

Old distance = 80 km
New distance = 60 km

Old fuel = 10 L
New fuel = 7.5 L

Estimated saving = 2.5 L
```

This should be clearly labelled:

> **Estimated fuel saving**

It should not be presented as an exact real-world measurement unless actual fuel data is available.

---

# 31. Frontend Pages

Create the following pages.

## Public

```text
/login
```

---

## Admin

```text
/dashboard

/collection-points

/collection-points/:id

/vehicles

/drivers

/routes

/routes/:id

/optimization

/analytics

/settings
```

---

## Driver

```text
/driver/dashboard

/driver/route

/driver/collection/:id
```

---

# 32. UI Design

The UI should be:

- Modern
- Professional
- Clean
- Responsive
- Dashboard-oriented
- Map-centric
- Easy to understand

Suggested visual direction:

```text
Primary:
Green / Eco tones

Background:
Light neutral

Cards:
White

Warnings:
Amber

Critical:
Red

Success:
Green
```

Avoid excessive gradients and unnecessary animations.

---

# 33. API Structure

Use:

```text
/api/auth

/api/users

/api/drivers

/api/vehicles

/api/depots

/api/collection-points

/api/waste

/api/optimization

/api/routes

/api/route-stops

/api/collections

/api/analytics

/api/notifications
```

---

# 34. Authentication

Use JWT.

Login:

```text
POST /api/auth/login
```

Response:

```json
{
  "access_token": "...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "name": "Admin",
    "role": "ADMIN"
  }
}
```

Protect admin-only APIs.

Protect driver-only APIs.

---

# 35. Recommended Project Structure

```text
plastic-waste-optimizer/
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── layouts/
│   │   ├── hooks/
│   │   ├── services/
│   │   ├── utils/
│   │   └── App.jsx
│   │
│   └── package.json
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   │
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── routes/
│   │   ├── services/
│   │   ├── repositories/
│   │   │
│   │   ├── optimization/
│   │   │   ├── solver.py
│   │   │   ├── distance_matrix.py
│   │   │   ├── constraints.py
│   │   │   └── scoring.py
│   │   │
│   │   └── database/
│   │
│   └── requirements.txt
│
├── data/
│   ├── collection_points.json
│   ├── vehicles.json
│   └── sample_data.json
│
├── tests/
│   ├── backend/
│   ├── optimization/
│   └── frontend/
│
├── docs/
│   ├── architecture.md
│   ├── api.md
│   └── optimization.md
│
├── .env.example
├── docker-compose.yml
├── README.md
└── Requirements.md
```

---

# 36. Development Strategy

The AI coding agent MUST NOT attempt to build everything at once.

Development must happen in phases.

---

# PHASE 0 — Project Initialization

Tasks:

1. Create repository
2. Create frontend
3. Create backend
4. Configure environment
5. Configure Git
6. Create database
7. Create README
8. Create architecture documentation

Acceptance criteria:

```text
Frontend runs.
Backend runs.
Database connects.
API health check works.
```

---

# PHASE 1 — Database

Implement:

```text
Users
Drivers
Vehicles
Depots
Collection Points
Waste Records
Routes
Route Stops
Collections
Optimization Runs
```

Create migrations.

Create seed data.

Acceptance criteria:

```text
Database can be initialized from scratch.
Seed data can be loaded.
CRUD operations work.
```

---

# PHASE 2 — Authentication

Implement:

```text
Admin login
Driver login
JWT
Role-based authorization
```

Acceptance criteria:

```text
Admin cannot access driver-only pages incorrectly.
Driver cannot access admin management pages.
```

---

# PHASE 3 — Collection Point Management

Implement:

```text
Create
Read
Update
Delete
Search
Filter
Map visualization
```

Acceptance criteria:

```text
Admin can create collection points.
Points appear on map.
Waste quantities are displayed.
Priority is visible.
```

---

# PHASE 4 — Vehicle Management

Implement:

```text
Create
Update
Delete
Assign driver
Set capacity
Set availability
```

Acceptance criteria:

```text
Vehicles appear in optimization input.
Unavailable vehicles are excluded.
Vehicle capacity is respected.
```

---

# PHASE 5 — Routing Engine

Integrate OSRM.

Implement:

```text
Distance matrix
Travel duration matrix
Road route geometry
```

Acceptance criteria:

```text
System can calculate road distance between points.
System can calculate travel duration.
System can render road route on map.
```

---

# PHASE 6 — Optimization Engine

Implement CVRP using OR-Tools.

Input:

```text
Depot
Vehicles
Capacity
Collection points
Demand
Distance matrix
```

Output:

```text
Vehicle routes
Stop sequence
Distance
Duration
Total waste
Utilization
```

Acceptance criteria:

```text
No vehicle exceeds capacity.
All feasible collection points are assigned.
Routes start/end at depot.
Distance is minimized.
```

---

# PHASE 7 — Optimization API

Expose:

```text
POST /api/optimization/generate
GET /api/optimization/:id
POST /api/optimization/:id/reoptimize
```

Acceptance criteria:

```text
Frontend can trigger optimization.
Backend returns routes.
Routes are persisted.
```

---

# PHASE 8 — Map & Route UI

Implement:

```text
Route visualization
Vehicle routes
Collection point markers
Stop sequence
Route details
```

Acceptance criteria:

```text
Admin can visually understand every generated route.
```

---

# PHASE 9 — Driver Interface

Implement:

```text
Assigned route
Start route
Current stop
Collection recording
Completion
Issue reporting
```

Acceptance criteria:

```text
Driver can complete an entire route without admin intervention.
```

---

# PHASE 10 — Analytics

Implement:

```text
Waste collected
Distance
Duration
Utilization
Distance savings
Estimated fuel savings
Collection completion
```

Acceptance criteria:

```text
Dashboard shows measurable impact.
```

---

# PHASE 11 — Testing

Create automated and manual tests.

Test:

```text
Authentication
CRUD
Optimization
Capacity
Routing
Collections
Analytics
```

Especially test:

```text
Vehicle capacity exceeded
No available vehicles
No collection points
One collection point
Large number of points
Invalid GPS coordinates
Failed collection
Route cancellation
Re-optimization
```

---

# PHASE 12 — Deployment

Recommended:

```text
Frontend → Vercel
Backend → Render / Railway / AWS
Database → PostgreSQL managed service
```

Use environment variables.

Never commit:

```text
API keys
JWT secrets
Database passwords
```

---

# 37. Optimization Engine — Detailed Logic

The optimization service should follow this sequence:

```text
Receive request
       ↓
Validate input
       ↓
Fetch collection points
       ↓
Fetch available vehicles
       ↓
Fetch depot
       ↓
Calculate priority
       ↓
Request road distance matrix
       ↓
Build CVRP model
       ↓
Add vehicle capacity constraints
       ↓
Add depot constraints
       ↓
Add priority weighting
       ↓
Run OR-Tools
       ↓
Extract routes
       ↓
Calculate route statistics
       ↓
Store optimization run
       ↓
Store routes
       ↓
Return result
```

---

# 38. Error Handling

The system should handle:

```text
No available vehicles
Insufficient total vehicle capacity
Invalid collection point
Invalid coordinates
Routing API unavailable
Optimization failure
Database failure
Authentication failure
```

Example:

```json
{
  "error": "INSUFFICIENT_CAPACITY",
  "message": "Available vehicle capacity is 1200kg but selected collection demand is 1450kg."
}
```

The UI should show a human-readable message.

---

# 39. Important Optimization Edge Cases

The system must handle:

### Case 1

Total waste:

```text
800 kg
```

Vehicle capacity:

```text
1000 kg
```

→ One vehicle can handle it.

### Case 2

Total waste:

```text
1500 kg
```

Vehicles:

```text
500 + 500 + 500
```

→ Three vehicles.

### Case 3

Total waste:

```text
1600 kg
```

Capacity:

```text
1500 kg
```

→ System should warn that not all waste can be collected.

### Case 4

One collection point:

```text
700 kg
```

Vehicle:

```text
500 kg
```

→ The system must not assign that demand to the vehicle without a supported split-collection strategy.

For the MVP, report it as an infeasible/exception case rather than silently violating capacity.

---

# 40. AI Agent Development Rules

The AI coding agent must follow these rules.

## Rule 1

Do not rewrite existing working modules unnecessarily.

## Rule 2

Do not create duplicate APIs.

## Rule 3

Do not create duplicate database models.

## Rule 4

Do not hardcode production API keys.

## Rule 5

Use environment variables.

## Rule 6

Write reusable components.

## Rule 7

Keep frontend and backend separated.

## Rule 8

Every major feature must have tests.

## Rule 9

Do not implement future features before MVP features are working.

## Rule 10

After every major phase, verify that the application still runs.

---

# 41. AI Agent Execution Workflow

The AI agent should work using:

```text
PLAN
 ↓
IMPLEMENT
 ↓
RUN
 ↓
TEST
 ↓
DEBUG
 ↓
VERIFY
 ↓
DOCUMENT
```

It should NOT:

```text
Generate 50 files
       ↓
Assume everything works
       ↓
Stop
```

---

# 42. Required Development Order

The agent MUST implement in this order:

```text
1. Project setup

2. Database

3. Authentication

4. Collection points

5. Vehicles

6. Routing service

7. Optimization engine

8. Optimization API

9. Map visualization

10. Route management

11. Driver interface

12. Collection tracking

13. Analytics

14. Testing

15. Deployment
```

Do not reverse this order without a strong technical reason.

---

# 43. Demo Dataset

Create a realistic seed dataset.

Minimum:

```text
1 Depot
20 Collection Points
3 Vehicles
3 Drivers
```

Recommended:

```text
1 Depot
30 Collection Points
5 Vehicles
5 Drivers
```

Each collection point should have:

```text
Name
Latitude
Longitude
Waste quantity
Waste type
Priority
Last collection date
```

---

# 44. Example Demo Scenario

Depot:

```text
Central Recycling Facility
```

Vehicles:

```text
V001 → 500kg
V002 → 750kg
V003 → 500kg
```

Collection points:

```text
CP01 → 100kg
CP02 → 200kg
CP03 → 150kg
CP04 → 300kg
CP05 → 80kg
CP06 → 250kg
...
```

Total demand should intentionally be greater than one vehicle's capacity so that multi-vehicle optimization can be demonstrated.

---

# 45. Performance Requirements

For a demo dataset of:

```text
100 collection points
10 vehicles
```

the optimization process should ideally complete within a few seconds to tens of seconds depending on routing and solver configuration.

The UI should show a loading state:

```text
Optimizing routes...
Calculating distances...
Applying vehicle constraints...
Generating routes...
```

Do not freeze the interface.

---

# 46. Security Requirements

Implement:

- Password hashing
- JWT authentication
- Role-based authorization
- Input validation
- SQL injection protection through ORM
- CORS configuration
- Environment variables
- File upload validation
- API error handling

Never expose:

```text
Database password
JWT secret
External API keys
```

---

# 47. Acceptance Criteria

The project is considered MVP-complete only when all of these work:

```text
[ ] Admin can log in

[ ] Admin can create collection points

[ ] Admin can see collection points on map

[ ] Admin can create vehicles

[ ] Admin can assign drivers

[ ] System can calculate road distances

[ ] System can generate multi-vehicle routes

[ ] Vehicle capacity is respected

[ ] Routes start and end at depot

[ ] Routes appear on map

[ ] Admin can assign routes

[ ] Driver can view assigned route

[ ] Driver can mark collection completed

[ ] Driver can record actual quantity

[ ] Dashboard updates collection statistics

[ ] System calculates route savings

[ ] System handles optimization errors

[ ] Tests pass

[ ] Application can be deployed
```

---

# 48. Definition of Success

The project should demonstrate this complete scenario:

```text
Admin
  ↓
Adds collection points
  ↓
Adds vehicles
  ↓
System knows waste quantities
  ↓
Admin clicks "Optimize Routes"
  ↓
Routing engine calculates road distances
  ↓
OR-Tools optimizes vehicle assignments
  ↓
System generates routes
  ↓
Routes displayed on map
  ↓
Drivers receive routes
  ↓
Drivers collect plastic
  ↓
Drivers record actual quantities
  ↓
Dashboard updates
  ↓
System shows operational savings
```

---

# 49. Final Product Goal

The final product should communicate this clearly:

> **"Our platform intelligently plans and monitors recyclable plastic collection by assigning collection points to appropriate vehicles and generating optimized, capacity-aware routes that reduce unnecessary travel, improve vehicle utilization, and increase collection efficiency."**

The system should prioritize:

```text
Correctness
   ↓
Reliability
   ↓
Optimization
   ↓
Usability
   ↓
Visual polish
   ↓
Advanced AI
```

Do NOT prioritize flashy AI features over a working optimization engine.

---

# 50. Final Instruction to AI Coding Agent

When using this document with an AI coding agent, instruct the agent:

> **Treat this Requirements.md as the source of truth for the project. Before implementing any feature, inspect the existing repository and understand the current architecture. Do not blindly overwrite existing code. Implement the project incrementally according to the development phases defined in this document. After each phase, run the application, execute relevant tests, verify integration, and report what was implemented, what was tested, and what remains. Prioritize a working MVP over optional features. Do not implement future features until all MVP acceptance criteria are satisfied.**

---

# 51. Recommended Build Milestones

## Milestone 1

```text
Backend + Database
```

Working.

## Milestone 2

```text
Collection Points + Vehicles
```

Working.

## Milestone 3 ⭐

```text
OR-Tools
+
OSRM
+
CVRP
```

Working.

This is the **technical core**.

## Milestone 4 ⭐

```text
Map
+
Optimized Routes
```

Working.

This is the **visual core**.

## Milestone 5

```text
Driver Collection
```

Working.

## Milestone 6

```text
Analytics
+
Before/After Comparison
```

Working.

## Milestone 7

```text
Testing
+
Deployment
+
Demo
```

Complete.

---

# 52. What NOT to Do

Do not start by building:

```text
❌ AI chatbot
❌ Fancy landing page
❌ Blockchain
❌ IoT
❌ Mobile app
❌ Computer vision
❌ Complex ML model
```

before:

```text
✓ Database
✓ Routing
✓ Optimization
✓ Map
✓ Vehicle capacity
✓ Collection workflow
```

are working.

Your **OR-Tools + road routing + capacity-aware multi-vehicle optimization** is the heart of this project.

Everything else supports that.

---

# 53. Team Leader's Master Workflow

As team leader, your personal workflow should be:

```text
                 REQUIREMENTS
                      │
                      ▼
                 ARCHITECTURE
                      │
                      ▼
                 TASK BREAKDOWN
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
       FRONTEND    BACKEND    OPTIMIZATION
          │           │           │
          └───────────┼───────────┘
                      ▼
                  INTEGRATION
                      │
                      ▼
                    TEST
                      │
                      ▼
                  DEMO BUILD
                      │
                      ▼
                 FINAL POLISH
                      │
                      ▼
                   SIH DEMO
```

Your biggest responsibility is keeping these branches synchronized.

For example:

```text
Optimizer says:
"Output will contain vehicle_id + ordered stops."

             ↓

Backend knows:
"I need to expose that output through /optimization."

             ↓

Frontend knows:
"I need to render those ordered stops."

             ↓

Maps developer knows:
"I need those stops to draw the route."

             ↓

Driver developer knows:
"I need those stops to create the driver's task list."
```

**That is what good technical leadership looks like.**

---

# 54. The First Thing Your Team Should Do

Before asking Antigravity to generate the entire application, create:

```text
Requirements.md
Architecture.md
Database Schema
API Specification
Optimization Specification
```

Then give the AI agent the instruction:

```text
Read Requirements.md completely.

Do not start coding immediately.

First inspect the repository and produce:

1. Current project structure
2. Proposed architecture
3. Technology requirements
4. Database implementation plan
5. API implementation plan
6. Optimization engine implementation plan
7. Frontend implementation plan
8. Dependency graph
9. Phase-by-phase development plan

Do not modify code yet.

Wait for approval after presenting the plan.
```

This is the approach I strongly recommend.

Once the plan is approved, tell it:

```text
Implement Phase 0 only.

After implementation:
1. Run the application.
2. Run tests.
3. Verify the health endpoint.
4. Verify database connectivity.
5. Report changed files.
6. Report test results.
7. Report any blockers.

Do not implement Phase 1 or later.
```

Then proceed phase by phase.

**This prevents the AI agent from creating a giant, unmaintainable codebase in one shot.**

---

## 🚀 One important recommendation for your SIH team

Since you're the **team leader**, don't try to personally learn/build everything simultaneously.

Your first leadership objective should be:

**Get the team to successfully produce this one sentence as a working prototype:**

> **“Given a depot, 20 plastic collection points, 3 vehicles with different capacities, and estimated waste quantities, our system automatically generates feasible optimized collection routes and displays them on a map.”**

Once your team achieves that, **you've crossed the hardest technical barrier**. Then driver tracking, analytics, AI prediction, notifications, and other features can be layered on top.

And when you give this to Antigravity, **use this `Requirements.md` as the master specification rather than one giant “build my project” prompt**. That will give you much more predictable results.