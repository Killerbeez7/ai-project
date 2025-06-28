import pandas as pd
from pathlib import Path
from typing import List

# Combine all csv files into one dataframe
def load_all_parts_data(data_path: Path) -> pd.DataFrame:
    
    all_files: List[Path] = list(data_path.glob("*.csv"))
    all_dfs: List[pd.DataFrame] = []

    for file_path in all_files:
        try:
            # Extract the part type from the filename
            part_type: str = file_path.stem.replace("-", "_")
            
            df = pd.read_csv(file_path, on_bad_lines="skip")
            df["type"] = part_type
            all_dfs.append(df)
        except Exception as e:
            print(f"Error loading {file_path}: {e}")

    if not all_dfs:
        return pd.DataFrame()

    # Concatenate all DataFrames into one
    combined_df = pd.concat(all_dfs, ignore_index=True)
    return combined_df

if __name__ == "__main__":
    # Example usage: Loads the data and prints information about the resulting DataFrame
    csv_dir = Path("data/csv")
    
    parts_df = load_all_parts_data(csv_dir)
    
    if not parts_df.empty:
        print("Successfully loaded all parts data.")
        print(f"Total number of parts: {len(parts_df)}")
        print(f"Columns: {parts_df.columns.tolist()}")
        print("\nPart types found:")
        print(parts_df["type"].value_counts())
        print("\nSample data:")
        print(parts_df.sample(5))
