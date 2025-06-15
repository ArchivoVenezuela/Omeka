# 📘 WorldCat Basic Metadata Fetcher

This Python script fetches **basic bibliographic metadata** from the WorldCat Discovery API using a list of hardcoded OCLC numbers. It's ideal for librarians, researchers, and digital humanities scholars needing quick access to clean, structured data.

---

## ✅ Features

- Uses the **WorldCat Discovery API** (JSON)
- Extracts:
  - `OCLC`
  - `Title`
  - `Creator`
  - `Contributor`
  - `Publisher`
  - `Date`
  - `WorldCat URL`
- Outputs a well-encoded `CSV` with Unicode support
- Handles accented characters and mojibake with a robust fixer

---

## 🛠 Requirements

- Python 3.7+
- `requests`
- `tqdm`

You can install dependencies with:

```bash
pip install requests tqdm
