# 🚀 ISBN/ISSN Fallback Extractor
# --------------------------------
# ✅ Pulls only ISBN / ISSN from Discovery API
# ✅ Hardcoded OCLC numbers
# ✅ Outputs minimal CSV

import requests
import csv
from tqdm import tqdm
import os

# === USER CONFIGURATION ===
WS_KEY = "YOUR_WS_KEY"
WS_SECRET = "YOUR_WS_SECRET"
OCLC_NUMBERS = [
    "976446533", "1416597355", "1090108276"  # Add more as needed
]
OUTPUT_CSV_PATH = os.path.join(os.path.expanduser("~"), "Downloads", "worldcat_identifiers_output.csv")
# ===========================

def fix_character_encoding(text):
    if isinstance(text, str):
        return text.replace("\u2013", "-").replace("\u2014", "-").replace("\n", " ").encode("latin1", errors="ignore").decode("utf-8", errors="ignore").strip()
    return text

def get_oauth_token():
    url = "https://oauth.oclc.org/token"
    auth = (WS_KEY, WS_SECRET)
    data = {"grant_type": "client_credentials", "scope": "wcapi"}
    resp = requests.post(url, auth=auth, data=data)
    resp.raise_for_status()
    return resp.json().get("access_token")

def fetch_json(oclc_number, token):
    url = f"https://americas.discovery.api.oclc.org/worldcat/search/v2/bibs/{oclc_number}"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers)
    return resp.json() if resp.status_code == 200 else None

def extract_identifiers(json_data):
    isbn_list = []
    issn_list = []

    identifier = json_data.get("identifier", {})
    if isinstance(identifier, dict):
        isbn_list += identifier.get("isbns", [])
        issn_list += identifier.get("issns", [])

        for item in identifier.get("items", []):
            if not isinstance(item, dict):
                continue
            t = item.get("type", "").lower()
            v = item.get("value", "")
            if t == "isbn":
                isbn_list.append(v)
            elif t == "issn":
                issn_list.append(v)

    return "; ".join(sorted(set(isbn_list))), "; ".join(sorted(set(issn_list)))

def extract_title(json_data):
    titles = json_data.get("title", {}).get("mainTitles", [])
    if titles and isinstance(titles[0], dict):
        return titles[0].get("text", "").split(" / ")[0].strip()
    return ""

def main():
    token = get_oauth_token()
    results = []

    for oclc in tqdm(OCLC_NUMBERS, desc="Fetching ISBN/ISSN"):
        json_data = fetch_json(oclc, token)
        if json_data:
            isbn, issn = extract_identifiers(json_data)
            title = extract_title(json_data)
            results.append({"OCLC": oclc, "Title": title, "ISBN": isbn, "ISSN": issn})

    with open(OUTPUT_CSV_PATH, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["OCLC", "Title", "ISBN", "ISSN"])
        writer.writeheader()
        writer.writerows(results)

    print(f"\n✅ Done. Output saved to: {OUTPUT_CSV_PATH}")

if __name__ == "__main__":
    main()