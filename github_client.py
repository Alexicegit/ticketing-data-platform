import requests
import os

OWNER = os.getenv("GITHUB_OWNER")
REPO = os.getenv("GITHUB_REPO")
TOKEN = os.getenv("GITHUB_TOKEN")
FOLDER = os.getenv("GITHUB_FOLDER")

headers = {
    "Authorization": f"Bearer {TOKEN}"
}

url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{FOLDER}"

response = requests.get(url, headers=headers)

files = response.json()