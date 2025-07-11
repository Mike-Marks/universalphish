import csv
import os
import requests
import subprocess
from datetime import datetime, timezone

CSV_URL = "http://data.phishtank.com/data/online-valid.csv"
RAW_FILENAME = "online-valid.csv"
CLEANED_FILENAME = "cleaned-feed.csv"
COMMIT_MSG = f"Update cleaned PhishTank feed ({datetime.now(timezone.utc).isoformat()})"
GITHUB_USER = "Mike-Marks"
GITHUB_REPO = "universalphish"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if not GITHUB_TOKEN:
    print("[!] GITHUB_TOKEN environment variable not set.")
    exit(1)

print("[*] Downloading PhishTank feed...")
response = requests.get(CSV_URL)
if response.status_code != 200:
    print(f"[!] Failed to download CSV: HTTP {response.status_code}")
    exit(1)

with open(RAW_FILENAME, "wb") as f:
    f.write(response.content)
print(f"[+] Raw feed saved as {RAW_FILENAME}")

print("[*] Cleaning feed...")
with open(RAW_FILENAME, newline='', encoding='utf-8') as raw_csv, \
     open(CLEANED_FILENAME, 'w', newline='', encoding='utf-8') as clean_csv:
    
    reader = csv.DictReader(raw_csv)
    writer = csv.writer(clean_csv)
    writer.writerow(["url"])  # write header

    for row in reader:
        writer.writerow([row["url"]])

print(f"[+] Cleaned feed saved as {CLEANED_FILENAME}")

try:
    subprocess.run(["git", "pull"], check=True)
    subprocess.run(["git", "add", CLEANED_FILENAME], check=True)
    commit = subprocess.run(["git", "commit", "-m", COMMIT_MSG], check=False)
    if commit.returncode != 0:
        print("[~] No new changes to commit.")
        exit(0)
except subprocess.CalledProcessError as e:
    print(f"[!] Git error: {e}")
    exit(1)

remote_url = f"https://{GITHUB_TOKEN}@github.com/{GITHUB_USER}/{GITHUB_REPO}.git"
subprocess.run(["git", "push", remote_url], check=True)
print("[+] Cleaned feed committed and pushed successfully.")
