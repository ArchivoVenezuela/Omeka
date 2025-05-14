import os
import requests
import csv
import json
import time

# 🔹 CONFIGURATION: Set your API keys and endpoints
# Replace the placeholders below with your actual API keys and endpoints.

# WorldCat API credentials
WS_KEY = "YOUR_WORLD_CAT_API_KEY"  # Replace with your WorldCat API key
WS_SECRET = "YOUR_WORLD_CAT_API_SECRET"  # Replace with your WorldCat API secret

# Omeka API credentials (if integrating with Omeka)
OMEKA_API_KEY = "YOUR_OMEKA_API_KEY"  # Replace with your Omeka API key
OMEKA_URL = "YOUR_OMEKA_API_URL"  # Replace with your Omeka API endpoint (e.g., https://your-omeka-site/api/items)

# File paths
EXCEL_FILE_PATH = "WorldCatList_clean_01.xlsx"  # Path to your input Excel file (if applicable)
CSV_FILE_PATH = "WorldCatData_output.csv"  # Path to save the output CSV file

# 🔹 Define the CSV columns
CSV_COLUMNS = [
    "Identifier", "Creator", "Title", "Date", "Colaboración", "Contributor", "Publisher",
    "Subject", "Tema", "Type", "Tipo", "Description", "Descripción", "Lenguaje", "Language",
    "Format", "Formato", "Rights", "Derechos", "Relation", "Relación", "ISBN", "Source",
    "Tags", "Etiquetas", "Website", "File URL", "Colección", "Collection", "Geolocation",
    "Alternative Title", "Notes"
]

def fetch_oclc_token():
    """Fetch OAuth token from WorldCat."""
    auth_url = "https://oauth.oclc.org/token"
    auth_data = (WS_KEY, WS_SECRET)
    payload = {"grant_type": 'client_credentials', "scope": 'wcapi'}
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    response = requests.post(auth_url, auth=auth_data, data=payload, headers=headers)

    if response.status_code == 200:
        token = response.json().get("access_token")
        print(f"✅ Token obtenido: {token}")  # Debugging
        return token
    else:
        print(response.text)
        print(f"❌ Error de autenticación. Código de estado: {response.status_code}")
        return None

def fetch_worldcat_data(oclc_number, token):
    """Fetch metadata from WorldCat for a given OCLC number."""
    resource = 'bibs'
    headers = {
        "Content-Type": "application/json",
        'Authorization': f"Bearer {token}"
    }
    api_url = f'https://americas.discovery.api.oclc.org/worldcat/search/v2/{resource}/{oclc_number}'

    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        print(f"✅ Datos obtenidos para OCLC {oclc_number}: {response.json()}")  # Debugging
        return response.json()
    else:
        print(f"❌ Error al obtener datos para OCLC {oclc_number}: {response.text}")
        return None

def clean_worldcat_data(worldcat_data):
    """Clean and map WorldCat metadata to match spreadsheet headings."""
    def extract_field(data, key, default="N/A"):
        """Helper function to safely extract and flatten fields."""
        value = data.get(key, default)
        if isinstance(value, list):
            return "; ".join(str(item) for item in value)
        elif isinstance(value, dict):
            return json.dumps(value)  # Convert dict to JSON string
        return str(value)

    def extract_nested_field(data, keys, default="N/A"):
        """Helper function to extract nested fields."""
        for key in keys:
            if isinstance(data, dict) and key in data:
                data = data[key]
            else:
                return default
        return str(data)

    return {
        "Identifier": extract_field(worldcat_data, "oclcNumber"),
        "Creator": extract_field(worldcat_data, "author", "Unknown Author"),
        "Title": extract_nested_field(worldcat_data, ["mainTitles", 0, "text"], "Unknown Title"),
        "Date": extract_field(worldcat_data, "publishDate", "Unknown Date"),
        "Colaboración": "",
        "Contributor": "",
        "Publisher": extract_field(worldcat_data, "publisher", "Unknown Publisher"),
        "Subject": extract_field(worldcat_data, "subject"),
        "Tema": "",
        "Type": extract_field(worldcat_data, "type"),
        "Tipo": "",
        "Description": extract_field(worldcat_data, "summary", "No description available."),
        "Descripción": "",
        "Lenguaje": extract_nested_field(worldcat_data, ["itemLanguage", "text"], "Unknown Language"),
        "Language": extract_nested_field(worldcat_data, ["itemLanguage", "text"], "Unknown Language"),
        "Format": extract_nested_field(worldcat_data, ["generalFormat"], "Unknown Format"),
        "Formato": "",
        "Rights": extract_field(worldcat_data, "rights"),
        "Derechos": "",
        "Relation": extract_field(worldcat_data, "relation"),
        "Relación": "",
        "ISBN": extract_field(worldcat_data, "isbn"),
        "Source": "",
        "Tags": "",
        "Etiquetas": "",
        "Website": "",
        "File URL": "",
        "Colección": "",
        "Collection": "",
        "Geolocation": "",
        "Alternative Title": "",
        "Notes": "",
    }

def write_to_csv(data, file_path):
    """Write data to a CSV file."""
    if not data:
        print("⚠️ No hay datos para escribir en el archivo CSV.")
        return

    try:
        with open(file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=CSV_COLUMNS)
            writer.writeheader()
            writer.writerows(data)
        print(f"✅ Datos escritos en {file_path}")
    except IOError as e:
        print(f"❌ Error al escribir el archivo CSV: {e}")

def batch_import_to_csv(oclc_numbers, token):
    """Process a list of OCLC numbers and export to CSV."""
    all_data = []
    for oclc in oclc_numbers:
        if not oclc.isdigit():
            print(f"⚠️ OCLC inválido: {oclc}. Saltando...")
            continue

        print(f"🔍 Obteniendo datos de WorldCat para OCLC: {oclc}")
        worldcat_data = fetch_worldcat_data(oclc, token)

        if worldcat_data:
            cleaned_data = clean_worldcat_data(worldcat_data)
            all_data.append(cleaned_data)
        else:
            print(f"⚠️ Saltando OCLC: {oclc}, datos no encontrados.")

        # Add a delay to avoid hitting API rate limits
        time.sleep(1)

    if all_data:
        write_to_csv(all_data, CSV_FILE_PATH)
    else:
        print("⚠️ No hay datos para escribir en el archivo CSV.")

# 🔹 List of OCLC Numbers to Import
oclc_numbers_list = ["982300105", "1184124221", "1388663702"]  # Example list

# Run the batch import
token = fetch_oclc_token()
if token:
    batch_import_to_csv(oclc_numbers_list, token)
else:
    print("❌ Falló la obtención del token de autenticación de WorldCat.")