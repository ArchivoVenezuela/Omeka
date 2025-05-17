import csv
import requests
import json
import urllib.parse

# --- User Credentials and File Path ---
WSKEY = "1BdwlXyyHwmFWtdrAUG4IqQNJsl1r5aFQIOj1DlP6nqLzqK6OXxDbwqoAiOD7swaCMrJMTbwKdM81cO4"
WSSECRET = "xFPiujVh+HLNGiCAymAkk00SFHh5/gfq"

INPUT_CSV = "books_without_OCLC.csv"
OUTPUT_CSV = "oclc_results.csv"

# --- Get access token with correct scope ---
def fetch_oclc_token(wskey, wssecret):
    token_url = "https://oauth.oclc.org/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    payload = {
        "grant_type": "client_credentials",
        "scope": "wcapi:view_bib"
    }
    response = requests.post(token_url, auth=(wskey, wssecret), data=payload, headers=headers)

    if response.status_code == 200:
        token = response.json().get("access_token")
        print("✅ Token obtained successfully.")
        return token
    else:
        print(f"❌ Failed to obtain token (status {response.status_code})")
        print(response.text)
        return None

# --- Search WorldCat by title and author ---
def search_oclc(title, author, token):
    base_url = "https://americas.discovery.api.oclc.org/worldcat/search/v2/bibs"
    query = f'ti:{title} AND au:{author}'
    encoded_query = urllib.parse.quote(query)
    url = f"{base_url}?q={encoded_query}&limit=1"

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        try:
            data = response.json()
            if data.get("numberOfRecords", 0) > 0 and "bibRecords" in data:
                return data["bibRecords"][0]["identifier"].get("oclcNumber", "")
            else:
                return None
        except Exception as e:
            print(f"⚠️ Error parsing response for '{title}' by '{author}': {e}")
            return None
    else:
        print(f"❌ Search failed for '{title}' by '{author}' (status {response.status_code})")
        return None

# --- Process CSV and write results ---
def process_csv(input_file, output_file, token):
    results = []

    with open(input_file, newline='', encoding='utf-8-sig') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ["oclc_number"] if "oclc_number" not in reader.fieldnames else reader.fieldnames

        for row in reader:
            existing_oclc = row.get("oclc_number", "").strip()
            title = row.get("title", "").strip()
            author = row.get("author", "").strip()

            if existing_oclc:
                print(f"✅ Skipping '{title}' by '{author}' — OCLC already present.")
                row["oclc_number"] = existing_oclc
            elif title and author:
                print(f"🔎 Searching for: {title} / {author}")
                oclc_number = search_oclc(title, author, token)
                row["oclc_number"] = oclc_number or ""
            else:
                print(f"⚠️ Missing title or author: {row}")
                row["oclc_number"] = ""

            results.append(row)

    with open(output_file, "w", newline='', encoding="utf-8-sig") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    print(f"✅ Results written to {output_file}")

# --- Main ---
if __name__ == "__main__":
    token = fetch_oclc_token(WSKEY, WSSECRET)

    if token:
        process_csv(INPUT_CSV, OUTPUT_CSV, token)
    else:
        print("🚫 Cannot proceed without valid token.")
