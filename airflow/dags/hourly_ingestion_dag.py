from __future__ import annotations

import subprocess
from datetime import datetime, timedelta
import logging

import duckdb
from airflow.decorators import dag, task
from airflow.providers.mysql.hooks.mysql import MySqlHook

DUCKDB_PATH = "/usr/local/airflow/include/data/warehouse/ecommerce.duckdb"
MYSQL_CONN_ID = "mysql_ecommerce"

logger = logging.getLogger(__name__)


def task_failure_alert(context):
    logger.error(
        "ALERT: Task %s in DAG %s failed.",
        context["task_instance"].task_id,
        context["dag"].dag_id,
    )


@dag(
    dag_id="mysql_to_duckdb_hourly_ingestion_dag",
    schedule="0 * * * *",
    start_date=datetime(2026, 4, 14),
    catchup=False,
    default_args={
        "owner": "airflow",
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
        "on_failure_callback": task_failure_alert,
    },
    tags=["mysql", "duckdb", "ingestion", "hourly"],
)
def mysql_to_duckdb_hourly_ingestion_dag():

    @task
    def load_table_to_duckdb(source_table: str, target_table: str) -> str:
        mysql_hook = MySqlHook(mysql_conn_id=MYSQL_CONN_ID)

        query = f"SELECT * FROM {source_table}"
        df = mysql_hook.get_pandas_df(sql=query)

        if df.empty:
            logger.warning("Source table %s is empty.", source_table)
            return f"{source_table} is empty"

        duck_con = duckdb.connect(DUCKDB_PATH)

        try:
            duck_con.register("staging_df", df)

            duck_con.execute(f"""
                CREATE OR REPLACE TABLE {target_table} AS
                SELECT *
                FROM staging_df
            """)

            row_count = duck_con.execute(
                f"SELECT COUNT(*) FROM {target_table}"
            ).fetchone()[0]

        finally:
            try:
                duck_con.unregister("staging_df")
            except Exception:
                pass
            duck_con.close()

        logger.info(
            "Loaded %s rows from MySQL table %s into DuckDB table %s.",
            row_count,
            source_table,
            target_table,
        )

        return f"Loaded {row_count} rows into {target_table}"

    load_orders = load_table_to_duckdb.override(task_id="load_orders")(
        source_table="orders",
        target_table="raw_orders",
    )

    load_order_items = load_table_to_duckdb.override(task_id="load_order_items")(
        source_table="order_items",
        target_table="raw_order_items",
    )

    load_payments = load_table_to_duckdb.override(task_id="load_payments")(
        source_table="payments",
        target_table="raw_payments",
    )

    @task
    def run_dbt_hourly_models():
        result = subprocess.run(
            ["dbt", "build", "--select", "+tag:hourly"],
            cwd="/usr/local/airflow/include/dbt/ecommerce_analytics",
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            raise Exception(f"dbt failed: {result.stderr}")

        return result.stdout
    
    dbt_task = run_dbt_hourly_models()

    load_orders >> load_order_items >> load_payments >> dbt_task


dag = mysql_to_duckdb_hourly_ingestion_dag()
