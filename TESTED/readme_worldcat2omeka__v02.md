# worldcat2omeka_v02.py

## Overview

This script retrieves bibliographic metadata from the WorldCat API for a list of OCLC numbers and exports the results to a CSV file, ready for import into Omeka or further processing. It is designed for use with Spanish-language and Latin American library materials, but works for any OCLC numbers.

## Features

- Fetches metadata for a batch of OCLC numbers from WorldCat.
- Outputs a CSV file with fields tailored for Omeka, including Spanish and English language fields.
- Automatically installs the `requests` library if it is not present.
- Handles Unicode/UTF-8 characters for Spanish and other languages.
- Leaves the "Tema" (Spanish Subject) field empty for manual translation.

## Requirements

- Python 3.7+
- Internet connection
- WorldCat API credentials (WS_KEY and WS_SECRET)
- (Optional) Omeka API credentials if you plan to extend the script for Omeka uploads

## Setup

1. **Clone or download this script.**

2. **Install Python dependencies:**  
   The script will automatically install the `requests` library if it is not already installed.

3. **Configure your credentials:**  
   Open the script and fill in these variables at the top:
   ```python
   WS_KEY = " [ADD YOUR WS KEY HERE] "
   WS_SECRET = " [ADD YOUR WS SECRET HERE] "
   OMEKA_API_KEY = " [ADD YOUR OMEKA API KEY HERE] "
   OMEKA_URL = " [ADD YOUR OMEKA URL HERE] "
   ```

4. **Edit the OCLC numbers list:**  
   Update the `oclc_numbers_list` variable with the OCLC numbers you want to process.

## Usage

Run the script from your terminal:

```sh
python3 worldcat2omeka_v02_16May2025.py
```

- The script will fetch metadata for each OCLC number and write the results to `WorldCatData_output.csv`.
- The CSV will be encoded as UTF-8 with BOM for compatibility with Excel and Omeka.
- The `"Tema"` column will be left empty for you to fill in manually.

## Output

- **CSV File:** `WorldCatData_output.csv`
- Fields include: Identifier, Creator, Title, Date, Publisher, Subject, Tema, Type, Description, Language, Lenguaje, ISBN, and more.

## Notes

- The script includes a 1-second delay between API requests to avoid rate limits.
- If you want to translate the "Subject" field into Spanish automatically, you can add a translation function (see script comments).
- The script is ready for further customization, such as direct Omeka uploads.

## Troubleshooting

- If you get authentication errors, double-check your WorldCat API credentials.
- If the script stops or skips records, check your internet connection and the validity of the OCLC numbers.
- For large batches, be mindful of WorldCat API rate limits.

## License

MIT License

---

**Developed for Archivo Venezuela /