import os
import subprocess
from pathlib import Path
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]


# Load .env
load_dotenv(PROJECT_ROOT / ".env")


print(
    "Snowflake account:",
    os.getenv("SNOWFLAKE_ACCOUNT")
)


subprocess.run(
    [
        "dbt",
        "debug",
        "--profiles-dir",
        str(PROJECT_ROOT / "config")
    ],
    cwd=PROJECT_ROOT / "dbt"
)