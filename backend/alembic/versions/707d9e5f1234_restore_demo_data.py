"""Restore demo operational dataset.

Revision ID: 707d9e5f1234
Revises: 706c9e4a8123
Create Date: 2026-09-14
"""

from datetime import datetime, timedelta
from typing import Sequence, Union

from alembic import op
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models import (
    User,
    UserRole,
    Driver,
    DriverStatus,
    Vehicle,
    VehicleStatus,
    Depot,
    CollectionPoint,
    WasteType,
    PriorityLevel,
    WasteRecord,
)
from app.services.priority_service import calculate_collection_point_priority


revision: str = "707d9e5f1234"
down_revision: Union[str, Sequence[str], None] = "706c9e4a8123"
branch_labels = None
depends_on = None


DEMO_DRIVERS = [
    {
        "name": "Rahul Sharma",
        "email": "rahul@ecoroute.org",
        "license": "MH-12-2021-0084921",
        "phone": "+91 98765 43210",
    },
    {
        "name": "Amit Patel",
        "email": "amit@ecoroute.org",
        "license": "MH-12-2020-0043812",
        "phone": "+91 98765 43211",
    },
    {
        "name": "Suresh Verma",
        "email": "suresh@ecoroute.org",
        "license": "MH-14-2019-0091234",
        "phone": "+91 98765 43212",
    },
    {
        "name": "Vikas Singh",
        "email": "vikas@ecoroute.org",
        "license": "MH-12-2022-0012984",
        "phone": "+91 98765 43213",
    },
    {
        "name": "Prakash Jadhav",
        "email": "prakash@ecoroute.org",
        "license": "MH-14-2023-0056789",
        "phone": "+91 98765 43214",
    },
]


DEMO_VEHICLES = [
    {
        "number": "MH-12-PQ-1001",
        "type": "E-Truck Heavy",
        "capacity": 1200.0,
        "driver_email": "rahul@ecoroute.org",
    },
    {
        "number": "MH-12-PQ-1002",
        "type": "E-Truck Medium",
        "capacity": 1000.0,
        "driver_email": "amit@ecoroute.org",
    },
    {
        "number": "MH-12-PQ-1003",
        "type": "Recycling Van",
        "capacity": 800.0,
        "driver_email": "suresh@ecoroute.org",
    },
    {
        "number": "MH-14-AZ-2004",
        "type": "E-Truck Heavy",
        "capacity": 1500.0,
        "driver_email": "vikas@ecoroute.org",
    },
    {
        "number": "MH-14-AZ-2005",
        "type": "E-Truck Medium",
        "capacity": 1000.0,
        "driver_email": "prakash@ecoroute.org",
    },
]


DEMO_COLLECTION_POINTS = [
    ("Baner Plastic Bin #1", "Baner High Street, Baner, Pune", 18.5590, 73.7868, 220.0, WasteType.PET, 3, True),
    ("Wakad IT Park Collection", "Datta Mandir Road, Wakad, Pune", 18.5987, 73.7621, 310.0, WasteType.HDPE, 5, True),
    ("Hinjewadi Phase 1 Bin", "Rajiv Gandhi IT Park, Hinjewadi", 18.5912, 73.7389, 450.0, WasteType.MIXED_PLASTIC, 7, True),
    ("Aundh Commercial Hub", "ITI Road, Aundh, Pune", 18.5602, 73.8078, 180.0, WasteType.PET, 2, False),
    ("Kothrud Depot Yard", "DP Road, Kothrud, Pune", 18.5074, 73.8077, 260.0, WasteType.PP, 4, False),
    ("Viman Nagar Mall Bin", "Phoenix Marketcity Road, Viman Nagar", 18.5679, 73.9143, 380.0, WasteType.PET, 6, True),
    ("Kalyani Nagar Recycling", "South Avenue, Kalyani Nagar", 18.5463, 73.9034, 150.0, WasteType.LDPE, 1, False),
    ("Hadapsar Industrial Bin", "Magarpatta City Main Entrance, Hadapsar", 18.5158, 73.9272, 420.0, WasteType.HDPE, 8, True),
    ("Shivajinagar Station Point", "JM Road, Shivajinagar, Pune", 18.5308, 73.8475, 200.0, WasteType.PET, 2, False),
    ("FC Road Commercial Bin", "Fergusson College Road, Pune", 18.5236, 73.8412, 290.0, WasteType.MIXED_PLASTIC, 4, True),
    ("Deccan Gymkhana Stop", "Karve Road, Deccan Gymkhana, Pune", 18.5167, 73.8415, 170.0, WasteType.PP, 3, False),
    ("Camp MG Road Center", "MG Road, Pune Camp", 18.5165, 73.8762, 240.0, WasteType.PET, 4, False),
    ("Swargate Bus Stand Yard", "Satara Road, Swargate, Pune", 18.5005, 73.8580, 310.0, WasteType.MIXED_PLASTIC, 5, True),
    ("Bibwewadi Market Yard", "Swami Vivekanand Road, Bibwewadi", 18.4735, 73.8643, 210.0, WasteType.HDPE, 3, False),
    ("Katraj Zoo Recycling Point", "Pune-Satara Highway, Katraj", 18.4529, 73.8569, 280.0, WasteType.PET, 5, False),
    ("Warje Highway Collection", "Mumbai-Bangalore Highway, Warje", 18.4820, 73.7932, 190.0, WasteType.LDPE, 2, False),
    ("Pimple Saudagar Center", "Govind Yashada Chowk, Pimple Saudagar", 18.5901, 73.7995, 330.0, WasteType.PET, 6, True),
    ("Chinchwad Station Bin", "Old Mumbai-Pune Highway, Chinchwad", 18.6276, 73.7997, 400.0, WasteType.MIXED_PLASTIC, 7, True),
    ("Pimpri Market Yard", "Shastri Nagar, Pimpri", 18.6298, 73.8124, 350.0, WasteType.HDPE, 4, True),
    ("Bhosari MIDC Hub #1", "Telco Road, Bhosari Industrial Area", 18.6385, 73.8471, 480.0, WasteType.OTHER_RECYCLABLE_PLASTIC, 9, True),
    ("Nigdi Pradhikaran Bin", "Appu Ghar Road, Nigdi, Pune", 18.6534, 73.7712, 230.0, WasteType.PET, 3, False),
    ("Kharadi EON Free Zone", "Kharadi IT Park Road, Kharadi", 18.5516, 73.9531, 390.0, WasteType.MIXED_PLASTIC, 6, True),
    ("Wagholi Commercial Point", "Nagar Road, Wagholi", 18.5794, 73.9812, 270.0, WasteType.PP, 4, False),
    ("Yerwada Jail Chowk Bin", "Airport Road, Yerwada, Pune", 18.5552, 73.8821, 160.0, WasteType.LDPE, 1, False),
    ("Vishrantwadi Junction", "Dhanori Road, Vishrantwadi", 18.5684, 73.8732, 210.0, WasteType.PET, 2, False),
    ("Kondhwa Market Point", "NIBM Road, Kondhwa, Pune", 18.4792, 73.8912, 320.0, WasteType.HDPE, 5, True),
    ("Undri City Center", "Undri-Pisoli Road, Pune", 18.4561, 73.9015, 180.0, WasteType.PP, 2, False),
    ("Dhanori Green Yard", "Lohegaon Road, Dhanori", 18.5831, 73.8981, 240.0, WasteType.PET, 3, False),
    ("Bavdhan Hub", "Chandani Chowk, Bavdhan, Pune", 18.5112, 73.7721, 290.0, WasteType.MIXED_PLASTIC, 4, False),
    ("Pashan Lake Gate Bin", "Pashan-NDA Road, Pashan", 18.5376, 73.7925, 140.0, WasteType.LDPE, 1, False),
]


def upgrade() -> None:
    connection = op.get_bind()
    db = Session(bind=connection)

    try:
        print("=== Restoring EcoRoute Demo Operational Dataset ===")

        # ---------------------------------------------------------
        # 1. Ensure all demo driver users exist
        # ---------------------------------------------------------
        driver_users = {}

        password_hash = get_password_hash("Password123!")

        for data in DEMO_DRIVERS:
            user = (
                db.query(User)
                .filter(User.email == data["email"])
                .first()
            )

            if not user:
                user = User(
                    name=data["name"],
                    email=data["email"],
                    password_hash=password_hash,
                    role=UserRole.DRIVER,
                )
                db.add(user)
                db.flush()
                print(f"[ADD] Driver user: {data['email']}")
            else:
                print(f"[KEEP] Existing user: {data['email']}")

            driver_users[data["email"]] = user

        db.flush()

        # ---------------------------------------------------------
        # 2. Ensure demo drivers exist
        # ---------------------------------------------------------
        drivers = {}

        for data in DEMO_DRIVERS:
            user = driver_users[data["email"]]

            driver = (
                db.query(Driver)
                .filter(Driver.user_id == user.id)
                .first()
            )

            if not driver:
                driver = (
                    db.query(Driver)
                    .filter(Driver.license_number == data["license"])
                    .first()
                )

            if not driver:
                driver = Driver(
                    user_id=user.id,
                    license_number=data["license"],
                    phone=data["phone"],
                    status=DriverStatus.AVAILABLE,
                )
                db.add(driver)
                db.flush()
                print(f"[ADD] Driver: {data['name']}")
            else:
                print(f"[KEEP] Driver: {data['name']}")

            drivers[data["email"]] = driver

        db.flush()

        # ---------------------------------------------------------
        # 3. Ensure demo vehicles exist
        # ---------------------------------------------------------
        for data in DEMO_VEHICLES:
            existing = (
                db.query(Vehicle)
                .filter(Vehicle.vehicle_number == data["number"])
                .first()
            )

            if existing:
                print(f"[KEEP] Vehicle: {data['number']}")
                continue

            driver = drivers[data["driver_email"]]

            vehicle = Vehicle(
                vehicle_number=data["number"],
                vehicle_type=data["type"],
                capacity_kg=data["capacity"],
                driver_id=driver.id,
                status=VehicleStatus.AVAILABLE,
                current_latitude=18.5204,
                current_longitude=73.8567,
            )

            db.add(vehicle)
            db.flush()

            print(f"[ADD] Vehicle: {data['number']}")

        # ---------------------------------------------------------
        # 4. Ensure central demo depot exists
        # ---------------------------------------------------------
        depot_name = "Central Recycling & Material Recovery Facility"

        depot = (
            db.query(Depot)
            .filter(Depot.name == depot_name)
            .first()
        )

        if not depot:
            depot = Depot(
                name=depot_name,
                address="Swargate Central Depot, Tilak Road, Pune, Maharashtra 411002",
                latitude=18.5018,
                longitude=73.8636,
            )

            db.add(depot)
            db.flush()

            print("[ADD] Central Recycling Depot")
        else:
            print("[KEEP] Central Recycling Depot")

        # ---------------------------------------------------------
        # 5. Ensure 30 demo collection points exist
        # ---------------------------------------------------------
        now = datetime.utcnow()

        for (
            name,
            address,
            latitude,
            longitude,
            quantity,
            waste_type,
            days_ago,
            overflow,
        ) in DEMO_COLLECTION_POINTS:

            existing = (
                db.query(CollectionPoint)
                .filter(CollectionPoint.name == name)
                .first()
            )

            if existing:
                print(f"[KEEP] Collection Point: {name}")

                # If the existing point has no waste record, restore it.
                record = (
                    db.query(WasteRecord)
                    .filter(
                        WasteRecord.collection_point_id == existing.id,
                        WasteRecord.source == "ESTIMATE",
                    )
                    .first()
                )

                if not record:
                    db.add(
                        WasteRecord(
                            collection_point_id=existing.id,
                            estimated_quantity_kg=existing.estimated_waste_kg,
                            source="ESTIMATE",
                        )
                    )
                    print(f"[ADD] Waste Record for: {name}")

                continue

            last_collection = now - timedelta(days=days_ago)

            calculated_priority, score = (
                calculate_collection_point_priority(
                    estimated_waste_kg=quantity,
                    waste_type=waste_type,
                    last_collection_date=last_collection,
                    overflow_status=overflow,
                )
            )

            collection_point = CollectionPoint(
                name=name,
                address=address,
                latitude=latitude,
                longitude=longitude,
                estimated_waste_kg=quantity,
                waste_type=waste_type,
                priority=calculated_priority,
                last_collection_date=last_collection,
                overflow_status=overflow,
                status="ACTIVE",
            )

            db.add(collection_point)
            db.flush()

            db.add(
                WasteRecord(
                    collection_point_id=collection_point.id,
                    estimated_quantity_kg=quantity,
                    source="ESTIMATE",
                )
            )

            print(
                f"[ADD] Collection Point: {name} "
                f"(priority={calculated_priority.value}, score={score})"
            )

        db.commit()

        print("=== Demo Dataset Restoration Complete ===")
        print(f"Users: {db.query(User).count()}")
        print(f"Drivers: {db.query(Driver).count()}")
        print(f"Vehicles: {db.query(Vehicle).count()}")
        print(f"Depots: {db.query(Depot).count()}")
        print(f"Collection Points: {db.query(CollectionPoint).count()}")
        print(f"Waste Records: {db.query(WasteRecord).count()}")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def downgrade() -> None:
    # Intentionally empty.
    #
    # This migration restores demo data while preserving user-created
    # records. Automatically deleting records during downgrade could
    # therefore destroy manually-created operational data.
    pass