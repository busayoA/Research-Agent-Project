import re
from collections import Counter

def detect_language(text):
    """
    Detect the language of a given text (limited to English, French, and Spanish).
    
    Args:
        text (str): The text to analyse
        
    Returns:
        str: The detected language code ('en', 'fr', 'es')
    """
    # Dictionary of language-specific characters and common words
    language_markers = {
        'en': ['the', 'and', 'is', 'of', 'to', 'in', 'a', 'for', 'that', 'with', 'you', 'it', 'not', 'on', 'this'],
        'es': ['el', 'la', 'los', 'las', 'y', 'en', 'de', 'que', 'es', 'un', 'una', 'por', 'con', 'para', 'como'],
        'fr': ['le', 'la', 'les', 'et', 'en', 'un', 'une', 'des', 'du', 'est', 'que', 'pour', 'dans', 'ce', 'pas']
    }
    
    # Normalise and tokenise text
    text = text.lower()
    words = re.findall(r'\b\w+\b', text)
    
    # Count occurrences of language-specific words
    language_scores = {}
    for lang, markers in language_markers.items():
        word_count = sum(1 for word in words if word in markers)
        if words:
            language_scores[lang] = word_count / len(words)
        else:
            language_scores[lang] = 0
    
    # Return the language with the highest score
    if not language_scores:
        return 'en'  # Default to English if no matches
    
    best_language = max(language_scores.items(), key=lambda x: x[1])
    
    # If the best score is too low, default to English
    if best_language[1] < 0.05:
        return 'en'
        
    return best_language[0]

def format_instructions_for_language(language_code):
    """
    Generate language-specific instructions for the model.
    
    Args:
        language_code (str): The language code
        
    Returns:
        str: Language-specific instructions
    """
    instructions = {
        'en': "Respond in English.",
        'es': "Responde en español.",
        'fr': "Répondez en français."
    }
    
    return instructions.get(language_code, "Respond in English.")

def get_supported_languages():
    """
    Returns a list of supported language codes.
    Currently only limited to the languages I can speak
    
    Returns:
        list: List of supported language codes
    """
    return ['en', 'es', 'fr']

def get_language_name(language_code):
    """
    Returns the full name of a language based on its code.
    
    Args:
        language_code (str): The language code
        
    Returns:
        str: The full language name
    """
    language_names = {
        'en': 'English',
        'es': 'Spanish (Español)',
        'fr': 'French (Français)'
    }
    
    return language_names.get(language_code, 'Unknown')