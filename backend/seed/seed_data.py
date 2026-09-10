import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy.orm import Session
from app.core.security import get_password_hash
from app.database.session import SessionLocal, engine
from app.database.base import Base
from app.models import (
    User, UserRole,
    Driver, DriverStatus,
    Vehicle, VehicleStatus,
    Depot,
    CollectionPoint, WasteType, PriorityLevel,
    WasteRecord
)
from app.services.priority_service import calculate_collection_point_priority

def seed_db():
    print("=== Initializing Database Seed Script ===")
    
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    try:
        # Check if seed data already exists
        if db.query(User).filter_by(email="admin@ecoroute.org").first():
            print("[INFO] Seed data already exists in database. Skipping seed.")
            return

        print("[SEEDB] Creating Demo Users...")
        # Password for all demo accounts: Password123!
        default_hash = get_password_hash("Password123!")

        admin_user = User(
            name="Operations Admin",
            email="admin@ecoroute.org",
            password_hash=default_hash,
            role=UserRole.ADMIN
        )
        manager_user = User(
            name="Rajesh Kumar (Operations Manager)",
            email="manager@ecoroute.org",
            password_hash=default_hash,
            role=UserRole.MANAGER
        )
        
        driver_users = [
          User(name="Rahul Sharma", email="rahul@ecoroute.org", password_hash=default_hash, role=UserRole.DRIVER),
          User(name="Amit Patel", email="amit@ecoroute.org", password_hash=default_hash, role=UserRole.DRIVER),
          User(name="Suresh Verma", email="suresh@ecoroute.org", password_hash=default_hash, role=UserRole.DRIVER),
          User(name="Vikas Singh", email="vikas@ecoroute.org", password_hash=default_hash, role=UserRole.DRIVER),
          User(name="Prakash Jadhav", email="prakash@ecoroute.org", password_hash=default_hash, role=UserRole.DRIVER),
        ]

        db.add_all([admin_user, manager_user] + driver_users)
        db.commit()

        print("[SEEDB] Creating Drivers Roster...")
        drivers = [
            Driver(user_id=driver_users[0].id, license_number="MH-12-2021-0084921", phone="+91 98765 43210", status=DriverStatus.AVAILABLE),
            Driver(user_id=driver_users[1].id, license_number="MH-12-2020-0043812", phone="+91 98765 43211", status=DriverStatus.AVAILABLE),
            Driver(user_id=driver_users[2].id, license_number="MH-14-2019-0091234", phone="+91 98765 43212", status=DriverStatus.AVAILABLE),
            Driver(user_id=driver_users[3].id, license_number="MH-12-2022-0012984", phone="+91 98765 43213", status=DriverStatus.AVAILABLE),
            Driver(user_id=driver_users[4].id, license_number="MH-14-2023-0056789", phone="+91 98765 43214", status=DriverStatus.AVAILABLE),
        ]
        db.add_all(drivers)
        db.commit()

        print("[SEEDB] Creating Vehicles Fleet...")
        vehicles = [
            Vehicle(vehicle_number="MH-12-PQ-1001", vehicle_type="E-Truck Heavy", capacity_kg=1200.0, driver_id=drivers[0].id, status=VehicleStatus.AVAILABLE, current_latitude=18.5204, current_longitude=73.8567),
            Vehicle(vehicle_number="MH-12-PQ-1002", vehicle_type="E-Truck Medium", capacity_kg=1000.0, driver_id=drivers[1].id, status=VehicleStatus.AVAILABLE, current_latitude=18.5204, current_longitude=73.8567),
            Vehicle(vehicle_number="MH-12-PQ-1003", vehicle_type="Recycling Van", capacity_kg=800.0, driver_id=drivers[2].id, status=VehicleStatus.AVAILABLE, current_latitude=18.5204, current_longitude=73.8567),
            Vehicle(vehicle_number="MH-14-AZ-2004", vehicle_type="E-Truck Heavy", capacity_kg=1500.0, driver_id=drivers[3].id, status=VehicleStatus.AVAILABLE, current_latitude=18.5204, current_longitude=73.8567),
            Vehicle(vehicle_number="MH-14-AZ-2005", vehicle_type="E-Truck Medium", capacity_kg=1000.0, driver_id=drivers[4].id, status=VehicleStatus.AVAILABLE, current_latitude=18.5204, current_longitude=73.8567),
        ]
        db.add_all(vehicles)
        db.commit()

        print("[SEEDB] Creating Central Recycling Depot...")
        depot = Depot(
            name="Central Recycling & Material Recovery Facility",
            address="Swargate Central Depot, Tilak Road, Pune, Maharashtra 411002",
            latitude=18.5018,
            longitude=73.8636
        )
        db.add(depot)
        db.commit()

        print("[SEEDB] Creating 30 Collection Points in Pune Region...")
        points_data = [
            ("Baner Plastic Bin #1", "Baner High Street, Baner, Pune", 18.5590, 73.7868, 220.0, WasteType.PET, PriorityLevel.HIGH, 3, True),
            ("Wakad IT Park Collection", "Datta Mandir Road, Wakad, Pune", 18.5987, 73.7621, 310.0, WasteType.HDPE, PriorityLevel.CRITICAL, 5, True),
            ("Hinjewadi Phase 1 Bin", "Rajiv Gandhi IT Park, Hinjewadi", 18.5912, 73.7389, 450.0, WasteType.MIXED_PLASTIC, PriorityLevel.CRITICAL, 7, True),
            ("Aundh Commercial Hub", "ITI Road, Aundh, Pune", 18.5602, 73.8078, 180.0, WasteType.PET, PriorityLevel.MEDIUM, 2, False),
            ("Kothrud Depot Yard", "DP Road, Kothrud, Pune", 18.5074, 73.8077, 260.0, WasteType.PP, PriorityLevel.HIGH, 4, False),
            ("Viman Nagar Mall Bin", "Phoenix Marketcity Road, Viman Nagar", 18.5679, 73.9143, 380.0, WasteType.PET, PriorityLevel.CRITICAL, 6, True),
            ("Kalyani Nagar Recycling", "South Avenue, Kalyani Nagar", 18.5463, 73.9034, 150.0, WasteType.LDPE, PriorityLevel.LOW, 1, False),
            ("Hadapsar Industrial Bin", "Magarpatta City Main Entrance, Hadapsar", 18.5158, 73.9272, 420.0, WasteType.HDPE, PriorityLevel.CRITICAL, 8, True),
            ("Shivajinagar Station Point", "JM Road, Shivajinagar, Pune", 18.5308, 73.8475, 200.0, WasteType.PET, PriorityLevel.MEDIUM, 2, False),
            ("FC Road Commercial Bin", "Fergusson College Road, Pune", 18.5236, 73.8412, 290.0, WasteType.MIXED_PLASTIC, PriorityLevel.HIGH, 4, True),
            ("Deccan Gymkhana Stop", "Karve Road, Deccan Gymkhana, Pune", 18.5167, 73.8415, 170.0, WasteType.PP, PriorityLevel.MEDIUM, 3, False),
            ("Camp MG Road Center", "MG Road, Pune Camp", 18.5165, 73.8762, 240.0, WasteType.PET, PriorityLevel.HIGH, 4, False),
            ("Swargate Bus Stand Yard", "Satara Road, Swargate, Pune", 18.5005, 73.8580, 310.0, WasteType.MIXED_PLASTIC, PriorityLevel.CRITICAL, 5, True),
            ("Bibwewadi Market Yard", "Swami Vivekanand Road, Bibwewadi", 18.4735, 73.8643, 210.0, WasteType.HDPE, PriorityLevel.MEDIUM, 3, False),
            ("Katraj Zoo Recycling Point", "Pune-Satara Highway, Katraj", 18.4529, 73.8569, 280.0, WasteType.PET, PriorityLevel.HIGH, 5, False),
            ("Warje Highway Collection", "Mumbai-Bangalore Highway, Warje", 18.4820, 73.7932, 190.0, WasteType.LDPE, PriorityLevel.LOW, 2, False),
            ("Pimple Saudagar Center", "Govind Yashada Chowk, Pimple Saudagar", 18.5901, 73.7995, 330.0, WasteType.PET, PriorityLevel.HIGH, 6, True),
            ("Chinchwad Station Bin", "Old Mumbai-Pune Highway, Chinchwad", 18.6276, 73.7997, 400.0, WasteType.MIXED_PLASTIC, PriorityLevel.CRITICAL, 7, True),
            ("Pimpri Market Yard", "Shastri Nagar, Pimpri", 18.6298, 73.8124, 350.0, WasteType.HDPE, PriorityLevel.HIGH, 4, True),
            ("Bhosari MIDC Hub #1", "Telco Road, Bhosari Industrial Area", 18.6385, 73.8471, 480.0, WasteType.OTHER_RECYCLABLE_PLASTIC, PriorityLevel.CRITICAL, 9, True),
            ("Nigdi Pradhikaran Bin", "Appu Ghar Road, Nigdi, Pune", 18.6534, 73.7712, 230.0, WasteType.PET, PriorityLevel.MEDIUM, 3, False),
            ("Kharadi EON Free Zone", "Kharadi IT Park Road, Kharadi", 18.5516, 73.9531, 390.0, WasteType.MIXED_PLASTIC, PriorityLevel.CRITICAL, 6, True),
            ("Wagholi Commercial Point", "Nagar Road, Wagholi", 18.5794, 73.9812, 270.0, WasteType.PP, PriorityLevel.MEDIUM, 4, False),
            ("Yerwada Jail Chowk Bin", "Airport Road, Yerwada, Pune", 18.5552, 73.8821, 160.0, WasteType.LDPE, PriorityLevel.LOW, 1, False),
            ("Vishrantwadi Junction", "Dhanori Road, Vishrantwadi", 18.5684, 73.8732, 210.0, WasteType.PET, PriorityLevel.MEDIUM, 2, False),
            ("Kondhwa Market Point", "NIBM Road, Kondhwa, Pune", 18.4792, 73.8912, 320.0, WasteType.HDPE, PriorityLevel.HIGH, 5, True),
            ("Undri City Center", "Undri-Pisoli Road, Pune", 18.4561, 73.9015, 180.0, WasteType.PP, PriorityLevel.LOW, 2, False),
            ("Dhanori Green Yard", "Lohegaon Road, Dhanori", 18.5831, 73.8981, 240.0, WasteType.PET, PriorityLevel.MEDIUM, 3, False),
            ("Bavdhan Hub", "Chandani Chowk, Bavdhan, Pune", 18.5112, 73.7721, 290.0, WasteType.MIXED_PLASTIC, PriorityLevel.HIGH, 4, False),
            ("Pashan Lake Gate Bin", "Pashan-NDA Road, Pashan", 18.5376, 73.7925, 140.0, WasteType.LDPE, PriorityLevel.LOW, 1, False),
        ]

        now = datetime.utcnow()
        collection_points = []
        for name, addr, lat, lng, qty, wtype, prio, days_ago, overflow in points_data:
            last_collection = now - timedelta(days=days_ago)
            # Derive the priority level from the same formula the API uses at
            # read/update time, rather than the hand-picked `prio` literal above.
            # Seeding with an independently-chosen enum value is what caused the
            # seeded priority badges to disagree with the live-computed priority
            # score shown in the UI (e.g. a 94-point bin labelled "HIGH").
            calculated_priority, _score = calculate_collection_point_priority(
                estimated_waste_kg=qty,
                waste_type=wtype,
                last_collection_date=last_collection,
                overflow_status=overflow
            )
            cp = CollectionPoint(
                name=name,
                address=addr,
                latitude=lat,
                longitude=lng,
                estimated_waste_kg=qty,
                waste_type=wtype,
                priority=calculated_priority,
                last_collection_date=last_collection,
                overflow_status=overflow,
                status="ACTIVE"
            )
            collection_points.append(cp)

        db.add_all(collection_points)
        db.commit()

        print("[SEEDB] Creating Initial Waste Records...")
        waste_records = [
            WasteRecord(
                collection_point_id=cp.id,
                estimated_quantity_kg=cp.estimated_waste_kg,
                source="ESTIMATE"
            )
            for cp in collection_points
        ]
        db.add_all(waste_records)
        db.commit()

        print("[SUCCESS] Database Seeded Successfully!")
        print(f"   * Users: {db.query(User).count()}")
        print(f"   * Drivers: {db.query(Driver).count()}")
        print(f"   * Vehicles: {db.query(Vehicle).count()}")
        print(f"   * Depots: {db.query(Depot).count()}")
        print(f"   * Collection Points: {db.query(CollectionPoint).count()}")

    except Exception as e:
        db.rollback()
        print(f"[ERROR] Seed script failed: {str(e)}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
