# Plastic Waste Collection Optimization Platform

> **Smart Waste Management + Capacitated Vehicle Routing Problem (CVRP) Optimization + Geospatial Web Platform**

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/Frontend-React_18-61DAFB.svg)](https://react.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Styling-Tailwind_CSS-38B2AC.svg)](https://tailwindcss.com/)
[![OR-Tools](https://img.shields.io/badge/Optimization-Google_OR--Tools-4285F4.svg)](https://developers.google.com/optimization)
[![OSRM](https://img.shields.io/badge/Routing-OpenStreetMap_OSRM-7E57C2.svg)](http://project-osrm.org/)

---

## 📌 Project Overview

The **Plastic Waste Collection Optimization Platform** is a data-driven operational system designed to optimize the collection of recyclable plastic waste from geographically distributed collection points.

By combining **Google OR-Tools (CVRP)** with **OpenStreetMap / OSRM road routing**, the platform generates capacity-aware, shortest-distance routes for multi-vehicle fleets, preventing payload overshoots while prioritizing critical high-overflow collection points.

---

## 🛠️ Technology Stack

* **Frontend**: React 18, Vite, Tailwind CSS, React Router v7, Leaflet / React-Leaflet, Recharts, Lucide Icons.
* **Backend**: Python 3.10+, FastAPI, Pydantic v2, SQLAlchemy 2.0 ORM, Alembic.
* **Database**: PostgreSQL (Production) / SQLite (Development Fallback).
* **Optimization**: Google OR-Tools (Capacitated Vehicle Routing Problem).
* **Geospatial Routing**: OpenStreetMap OSRM API (NxM Distance & Duration Matrix + Snapped Road Polylines).
* **Auth**: JWT Authentication with `bcrypt` password hashing and Role-Based Access Control (`ADMIN`, `DRIVER`, `MANAGER`).

---

## 🚀 Quick Start & Installation

### Prerequisites
* **Node.js**: v18+ (Tested on Node v24)
* **Python**: v3.10+ (Tested on Python 3.14)
* **Git**

### 1. Clone & Setup Environment
```bash
git clone <repository-url>
cd SIH
cp .env.example .env
```

### 2. Backend Setup
```bash
cd backend
python -m pip install -r requirements.txt
python -m pytest   # Run health check tests
python -m uvicorn app.main:app --reload --port 8000
```
* **Swagger API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
* **Health Check API**: [http://localhost:8000/api/health](http://localhost:8000/api/health)

### 3. Frontend Setup
```bash
cd frontend
npm install --legacy-peer-deps
npm run dev
```
* **Web App Portal**: [http://localhost:5173](http://localhost:5173)

---

## 🐳 Docker Deployment

To run both backend, frontend, and PostgreSQL database in Docker containers:
```bash
docker-compose up --build
```

---

## 🧪 Testing

Run backend test suite:
```bash
cd backend
python -m pytest
```

---

## 📋 Implementation Milestones

- [x] **Phase 0**: Initialization, Folder Setup, Environment, Health Check & Architecture Documentation.
- [x] **Phase 1**: Database Models, Migrations & Demo Dataset Seeding.
- [x] **Phase 2**: JWT Authentication & Role-Based Authorization.
- [x] **Phase 3**: Collection Point Management & Priority Calculation Engine.
- [x] **Phase 4**: Vehicle Fleet Management & Driver Roster.
- [x] **Phase 5**: OSRM Road Distance & Geometry Service.
- [x] **Phase 6**: Google OR-Tools CVRP Optimization Engine.
- [x] **Phase 7**: Optimization REST APIs & Persistence.
- [x] **Phase 8**: Leaflet Map Visualization & Snapped Road Routes.
- [x] **Phase 9**: Driver Mobile Execution Portal.
- [x] **Phase 10**: Analytics Dashboard & Fuel Savings Estimation.
- [x] **Phase 11**: End-to-End Testing & Hardening.
- [x] **Phase 12**: Deployment Setup.

