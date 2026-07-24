from datetime import datetime, timedelta
import sys
import os


PROJECT_ROOT = "/opt/airflow"

if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)


from airflow import DAG
from airflow.operators.python import PythonOperator

from ingestion.github_loader import GitHubLoader



default_args = {

    "owner": "data-engineering",

    "depends_on_past": False,

    "retries": 2,

    "retry_delay": timedelta(minutes=5)

}



def load_reseller_files():

    loader = GitHubLoader()

    loader.run()



with DAG(

    dag_id="reseller_csv_github_to_snowflake",

    default_args=default_args,

    schedule_interval="0 2 * * *",

    start_date=datetime(2026, 1, 1),

    catchup=False,

    tags=[
        "github",
        "snowflake"
    ]

) as dag:


    load_task = PythonOperator(

        task_id="load_new_reseller_files",

        python_callable=load_reseller_files

    )


    load_task