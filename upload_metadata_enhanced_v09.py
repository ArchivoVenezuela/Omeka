# -*- coding: utf-8 -*-

import os
import requests
import pandas as pd
import json
import time
from urllib.parse import urljoin

# This script handles the following fields: Title, Creator, Contributor, Subject, Type, Description,
# Date, Language, Publisher, Relation, Source, Tags, URL, File URL, Collection, Format, 
# Rights, Identifier

#This script does not handle tags, geolocation, thumbnails

# 🔹 CONFIGURATION 🔹
DEBUG = True  # Enable debugging
OMEKA_BASE_URL = "https://archivovenezuela.com/test/"  # Omeka site base URL
OMEKA_API_URL = urljoin(OMEKA_BASE_URL, "api/items")
OMEKA_COLLECTIONS_URL = urljoin(OMEKA_BASE_URL, "api/collections")
API_KEY = "5988565c1c5bb494fa94153c3b4b3874b82e49fb"  # 🔑 Replace with your API key 
CSV_FILE = r"C:\Users\Pat\Downloads\Bilingual_Metadata_Spanish_CSV_TEST_05.csv"  # Replace with spreadsheet csv-utf8
UPLOAD_LIMIT = 5  # Limit number of items to upload (set to None for all items)
RETRY_ATTEMPTS = 3  # Number of retry attempts for API requests
RETRY_DELAY = 2  # Delay between retry attempts in seconds

# Dublin Core element IDs mapping
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
    "Spatial Coverage": 38,  # Using "Coverage" element for spatial coverage
    "Alternative Title": 51,  # Added explicit mapping for Alternative Title
}

# 🔹 Helper functions 🔹
def log_message(message, level="INFO"):
    """Print formatted log messages."""
    icons = {
        "INFO": "ℹ️",
        "SUCCESS": "✅",
        "ERROR": "❌",
        "WARNING": "⚠️",
        "DEBUG": "🔍"
    }
    
    icon = icons.get(level.upper(), "ℹ️")
    print(f"{icon} {message}")

# 🔹 Create an item in Omeka
def create_item(metadata, collection_id=None, tags=None):
    """
    Create an item in Omeka with correctly formatted metadata.
    
    Args:
        metadata (dict): Item metadata
        collection_id (int, optional): ID of collection to add item to
        tags (list, optional): List of tags to add to item
    
    Returns:
        int: ID of created item or None if failed
    """
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    params = {"key": API_KEY}
    
    # Prepare item data
    item_data = {
        "element_texts": metadata["element_texts"],
        "public": True
    }
    
    # Add collection if specified
    if collection_id:
        item_data["collection"] = {"id": collection_id}
    
    # Add tags if specified
    if tags and isinstance(tags, list) and len(tags) > 0:
        item_data["tags"] = tags
    
    # Try to create the item with retry mechanism
    for attempt in range(RETRY_ATTEMPTS):
        try:
            response = requests.post(
                OMEKA_API_URL,
                json=item_data,
                headers=headers,
                params=params,
                timeout=30
            )
            
            if response.status_code == 201:
                item_id = response.json().get('id')
                log_message(f"Item created: ID {item_id}", "SUCCESS")
                return item_id
            else:
                log_message(f"Error creating item (Attempt {attempt+1}/{RETRY_ATTEMPTS}): {response.status_code} - {response.text}", "ERROR")
                
                if attempt < RETRY_ATTEMPTS - 1:
                    time.sleep(RETRY_DELAY)
                    
        except requests.exceptions.RequestException as e:
            log_message(f"Request failed (Attempt {attempt+1}/{RETRY_ATTEMPTS}): {str(e)}", "ERROR")
            
            if attempt < RETRY_ATTEMPTS - 1:
                time.sleep(RETRY_DELAY)
    
    return None

# 🔹 Get collection ID by name
def get_collection_id(collection_name):
    """
    Get collection ID by name.
    
    Args:
        collection_name (str): Name of the collection
    
    Returns:
        int: Collection ID or None if not found
    """
    if not collection_name:
        return None
        
    params = {"key": API_KEY}
    
    try:
        response = requests.get(OMEKA_COLLECTIONS_URL, params=params, timeout=30)
        
        if response.status_code == 200:
            collections = response.json()
            
            for collection in collections:
                for element_text in collection.get('element_texts', []):
                    if (element_text.get('element', {}).get('name') == 'Title' and 
                        element_text.get('text', '').strip().lower() == collection_name.strip().lower()):
                        return collection.get('id')
            
            # If collection not found, create it
            collection_id = create_collection(collection_name)
            return collection_id
            
        else:
            log_message(f"Failed to fetch collections: {response.text}", "ERROR")
            return None
            
    except Exception as e:
        log_message(f"Error getting collection ID: {str(e)}", "ERROR")
        return None

# 🔹 Create collection
def create_collection(collection_name):
    """
    Create a new collection in Omeka.
    
    Args:
        collection_name (str): Name of the collection
    
    Returns:
        int: ID of created collection or None if failed
    """
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    params = {"key": API_KEY}
    
    collection_data = {
        "element_texts": [
            {
                "element": {"id": DC_ELEMENTS["Title"]},
                "text": collection_name,
                "html": True
            }
        ],
        "public": True
    }
    
    for attempt in range(RETRY_ATTEMPTS):
        try:
            response = requests.post(
                OMEKA_COLLECTIONS_URL,
                json=collection_data,
                headers=headers,
                params=params,
                timeout=30
            )
            
            if response.status_code == 201:
                collection_id = response.json().get('id')
                log_message(f"Collection created: ID {collection_id}", "SUCCESS")
                return collection_id
            else:
                log_message(f"Error creating collection (Attempt {attempt+1}/{RETRY_ATTEMPTS}): {response.status_code} - {response.text}", "ERROR")
                
                if attempt < RETRY_ATTEMPTS - 1:
                    time.sleep(RETRY_DELAY)
                    
        except requests.exceptions.RequestException as e:
            log_message(f"Request failed (Attempt {attempt+1}/{RETRY_ATTEMPTS}): {str(e)}", "ERROR")
            
            if attempt < RETRY_ATTEMPTS - 1:
                time.sleep(RETRY_DELAY)
    
    return None

# 🔹 Parse tags from string
def parse_tags(tags_string):
    """
    Parse tags from a string into a list.
    
    Args:
        tags_string (str): String of tags (comma, semicolon, or space-separated)
    
    Returns:
        list: List of tags
    """
    if not tags_string or not isinstance(tags_string, str):
        return []
        
    # Try different separators
    for separator in [',', ';', '|']:
        if separator in tags_string:
            return [tag.strip() for tag in tags_string.split(separator) if tag.strip()]
    
    # Fall back to space separation (only if no other separators found)
    return [tag.strip() for tag in tags_string.split() if tag.strip()]

# 🔹 Read CSV file
def read_csv(csv_file):
    """
    Read CSV file and return data as a list of dictionaries.
    
    Args:
        csv_file (str): Path to CSV file
    
    Returns:
        list: List of dictionaries containing CSV data
    """
    try:
        # Try reading with UTF-8 encoding first
        df = pd.read_csv(csv_file, encoding='utf-8', low_memory=False)
        log_message("CSV file read successfully with UTF-8 encoding", "INFO")
    except UnicodeDecodeError:
        # If UTF-8 fails, try with Latin-1 encoding
        try:
            df = pd.read_csv(csv_file, encoding='latin-1', low_memory=False)
            log_message("CSV file read successfully with Latin-1 encoding", "INFO")
        except Exception as e:
            log_message(f"Error reading CSV file: {str(e)}", "ERROR")
            return []
    except Exception as e:
        log_message(f"Error reading CSV file: {str(e)}", "ERROR")
        return []
    
    # Drop empty columns
    df.dropna(axis=1, how='all', inplace=True)
    
    # Drop empty rows
    df.dropna(axis=0, how='all', inplace=True)
    
    # Convert all column names to string and strip whitespace
    df.columns = [str(col).strip() for col in df.columns]
    
    # Fill NaN values with empty strings
    df = df.fillna('')
    
    if DEBUG:
        log_message("CSV File Content (First 5 rows):", "DEBUG")
        print(df.head())
        log_message(f"Total rows in CSV: {len(df)}", "INFO")
        log_message(f"Columns found: {', '.join(df.columns)}", "INFO")
    
    return df.to_dict(orient="records")

# 🔹 Convert CSV row to Omeka metadata format
def format_metadata(row):
    """
    Convert CSV row into Omeka metadata format.
    
    Args:
        row (dict): Dictionary representing a row from the CSV file
    
    Returns:
        dict: Formatted metadata for Omeka API
    """
    metadata = {"element_texts": []}
    
    # Process each field in the row
    for field, value in row.items():
        field = field.strip()
        
        # Skip empty values and fields we handle separately
        if not value or str(value).lower() in ('nan', 'none', ''):
            continue
            
        # Skip geolocation field to avoid conflicts with plugin
        if field.lower() == 'geolocation':
            continue
            
        # Skip file URL field since we're not processing files
        if field.lower() in ['file url', 'fileurl', 'file_url']:
            continue
            
        if field.lower() in ['collection', 'tags']:
            continue  # These fields are handled separately
            
        value = str(value).strip()
            
        # Handle URL field specifically (map to Relation)
        if field.lower() == 'url':
            metadata["element_texts"].append({
                "element": {"id": DC_ELEMENTS["Relation"]},
                "text": value,
                "html": True
            })
            continue
            
        # Process known Dublin Core elements
        if field in DC_ELEMENTS or field.replace('DC:', '') in DC_ELEMENTS:
            # Handle fields with or without 'DC:' prefix
            clean_field = field.replace('DC:', '')
            element_id = DC_ELEMENTS.get(clean_field) or DC_ELEMENTS.get(field)
            
            if element_id:
                # Create properly formatted metadata entry
                metadata["element_texts"].append({
                    "element": {"id": element_id},
                    "text": value,
                    "html": True  # Mark as HTML to ensure proper formatting
                })
    
    if DEBUG and metadata["element_texts"]:
        log_message(f"Formatted metadata: {len(metadata['element_texts'])} elements", "DEBUG")
    
    return metadata

# 🔹 Main function to upload items
def upload_items():
    """Read CSV and upload items to Omeka."""
    log_message("Starting batch upload process", "INFO")
    
    # Read CSV data
    data = read_csv(CSV_FILE)
    if not data:
        log_message("No data found in CSV file. Exiting.", "ERROR")
        return
    
    # Limit number of items to upload if specified
    if UPLOAD_LIMIT and isinstance(UPLOAD_LIMIT, int):
        data = data[:UPLOAD_LIMIT]
        log_message(f"Processing first {UPLOAD_LIMIT} items", "INFO")
    
    # Process each row
    successful_uploads = 0
    for index, row in enumerate(data):
        log_message(f"Processing item {index+1}/{len(data)}", "INFO")
        
        # Format metadata
        metadata = format_metadata(row)
        
        if not metadata["element_texts"]:
            log_message(f"No valid metadata found for item {index+1}. Skipping.", "WARNING")
            continue
        
        # Get collection ID if specified
        collection_id = None
        for collection_field in ['Collection', 'collection']:
            if collection_field in row and row[collection_field]:
                collection_id = get_collection_id(row[collection_field])
                break
        
        # Parse tags
        tags = []
        for tags_field in ['Tags', 'tags']:
            if tags_field in row and row[tags_field]:
                tags = parse_tags(row[tags_field])
                if tags:
                    log_message(f"Found {len(tags)} tags: {', '.join(tags)}", "INFO")
                break
        
        # Create item (without file processing)
        item_id = create_item(metadata, collection_id, tags)
        if item_id:
            successful_uploads += 1
            
            # Log file URL that was not processed
            for file_field in ['File URL', 'file url', 'fileurl', 'file_url']:
                if file_field in row and row[file_field]:
                    file_url = row[file_field].strip()
                    log_message(f"Skipped file URL: {file_url} (file processing disabled)", "INFO")
                    break
    
    log_message(f"Batch upload completed: {successful_uploads} of {len(data)} items uploaded successfully", "INFO")

# 🔹 Run the script
if __name__ == "__main__":
    upload_items()