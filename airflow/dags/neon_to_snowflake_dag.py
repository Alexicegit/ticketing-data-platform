from datetime import datetime, timedelta

from airflow import DAG

from airflow.operators.python import PythonOperator

import sys


sys.path.append(
    "/path/to/ticketing-data-platform/ingestion"
)


from neon_to_snowflake_loader import main



default_args = {

    "owner": "data-engineering",

    "depends_on_past": False,

    "retries": 2,

    "retry_delay": timedelta(minutes=5)

}



with DAG(

    dag_id="neon_to_snowflake_daily",

    default_args=default_args,

    description="Load Neon data into Snowflake RAW",

    schedule="@daily",

    start_date=datetime(2026,1,1),

    catchup=False

) as dag:



    load_neon_to_raw = PythonOperator(

        task_id="load_neon_to_raw",

        python_callable=main

    )



    load_neon_to_raw