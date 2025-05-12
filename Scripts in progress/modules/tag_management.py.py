# modules/tag_management.py
import nltk  # pip install nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import re

nltk.download('punkt', quiet=True)  # Download tokenizer data if not already present
nltk.download('stopwords', quiet=True) # Download stopwords

def manage_tags(data, num_keywords=5):
    """
    Manages tags by extracting keywords from descriptions and translating them.

    Args:
        data (list): A list of dictionaries with item data.
        num_keywords (int): The number of keywords to extract.

    Returns:
        list: A list of dictionaries with updated tags.
    """
    stop_words = set(stopwords.words('english') + stopwords.words('spanish')) # Combined stopwords

    for row in data:
        description_en = row.get('Description (EN)', '')
        description_es = row.get('Description (ES)', '')

        # Combine descriptions for more comprehensive tag extraction
        combined_description = f"{description_en} {description_es}"

        keywords = extract_keywords(combined_description, stop_words, num_keywords) # Keywords in main language
        row['Tags (EN)'] = row.get('Tags (EN)', '') + ', ' + ', '.join(keywords) if keywords else row.get('Tags (EN)', '')
        
        # Attempt to translate keywords to Spanish if 'Tags (ES)' is empty (or vice versa)
        if not row.get('Tags (ES)', '') and keywords:
            from .utils import translate_data # Import locally to avoid circular import
            # Create a temporary dictionary for translation
            temp_data = [{'Tags (EN)': ', '.join(keywords)}] # Create a temporary structure for translation
            translated_temp_data = translate_data(temp_data, target_language="es")
            row['Tags (ES)'] = row.get('Tags (ES)', '') + ', ' + translated_temp_data[0].get('Tags (ES)', '') # Append to existing tags

    return data

def extract_keywords(text, stop_words, num_keywords=5):
    """
    Extracts keywords from text using NLTK.

    Args:
        text (str): The text to extract keywords from.
        stop_words (set): A set of stopwords to exclude.
        num_keywords (int): The number of keywords to extract.

    Returns:
        list: A list of keywords.
    """
    text = re.sub(r'[^\w\s]', '', text) # Remove punctuation
    word_tokens = word_tokenize(text.lower()) # Tokenize and lowercase
    filtered_words = [w for w in word_tokens if w not in stop_words and len(w) > 2] # Remove short words
    
    # Basic frequency analysis for keywords (can be improved with more sophisticated methods)
    word_counts = {}
    for word in filtered_words:
        word_counts[word] = word_counts.get(word, 0) + 1

    sorted_words = sorted(word_counts.items(), key=lambda item: item[1], reverse=True)
    return [word for word, count in sorted_words[:num_keywords]] # Return top N keywords