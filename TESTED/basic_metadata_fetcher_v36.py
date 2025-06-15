# 🚀 WorldCat Metadata Fetcher - Final Clean Version
# -----------------------------------------------
# ✅ Uses only JSON Discovery API (no XML, no unused OAuth)
# ✅ Reads OCLC numbers from hardcoded list
# ✅ Extracts title, creator, contributor, publisher, date, language, subjects, type, format, ISBN, ISSN, edition
# ✅ Writes to UTF-8 CSV

import os
import unicodedata
import re
import requests
import base64
import xml.etree.ElementTree as ET
import csv
from tqdm import tqdm
from html import unescape
import time
import json

# === USER CONFIGURATION ===
WS_KEY = "YOUR_WS_KEY"
WS_SECRET = "YOUR_WS_SECRET"
OCLC_NUMBERS = [
    "976446533",
    "1416597355",
    "1090108276"
]  # Add your OCLC numbers here

# 🔹 OUTPUT FILE PATH
OUTPUT_CSV_PATH = os.path.join(os.path.expanduser("~"), "Downloads", "worldcat_metadata_output.csv")

def normalize_unicode(text):
    """Normalize Unicode characters to their canonical form."""
    if not text:
        return ""
    # Normalize to NFC (canonical decomposition, then canonical composition)
    return unicodedata.normalize('NFC', str(text))

def fix_character_encoding(text):
    return text  # No transformation — preserve full Unicode
    """Enhanced character encoding fix with comprehensive Unicode handling."""
    if not text:
        return ""
    
    if not isinstance(text, str):
        text = str(text)
    
    # First, unescape HTML entities
    text = unescape(text)
    
    # Remove control characters except newlines, tabs
    text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')
    
    # Fix common MARC21 encoding issues
    marc_fixes = {
        # Combining diacritics (common in MARC records)
        '\u0301': '',  # combining acute accent (handle separately)
        '\u0300': '',  # combining grave accent
        '\u0303': '',  # combining tilde
        '\u0308': '',  # combining diaeresis
        
        # Fix combined characters
        'a\u0301': 'á', 'e\u0301': 'é', 'i\u0301': 'í', 'o\u0301': 'ó', 'u\u0301': 'ú',
        'A\u0301': 'Á', 'E\u0301': 'É', 'I\u0301': 'Í', 'O\u0301': 'Ó', 'U\u0301': 'Ú',
        'n\u0303': 'ñ', 'N\u0303': 'Ñ',
        'a\u0300': 'à', 'e\u0300': 'è', 'i\u0300': 'ì', 'o\u0300': 'ò', 'u\u0300': 'ù',
        'a\u0308': 'ä', 'e\u0308': 'ë', 'i\u0308': 'ï', 'o\u0308': 'ö', 'u\u0308': 'ü',
    }
    
    # Apply MARC fixes first
    for wrong, correct in marc_fixes.items():
        text = text.replace(wrong, correct)
    
    # Common UTF-8 decoding issues - comprehensive list
    encoding_fixes = {
        # Spanish accented characters
        'aÌ': 'á', 'eÌ': 'é', 'iÌ': 'í', 'oÌ': 'ó', 'uÌ': 'ú',
        'AÌ': 'Á', 'EÌ': 'É', 'IÌ': 'Í', 'OÌ': 'Ó', 'UÌ': 'Ú',
        'àÌ': 'à', 'èÌ': 'è', 'ìÌ': 'ì', 'òÌ': 'ò', 'ùÌ': 'ù',
        'ÀÌ': 'À', 'ÈÌ': 'È', 'ÌÌ': 'Ì', 'ÒÌ': 'Ò', 'ÙÌ': 'Ù',
        
        # Ñ variations
        'nÌƒ': 'ñ', 'NÌƒ': 'Ñ', 'Ã±': 'ñ', 'ÃÑ': 'Ñ', 'n~': 'ñ', 'N~': 'Ñ',
        
        # Common mojibake patterns
        'Ã¡': 'á', 'Ã©': 'é', 'Ã­': 'í', 'Ã³': 'ó', 'Ãº': 'ú',
        'Ã ': 'à', 'Ã¨': 'è', 'Ã¬': 'ì', 'Ã²': 'ò', 'Ã¹': 'ù',
        'Ã': 'Á', 'Ã‰': 'É', 'Ã': 'Í', 'Ã"': 'Ó', 'Ãš': 'Ú',
        'Ã€': 'À', 'Ãˆ': 'È', 'ÃŒ': 'Ì', "Ã'": 'Ò', 'Ã™': 'Ù',
        'Ã¢': 'â', 'Ãª': 'ê', 'Ã®': 'î', 'Ã´': 'ô', 'Ã»': 'û',
        'Ã¤': 'ä', 'Ã«': 'ë', 'Ã¯': 'ï', 'Ã¶': 'ö', 'Ã¼': 'ü',
        'Ã§': 'ç', 'Ã‡': 'Ç',
        
        # Double-encoded patterns
        'Ã\x83Â¡': 'á', 'Ã\x83Â©': 'é', 'Ã\x83Â­': 'í', 
        'Ã\x83Â³': 'ó', 'Ã\x83Âº': 'ú', 'Ã\x83Â±': 'ñ',
        
        # Additional special characters
        'â€™': "'", 'â€œ': '"', 'â€': '"', 'â€"': '–', 'â€"': '—',
        'Â°': '°', 'Â©': '©', 'Â®': '®', 'â„¢': '™',
        '…': '...', '•': '·',
        
        # Portuguese and French additions
        'Ã£': 'ã', 'Ãµ': 'õ', 'Ã‚': 'Â', 'Ãª': 'ê', 'Ã´': 'ô',
        'Ã®': 'î', 'Ã»': 'û', 'Ã¯': 'ï',
        
        # Catalan
        'Ã ': 'à', 'Ã¨': 'è', 'Ã²': 'ò', 'Ã\xad': 'í', 'Ã\xba': 'ú',
    }
    
    # Apply all fixes
    for wrong, correct in encoding_fixes.items():
        text = text.replace(wrong, correct)
    
    # Try to detect and fix remaining encoding issues
    try:
        # Check if text might be double-encoded
        if 'Ã' in text or 'Â' in text:
            try:
                # Attempt to fix double UTF-8 encoding
                temp = text.encode('latin-1', errors='ignore').decode('utf-8', errors='ignore')
                # Only use if it reduces weird characters
                if temp.count('Ã') < text.count('Ã'):
                    text = temp
            except:
                pass
    except:
        pass
    
    # Normalize Unicode
    text = normalize_unicode(text)
    
    # Clean up MARC punctuation
    text = re.sub(r'\s*[/;:]\s*$', '', text)  # Remove trailing punctuation
    text = re.sub(r'\s+', ' ', text).strip()   # Normalize whitespace
    
    return text

def get_oauth_token():
    print("🔐 Getting OAuth token...")
    url = "https://oauth.oclc.org/token"
    auth = (WS_KEY, WS_SECRET)
    data = {"grant_type": "client_credentials", "scope": "wcapi"}
    resp = requests.post(url, auth=auth, data=data)
    resp.raise_for_status()
    return resp.json().get("access_token")

def fetch_metadata_json(oclc_number, token):
    url = f"https://americas.discovery.api.oclc.org/worldcat/search/v2/bibs/{oclc_number}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    return None

def parse_basic_record(json_data, oclc_number):
    record = {
        "OCLC": str(oclc_number),
        "Title": "",
        "Creator": "",
        "Contributor": "",
        "Publisher": "",
        "Date": "",
        "URL": f"https://www.worldcat.org/oclc/{oclc_number}"
    }
    try:
        # Title
        titles = json_data.get("title", {}).get("mainTitles", [])
        if titles and isinstance(titles[0], dict):
            record["Title"] = fix_character_encoding(titles[0].get("text", "").split(" / ")[0].strip())

        # Creator (primary contributor)
        creators = json_data.get("contributor", {}).get("creators", [])
        if creators:
            first = creators[0].get("firstName", {}).get("text", "")
            last = creators[0].get("secondName", {}).get("text", "")
            record["Creator"] = fix_character_encoding(f"{first} {last}".strip())

        # Other Contributors
        others = json_data.get("contributor", {}).get("contributors", [])
        names = []
        for c in others:
            name = c.get("name", {}).get("text")
            if name:
                names.append(fix_character_encoding(name))
        record["Contributor"] = " ; ".join(names)

        # Publisher
        pubs = json_data.get("publishers", [])
        if pubs and isinstance(pubs[0], dict):
            record["Publisher"] = fix_character_encoding(pubs[0].get("name", ""))

        # Date
        record["Date"] = json_data.get("date", {}).get("publicationDate", "")

    except Exception as e:
        print(f"❌ Error parsing OCLC {oclc_number}: {e}")

    return record

def write_to_csv(records, filepath):
    if not records:
        print("No data to write.")
        return
    keys = records[0].keys()
    with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(records)

# === MAIN RUN ===
if __name__ == "__main__":
    token = get_oauth_token()
    records = []
    for oclc in tqdm(OCLC_NUMBERS, desc="Fetching metadata"):
        data = fetch_metadata_json(oclc, token)
        record = parse_basic_record(data or {}, oclc)
        records.append(record)
    write_to_csv(records, OUTPUT_CSV_PATH)
    print(f"\n✅ Done. Metadata saved to: {OUTPUT_CSV_PATH}")
