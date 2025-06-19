import requests
import pandas as pd

def check_links(df):
    df = df.copy()
    report_rows = []

    url_fields = [col for col in df.columns if df[col].astype(str).str.startswith("http").any()]

    for idx, row in df.iterrows():
        for field in url_fields:
            url = row.get(field)
            if pd.notna(url) and isinstance(url, str) and url.startswith("http"):
                try:
                    r = requests.head(url, allow_redirects=True, timeout=5)
                    status = r.status_code
                    final_url = r.url
                    is_valid = status == 200
                    error = ""
                except Exception as e:
                    status = "Error"
                    final_url = ""
                    is_valid = False
                    error = str(e)

                report_rows.append({
                    "Index": idx,
                    "Field": field,
                    "URL": url,
                    "Final URL": final_url or "N/A",
                    "Status": status,
                    "Valid": "✅" if is_valid else "❌",
                    "Error": error
                })

    return pd.DataFrame(report_rows), df
