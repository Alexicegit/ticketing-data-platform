"""
reseller_csv_loader.py

Purpose:
--------
Loads reseller CSV files from GitHub repository into Snowflake RAW schema.

Workflow:
---------
1. Read configuration from .env
2. Connect to GitHub
3. Discover CSV files
4. Download new CSV files
5. Standardize columns
6. Add audit columns
7. Load to Snowflake staging table

Designed for Airflow execution.
"""

import os
import logging
from io import StringIO
from pathlib import Path
from datetime import datetime, timezone

import pandas as pd
import requests
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
from dotenv import load_dotenv


# ==========================================================
# CONFIGURATION
# ==========================================================

ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / ".env")

# ==========================================================
# LOGGING
# ==========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)

# ==========================================================
# GITHUB SETTINGS
# ==========================================================

GITHUB_OWNER = os.getenv("GITHUB_OWNER")
GITHUB_REPO = os.getenv("GITHUB_REPO")
GITHUB_BRANCH = os.getenv("GITHUB_BRANCH", "main")
GITHUB_FOLDER = os.getenv("GITHUB_FOLDER")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

GITHUB_HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

# ==========================================================
# SNOWFLAKE SETTINGS
# ==========================================================

SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")
SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER")
SNOWFLAKE_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD")
SNOWFLAKE_WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE")
SNOWFLAKE_DATABASE = os.getenv("SNOWFLAKE_DATABASE")
SNOWFLAKE_SCHEMA = os.getenv("SNOWFLAKE_SCHEMA")

TARGET_TABLE = "STG_RESELLER_TICKET_SALES"

SOURCE_SYSTEM = "GITHUB"

# ==========================================================
# COLUMN MAPPING
# ==========================================================

COLUMN_MAPPING = {
    "ticket_id": "TICKET_ID",
    "event_id": "EVENT_ID",
    "customer_id": "CUSTOMER_ID",
    "quantity": "QUANTITY",
    "sale_amount": "TOTAL_AMOUNT",
    "purchase_date": "PURCHASE_DATE",
    "reseller_id": "RESELLER_ID"
}


# ==========================================================
# GITHUB
# ==========================================================

def list_csv_files():

    url = (
        f"https://api.github.com/repos/"
        f"{GITHUB_OWNER}/{GITHUB_REPO}"
        f"/contents/{GITHUB_FOLDER}"
    )

    response = requests.get(
        url,
        headers=GITHUB_HEADERS,
        params={"ref": GITHUB_BRANCH}
    )

    response.raise_for_status()

    files = response.json()

    return [
        file
        for file in files
        if file["name"].lower().endswith(".csv")
    ]


def download_csv(download_url):

    response = requests.get(
        download_url,
        headers=GITHUB_HEADERS
    )

    response.raise_for_status()

    return pd.read_csv(StringIO(response.text))


# ==========================================================
# DATA TRANSFORMATION
# ==========================================================

def transform_dataframe(df, file_name):

    df.columns = [
        column.strip().lower()
        for column in df.columns
    ]

    df.rename(
        columns=COLUMN_MAPPING,
        inplace=True
    )

    df["LOAD_TS"] = datetime.now(timezone.utc)

    df["SOURCE_SYSTEM"] = SOURCE_SYSTEM

    df["SOURCE_FILE"] = file_name

    return df


# ==========================================================
# SNOWFLAKE
# ==========================================================

def get_connection():

    return snowflake.connector.connect(
        account=SNOWFLAKE_ACCOUNT,
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        warehouse=SNOWFLAKE_WAREHOUSE,
        database=SNOWFLAKE_DATABASE,
        schema=SNOWFLAKE_SCHEMA
    )


def load_dataframe(df):

    conn = get_connection()

    try:

        success, chunks, rows, _ = write_pandas(
            conn,
            df,
            TARGET_TABLE,
            auto_create_table=False
        )

        logger.info(
            "Loaded %s rows into %s",
            rows,
            TARGET_TABLE
        )

        return success

    finally:
        conn.close()


# ==========================================================
# MAIN
# ==========================================================

def main():

    logger.info("Starting GitHub -> Snowflake load")

    csv_files = list_csv_files()

    logger.info(
        "Found %s CSV files",
        len(csv_files)
    )

    for file in csv_files:

        logger.info(
            "Processing %s",
            file["name"]
        )

        df = download_csv(
            file["download_url"]
        )

        df = transform_dataframe(
            df,
            file["name"]
        )

        load_dataframe(df)

    logger.info(
        "GitHub ingestion completed successfully"
    )


if __name__ == "__main__":
    main()