import pandas as pd
from pathlib import Path
from typing import Dict, Any, List
import itertools

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
    }

    def __init__(self, parts_df: pd.DataFrame, num_candidates: int = 5):
        self.parts_df = self._clean_data(parts_df)
        self.num_candidates = num_candidates

    # Remove '$' and convert 'price' to a numeric type
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        df["price"] = pd.to_numeric(
            df["price"].astype(str).str.replace(r"\\$|,", "", regex=True),
            errors="coerce",
        )
        df.dropna(subset=["price", "score"], inplace=True)
        return df

    def recommend(self, budget: float, usage: str) -> Dict[str, Dict[str, Any]]:
        allocations = self.BUDGET_ALLOCATIONS.get(
            usage, self.BUDGET_ALLOCATIONS["gaming"]
        )
        weights = self.SYNERGY_WEIGHTS.get(usage, self.SYNERGY_WEIGHTS["gaming"])

        candidate_parts = {}
        for part_type in self.ESSENTIAL_COMPONENTS:
            part_budget = budget * allocations.get(part_type, 0)
            
            # Base query for parts within budget
            possible_parts_df = self.parts_df[
                (self.parts_df["type"] == part_type) & 
                (self.parts_df["price"] <= part_budget)
            ]

            # Add pre-filter for CPUs to ensure they have socket data
            if part_type == "cpu":
                possible_parts_df = possible_parts_df.dropna(subset=["socket"])

            top_candidates = possible_parts_df.nlargest(self.num_candidates, "score")
            
            if not top_candidates.empty:
                candidate_parts[part_type] = top_candidates.to_dict('records')

        if len(candidate_parts) != len(self.ESSENTIAL_COMPONENTS):
            return {} # Cannot form a build if any part type has no candidates

        # Create all possible build combinations
        build_combinations = list(itertools.product(*candidate_parts.values()))

        best_build = {}
        max_score = -1

        for combo in build_combinations:
            current_build = {part["type"]: part for part in combo}
            
            total_cost = sum(part["price"] for part in current_build.values())

            if total_cost > budget:
                continue

            cpu = current_build.get("cpu", {})
            mobo = current_build.get("motherboard", {})
            if cpu.get("socket") != mobo.get("socket"):
                continue

            build_score = sum(
                part["score"] * weights.get(part_type, 1.0)
                for part_type, part in current_build.items()
            )

            if build_score > max_score:
                max_score = build_score
                best_build = current_build

        return best_build


if __name__ == "__main__":
    import sys
    from pathlib import Path

    project_root = Path(__file__).parent.parent.parent
    sys.path.append(str(project_root))

    from src.data.data_loader import load_all_parts_data

    db_path = project_root / "data" / "parts.db"
    all_parts = load_all_parts_data(db_path)

    if not all_parts.empty:
        recommender = Recommender(all_parts)

        test_budget = 5000.00
        test_usage = "gaming"
        recommended_build = recommender.recommend(test_budget, test_usage)

        if recommended_build:
            print(f"--- Recommended Build for Gaming on a ${test_budget} budget ---")
            total_cost = 0
            for part_type, part_info in recommended_build.items():
                # Print socket info for verification
                if part_type in ["cpu", "motherboard"]:
                    socket = part_info.get("socket", "N/A")
                    print(
                        f"- {part_type.replace('_', ' ').title()}: {part_info.get('name')} (Socket: {socket}) (${part_info.get('price', 0):.2f})"
                    )
                else:
                    price = part_info.get("price", 0)
                    total_cost += price
                    print(
                        f"- {part_type.replace('_', ' ').title()}: {part_info.get('name')} (${price:.2f})"
                    )

            # Recalculate total cost to include all parts in the printout
            final_cost = sum(
                part.get("price", 0) for part in recommended_build.values()
            )
            print(f"\nTotal Estimated Cost: ${final_cost:.2f}")
        else:
            print(f"Could not form a complete build for a ${test_budget} budget.")
