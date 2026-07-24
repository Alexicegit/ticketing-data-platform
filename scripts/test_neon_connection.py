import os
import psycopg2
from dotenv import load_dotenv


load_dotenv()


conn = psycopg2.connect(
    os.getenv("POSTGRES_CONNECTION_STRING")
)


cursor = conn.cursor()


cursor.execute(
    """
    SELECT COUNT(*)
    FROM b2b_ticketing.ticket_sales
    """
)


print(cursor.fetchone())


cursor.close()
conn.close()