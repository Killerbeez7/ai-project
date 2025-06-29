from typing import Dict, List

ESSENTIAL_COMPONENTS: List[str] = [
    "cpu",
    "motherboard",
    "memory",
    "internal_hard_drive",
    "video_card",
    "case",
    "power_supply",
]

BUDGET_ALLOCATIONS: Dict[str, Dict[str, float]] = {
    "gaming": {
        "cpu": 0.20,
        "video_card": 0.40,
        "motherboard": 0.10,
        "memory": 0.10,
        "internal_hard_drive": 0.08,
        "power_supply": 0.07,
        "case": 0.05,
    },
    "design": {
        "cpu": 0.30,
        "video_card": 0.25,
        "motherboard": 0.10,
        "memory": 0.15,
        "internal_hard_drive": 0.10,
        "power_supply": 0.05,
        "case": 0.05,
    },
    "video_editing": {
        "cpu": 0.35,
        "video_card": 0.25,
        "motherboard": 0.05,
        "memory": 0.20,
        "internal_hard_drive": 0.10,
        "power_supply": 0.03,
        "case": 0.02,
    },
    "office_work": {
        "cpu": 0.25,
        "video_card": 0.10,
        "motherboard": 0.15,
        "memory": 0.15,
        "internal_hard_drive": 0.20,
        "power_supply": 0.05,
        "case": 0.10,
    },
}

SYNERGY_WEIGHTS: Dict[str, Dict[str, float]] = {
    "gaming": {
        "cpu": 0.8, 
        "video_card": 1.2, 
        "memory": 1.0, 
        "internal_hard_drive": 1.0,
        "motherboard": 1.0,
        "power_supply": 1.0,
        "case": 1.0,
    },
    "design": {
        "cpu": 1.2, 
        "video_card": 0.8, 
        "memory": 1.1, 
        "internal_hard_drive": 1.0,
        "motherboard": 1.0,
        "power_supply": 1.0,
        "case": 1.0,
    },
    "video_editing": {
        "cpu": 1.2,
        "video_card": 1.0,
        "memory": 1.1,
        "internal_hard_drive": 1.0,
        "motherboard": 1.0,
        "power_supply": 1.0,
        "case": 1.0,
    },
    "office_work": {
        "cpu": 1.1,
        "video_card": 0.7,
        "memory": 1.0,
        "internal_hard_drive": 1.2,
        "motherboard": 1.0,
        "power_supply": 1.0,
        "case": 1.0,
    },
}

MINIMUM_SPEND: Dict[str, float] = {
    "cpu": 100.00,
    "motherboard": 85.00,
    "memory": 40.00,
    "internal_hard_drive": 40.00,
    "video_card": 150.00,
    "power_supply": 50.00,
    "case": 45.00,
} 