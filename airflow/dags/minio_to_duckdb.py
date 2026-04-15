from __future__ import annotations
 
import io
import os
from datetime import datetime, timedelta
 
import boto3
import duckdb
import pandas as pd
from airflow.decorators import dag, task
from botocore.client import Config
 
MINIO_ENDPOINT  = "http://host.docker.internal:9000"  
MINIO_ACCESS    = "admin"
MINIO_SECRET    = "MySQL_123"
BUCKET_NAME     = "ecommerce"
OBJECT_NAME     = "raw/shipments.csv"
 
DUCKDB_PATH     = "/usr/local/airflow/include/warehouse/ecommerce.duckdb"
RAW_TABLE       = "raw_shipments"
 
DBT_PROJECT_DIR = "/usr/local/airflow/include/dbt/ecommerce_analytics"
 
 
@dag(
    dag_id="minio_to_duckdb",
    description="Load shipments CSV from MinIO into DuckDB, then run dbt",
    start_date=datetime(2025, 1, 1),
    schedule="@daily",
    catchup=False,
    default_args={
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
    },
    tags=["etl", "minio", "daily"],
)
def minio_to_duckdb_dag():
 
    @task()
    def extract_from_minio() -> str:
        s3 = boto3.client(
            "s3",
            endpoint_url=MINIO_ENDPOINT,
            aws_access_key_id=MINIO_ACCESS,
            aws_secret_access_key=MINIO_SECRET,
            config=Config(signature_version="s3v4"),
            region_name="us-east-1",
        )
 
        response = s3.get_object(Bucket=BUCKET_NAME, Key=OBJECT_NAME)
        csv_content = response["Body"].read().decode("utf-8")
        return csv_content
 
    @task()
    def transform_with_pandas(csv_content: str) -> str:
        df = pd.read_csv(io.StringIO(csv_content))

        # Стандартизація назв колонок (snake_case, lowercase)
        df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

        # Парсинг дат
        df["shipment_date"] = pd.to_datetime(df["shipment_date"], errors="coerce")
        df["delivery_date"]  = pd.to_datetime(df["delivery_date"],  errors="coerce")
 
        # Числові типи
        df["shipping_cost"] = pd.to_numeric(df["shipping_cost"], errors="coerce")
 
        # Службове поле — коли завантажили
        df["_loaded_at"] = datetime.utcnow().isoformat()
 
        return df.to_json(orient="records", date_format="iso")
 
    @task()
    def load_to_duckdb(json_data: str) -> None:
    
        df = pd.read_json(json_data, orient="records")
 
        os.makedirs(os.path.dirname(DUCKDB_PATH), exist_ok=True)
 
        con = duckdb.connect(DUCKDB_PATH)
 
        # Створюємо схему raw якщо не існує
        con.execute("CREATE SCHEMA IF NOT EXISTS raw")
 
        # Перезаписуємо таблицю (idempotent)
        con.execute(f"DROP TABLE IF EXISTS raw.{RAW_TABLE}")
        con.execute(f"CREATE TABLE raw.{RAW_TABLE} AS SELECT * FROM df")
 
        row_count = con.execute(f"SELECT COUNT(*) FROM raw.{RAW_TABLE}").fetchone()[0]
 
        con.close()
 
    @task.bash()
    def run_dbt_daily() -> str:
        return f"cd {DBT_PROJECT_DIR} && dbt build --select tag:daily"
 
    @task.bash()
    def run_dbt_hourly() -> str:
        return f"cd {DBT_PROJECT_DIR} && dbt build --select tag:hourly"
 
    raw_csv      = extract_from_minio()
    transformed  = transform_with_pandas(raw_csv)
    loaded       = load_to_duckdb(transformed)
 
    # dbt запускається після завантаження в DuckDB
    loaded >> run_dbt_daily() >> run_dbt_hourly()
 
 
minio_to_duckdb_dag()