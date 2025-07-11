import os
import requests
import subprocess
from datetime import datetime, timezone

CSV_URL = "http://data.phishtank.com/data/online-valid.csv"
CSV_FILENAME = "online-valid.csv"
COMMIT_MSG = f"Update PhishTank feed ({datetime.now(timezone.utc).isoformat()})"
GITHUB_USER = "Mike-Marks"
GITHUB_REPO = "universalphish"

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if not GITHUB_TOKEN:
    print("[!] GITHUB_TOKEN environment variable not set.")
    print("Set it using: $env:GITHUB_TOKEN='your_token_here' (PowerShell)")
    exit(1)

print("[*] Downloading PhishTank feed...")
resp = requests.get(CSV_URL)
if resp.status_code != 200:
    print(f"[!] Failed to download CSV: HTTP {resp.status_code}")
    exit(1)

with open(CSV_FILENAME, "wb") as f:
    f.write(resp.content)
print(f"[+] Feed saved as {CSV_FILENAME}")

try:
    subprocess.run(["git", "pull"], check=True)
    subprocess.run(["git", "add", CSV_FILENAME], check=True)
    subprocess.run(["git", "commit", "-m", COMMIT_MSG], check=True)
except subprocess.CalledProcessError:
    print("[!] No changes to commit or Git error occurred.")
    exit(1)

remote_url = f"https://{GITHUB_TOKEN}@github.com/{GITHUB_USER}/{GITHUB_REPO}.git"
subprocess.run(["git", "push", remote_url], check=True)

print("[+] Repo updated successfully.")

