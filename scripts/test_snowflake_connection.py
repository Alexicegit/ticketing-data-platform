import os
import snowflake.connector
from dotenv import load_dotenv


load_dotenv()


conn = snowflake.connector.connect(

    user=os.getenv("SNOWFLAKE_USER"),

    password=os.getenv("SNOWFLAKE_PASSWORD"),

    account=os.getenv("SNOWFLAKE_ACCOUNT"),

    warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),

    database="B2B_EVENT_TICKETING",

    schema="RAW"

)


cursor = conn.cursor()


cursor.execute(
    "SELECT CURRENT_DATABASE(), CURRENT_SCHEMA()"
)


print(cursor.fetchone())


cursor.close()
conn.close()