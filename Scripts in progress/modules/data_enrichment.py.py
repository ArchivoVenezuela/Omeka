# modules/data_enrichment.py
import csv
import requests
import json

def enrich_data(csv_path):
    """
    Enriches data from a CSV file using external APIs (e.g., Open Library, Google Books).

    Args:
        csv_path (str): Path to the input CSV file.

    Returns:
        list: A list of dictionaries, with enriched data.
    """
    enriched_data = []
    with open(csv_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Try to enrich with ISBN
            if row['Source'] and "ISBN" in row['Source']: # Check for ISBN in 'Source' field
                isbn = row['Source'].replace("ISBN: ", "").strip() # Extract ISBN
                enriched_row = enrich_with_isbn(row, isbn)
            else:
                # If no ISBN, try enriching with title and author
                 enriched_row = enrich_with_title_author(row)

            enriched_data.append(enriched_row)
    return enriched_data

def enrich_with_isbn(row, isbn):
    """Enriches a row with data from the Open Library and Google Books APIs using ISBN."""
    try:
        open_library_url = f"https://openlibrary.org/isbn/{isbn}.json"
        response = requests.get(open_library_url)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        data = response.json()

        row['Title'] = row['Title'] or data.get('title', '') # Update if field is empty
        row['Título'] = row['Título'] or data.get('title', '')
        if 'authors' in data:
            author_keys = [author['author']['key'] for author in data['authors']]
            authors_data = []
            for key in author_keys:
                author_url = f"https://openlibrary.org{key}.json"
                try: # Nested try-except for individual authors
                    author_response = requests.get(author_url)
                    author_response.raise_for_status()
                    author_data = author_response.json()
                    authors_data.append(author_data.get('name', ''))
                except requests.exceptions.RequestException as e:
                    print(f"Error fetching author data: {e}")  # Error for individual author
            row['Creator'] = row['Creator'] or ', '.join(authors_data) # Update if field is empty

        # Add description if available from Open Library (may need further processing)
        if 'description' in data:
            description = data['description']
            if isinstance(description, dict):
                row['Description (EN)'] = row.get('Description (EN)', '') or description.get('value', '') # Prefer existing
            else:
                row['Description (EN)'] = row.get('Description (EN)', '') or description
        
        # Try Google Books for more details
        try: # Nested try-except for Google Books
            google_books_url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
            google_response = requests.get(google_books_url)
            google_response.raise_for_status()
            google_data = google_response.json()
            if google_data.get('totalItems', 0) > 0:
                volume_info = google_data['items'][0]['volumeInfo']
                row['Publisher'] = row['Publisher'] or volume_info.get('publisher', '')
                row['Date'] = row['Date'] or volume_info.get('publishedDate', '')
                # Add subjects if available
                subjects = volume_info.get('categories', [])
                row['Subject (EN)'] = row['Subject (EN)'] or ', '.join(subjects)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching Google Books data for ISBN {isbn}: {e}") # Error for Google Books

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for ISBN {isbn}: {e}")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON for ISBN {isbn}: {e}")
    return row

def enrich_with_title_author(row):
    """Enriches a row with data from Google Books API using title and author."""
    title = row.get('Title', '')
    author = row.get('Creator', '')
    if not title or not author:
        return row # Can't enrich without title or author
    try:
        query = f"intitle:{title}+inauthor:{author}"
        google_books_url = f"https://www.googleapis.com/books/v1/volumes?q={query}"
        response = requests.get(google_books_url)
        response.raise_for_status()
        google_data = response.json()
        if google_data.get('totalItems', 0) > 0:
            volume_info = google_data['items'][0]['volumeInfo']
            row['Publisher'] = row['Publisher'] or volume_info.get('publisher', '')
            row['Date'] = row['Date'] or volume_info.get('publishedDate', '')
            # Add subjects if available
            subjects = volume_info.get('categories', [])
            row['Subject (EN)'] = row['Subject (EN)'] or ', '.join(subjects)
            row['Description (EN)'] = row.get('Description (EN)', '') or volume_info.get('description', '') # Add Google Books description if none exists

    except requests.exceptions.RequestException as e:
        print(f"Error fetching Google Books data for title '{title}' and author '{author}': {e}")
    except json.JSONDecodeError as e:
        print(f"Error decoding Google Books JSON for title '{title}' and author '{author}': {e}")
    return row