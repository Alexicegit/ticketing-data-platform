"""
github_client.py

Handles all GitHub interactions.

Responsibilities:
- List CSV files from GitHub
- Return file metadata
- Download CSV files
"""

import os
from io import StringIO

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()


class GitHubClient:
    """GitHub API client."""

    def __init__(self):

        self.owner = os.getenv("GITHUB_OWNER")
        self.repo = os.getenv("GITHUB_REPO")
        self.branch = os.getenv("GITHUB_BRANCH", "main")
        self.folder = os.getenv("GITHUB_FOLDER")
        self.token = os.getenv("GITHUB_TOKEN")

        self.base_url = (
            f"https://api.github.com/repos/{self.owner}/{self.repo}"
        )

        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json"
        }

    def list_csv_files(self):
        """Return all CSV files from configured folder."""

        url = f"{self.base_url}/contents/{self.folder}"

        response = requests.get(
            url,
            headers=self.headers,
            params={"ref": self.branch}
        )

        response.raise_for_status()

        files = response.json()

        return [
            {
                "name": file["name"],
                "sha": file["sha"],
                "size": file["size"],
                "download_url": file["download_url"]
            }
            for file in files
            if file["name"].lower().endswith(".csv")
        ]

    def download_csv(self, download_url):
        """Download CSV and return dataframe."""

        response = requests.get(download_url)

        response.raise_for_status()

        return pd.read_csv(StringIO(response.text))