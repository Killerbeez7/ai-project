import pandas as pd
from pathlib import Path
from typing import Dict, Any, List

from data.data_loader import load_all_parts_data

# Recommends a PC build based on a given budget and usage profile
class Recommender:
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
            "cpu": 0.23,
            "video_card": 0.40,
            "motherboard": 0.09,
            "memory": 0.10,
            "internal_hard_drive": 0.06,
            "power_supply": 0.06,
            "case": 0.06,
        },
        "design": {
            "cpu": 0.33,
            "video_card": 0.25,
            "motherboard": 0.09,
            "memory": 0.17,
            "internal_hard_drive": 0.09,
            "power_supply": 0.05,
            "case": 0.02,
        },
    }

    def __init__(self, parts_df: pd.DataFrame):
        self.parts_df = self._clean_data(parts_df)

    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        # Remove '$' and convert 'price' to a numeric type
        df["price"] = pd.to_numeric(
            df["price"].astype(str).str.replace(r"\$", "", regex=True), 
            errors="coerce"
        )
        # Drop rows where price is NaN
        df.dropna(subset=["price"], inplace=True)
        return df

    def recommend(self, budget: float, usage: str) -> Dict[str, Dict[str, Any]]:
        # Recommends a PC build based on a given budget and usage profile
        build = {}
        allocations = self.BUDGET_ALLOCATIONS.get(usage, self.BUDGET_ALLOCATIONS["gaming"])

        for part_type in self.ESSENTIAL_COMPONENTS:
            part_budget = budget * allocations.get(part_type, 0)
            
            # Filter for parts of the correct type and within budget
            # TODO: add more filters here
            possible_parts = self.parts_df[
                (self.parts_df["type"] == part_type) & 
                (self.parts_df["price"] <= part_budget)
            ]

            if possible_parts.empty:
                return {}

            # Pick the most expensive part within the budget slice
            best_part = possible_parts.loc[possible_parts["price"].idxmax()]
            build[part_type] = best_part.to_dict()

        return build

if __name__ == "__main__":
    data_path = Path("data/csv")
    all_parts = load_all_parts_data(data_path)

    if not all_parts.empty:
        recommender = Recommender(all_parts)

        test_budget = 5000.00
        test_usage = "gaming"
        recommended_build = recommender.recommend(test_budget, test_usage)

        if recommended_build:
            print(f"--- Recommended Build for Gaming on a ${test_budget} budget ---")
            total_cost = 0
            for part_type, part_info in recommended_build.items():
                price = part_info.get('price', 0)
                total_cost += price
                print(f"- {part_type.replace('_', ' ').title()}: {part_info.get('name')} (${price:.2f})")
            print(f"\nTotal Estimated Cost: ${total_cost:.2f}")
        else:
            print(f"Could not form a complete build for a ${test_budget} budget.") 