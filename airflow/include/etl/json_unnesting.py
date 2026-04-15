import pandas as pd
import json
import duckdb
import os


def load_json_to_duckdb():
    json_path = "/usr/local/airflow/include/data/raw/json/reviews.json"
    db_path = "/usr/local/airflow/include/warehouse/ecommerce.duckdb"

    with open(json_path) as f:
        data = json.load(f)

    df = pd.json_normalize(data)

    df.columns = df.columns.str.replace("metadata.", "")
    df = df.drop(columns=["verified_purchase"])

    df["review_created_at"] = pd.to_datetime(df["review_created_at"])

    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    con = duckdb.connect(db_path)

    con.execute("""
        CREATE OR REPLACE TABLE raw_reviews AS
        SELECT * FROM df
    """)

    con.close()

if __name__ == "__main__":
    load_json_to_duckdb()
    