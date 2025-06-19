import streamlit as st
import pandas as pd
from fetcher import fetch_oclc_token, fetch_worldcat_data, clean_worldcat_data, CSV_COLUMNS
import time
import json
import requests
import io  # Needed for download buffer

# ---------------- Omeka config ----------------
OMEKA_API_KEY = "your_omeka_api_key"
OMEKA_URL = "your_omeka_url"

# ✅ Only allow these valid Dublin Core fields
VALID_FIELDS = {
    "Identifier", "Title", "Título",
    "Creator", "Contributor",
    "Subject (EN)", "Subject (ES)",
    "Type (EN)", "Tipo (ES)",
    "Description", "Descripción",
    "Date", "Language", "Lenguaje",
    "Format", "Formato",
    "Rights", "Derechos",
    "Publisher",
    "Coverage", "Cobertura",
    "Relation", "Relación",
    "Source"
}

# ✅ Convert DataFrame row to Omeka JSON
def row_to_omeka_json(row):
    metadata = []
    for field, value in row.items():
        if field not in VALID_FIELDS:
            continue
        if str(value).strip() == "":
            continue
        metadata.append({
            "element": {"name": field},
            "text": value,
            "html": False
        })
    return {
        "public": True,
        "featured": False,
        "element_texts": metadata
    }

# ✅ Upload single item to Omeka via API
def upload_item_to_omeka(row):
    omeka_data = row_to_omeka_json(row)
    response = requests.post(
        OMEKA_URL,
        headers={"Content-Type": "application/json"},
        params={"key": OMEKA_API_KEY},
        data=json.dumps(omeka_data)
    )
    return response

# ---------------- Streamlit UI ----------------
st.set_page_config(page_title="Archivo Venezuela Tool", layout="wide")
st.title("📚 Archivo Venezuela Metadata Tool")

# Upload CSV
uploaded_file = st.file_uploader("Upload a CSV with OCLC numbers", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.write("Uploaded OCLC Numbers:")
    st.dataframe(df)

    if st.button("Fetch Metadata"):
        token = fetch_oclc_token()
        if not token:
            st.error("❌ Failed to fetch token. Check API keys.")
        else:
            all_metadata = []
            progress_bar = st.progress(0)
            status_text = st.empty()
            total = len(df)

            for idx, oclc in enumerate(df['oclc']):
                status_text.text(f"🔄 Fetching metadata for OCLC {oclc} ({idx + 1}/{total})...")
                try:
                    data = fetch_worldcat_data(str(oclc), token)
                    if data:
                        cleaned = clean_worldcat_data(data)
                        all_metadata.append(cleaned)
                    else:
                        st.warning(f"⚠️ OCLC {oclc} not found or failed.")
                except Exception as e:
                    st.warning(f"⚠️ OCLC {oclc} failed with error: {e}")
                progress_bar.progress((idx + 1) / total)
                time.sleep(0.5)

            result_df = pd.DataFrame(all_metadata)
            result_df = result_df.reindex(columns=CSV_COLUMNS)

            # ✅ Store for next step
            st.session_state["result_df"] = result_df

            st.success(f"✅ Metadata fetched for {len(all_metadata)} out of {total} OCLC numbers.")
            st.dataframe(result_df)

            # ✅ CSV download
            csv = result_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("⬇️ Download CSV", data=csv, file_name="metadata_output.csv")

# ---------------- Upload to Omeka ----------------
if "result_df" in st.session_state:
    if st.button("📤 Upload to Omeka"):
        result_df = st.session_state["result_df"]
        with st.spinner("Uploading items to Omeka..."):
            success_count = 0
            total = len(result_df)
            for idx, row in result_df.iterrows():
                response = upload_item_to_omeka(row)
                title = row.get("Title") or f"Item {idx + 1}"
                if response.status_code == 201:
                    st.success(f"✅ [{idx + 1}/{total}] '{title}' uploaded.")
                    success_count += 1
                else:
                    st.error(f"❌ [{idx + 1}/{total}] '{title}' failed: {response.status_code} - {response.text}")
            st.success(f"🎉 Final Result: {success_count} out of {total} items uploaded to Omeka.")

# ---------------- FAST Subject Enrichment ----------------
# --- FAST START ---

DEEPL_API_KEY = ""  # Optional: Paste your DeepL API key here

def extract_fast_subjects(worldcat_data):
    subjects = []

    if "subjects" in worldcat_data:
        for item in worldcat_data["subjects"]:
            vocab = item.get("vocabulary", "").lower()
            if vocab == "fast":
                label = item.get("subjectName", {}).get("text")
                uri = item.get("uri") or item.get("@id", "")
                if label:
                    subjects.append((label, uri))
    return subjects



def translate_to_spanish(text):
    # Manual fallback dictionary
    manual_translations = {
        "Short stories": "Cuentos cortos",
        "Fiction": "Ficción",
        "Novels": "Novelas",
        "Politics": "Política",
        "Refugees": "Refugiados",
        "Venezuela": "Venezuela",  # Proper nouns usually stay the same
        "Poetry": "Poesía",
        "History": "Historia"
    }

    if text in manual_translations:
        return manual_translations[text]

    # Optional DeepL fallback
    if DEEPL_API_KEY:
        url = "https://api-free.deepl.com/v2/translate"
        params = {
            "auth_key": DEEPL_API_KEY,
            "text": text,
            "target_lang": "ES"
        }
        response = requests.post(url, data=params)
        return response.json()["translations"][0]["text"]
    
    return ""  # No translation available


st.markdown("---")
st.header("📚 FAST Subject Enrichment")
st.write("Upload a CSV with OCLC numbers to fetch FAST subject headings in English and Spanish.")

fast_file = uploaded_file  # Reuse the same uploaded file

if fast_file:
    fast_file.seek(0)  # ✅ Reset stream before second read
    fast_df = pd.read_csv(fast_file)
    
    if 'oclc' not in fast_df.columns:
        st.error("CSV must have a column named 'oclc'")
    else:
        if st.button("🚀 Enrich with FAST Subjects"):
            enriched_data = []
            token = fetch_oclc_token()

            if not token:
                st.error("❌ Failed to fetch token. Check OCLC API keys.")
            else:
                with st.spinner("Fetching FAST subjects..."):
                    for idx, row in fast_df.iterrows():
                        oclc = str(row["oclc"])
                        try:
                            data = fetch_worldcat_data(oclc, token)


                            subjects = extract_fast_subjects(data)
                            for label_en, uri in subjects:
                                label_es = translate_to_spanish(label_en)
                                enriched_data.append({
                                    "oclc_number": oclc,
                                    "label_en": label_en,
                                    "label_es": label_es,
                                    "uri": uri
                                })
                        except Exception as e:
                            st.warning(f"Failed for OCLC {oclc}: {e}")

                if enriched_data:
                    fast_output_df = pd.DataFrame(enriched_data)
                    st.dataframe(fast_output_df)

                    # Download button
                    csv_buffer = io.StringIO()
                    fast_output_df.to_csv(csv_buffer, index=False)
                    st.download_button(
                        label="📥 Download FAST Enrichment CSV",
                        data=csv_buffer.getvalue(),
                        file_name="fast_subject_enrichment.csv",
                        mime="text/csv"
                    )
                else:
                    st.info("No FAST subjects found.")

