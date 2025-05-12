import os
import requests
import pandas as pd
from urllib.parse import urljoin

# 🔧 Configuration
OMEKA_BASE_URL = "https://archivovenezuela.com/en/"
OMEKA_API_URL = urljoin(OMEKA_BASE_URL, "api/items")
OMEKA_COLLECTIONS_URL = urljoin(OMEKA_BASE_URL, "api/collections")
API_KEY = "YOUR_API_KEY_HERE"
CSV_FILE = "PATH_TO_YOUR_CSV_FILE"
UPLOAD_LIMIT = 5

# 🏷️ Dublin Core Elements
DC_ELEMENTS = {
    "Title": 50,
    "Creator": 39,
    "Contributor": 37,
    "Subject": 49,
    "Type": 51,
    "Description": 41,
    "Date": 40,
    "Language": 44,
    "Publisher": 45,
    "Relation": 46,
    "Source": 48,
    "Format": 42,
    "Identifier": 43,
    "Rights": 47,
    "Notes": 38
}

def log_message(message, level="INFO"):
    icons = {
        "INFO": "INFO:",
        "SUCCESS": "✅",
        "ERROR": "❌",
        "WARNING": "⚠️"
    }
    print(f"{icons.get(level, 'INFO:')} {message}")

def parse_tags(tags_string):
    if not tags_string or not isinstance(tags_string, str):
        return []
    for sep in [',', ';', '|']:
        if sep in tags_string:
            return [tag.strip() for tag in tags_string.split(sep) if tag.strip()]
    return [tag.strip() for tag in tags_string.split() if tag.strip()]

def read_csv(csv_file):
    try:
        df = pd.read_csv(csv_file, encoding='utf-8').fillna('')
        df.columns = [str(col).strip() for col in df.columns]
        return df.to_dict(orient="records")
    except Exception as e:
        log_message(f"Error reading CSV: {str(e)}", "ERROR")
        return []

def format_metadata(row):
    metadata = {"element_texts": []}
    for field, value in row.items():
        if pd.isna(value) or str(value).strip().lower() in ("", "nan", "none"):
            continue
        value = str(value).strip()
        if field == "Date" and value.endswith(".0"):
            value = value[:-2]
        if field in ["Collection", "Tags", "File", "Local File", "Geolocation"]:
            continue
        if field in DC_ELEMENTS:
            metadata["element_texts"].append({
                "element": {"id": DC_ELEMENTS[field]},
                "text": value,
                "html": True
            })
    return metadata

def get_collection_id(name):
    if not name:
        return None
    try:
        r = requests.get(OMEKA_COLLECTIONS_URL, params={"key": API_KEY})
        for col in r.json():
            for text in col.get("element_texts", []):
                if text.get("element", {}).get("name") == "Title" and text.get("text", "").strip().lower() == name.strip().lower():
                    return col.get("id")
        return create_collection(name)
    except Exception as e:
        log_message(f"Collection fetch failed: {str(e)}", "ERROR")
        return None

def create_collection(name):
    data = {
        "element_texts": [
            {
                "element": {"id": DC_ELEMENTS["Title"]},
                "text": name,
                "html": True
            }
        ],
        "public": True
    }
    try:
        r = requests.post(OMEKA_COLLECTIONS_URL, json=data, params={"key": API_KEY})
        if r.status_code == 201:
            log_message(f"✅ Collection created: {name}")
            return r.json().get("id")
        else:
            log_message(f"Failed to create collection: {r.status_code} {r.text}", "ERROR")
    except Exception as e:
        log_message(f"Error creating collection: {str(e)}", "ERROR")
    return None

def create_item(metadata, collection_id=None, tags=None):
    item = {
        "element_texts": metadata["element_texts"],
        "public": True
    }
    if collection_id:
        item["collection"] = {"id": collection_id}
    if tags:
        item["tags"] = tags
    try:
        r = requests.post(OMEKA_API_URL, json=item, params={"key": API_KEY})
        if r.status_code == 201:
            log_message("✅ Item created", "SUCCESS")
            return r.json().get("id")
        else:
            log_message(f"❌ Failed to create item: {r.status_code} {r.text}", "ERROR")
    except Exception as e:
        log_message(f"Request failed: {str(e)}", "ERROR")
    return None

def upload_items():
    log_message("🚀 Starting batch upload process")
    data = read_csv(CSV_FILE)
    if UPLOAD_LIMIT:
        data = data[:UPLOAD_LIMIT]
        log_message(f"Uploading first {UPLOAD_LIMIT} items")
    success = 0
    for index, row in enumerate(data):
        log_message(f"📄 Processing item {index+1}/{len(data)}")
        metadata = format_metadata(row)
        if not metadata["element_texts"]:
            log_message("⚠️ No valid metadata found. Skipping.")
            continue
        collection_id = None
        for field in ['Collection']:
            if field in row and row[field]:
                collection_id = get_collection_id(row[field])
                break
        tags = []
        for tag_field in ['Tags']:
            if tag_field in row and row[tag_field]:
                tags = parse_tags(row[tag_field])
                break
        item_id = create_item(metadata, collection_id, tags)
        if item_id:
            success += 1
    log_message(f"✅ Upload complete: {success} of {len(data)} items")

if __name__ == "__main__":
    upload_items()
