import requests
import pandas as pd

# Fetch all items from Omeka API
def fetch_all_omeka_items(api_url, api_key=None):
    items = []
    page = 1
    while True:
        params = {"page": page}
        if api_key:
            params["key"] = api_key
        response = requests.get(api_url, params=params)
        data = response.json()
        if not data:
            break
        items.extend(data)
        page += 1
    return items

# Convert Omeka item list into a clean DataFrame
def omeka_items_to_dataframe(items):
    rows = []
    for item in items:
        row = {"Omeka ID": item.get("id")}
        for element in item.get("element_texts", []):
            field = element["element"]["name"]
            row[field] = element["text"]
        rows.append(row)
    return pd.DataFrame(rows)
