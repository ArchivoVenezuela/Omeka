import pandas as pd
import re
from html import unescape

REQUIRED_FIELDS = [
    "Title", "Título",
    "Creator",
    "Language", "Lenguaje",
    "Date",
    "Rights", "Derechos"
]

def clean_html(raw_text):
    if not isinstance(raw_text, str):
        return raw_text
    text = re.sub(r"<[^>]+>", "", raw_text)  # Remove HTML tags
    return unescape(text).strip()

def validate_metadata(df):
    report_rows = []
    df = df.copy()
    completeness_column = []

    for idx, row in df.iterrows():
        missing_fields = []
        for field in REQUIRED_FIELDS:
            if field not in row or pd.isna(row[field]) or str(row[field]).strip() == "":
                missing_fields.append(field)

        completeness_column.append("✅" if len(missing_fields) == 0 else "❌")

        report_rows.append({
            "Index": idx,
            "Identifier": row.get("Identifier", "N/A"),
            "Title (Cleaned)": clean_html(row.get("Title") or row.get("Título", "N/A")),
            "Missing Fields": ", ".join(missing_fields) if missing_fields else "None",
            "Complete": "✅" if len(missing_fields) == 0 else "❌"
        })

    df["Metadata Complete"] = completeness_column

    return pd.DataFrame(report_rows), df
