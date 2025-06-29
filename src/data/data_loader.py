import pandas as pd
from pathlib import Path
import sqlite3
from typing import List
import numpy as np


# Establishes a connection to the SQLite database.
def get_db_connection(db_path: Path) -> sqlite3.Connection:
    try:
        conn = sqlite3.connect(db_path, check_same_thread=False)
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        raise


# Retrieves all table names from the database.
def get_all_table_names(conn: sqlite3.Connection) -> List[str]:
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    return [table[0] for table in cursor.fetchall()]


# Loads all parts data from the SQLite database by combining all tables.
def load_all_parts_data(db_path: Path) -> pd.DataFrame:
    conn = get_db_connection(db_path)
    all_dfs = []

    try:
        table_names = get_all_table_names(conn)

        for table_name in table_names:
            try:
                # Query the table
                query = f'SELECT * FROM "{table_name}"'
                df = pd.read_sql_query(query, conn)
                # Set/overwrite the 'type' column with the table name
                df["type"] = table_name
                all_dfs.append(df)
            except Exception as e:
                print(f"Error loading table {table_name}: {e}")

    finally:
        conn.close()

    if not all_dfs:
        return pd.DataFrame()

    # Concatenate all DataFrames into one
    combined_df = pd.concat(all_dfs, ignore_index=True)
    # Replace numpy NaN with Python None for API compatibility
    combined_df.replace({np.nan: None}, inplace=True)
    return combined_df


if __name__ == "__main__":
    project_root = Path(__file__).parent.parent.parent
    db_path = project_root / "data" / "parts.db"

    parts_df = load_all_parts_data(db_path)

    if not parts_df.empty:
        print("Successfully loaded all parts data from the database.")
        print(f"Total number of parts: {len(parts_df)}")
        print(f"Columns: {parts_df.columns.tolist()}")
        print("\nPart types found:")
        print(parts_df["type"].value_counts())
        print("\nSample data:")
        print(parts_df.sample(5))
