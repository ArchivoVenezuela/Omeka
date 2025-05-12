# -*- coding: utf-8 -*-
import os
import requests
import pandas as pd
import json
import time
from urllib.parse import urljoin

# 🔹 CONFIGURACIÓN 🔹
DEBUG = True
OMEKA_BASE_URL = "https://archivovenezuela.com/"
OMEKA_API_URL = urljoin(OMEKA_BASE_URL, "api/items")
OMEKA_COLLECTIONS_URL = urljoin(OMEKA_BASE_URL, "api/collections")
API_KEY = "YOUR_API_KEY_HERE"
CSV_FILE = "PATH_TO_YOUR_CSV_FILE"
UPLOAD_LIMIT = 5
RETRY_ATTEMPTS = 3
RETRY_DELAY = 2

# Element ID mapping for Dublin Core
DC_ELEMENTS = {
    "Title": 50,
    "Creator": 39,
    "Contributor": 37,
    "Subject": 49,
    "Tema": 49,
    "Type": 51,
    "Tipo": 51,
    "Description": 41,
    "Descripción": 41,
    "Date": 40,
    "Language": 44,
    "Idioma": 44,
    "Publisher": 45,
    "Relation": 46,
    "Source": 48,
    "Format": 42,
    "Formato": 42,
    "Identifier": 43,
    "Rights": 47,
    "Derechos": 47,
    "Notes": 41  # Will be added as private metadata
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

def get_collection_id(collection_name):
    if not collection_name:
        return None
    params = {"key": API_KEY}
    try:
        response = requests.get(OMEKA_COLLECTIONS_URL, params=params, timeout=30)
        if response.status_code == 200:
            for collection in response.json():
                for element in collection.get("element_texts", []):
                    if element.get("element", {}).get("name") == "Title" and element.get("text", "").lower() == collection_name.lower():
                        return collection["id"]
        return create_collection(collection_name)
    except Exception as e:
        log_message(f"Error getting collection: {e}", "ERROR")
        return None

def create_collection(name):
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    params = {"key": API_KEY}
    data = {
        "element_texts": [{"element": {"id": DC_ELEMENTS["Title"]}, "text": name, "html": True}],
        "public": True
    }
    try:
        response = requests.post(OMEKA_COLLECTIONS_URL, headers=headers, params=params, json=data)
        if response.status_code == 201:
            collection_id = response.json().get("id")
            log_message(f"✅ Collection created: {name}", "SUCCESS")
            return collection_id
    except Exception as e:
        log_message(f"Failed to create collection: {e}", "ERROR")
    return None

def format_metadata(row):
    metadata = {"element_texts": []}
    for field, value in row.items():
        if not value or str(value).lower() in ("nan", "none"):
            continue
        # Normaliza el valor a cadena
        if isinstance(value, float) and value.is_integer():
            value = str(int(value))  # Convierte 2024.0 a "2024"
        else:
            value = str(value).strip()
        if field in ["Tags", "tags", "Etiquetas", "etiquetas", "Collection", "collection", "Colección", "colección"]:
            continue
        if field in DC_ELEMENTS:
            metadata["element_texts"].append({
                "element": {"id": DC_ELEMENTS[field]},
                "text": value,
                "html": True
            })
    return metadata

def create_item(metadata, collection_id=None, tags=None, private_notes=None):
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    params = {"key": API_KEY}
    item_data = {
        "element_texts": metadata["element_texts"],
        "public": True
    }
    if collection_id:
        item_data["collection"] = {"id": collection_id}
    if tags:
        item_data["tags"] = tags
    if private_notes:
        item_data["element_texts"].append({
            "element": {"id": DC_ELEMENTS["Notes"]},
            "text": private_notes,
            "html": True
        })
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

def read_csv(path):
    try:
        df = pd.read_csv(path, encoding='utf-8').fillna('')
        df.columns = [col.strip() for col in df.columns]
        return df.to_dict(orient="records")
    except Exception as e:
        log_message(f"CSV read error: {e}", "ERROR")
        return []

def upload_items():
    log_message("🚀 Starting batch upload process")
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
        metadata = format_metadata(row)
        if not metadata["element_texts"]:
            log_message("⚠️ No valid metadata found. Skipping.", "WARNING")
            continue

        collection_id = None
        for col in ["Collection", "collection", "Colección", "colección"]:
            if col in row and row[col]:
                collection_id = get_collection_id(row[col])
                break

        tags = []
        for tag_col in ["Tags", "tags", "Etiquetas", "etiquetas"]:
            if tag_col in row and row[tag_col]:
                tags = parse_tags(row[tag_col])
                break

        private_notes = row.get("Notes", "").strip()

        item_id = create_item(metadata, collection_id, tags, private_notes)
        if item_id:
            successful_uploads += 1

    log_message(f"✅ ✅ Upload complete: {successful_uploads} of {len(data)} items")

if __name__ == "__main__":
    upload_items()
