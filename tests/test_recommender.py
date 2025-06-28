import pandas as pd
import pytest
from pathlib import Path

from src.core.recommender import Recommender
from src.data.data_loader import load_all_parts_data

@pytest.fixture(scope="module")
def parts_data() -> pd.DataFrame:
    data_path = Path("data/csv")
    return load_all_parts_data(data_path)

@pytest.fixture
def recommender(parts_data: pd.DataFrame) -> Recommender:
    return Recommender(parts_data)

def test_recommendation_within_budget(recommender: Recommender):
    budget = 2000.00
    usage = "gaming"
    build = recommender.recommend(budget, usage)

    assert build, "The recommender should have returned a valid build."

    total_cost = sum(part["price"] for part in build.values())
    assert total_cost <= budget, "Total cost of the build should not exceed the budget."

def test_essential_components_are_present(recommender: Recommender):
    budget = 2000.00
    usage = "gaming"
    build = recommender.recommend(budget, usage)
    
    assert build, "The recommender should have returned a valid build."

    recommended_parts = build.keys()
    for part_type in Recommender.ESSENTIAL_COMPONENTS:
        assert part_type in recommended_parts, f"Essential component '{part_type}' is missing from the build." 