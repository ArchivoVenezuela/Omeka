import requests
import pandas as pd

def validate_images(df):
    df = df.copy()
    report_rows = []

    image_fields = [col for col in df.columns if df[col].astype(str).str.startswith("http").any()]

    for idx, row in df.iterrows():
        for field in image_fields:
            url = row.get(field)
            if pd.notna(url) and isinstance(url, str) and url.startswith("http"):
                try:
                    r = requests.get(url, stream=True, timeout=5)
                    mime_type = r.headers.get("Content-Type", "")
                    is_image = mime_type.startswith("image/")
                    error = ""
                except Exception as e:
                    mime_type = ""
                    is_image = False
                    error = str(e)

                report_rows.append({
                    "Index": idx,
                    "Field": field,
                    "URL": url,
                    "MIME Type": mime_type or "N/A",
                    "Valid Image": "✅" if is_image else "❌",
                    "Error": error
                })

    return pd.DataFrame(report_rows), df
