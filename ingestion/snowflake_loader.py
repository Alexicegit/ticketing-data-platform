import os
from pathlib import Path

import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
from dotenv import load_dotenv
import pandas as pd



# ---------------------------------------------------------
# Load .env
# ---------------------------------------------------------

ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(ENV_PATH)


class SnowflakeLoader:

    def __init__(self):

        self.conn = snowflake.connector.connect(
            account=os.getenv("SNOWFLAKE_ACCOUNT"),
            user=os.getenv("SNOWFLAKE_USER"),
            password=os.getenv("SNOWFLAKE_PASSWORD"),
            warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
            database=os.getenv("SNOWFLAKE_DATABASE"),
            schema=os.getenv("SNOWFLAKE_SCHEMA"),
            role=os.getenv("SNOWFLAKE_ROLE")
        )

    def close(self):
        self.conn.close()

    # -------------------------------------------------

    def load_dataframe(
        self,
        dataframe,
        table_name
    ):

        success, nchunks, nrows, _ = write_pandas(
            conn=self.conn,
            df=dataframe,
            table_name=table_name,
            auto_create_table=False,
            overwrite=False
        )

        return success, nrows

    # -------------------------------------------------

    def execute(self, sql, params=None):

        cur = self.conn.cursor()

        try:

            cur.execute(sql, params)

            return cur.fetchall()

        finally:

            cur.close()

    # -------------------------------------------------

    def file_already_loaded(
        self,
        file_name,
        file_sha
    ):

        sql = """
        SELECT COUNT(*)
        FROM AUDIT.FILE_LOAD_HISTORY
        WHERE FILE_NAME=%s
          AND FILE_SHA=%s
          AND STATUS='SUCCESS'
        """

        result = self.execute(
            sql,
            (file_name, file_sha)
        )

        return result[0][0] > 0

    # -------------------------------------------------

    def insert_file_history(
        self,
        file_name,
        file_sha,
        rows_loaded,
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
            CURRENT_TIMESTAMP,
            %s,
            %s,
            %s
        )
        """

        self.execute(
            sql,
            (
                file_name,
                file_sha,
                rows_loaded,
                status,
                error_message
            )
        )

if __name__ == "__main__":

    loader = SnowflakeLoader()

    print("Connected to Snowflake successfully!")
    
    print("\nCurrent database information:")
    result = loader.execute("""
        SELECT
            CURRENT_DATABASE(),
            CURRENT_SCHEMA(),
            CURRENT_WAREHOUSE(),
            CURRENT_ROLE(),
            CURRENT_USER();
    """)

    print(result)

    loader.close()