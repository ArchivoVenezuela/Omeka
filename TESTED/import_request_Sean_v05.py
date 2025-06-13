import os
import requests
import csv
import json

# 🔹 CONFIGURATION: Set your API keys and endpoints
WS_KEY = "xxx"
WS_SECRET = "xxxx"
OMEKA_API_KEY = "xxxxx"
OMEKA_URL = "https://archivovenezuela.com/test/api/items"

# Set the path to the Downloads folder explicitly
CSV_FILE_PATH = r"C:\Users\Pat\Downloads\worldcat_to_omeka.csv"

def fetch_oclc_token():
    """Fetch OAuth token from WorldCat."""
    auth_url = "https://oauth.oclc.org/token"
    auth_data = (WS_KEY, WS_SECRET)
    payload = {"grant_type": 'client_credentials', "scope": 'wcapi'}
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    response = requests.post(auth_url, auth=auth_data, data=payload, headers=headers)

    if response.status_code == 200:
        token = response.json().get("access_token")
        return token
    else:
        print(response.text)
        print(f"Authentication failed. Status code: {response.status_code}")
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
        return response.json()
    else:
        print(f"Error fetching OCLC {oclc_number}: {response.text}")
        return None

def clean_worldcat_data(worldcat_data):
    """Clean and map WorldCat metadata to match spreadsheet headings."""
    return {
        "Identifier": worldcat_data.get("oclcNumber", "N/A"),
        "Creator": worldcat_data.get("author", "Unknown Author"),
        "Title": worldcat_data.get("title", "Unknown Title"),
        "Date": worldcat_data.get("publishDate", "Unknown Date"),
        "Colaboración": "",  # Custom field, add logic if needed
        "Contributor": "",  # Custom field, add logic if needed
        "Publisher": worldcat_data.get("publisher", "Unknown Publisher"),
        "Subject": worldcat_data.get("subject", "N/A"),
        "Tema": "",  # Custom field, add logic if needed
        "Type": worldcat_data.get("type", "N/A"),
        "Tipo": "",  # Custom field, add logic if needed
        "Description": worldcat_data.get("summary", "No description available."),
        "Descripción": "",  # Custom field, add logic if needed
        "Lenguaje": worldcat_data.get("language", "N/A"),
        "Language": worldcat_data.get("language", "N/A"),
        "Format": worldcat_data.get("format", "N/A"),
        "Formato": "",  # Custom field, add logic if needed
        "Rights": worldcat_data.get("rights", "N/A"),
        "Derechos": "",  # Custom field, add logic if needed
        "Relation": worldcat_data.get("relation", "N/A"),
        "Relación": "",  # Custom field, add logic if needed
        "ISBN": worldcat_data.get("isbn", "N/A"),
        "Source": "",  # Custom field, add logic if needed
        "Tags": "",  # Custom field, add logic if needed
        "Etiquetas": "",  # Custom field, add logic if needed
        "Website": "",  # Custom field, add logic if needed
        "File URL": "",  # Custom field, add logic if needed
        "Colección": "",  # Custom field, add logic if needed
        "Collection": "",  # Custom field, add logic if needed
        "Geolocation": "",  # Custom field, add logic if needed
        "Alternative Title": "",  # Custom field, add logic if needed
        "Notes": "",  # Custom field, add logic if needed
    }

def write_to_csv(data, file_path):
    """Write data to a CSV file."""
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    print(f"✅ Data written to {file_path}")

def post_to_omeka(omeka_data):
    """Post metadata to Omeka Classic."""
    headers = {"Content-Type": "application/json"}
    params = {"key": OMEKA_API_KEY}
    response = requests.post(OMEKA_URL, headers=headers, params=params, data=json.dumps(omeka_data))

    if response.status_code == 201:
        print("✅ Successfully added item to Omeka!")
    else:
        print(f"❌ Error adding item to Omeka: {response.status_code} - {response.text}")

def batch_import_to_csv(oclc_numbers, token):
    """Process a list of OCLC numbers and export to CSV."""
    all_data = []
    for oclc in oclc_numbers:
        print(f"🔍 Fetching WorldCat data for OCLC: {oclc}")
        worldcat_data = fetch_worldcat_data(oclc, token)

        if worldcat_data:
            print(f"🔄 Cleaning data for OCLC: {oclc}")
            cleaned_data = clean_worldcat_data(worldcat_data)
            all_data.append(cleaned_data)
        else:
            print(f"⚠️ Skipping OCLC: {oclc}, data not found.")

    if all_data:
        write_to_csv(all_data, CSV_FILE_PATH)
    else:
        print("⚠️ No data to write to CSV.")

# 🔹 List of OCLC Numbers to Import
oclc_numbers_list = ["982300105","1184124221","1388663702","1395880768","1416597355","1056251997","1373305200","976446533","1225067691","1162821296","1256654950","1138930154","55498894","881468890","957078021","844213140","1377551150","1504368169","800946011","1460998034","1407231958","1085608763","1382331333","1315024446","1394052275","1311965024","1191456920","1258071524","852434083","1498473840","1300851609","1342600403","1086234760","1477972849","1144978250","1450108331","1247722232","1376380183","1392445677","1374999420","1478164973","1198350401","1190381386","1019428214","1124074515","112063"]  # Replace with actual OCLC numbers

# Run the batch import
token = fetch_oclc_token()
if token:
    batch_import_to_csv(oclc_numbers_list, token)
else:
    print("Failed to fetch WorldCat authentication token.")
