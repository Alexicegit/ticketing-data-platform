"""
github_client.py

Handles all communication with GitHub.

Responsibilities:
- List reseller CSV files
- Download CSV files
- Get file metadata (SHA, size, etc.)

Used by:
    github_loader.py
"""

import os
import requests
from pathlib import Path
from dotenv import load_dotenv

# ---------------------------------------------------------
# Load .env
# ---------------------------------------------------------

ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(ENV_PATH)

print(ENV_PATH)


#PROJECT_ROOT = Path(__file__).resolve().parent.parent
#load_dotenv(PROJECT_ROOT / ".env")


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

GITHUB_OWNER = os.getenv("GITHUB_OWNER")
GITHUB_REPO = os.getenv("GITHUB_REPO")
GITHUB_BRANCH = os.getenv("GITHUB_BRANCH", "main")
GITHUB_FOLDER = os.getenv("GITHUB_FOLDER")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

BASE_URL = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}"

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}


class GitHubClient:
    """
    GitHub API Client
    """

    def __init__(self):
        self.base_url = BASE_URL
        self.headers = HEADERS

    # -----------------------------------------------------
    # List all reseller CSV files
    # -----------------------------------------------------

    def list_csv_files(self):
        """
        Returns a list of CSV files available
        inside reseller_files folder.

        Example output:

        [
            {
                "name": "...csv",
                "download_url": "...",
                "sha": "...",
                "size": 1024
            }
        ]
        """

        url = (
            f"{self.base_url}/contents/"
            f"{GITHUB_FOLDER}?ref={GITHUB_BRANCH}"
        )

        response = requests.get(
            url,
            headers=self.headers,
            timeout=30
        )

        response.raise_for_status()

        files = response.json()

        csv_files = []

        for file in files:

            if (
                file["type"] == "file"
                and file["name"].lower().endswith(".csv")
            ):

                csv_files.append({
                    "name": file["name"],
                    "path": file["path"],
                    "download_url": file["download_url"],
                    "sha": file["sha"],
                    "size": file["size"]
                })

        return csv_files

    # -----------------------------------------------------
    # Download a CSV
    # -----------------------------------------------------

    def download_csv(self, download_url):
        """
        Downloads CSV file and returns
        file content.

        Used later by pandas.
        """

        response = requests.get(
            download_url,
            headers=self.headers,
            timeout=60
        )

        response.raise_for_status()

        return response.content

    # -----------------------------------------------------
    # Download CSV directly as DataFrame
    # -----------------------------------------------------

    def download_dataframe(self, download_url):
        """
        Downloads CSV
        Returns pandas DataFrame
        """

        import pandas as pd
        from io import StringIO

        response = requests.get(
            download_url,
            headers=self.headers,
            timeout=60
        )

        response.raise_for_status()

        return pd.read_csv(
            StringIO(response.text)
        )

    # -----------------------------------------------------
    # Check repository connection
    # -----------------------------------------------------

    def test_connection(self):
        """
        Returns True if GitHub is reachable.
        """

        url = self.base_url

        response = requests.get(
            url,
            headers=self.headers,
            timeout=30
        )

        response.raise_for_status()

        return True


# ---------------------------------------------------------
# Test
# ---------------------------------------------------------

if __name__ == "__main__":

    client = GitHubClient()

    print("Testing GitHub connection...")

    if client.test_connection():

        print("Connected successfully.\n")

    files = client.list_csv_files()

    print(f"Found {len(files)} CSV files\n")

    for file in files:

        print(file["name"])