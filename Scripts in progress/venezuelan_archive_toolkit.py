import csv
import argparse # Allows you to run this script from the command line with arguments
import os
from modules import data_enrichment, image_retrieval, tag_management

def main():
    parser = argparse.ArgumentParser(description="Automates tasks for building a Venezuelan diaspora digital archive.")
    parser.add_argument("input_csv", help="Path to the input CSV file (WorldCat download)")
    parser.add_argument("output_csv", help="Path to save the processed CSV file")
    parser.add_argument("--language", choices=["en", "es"], default="en", help="Target language for translation (en or es)") # New argument for language choice
    args = parser.parse_args()

    # 1. Data Enrichment
    print("Enriching data...")
    enriched_data = data_enrichment.enrich_data(args.input_csv) # Simplified call
    
    # 2. Translation
    print("Translating fields...")
    translated_data = translation_tools.translate_data(enriched_data, args.language) # Added language argument
    
    # 3. Image Retrieval
    print("Retrieving cover images...")
    image_retrieval.retrieve_images(translated_data) # No need to return, saves directly
    
    # 4. Tag Management
    print("Managing tags...")
    tagged_data = tag_management.manage_tags(translated_data)
    
    # Write the final processed data to a CSV
    print(f"Writing output to {args.output_csv}...")
    write_csv(tagged_data, args.output_csv)
    
    print("Workflow complete!")

def write_csv(data, output_path):
    """Writes the processed data to a CSV file."""
    fieldnames = data[0].keys() # Get field names from the first item
    with open(output_path, 'w', encoding='utf-8', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

if __name__ == "__main__":
    main()