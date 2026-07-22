import os, re
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
PATTERN = re.compile(r"^DailySales_(\d{2})(\d{2})(\d{4})_([A-Za-z0-9_-]+)\.csv$", re.I)
def get_env(name, default=None, required=False):
    value = os.getenv(name, default)
    if required and not value:
        raise ValueError(f"Missing environment variable: {name}")
    return value
def parse_reseller_file_name(file_name):
    m = PATTERN.match(Path(file_name).name)
    if not m:
        raise ValueError(f"Invalid reseller file name: {file_name}")
    mm, dd, yyyy, reseller_id = m.groups()
    return {"sale_date": datetime.strptime(mm+dd+yyyy, "%m%d%Y").date(), "reseller_id": reseller_id}
