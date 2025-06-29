import pandas as pd
import pytest
from pathlib import Path

from src.core.recommender import Recommender
from src.data.data_loader import load_all_parts_data
from src.config import ESSENTIAL_COMPONENTS

# --- Test Fixtures ---

@pytest.fixture(scope="session")
def db_path() -> Path:
    """Returns the path to the database, assuming it's in the project root."""
    return Path(__file__).parent.parent / "data" / "parts.db"

@pytest.fixture(scope="session")
def parts_data(db_path: Path) -> pd.DataFrame:
    """Loads all parts data from the database once per test session."""
    assert db_path.exists(), "Database file not found. Please run src/data/database.py first."
    return load_all_parts_data(db_path)

@pytest.fixture
def recommender(parts_data: pd.DataFrame) -> Recommender:
    """Creates a Recommender instance for each test."""
    return Recommender(parts_data)

# --- Test Cases ---

def test_recommendation_within_budget(recommender: Recommender):
    """
    Tests if the total cost of the recommended build is within the specified budget.
    """
    budget = 2500.00
    usage = "gaming"
    build = recommender.recommend(budget, usage)[0]

    assert build, "A valid build should be returned for a reasonable budget."
    
    total_cost = sum(part["price"] for part in build.values())
    assert total_cost <= budget, f"Build cost ${total_cost} exceeded budget ${budget}."

def test_essential_components_are_present(recommender: Recommender):
    """
    Tests if all essential components are included in the recommended build.
    """
    budget = 2500.00
    usage = "gaming"
    build = recommender.recommend(budget, usage)[0]
    
    assert build, "A valid build should be returned."

    recommended_parts = build.keys()
    for part_type in ESSENTIAL_COMPONENTS:
        assert part_type in recommended_parts, f"Essential component '{part_type}' is missing."

def test_cpu_motherboard_socket_compatibility(recommender: Recommender):
    """
    Tests if the CPU and Motherboard in the recommended build have the same socket type.
    """
    budget = 2500.00
    usage = "gaming"
    build = recommender.recommend(budget, usage)[0]
    
    assert build and "cpu" in build and "motherboard" in build, "Build must contain a CPU and Motherboard."
    
    cpu_socket = build["cpu"].get("socket")
    mobo_socket = build["motherboard"].get("socket")

    assert cpu_socket is not None, "Selected CPU must have socket information."
    assert mobo_socket is not None, "Selected Motherboard must have socket information."
    assert cpu_socket == mobo_socket, "CPU and Motherboard sockets must match."

def test_synergy_weights_for_gaming(recommender: Recommender):
    """
    Tests if 'gaming' usage prioritizes 'video_card' score as per synergy weights.
    It does this by comparing the score-to-price ratio.
    """
    budget = 3000.00
    build = recommender.recommend(budget, "gaming")[0]

    assert build, "A valid gaming build should be returned."
    
    # In a gaming build, the video card should provide high performance for its cost.
    # We check if its score-to-price ratio is higher than the CPU's, as weighted.
    video_card = build.get("video_card", {})
    cpu = build.get("cpu", {})

    assert video_card and cpu, "Build must contain a CPU and Video Card."
    
    gpu_score_per_dollar = video_card["score"] / video_card["price"]
    cpu_score_per_dollar = cpu["score"] / cpu["price"]
    
    gaming_weights = recommender.synergy_weights["gaming"]
    
    # The weighted score-per-dollar for the GPU should be higher, indicating it was prioritized.
    assert (gpu_score_per_dollar * gaming_weights["video_card"]) > (cpu_score_per_dollar * gaming_weights["cpu"])

def test_graceful_failure_with_low_budget(recommender: Recommender):
    """
    Tests if the recommender returns an empty dictionary for a budget that is too low.
    """
    budget = 100.00  # An unrealistically low budget
    usage = "gaming"
    build = recommender.recommend(budget, usage)[0]

    assert build == {}, "Recommender should return an empty build for a very low budget."

def test_all_parts_have_score_and_price(parts_data: pd.DataFrame):
    """
    Tests that the final loaded DataFrame has no null values for 'price' or 'score'.
    """
    assert not parts_data["price"].isnull().any(), "All parts must have a price."
    assert not parts_data["score"].isnull().any(), "All parts must have a score." 