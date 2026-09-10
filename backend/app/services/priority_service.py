from datetime import datetime
from typing import Tuple
from app.models.enums import WasteType, PriorityLevel

# Recyclability value multiplier per plastic type
RECYCLABILITY_WEIGHTS = {
    WasteType.PET: 1.2,
    WasteType.HDPE: 1.1,
    WasteType.PP: 1.0,
    WasteType.LDPE: 0.9,
    WasteType.MIXED_PLASTIC: 0.8,
    WasteType.OTHER_RECYCLABLE_PLASTIC: 0.7,
}

# Standard max bin capacity reference (kg)
STANDARD_MAX_CAPACITY_KG = 500.0

def calculate_collection_point_priority(
    estimated_waste_kg: float,
    waste_type: WasteType,
    last_collection_date: datetime,
    overflow_status: bool
) -> Tuple[PriorityLevel, float]:
    """
    Calculates priority score (0.0 to 100.0+) and returns appropriate PriorityLevel.
    
    Formula components:
    - Waste Fill Ratio (0-40 pts): (estimated_waste_kg / MAX_CAPACITY) * 40
    - Days Since Last Collection (0-30 pts): 5 pts per day (max 30 pts)
    - Overflow Penalty (30 pts): +30 if overflow_status is True
    - Plastic Type Multiplier: (0.7x to 1.2x)
    """
    # 1. Days since collection score
    now = datetime.utcnow()
    if last_collection_date:
        days_since = (now - last_collection_date).days
    else:
        days_since = 7  # Default if never collected
    
    days_score = min(days_since * 5.0, 30.0)

    # 2. Fill level score
    fill_ratio = min(estimated_waste_kg / STANDARD_MAX_CAPACITY_KG, 1.2)
    fill_score = fill_ratio * 40.0

    # 3. Overflow penalty
    overflow_score = 30.0 if overflow_status else 0.0

    # Base raw score
    raw_score = fill_score + days_score + overflow_score

    # Apply plastic recyclability multiplier
    multiplier = RECYCLABILITY_WEIGHTS.get(waste_type, 1.0)
    final_score = round(raw_score * multiplier, 2)

    # Determine priority level threshold.
    # Buckets match the score scale surfaced in the UI (map legend / optimization
    # studio): 80+ Critical, 60-80 High, 30-60 Medium, <30 Low. An overflowing
    # bin is always treated as Critical regardless of score, matching the
    # "Mark as Bin Overflowing (Triggers CRITICAL Priority)" behaviour exposed
    # in the Create Collection Point form.
    if overflow_status or final_score >= 80.0:
        level = PriorityLevel.CRITICAL
    elif final_score >= 60.0:
        level = PriorityLevel.HIGH
    elif final_score >= 30.0:
        level = PriorityLevel.MEDIUM
    else:
        level = PriorityLevel.LOW

    return level, final_score
