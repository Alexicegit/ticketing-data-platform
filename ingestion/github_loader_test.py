"""
github_loader.py

Loads GitHub CSV files into Snowflake RAW layer.

Enterprise Features:
- SHA duplicate detection
- Audit history
- Watermark tracking
- Audit columns
- File load logging

Used By:
- Airflow
- Manual execution
"""

import logging
import os
from datetime import datetime

import snowflake.connector
from dotenv import load_dotenv
from snowflake.connector.pandas_tools import write_pandas

from github_client import GitHubClient

load_dotenv()

# =============================================================================
# LOGGING
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)

# =============================================================================
# SNOWFLAKE CONFIG
# =============================================================================

SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")
SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER")
SNOWFLAKE_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD")
SNOWFLAKE_WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE")
SNOWFLAKE_DATABASE = os.getenv("SNOWFLAKE_DATABASE")
SNOWFLAKE_SCHEMA = os.getenv("SNOWFLAKE_SCHEMA")
SNOWFLAKE_ROLE = os.getenv("SNOWFLAKE_ROLE")


class GitHubLoader:

    def __init__(self):

        self.github = GitHubClient()

        self.conn = snowflake.connector.connect(
            account=SNOWFLAKE_ACCOUNT,
            user=SNOWFLAKE_USER,
            password=SNOWFLAKE_PASSWORD,
            warehouse=SNOWFLAKE_WAREHOUSE,
            database=SNOWFLAKE_DATABASE,
            schema=SNOWFLAKE_SCHEMA,
            role=SNOWFLAKE_ROLE
        )

    # =========================================================================
    # AUDIT CHECKS
    # =========================================================================

    def already_processed(self, file_sha):
        """
        Check whether file was already successfully loaded.
        """

        sql = """
        SELECT 1
        FROM AUDIT.FILE_LOAD_HISTORY
        WHERE FILE_SHA = %s
          AND STATUS = 'SUCCESS'
        LIMIT 1
        """

        cursor = self.conn.cursor()

        try:
            cursor.execute(sql, (file_sha,))
            return cursor.fetchone() is not None

        finally:
            cursor.close()

    # =========================================================================
    # AUDIT HISTORY
    # =========================================================================

    def insert_load_history(
        self,
        file_name,
        file_sha,
        record_count,
        status,
        error_message=None
    ):

        sql = """
        INSERT INTO AUDIT.FILE_LOAD_HISTORY
        (
            FILE_NAME,
            FILE_SHA,
            LOAD_DATE,
            RECORD_COUNT,
            STATUS,
            ERROR_MESSAGE
        )
        VALUES
        (
            %s,
            %s,
            CURRENT_TIMESTAMP(),
            %s,
            %s,
            %s
        )
        """

        cursor = self.conn.cursor()

        try:
            cursor.execute(
                sql,
                (
                    file_name,
                    file_sha,
                    record_count,
                    status,
                    error_message
                )
            )

        finally:
            cursor.close()

    # =========================================================================
    # WATERMARK
    # =========================================================================

    def update_watermark(self, table_name, file_sha):

        sql = f"""
        MERGE INTO AUDIT.LOAD_WATERMARK tgt
        USING (
            SELECT
                '{table_name}' AS SOURCE_NAME,
                '{file_sha}' AS LAST_FILE_SHA
        ) src
        ON tgt.SOURCE_NAME = src.SOURCE_NAME

        WHEN MATCHED THEN
        UPDATE SET
            LAST_FILE_SHA = src.LAST_FILE_SHA,
            LOAD_DATE = CURRENT_TIMESTAMP()

        WHEN NOT MATCHED THEN
        INSERT
        (
            SOURCE_NAME,
            LAST_FILE_SHA,
            LOAD_DATE
        )
        VALUES
        (
            src.SOURCE_NAME,
            src.LAST_FILE_SHA,
            CURRENT_TIMESTAMP()
        )
        """

        cursor = self.conn.cursor()

        try:
            cursor.execute(sql)

        finally:
            cursor.close()

    # =========================================================================
    # AUDIT COLUMNS
    # =========================================================================

    def add_audit_columns(self, df, file_name, file_sha):

        df["FILE_NAME"] = file_name
        df["FILE_SHA"] = file_sha
        df["LOADED_AT"] = datetime.utcnow()

        return df

    # =========================================================================
    # LOAD DATA
    # =========================================================================

    def load_dataframe(self, df, table_name):

        success, chunks, rows, _ = write_pandas(
            conn=self.conn,
            df=df,
            table_name=table_name,
            auto_create_table=False
        )

        return rows

    # =========================================================================
    # MAIN PROCESS
    # =========================================================================

    def process_files(self):

        files = self.github.list_csv_files()

        logger.info("Found %s files", len(files))

        for file in files:

            file_name = file["name"]
            file_sha = file["sha"]

            table_name = (
                file_name
                .replace(".csv", "")
                .upper()
            )

            try:

                if self.already_processed(file_sha):

                    logger.info(
                        "Skipping %s (already processed)",
                        file_name
                    )

                    self.insert_load_history(
                        file_name=file_name,
                        file_sha=file_sha,
                        record_count=0,
                        status="SKIPPED",
                        error_message="File already processed"
                    )

                    continue

                logger.info("Loading %s", file_name)

                df = self.github.download_csv(
                    file["download_url"]
                )

                df = self.add_audit_columns(
                    df,
                    file_name,
                    file_sha
                )

                rows_loaded = self.load_dataframe(
                    df,
                    table_name
                )

                self.insert_load_history(
                    file_name=file_name,
                    file_sha=file_sha,
                    record_count=rows_loaded,
                    status="SUCCESS"
                )

                self.update_watermark(
                    table_name,
                    file_sha
                )

                logger.info(
                    "%s loaded successfully",
                    file_name
                )

            except Exception as ex:

                self.insert_load_history(
                    file_name=file_name,
                    file_sha=file_sha,
                    record_count=0,
                    status="FAILED",
                    error_message=str(ex)
                )

                logger.exception(
                    "Failed loading %s",
                    file_name
                )

                raise

    def close(self):

        if self.conn:
            self.conn.close()


if __name__ == "__main__":

    loader = GitHubLoader()

    try:
        loader.process_files()

    finally:
        loader.close()