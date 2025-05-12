# modules/image_retrieval.py
import requests
from io import BytesIO
from PIL import Image
import os
import urllib.parse # Import urllib for URL encoding

def retrieve_images(data, image_folder="images"):
    """
    Retrieves cover images based on title and saves them to a folder.

    Args:
        data (list): A list of dictionaries with book information.
        image_folder (str): The folder to save images to.
    """
    if not os.path.exists(image_folder):
        os.makedirs(image_folder)

    for row in data:
        title = row.get("Title", "").strip()
        isbn = row.get("Source", "").replace("ISBN: ", "").strip()  # Try to get ISBN

        if title:
            image_path = os.path.join(image_folder, f"{slugify(title)}.jpg") # Create the filepath
            if os.path.exists(image_path):
                print(f"Image already exists for '{title}', skipping...")
                continue # Skip if the image already exists

            image_url = None # Initialize outside the try block
            if isbn:
                image_url = get_cover_from_openlibrary(isbn) # Try Open Library first
            if not image_url: # If no ISBN or Open Library fails, try Google Books
                image_url = get_cover_from_google_books(title)

            if image_url:
                try:
                    response = requests.get(image_url, stream=True)
                    response.raise_for_status() # Check for HTTP errors
                    image = Image.open(BytesIO(response.content))
                    image.save(image_path)
                    print(f"Saved cover image for '{title}' to {image_path}")
                    row["Files (if available)"] = os.path.abspath(image_path) # Save path in the CSV
                except requests.exceptions.RequestException as e:
                    print(f"Error downloading image for '{title}' from {image_url}: {e}")
                except Exception as e: # Catch other image processing errors
                    print(f"Error processing image for '{title}' from {image_url}: {e}")
            else:
                print(f"No cover image found for '{title}'.")
        else:
            print("No title provided, skipping image retrieval.")

def get_cover_from_openlibrary(isbn):
    """Retrieves a cover image URL from Open Library based on ISBN."""
    try:
        url = f"https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg"  # Large size
        response = requests.head(url) # Use HEAD request to check if image exists
        if response.status_code == 200: # 200 OK means the image exists
            return url
        else:
            return None # Image not found on Open Library
    except requests.exceptions.RequestException:
        return None

def get_cover_from_google_books(title):
    """Retrieves a cover image URL from Google Books based on title."""
    try:
        quoted_title = urllib.parse.quote(title) # URL-encode the title
        url = f"https://www.googleapis.com/books/v1/volumes?q=intitle:{quoted_title}"
        response = requests.get(url)
        response.raise_for_status() # Check for HTTP errors
        data = response.json()
        if data.get("totalItems", 0) > 0:
            image_links = data["items"][0]["volumeInfo"].get("imageLinks")
            if image_links and "thumbnail" in image_links:
                return image_links["thumbnail"] # Return thumbnail
        return None
    except requests.exceptions.RequestException:
        return None
    except (KeyError, IndexError, TypeError): # Handle cases where the JSON structure is not as expected
        return None

def slugify(text):
    """Generates a URL-friendly slug from text."""
    text = text.lower()
    text = ''.join(c for c in text if c.isalnum() or c == ' ')
    return text.replace(' ', '_') # Replace spaces with underscores