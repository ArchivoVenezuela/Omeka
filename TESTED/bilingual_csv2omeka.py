# -*- coding: utf-8 -*-
import os
import requests
import pandas as pd
import json
import time
from urllib.parse import urljoin

# 🔹 CONFIGURATION 🔹
OMEKA_BASE_URL = "https://archivovenezuela.com/test/" 
OMEKA_API_URL = urljoin(OMEKA_BASE_URL, "api/items")
OMEKA_COLLECTIONS_URL = urljoin(OMEKA_BASE_URL, "api/collections")
API_KEY = "............" #Insert your API Key
CSV_FILE = r"C:\Users\.....\.......\Bilingual_metadata_template.csv" #Insert path to your CSV spreadsheet
UPLOAD_LIMIT = 5  # Limit the number of items to upload (set to None for all rows)
RETRY_ATTEMPTS = 3
RETRY_DELAY = 2

# Element IDs for Dublin Core elements
DC_ELEMENTS = {
    "Identifier": 43,
    "Title": 50,
    "Creator": 39,
    "Contributor": 37,
    "Subject": 49,
    "Type": 51,
    "Description": 41,
    "Date": 40,
    "Language": 44,
    "Format": 42,
    "Rights": 47,
    "Publisher": 45,
    "Relation": 46,
    "Source": 48
}

# Logging function
def log_message(message, level="INFO"):
    icons = {
        "INFO": "INFO:",
        "SUCCESS": "✅",
        "ERROR": "❌",
        "WARNING": "⚠️"
    }
    print(f"{icons.get(level, 'INFO:')} {message}")

# Format row metadata for Omeka API
def format_metadata(row, language="EN"):
    metadata = {"element_texts": []}
    for field, value in row.items():
        if not value or str(value).lower() in ("nan", "none"):
            continue
        
        # Map fields dynamically based on language
        if language == "EN":
            if field in ["Title", "Subject (EN)", "Type (EN)", "Description (EN)", "Tags (EN)"]:
                element = DC_ELEMENTS.get(field.replace(" (EN)", ""))
            else:
                element = DC_ELEMENTS.get(field)
        elif language == "ES":
            if field in ["Título", "Subject (ES)", "Tipo (ES)", "Description (ES)", "Tags (ES)"]:
                element = DC_ELEMENTS.get(field.replace(" (ES)", ""))
            else:
                element = DC_ELEMENTS.get(field)
        else:
            element = DC_ELEMENTS.get(field)

        if element:
            metadata["element_texts"].append({
                "element": {"id": element},
                "text": str(value).strip(),
                "html": True
            })
    return metadata

# Create an item in Omeka
def create_item(metadata):
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    params = {"key": API_KEY}
    item_data = {
        "element_texts": metadata["element_texts"],
        "public": True
    }
    for attempt in range(RETRY_ATTEMPTS):
        try:
            response = requests.post(OMEKA_API_URL, headers=headers, params=params, json=item_data)
            if response.status_code == 201:
                return response.json().get("id")
            else:
                log_message(f"Error creating item ({response.status_code}): {response.text}", "ERROR")
                if attempt < RETRY_ATTEMPTS - 1:
                    time.sleep(RETRY_DELAY)
        except Exception as e:
            log_message(f"Exception on item creation: {e}", "ERROR")
            time.sleep(RETRY_DELAY)
    return None

# Read CSV file
def read_csv(path):
    try:
        df = pd.read_csv(path, encoding='utf-8').fillna('')
        df.columns = [col.strip() for col in df.columns]
        return df.to_dict(orient="records")
    except Exception as e:
        log_message(f"CSV read error: {e}", "ERROR")
        return []

# Main upload function
def upload_items(language="EN"):
    log_message(f"🚀 Starting batch upload process for {language} site")
    data = read_csv(CSV_FILE)
    if not data:
        log_message("CSV is empty or unreadable.", "ERROR")
        return
    if UPLOAD_LIMIT:
        data = data[:UPLOAD_LIMIT]
        log_message(f"Uploading first {UPLOAD_LIMIT} items")

    successful_uploads = 0
    for index, row in enumerate(data):
        log_message(f"📄 Processing item {index+1}/{len(data)}")
        metadata = format_metadata(row, language)
        if not metadata["element_texts"]:
            log_message("⚠️ No valid metadata found. Skipping.", "WARNING")
            continue

        item_id = create_item(metadata)
        if item_id:
            successful_uploads += 1

    log_message(f"✅ ✅ Upload complete: {successful_uploads} of {len(data)} items for {language} site")

if __name__ == "__main__":
    # Upload for both English and Spanish fields
    upload_items(language="EN")
    upload_items(language="ES")