import os
import csv
import json
import time

try:
    import requests
except ImportError:
    import subprocess
    import sys
    print("🔄 Installing 'requests' library...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests

# 🔹 CONFIGURATION: Set your API keys and endpoints
WS_KEY = " [ADD YOUR WS KEY HERE] "
WS_SECRET = " [ADD YOUR WS SECRET HERE] "
OMEKA_API_KEY = " [ADD YOUR OMEKA API KEY HERE] "
OMEKA_URL = " [ ADD YOUR OMEKA URL HERE] " #EXAMPLE: https://archivovenezuela.com/test/api/items"
EXCEL_FILE_PATH = "WorldCatList_clean_01.xlsx"
CSV_FILE_PATH = "WorldCatData_output.csv"  # Define the output CSV file path
    
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
    api_url = f'https://americas.discovery.api.oclc.org/worldcat/search/v2/bibs/{oclc_number}'

    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        print(f"✅ Datos obtenidos para OCLC {oclc_number}: {response.json()}")  # Debugging
        return response.json()
    else:
        print(f"❌ Error al obtener datos para OCLC {oclc_number}: {response.text}")
        return None

def clean_worldcat_data(worldcat_data):
    def get_nested(data, keys, default=""):
        for key in keys:
            if isinstance(data, dict):
                data = data.get(key, default)
            elif isinstance(data, list) and isinstance(key, int) and len(data) > key:
                data = data[key]
            else:
                return default
        return data if data is not None else default

    # Subject extraction and translation
    subjects = []
    for subj in worldcat_data.get("subjects", []):
        subj_text = get_nested(subj, ["subjectName", "text"], "")
        if subj_text:
            subjects.append(subj_text)
    subjects_str = "; ".join(subjects)
    tema_str = ""  # Fill manually later
    # Creator extraction
    creators = []
    for creator in get_nested(worldcat_data, ["contributor", "creators"], []):
        first = get_nested(creator, ["firstName", "text"], "")
        last = get_nested(creator, ["secondName", "text"], "")
        name = f"{first} {last}".strip()
        if name:
            creators.append(name)
    creators_str = "; ".join(creators)

    publisher = get_nested(worldcat_data, ["publishers", 0, "publisherName", "text"], "")
    raw_title = get_nested(worldcat_data, ["title", "mainTitles", 0, "text"], "")
    title = raw_title.split(" /")[0].strip() if " /" in raw_title else raw_title.strip()
    pub_date = get_nested(worldcat_data, ["date", "publicationDate"], "")
    language_code = get_nested(worldcat_data, ["language", "itemLanguage"], "")

    # Language mapping
    lang_map_en = {"spa": "Spanish", "eng": "English", "fre": "French"}
    lang_map_es = {"spa": "Español", "eng": "Inglés", "fre": "Francés"}
    language = lang_map_en.get(language_code, language_code)
    lenguaje = lang_map_es.get(language_code, language_code)

    oclc_number = get_nested(worldcat_data, ["identifier", "oclcNumber"], "")
    isbns = get_nested(worldcat_data, ["identifier", "isbns"], [])
    isbn_str = "; ".join(isbns) if isinstance(isbns, list) else isbns

    description = get_nested(worldcat_data, ["description", "physicalDescription"], "")
    general_format = get_nested(worldcat_data, ["format", "generalFormat"], "")

    tipo = "Libro impreso" if general_format == "Book" else ""
    formato = "Libro impreso" if general_format == "Book" else ""

    return {
        "Identifier": oclc_number,
        "Creator": creators_str,
        "Title": title,
        "Date": pub_date,
        "Colaboración": "",
        "Contributor": "",
        "Publisher": publisher,
        "Subject": subjects_str,
        "Tema": tema_str,
        "Type": general_format,
        "Tipo": tipo,
        "Description": description,
        "Descripción": "",
        "Lenguaje": lenguaje,
        "Language": language,
        "Format": general_format,
        "Formato": formato,
        "Rights": "",
        "Derechos": "",
        "Relation": "",
        "Relación": "",
        "ISBN": isbn_str,
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
        with open(file_path, mode='w', newline='', encoding='utf-8-sig') as file:  # <-- use utf-8-sig
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
oclc_numbers_list = [
    "976446533", "1416597355", "1090108276", "1039936116", "1429659986",
    "852230773", "992087253", "1394052275", "1418777092", "1437556492",
    "1191456920", "1258071524", "1407231958", "1193984669", "1124074515",
    "1504735685", "859538618", "801438344", "773194800", "773194800",
    "1356047559", "1286428715", "1470855959", "233599065", "1504368169",
    "1377551150", "1377551150", "1264983647", "881244527", "893442097",
    "1499673584", "1056251997", "1292476738", "1508825565", "1188378401",
    "5314520", "901517849", "901517849", "1506459071", "853496799",
    "47629593", "784152518", "784152518", "1461737942", "983209733",
    "41301942", "1443162778", "1443162778", "659510526", "611942863",
    "1226073324", "1226073324", "994835870", "1042101908", "1042101908",
    "946105414", "946105414", "1450578794", "1395872506", "55498894",
    "55498894", "1006751601", "947087330", "1506293254", "947063395",
    "1376380183", "1130107116", "1225067691", "1247722232", "1104218256",
    "1104218256", "1257031810", "927705399", "1000507315", "1000507315",
    "1256654950", "1256654950", "1190381386", "1022282877", "1430189586",
    "1423251529", "982300105", "1342600403", "1138930154", "1138930154",
    "1312274846", "1022282877", "1477972914", "1485639545", "946093464",
    "1105954151", "953695638", "957078021", "1490382028", "1456542652",
    "1431976718", "1114265124", "953698089", "1490382028", "1342600403",
    "1019428214", "1311965024"
]

# Run the batch import
token = fetch_oclc_token()
if token:
    batch_import_to_csv(oclc_numbers_list, token)
else:
    print("❌ Falló la obtención del token de autenticación de WorldCat.")
    