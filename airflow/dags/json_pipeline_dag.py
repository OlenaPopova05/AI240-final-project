from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime

from include.etl.json_unnesting import load_json_to_duckdb


default_args = {
    "start_date": datetime(2024, 1, 1),
}


with DAG(
    dag_id="json_reviews_pipeline",
    schedule="@hourly",
    catchup=False,
    default_args=default_args,
) as dag:

    load_json = PythonOperator(
        task_id="load_json_to_duckdb",
        python_callable=load_json_to_duckdb,
    )

    run_dbt_hourly = BashOperator(
        task_id="run_dbt_hourly",
        bash_command="""
        cd /usr/local/airflow/include/dbt/ecommerce_analytics &&
        dbt build --select tag:hourly
        """,
    )

    run_dbt_daily = BashOperator(
        task_id="run_dbt_daily",
        bash_command="""
        cd /usr/local/airflow/include/dbt/ecommerce_analytics &&
        dbt build --select tag:daily
        """,
    )

    load_json >> run_dbt_hourly >> run_dbt_daily