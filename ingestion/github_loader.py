"""
github_loader.py

Loads new reseller CSV files from GitHub into
Snowflake RAW schema.

This script is intended to be executed daily by Airflow.
"""


import logging
import re
import pandas as pd

from datetime import datetime, timezone
from github_client import GitHubClient
from snowflake_loader import SnowflakeLoader


# ==========================================================
# Logging Configuration
# ==========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


# ==========================================================
# CSV Column -> Snowflake Column Mapping
# ==========================================================

COLUMN_MAPPING = {

    "Transaction ID": "TRANSACTION_ID",

    "Event name": "EVENT_NAME",

    "Number of purchased tickets":
        "NUMBER_OF_PURCHASED_TICKETS",

    "Total amount":
        "TOTAL_AMOUNT",

    "Sales channel":
        "SALES_CHANNEL",

    "Customer first name":
        "CUSTOMER_FIRST_NAME",

    "Customer last name":
        "CUSTOMER_LAST_NAME",

    "Office location":
        "OFFICE_LOCATION",

    "Created Date":
        "CREATED_DATE"
}


# ==========================================================
# Target Snowflake Columns
# ==========================================================

TARGET_COLUMNS = [

    "TRANSACTION_ID",

    "RESELLER_ID",

    "EVENT_NAME",

    "NUMBER_OF_PURCHASED_TICKETS",

    "TOTAL_AMOUNT",

    "SALES_CHANNEL",

    "CUSTOMER_FIRST_NAME",

    "CUSTOMER_LAST_NAME",

    "OFFICE_LOCATION",

    "CREATED_DATE",

    "SOURCE_FILE_NAME",

    "LOAD_TS",

    "SOURCE_SYSTEM"
]


SOURCE_SYSTEM = "GITHUB"



class GitHubLoader:


    def __init__(self):

        self.github = GitHubClient()

        self.snowflake = SnowflakeLoader()



    # ======================================================
    # Extract reseller id from filename
    # Format:
    # DailySales_MMDDYYYY_RESXXX.csv
    #
    # Example:
    # DailySales_01052020_RES005.csv
    # ======================================================

    def extract_reseller_id(self, file_name):

        pattern = (
            r"DailySales_(\d{8})_(RES\d+)\.csv"
        )


        match = re.match(
            pattern,
            file_name,
            re.IGNORECASE
        )


        if not match:

            raise ValueError(
                f"Invalid filename format: {file_name}"
            )


        sale_date = match.group(1)

        reseller_id = match.group(2)


        logger.info(
            f"Sale date from filename: {sale_date}"
        )


        logger.info(
            f"Reseller ID from filename: {reseller_id}"
        )


        return reseller_id



    # ======================================================
    # Process Individual CSV
    # ======================================================

    def process_file(self, file_info):


        file_name = file_info["name"]

        file_sha = file_info["sha"]


        logger.info(
            f"Processing {file_name}"
        )



        # --------------------------------------------------
        # Duplicate check
        # --------------------------------------------------

        if self.snowflake.file_already_loaded(

            file_name,

            file_sha

        ):


            logger.info(
                f"Skipping {file_name} (already loaded)"
            )

            return



        # --------------------------------------------------
        # Extract reseller ID
        # --------------------------------------------------

        reseller_id = self.extract_reseller_id(
            file_name
        )



        # --------------------------------------------------
        # Download CSV
        # --------------------------------------------------

        logger.info(
            "Downloading CSV from GitHub..."
        )


        df = self.github.download_csv(

            file_info["download_url"]

        )


        logger.info(
            f"{len(df)} records downloaded"
        )


        logger.info(
            f"Source columns: {list(df.columns)}"
        )



        # --------------------------------------------------
        # Rename CSV columns
        # --------------------------------------------------

        df.rename(

            columns=COLUMN_MAPPING,

            inplace=True

        )


        logger.info(
            f"Mapped columns: {list(df.columns)}"
        )



        # --------------------------------------------------
        # Add metadata columns
        # --------------------------------------------------

        df["RESELLER_ID"] = reseller_id


        df["SOURCE_FILE_NAME"] = file_name


        df["LOAD_TS"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


        df["SOURCE_SYSTEM"] = SOURCE_SYSTEM



        # --------------------------------------------------
        # Add missing target columns
        # --------------------------------------------------

        for column in TARGET_COLUMNS:


            if column not in df.columns:


                logger.warning(

                    f"Column {column} missing. "
                    "Adding NULL values."

                )


                df[column] = None



        # --------------------------------------------------
        # Arrange columns
        # --------------------------------------------------

        df = df[TARGET_COLUMNS]



        logger.info(

            f"Final dataframe columns: {list(df.columns)}"

        )


        logger.info(

            f"LOAD_TS datatype: {df['LOAD_TS'].dtype}"

        )



        # --------------------------------------------------
        # Load into Snowflake
        # --------------------------------------------------

        logger.info(
            "Loading data into Snowflake..."
        )


        success, rows = self.snowflake.load_dataframe(

            dataframe=df,

            table_name="RESELLER_DAILY_SALES"

        )



        if success:


            logger.info(

                f"{rows} rows loaded successfully"

            )


            self.snowflake.insert_file_history(

                file_name=file_name,

                file_sha=file_sha,

                rows_loaded=rows,

                status="SUCCESS"

            )


        else:


            raise Exception(

                "write_pandas returned False"

            )



    # ======================================================
    # Run Loader
    # ======================================================

    def run(self):


        start = datetime.now()


        logger.info(
            "--------------------------------------------"
        )

        logger.info(
            "Starting GitHub CSV ingestion"
        )

        logger.info(
            "--------------------------------------------"
        )



        files = self.github.list_csv_files()



        logger.info(

            f"{len(files)} CSV files found"

        )



        success = 0

        failed = 0



        for file in files:


            try:


                self.process_file(file)


                success += 1



            except Exception as ex:


                logger.exception(

                    f"Error processing {file['name']}: {ex}"

                )


                failed += 1



                try:


                    self.snowflake.insert_file_history(

                        file_name=file["name"],

                        file_sha=file["sha"],

                        rows_loaded=0,

                        status="FAILED",

                        error_message=str(ex)

                    )


                except Exception:


                    logger.exception(

                        "Unable to insert audit record"

                    )



        end = datetime.now()



        logger.info(
            "--------------------------------------------"
        )

        logger.info(
            f"Started : {start}"
        )

        logger.info(
            f"Finished: {end}"
        )

        logger.info(
            f"Successful Files : {success}"
        )

        logger.info(
            f"Failed Files     : {failed}"
        )

        logger.info(
            "--------------------------------------------"
        )



        self.snowflake.close()



# ==========================================================

if __name__ == "__main__":


    loader = GitHubLoader()

    loader.run()