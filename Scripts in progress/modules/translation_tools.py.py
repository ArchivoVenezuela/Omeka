# modules/translation_tools.py
from googletrans import Translator # pip install googletrans==4.0.0-rc1
import time # Import time module

def translate_data(data, target_language="es"):
    """
    Translates specified fields in the data using Google Translate.

    Args:
        data (list): A list of dictionaries to translate.
        target_language (str): The target language code ("es" for Spanish, "en" for English).

    Returns:
        list: A list of dictionaries with translated fields.
    """
    translator = Translator() # Initialize the translator here
    translated_data = []
    for row in data:
        translated_row = row.copy() # Create a copy to avoid modifying original
        
        # Fields to translate based on target language
        if target_language == "es":
            fields_to_translate = [("Description (EN)", "Description (ES)"),
                                  ("Tags (EN)", "Tags (ES)"),
                                  ("Relation", "Relación")] # Using tuples
        elif target_language == "en":
            fields_to_translate = [("Description (ES)", "Description (EN)"),
                                  ("Tags (ES)", "Tags (EN)"),
                                  ("Relación", "Relation")]
        else:
            print(f"Unsupported target language: {target_language}")
            return data # Return original data if language is unsupported

        for source_field, dest_field in fields_to_translate:
            text_to_translate = translated_row.get(source_field, "") # Get text from source
            if text_to_translate:
                try:
                    translation = translator.translate(text_to_translate, dest=target_language)
                    translated_row[dest_field] = translation.text # Set translated text
                    time.sleep(1)  # Be nice to the API - pause for 1 second
                except Exception as e:
                    print(f"Translation error for '{text_to_translate}': {e}") # Log errors
                    translated_row[dest_field] = f"Translation Failed: {e}" # Set an error message

        translated_data.append(translated_row)
    return translated_data