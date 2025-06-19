import os
import requests
import csv
import json
import time
from dotenv import load_dotenv
from googletrans import Translator


load_dotenv()
translator = Translator()


# ✅ API credentials
WS_KEY = os.getenv("WS_KEY")
WS_SECRET = os.getenv("WS_SECRET")

# ✅ Output file path
CSV_FILE_PATH = "worldcat_bilingual_metadata.csv"

# ✅ Define bilingual column headers (matching your spreadsheet)
CSV_COLUMNS = [
    "Identifier", "Title", "Título", "Creator", "Contributor",
    "Subject (EN)", "Subject (ES)", "Type (EN)", "Tipo (ES)",
    "Description", "Descripción", "Date", "Language", "Lenguaje",
    "Format", "Formato", "Rights", "Derechos", "Publisher",
    "Cobertura", "Coverage", "Relation", "Relación", "Source"
]


# ✅ Token fetch function
def fetch_oclc_token():
    url = "https://oauth.oclc.org/token"
    auth_data = (WS_KEY, WS_SECRET)
    payload = {"grant_type": 'client_credentials', "scope": 'wcapi'}
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(url, auth=auth_data, data=payload, headers=headers)

    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        print("❌ Token Error:", response.text)
        return None

# ✅ Fetch metadata from WorldCat
import json

def fetch_worldcat_data(oclc_number, token):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    url = f"https://americas.discovery.api.oclc.org/worldcat/search/v2/bibs/{oclc_number}"

    response = requests.get(url, headers=headers)

    print(f"📡 Fetching OCLC: {oclc_number}")
    print(f"🔁 URL: {url}")
    print(f"📄 Status Code: {response.status_code}")

    if response.status_code == 200:
        json_data = response.json()
        print(json.dumps(json_data, indent=2))  # 🔍 See the full response
        return json_data
    else:
        print("❌ Error:", response.text)
        return None




# ✅ Clean and match data to bilingual column format
from googletrans import Translator
translator = Translator()

def clean_worldcat_data(data):
    def safe_translate(text):
        try:
            return translator.translate(text, src="en", dest="es").text if text else ""
        except:
            return ""

    def get_nested_text(obj, *keys):
        try:
            for key in keys:
                obj = obj[key]
            return obj
        except:
            return ""

    def get_subjects(subject_list):
        try:
            return "; ".join([s["subjectName"]["text"] for s in subject_list if "subjectName" in s])
        except:
            return ""

    def get_creator(contributors):
        try:
            creators = contributors.get("creators", [])
            names = []
            for c in creators:
                first = c.get("firstName", {}).get("text", "")
                last = c.get("secondName", {}).get("text", "")
                full = f"{first} {last}".strip()
                if full:
                    names.append(full)
            return "; ".join(names)
        except:
            return ""

    # Extract fields
    title = get_nested_text(data, "title", "mainTitles", 0, "text")
    subjects = get_subjects(data.get("subjects", []))
    creator = get_creator(data.get("contributor", {}))
    publisher = get_nested_text(data, "publishers", 0, "publisherName", "text")
    pub_date = get_nested_text(data, "date", "publicationDate")
    language = get_nested_text(data, "language", "itemLanguage")
    format_en = get_nested_text(data, "format", "generalFormat")
    description = get_nested_text(data, "description", "physicalDescription")
    oclc = get_nested_text(data, "identifier", "oclcNumber")

    return {
        "Identifier": oclc,
        "Title": title,
        "Título": safe_translate(title),
        "Creator": creator,
        "Contributor": "",  # Optional
        "Subject (EN)": subjects,
        "Subject (ES)": safe_translate(subjects),
        "Type (EN)": format_en,
        "Tipo (ES)": safe_translate(format_en),
        "Description": description,
        "Descripción": safe_translate(description),
        "Date": pub_date,
        "Language": language,
        "Lenguaje": safe_translate(language),
        "Format": format_en,
        "Formato": safe_translate(format_en),
        "Rights": "",  # Not available in your JSON
        "Derechos": "",
        "Publisher": publisher,
        "Cobertura": "",
        "Coverage": "",
        "Relation": "",
        "Relación": "",
        "Source": ""
    }








# ✅ Write to CSV
def write_to_csv(data, file_path):
    with open(file_path, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(data)
    print(f"✅ CSV written to {file_path}")

# ✅ Batch process
def batch_import(oclc_numbers, token):
    all_data = []
    for oclc in oclc_numbers:
        print(f"🔍 Fetching {oclc}...")
        raw = fetch_worldcat_data(oclc, token)
        if raw:
            cleaned = clean_worldcat_data(raw)
            all_data.append(cleaned)
        time.sleep(1)  # Prevent rate limit

    if all_data:
        write_to_csv(all_data, CSV_FILE_PATH)
    else:
        print("⚠️ No data fetched.")

# ✅ OCLC numbers to import
oclc_numbers_list = ["982300105", "1184124221", "1388663702"]

if __name__ == "__main__":
    token = fetch_oclc_token()
    if token:
        batch_import(oclc_numbers_list, token)
    else:
        print("❌ Token fetch failed.")


