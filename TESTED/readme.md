README: WorldCat to Omeka Metadata Script
Overview
This Python script fetches metadata for a list of OCLC numbers from the WorldCat API and exports the data to a CSV file. The CSV file is formatted to match the metadata fields used in an Omeka site. The script also includes functionality to clean and map the metadata fields to the required format.

Features
Fetches metadata from the WorldCat API using OCLC numbers.
Cleans and maps metadata fields to match Omeka's requirements.
Exports the metadata to a CSV file with predefined columns.
Handles nested and missing fields in the WorldCat API response.
Includes error handling for invalid OCLC numbers and API issues.
Requirements
Python 3.x
The following Python libraries:
requests
csv
json
time
Install missing libraries using:

Configuration
API Keys and Endpoints:

Update the WS_KEY and WS_SECRET variables with your WorldCat API credentials.
Update the OMEKA_API_KEY and OMEKA_URL variables if you plan to integrate with Omeka.
File Paths:

Set the EXCEL_FILE_PATH variable to the path of your input file (if applicable).
Set the CSV_FILE_PATH variable to the desired output file path for the CSV.
CSV Columns:

The script uses a predefined list of columns (CSV_COLUMNS) to structure the output CSV file. These columns match the metadata fields used in your Omeka site.
How to Use
Prepare a List of OCLC Numbers:

Add the OCLC numbers you want to process to the oclc_numbers_list variable in the script.
Run the Script:

Execute the script in your terminal:
Output:

The script will generate a CSV file at the location specified in CSV_FILE_PATH.
Script Workflow
Fetch OAuth Token:

The fetch_oclc_token function retrieves an authentication token from the WorldCat API.
Fetch Metadata:

The fetch_worldcat_data function fetches metadata for each OCLC number using the WorldCat API.
Clean Metadata:

The clean_worldcat_data function maps and cleans the metadata fields to match the Omeka site's requirements.
Export to CSV:

The write_to_csv function writes the cleaned metadata to a CSV file.
Error Handling
Invalid OCLC numbers are skipped with a warning.
Missing or nested fields in the API response are handled gracefully with default values.
API rate limits are respected by adding a delay between requests.
Customization
Add New Metadata Fields:

Update the clean_worldcat_data function to extract additional fields from the WorldCat API response.
Add the new fields to the CSV_COLUMNS list.
Integrate with Omeka:

Use the OMEKA_API_KEY and OMEKA_URL variables to send the metadata directly to your Omeka site via its API.
Example Output
The generated CSV file will include the following columns:

License
This script is provided "as is" without warranty of any kind. Use it at your own risk.

Contact
For questions or support, please contact:

Name: Patricia Valladares
Email: [Your Email Address]
Enjoy using the script!---

License
This script is provided "as is" without warranty of any kind. Use it at your own risk.

Contact
For questions or support, please contact:

Name: Archivo Venezuela
Email: info.archivo.venezuela@gmail.com
Enjoy using the script!