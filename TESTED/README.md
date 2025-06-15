# 📚 ISBN/ISSN Fallback Extractor

This Python script extracts **ISBN** and **ISSN** identifiers from WorldCat using the Discovery API. It's designed for batch processing of OCLC numbers and outputs a clean CSV file with the results.

---

## ✅ Features

- Fetches **ISBN** and **ISSN** (if available) via the WorldCat Discovery API.
- Uses hardcoded OCLC numbers — great for quick runs or integration into pipelines.
- Prints titles in the output to help match records with other datasets.
- Outputs clean, UTF-8 encoded CSV to your **Downloads** folder.

---

## 🔧 Requirements

- Python 3.7+
- External libraries:
  - `requests`
  - `tqdm`

Install dependencies (if needed):
```bash
pip install requests tqdm
