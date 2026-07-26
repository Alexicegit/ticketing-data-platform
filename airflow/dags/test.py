import os
from pathlib import Path
from dotenv import load_dotenv

ENV_PATH = Path(__file__).resolve().parents[2] / ".env"

print(f"Loading .env from: {ENV_PATH}")

load_dotenv(dotenv_path=ENV_PATH)

print(
    "POSTGRES_CONNECTION_STRING =",
    os.getenv("POSTGRES_CONNECTION_STRING")
)