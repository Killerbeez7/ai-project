import sqlite3
import pandas as pd
from pathlib import Path
import logging
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


# Establishes a connection to the SQLite database
def get_db_connection(db_path: Path) -> sqlite3.Connection:
    try:
        conn = sqlite3.connect(db_path, check_same_thread=False)
        logging.info(f"Successfully connected to database at {db_path}")
        return conn
    except sqlite3.Error as e:
        logging.error(f"Error connecting to database: {e}")
        raise


# Makes an educated guess for a CPU's socket based on its name (fixing missing data issue)
def get_socket_from_name(name: str) -> str | None:

    if not isinstance(name, str):
        return None

    name_lower = name.lower()

    # Intel Sockets - Check for generation
    if re.search(r"i\d-(1[2-4])\d{3}", name_lower):
        return "LGA1700"
    if re.search(r"i\d-1[0-1]\d{3}", name_lower):
        return "LGA1200"
    if re.search(r"i\d-[7-9]\d{3}", name_lower):
        return "LGA1151"

    # AMD Sockets
    if "ryzen" in name_lower and "threadripper" not in name_lower:
        if re.search(r"\s[7-9]\d{3}x?3?d?", name_lower):
            return "AM5"
        if re.search(r"\s[1-5]\d{3}g?x?3?d?", name_lower):
            return "AM4"
    if "threadripper" in name_lower:
        return "sTRX4"

    return None


# Reads a CSV, enriches it with socket/score data, and creates a table.
def create_table_from_csv(
    conn: sqlite3.Connection,
    csv_path: Path,
    scores_cpu_df: pd.DataFrame,
    scores_gpu_df: pd.DataFrame,
):
    table_name = csv_path.stem.replace("-", "_")
    try:
        df = pd.read_csv(csv_path)

        df.columns = (
            df.columns.str.strip()
            .str.lower()
            .str.replace(" ", "_")
            .str.replace(r"[^a-zA-Z0-9_]", "", regex=True)
        )

        if "price" not in df.columns:
            logging.warning(f"'price' column not found in {csv_path.name}. Skipping.")
            return

        if table_name == "cpu":
            df["socket"] = df["name"].apply(get_socket_from_name)
            merged_df = pd.merge(
                df, scores_cpu_df, left_on="name", right_on="cpu_name", how="left"
            )
            df["score"] = merged_df["rating"]
        elif table_name == "video_card":
            merged_df = pd.merge(
                df, scores_gpu_df, left_on="name", right_on="videocard", how="left"
            )
            df["score"] = merged_df["3d_rating"]

        # For all other parts, or if a score wasn't found, fallback to price
        if "score" not in df.columns:
            df["score"] = df["price"]
        else:
            df["score"].fillna(df["price"], inplace=True)

        # Clean up columns before writing to DB
        df = df[
            [
                col
                for col in df.columns
                if col not in ["cpu_name", "videocard", "3d_rating", "rating"]
            ]
        ]

        df.to_sql(table_name, conn, if_exists="replace", index=False)
        logging.info(f"Successfully created/enriched table '{table_name}'")

    except Exception as e:
        logging.error(f"An error occurred for {csv_path.name}: {e}")


# Populates the database with tables from all CSV files in a directory.
def populate_database_from_csv_directory(
    conn: sqlite3.Connection, csv_dir: Path, scores_dir: Path
):
    try:
        cpu_scores_df = pd.read_csv(scores_dir / "CPUModelSummary.csv")
        gpu_scores_df = pd.read_csv(scores_dir / "VideocardModelSummary.csv")
        # Standardize column names for easier merging
        cpu_scores_df.columns = ["cpu_name", "rating"] + cpu_scores_df.columns[
            2:
        ].tolist()
        gpu_scores_df.columns = ["videocard", "3d_rating"] + gpu_scores_df.columns[
            2:
        ].tolist()
    except FileNotFoundError as e:
        logging.error(f"Score file not found: {e}")
        return

    for csv_file in csv_dir.glob("*.csv"):
        create_table_from_csv(conn, csv_file, cpu_scores_df, gpu_scores_df)


def main():
    """Main function to create and populate the database."""
    project_root = Path(__file__).parent.parent.parent
    db_path = project_root / "data" / "parts.db"
    csv_dir = project_root / "data" / "csv"
    scores_dir = project_root / "data"

    # Ensure the parent directory for the database exists
    db_path.parent.mkdir(exist_ok=True)

    # Delete old DB if it exists
    if db_path.exists():
        db_path.unlink()
        logging.info("Removed old database file.")

    conn = None
    try:
        conn = get_db_connection(db_path)
        populate_database_from_csv_directory(conn, csv_dir, scores_dir)
        logging.info("Database population process completed.")
    finally:
        if conn:
            conn.close()
            logging.info("Database connection closed.")


if __name__ == "__main__":
    main()
