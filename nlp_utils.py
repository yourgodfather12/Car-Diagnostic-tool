from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from fuzzywuzzy import fuzz
from collections import Counter
import re
import logging

def extract_keywords(text, language='en'):
    '''Extract keywords from text, removing stopwords.'''
    try:
        stopwords = set(ENGLISH_STOP_WORDS)
        words = re.findall(r'\b\w+\b', text.lower())
        keywords = [word for word in words if word not in stopwords and len(word) > 2]
        return Counter(keywords)
    except Exception as e:
        logging.error(f"Error extracting keywords: {e}", exc_info=True)
        return Counter()

def fuzzy_match(text1, text2):
    '''Calculate the fuzzy matching score between two strings.'''
    try:
        return fuzz.ratio(text1.lower(), text2.lower()) / 100
    except Exception as e:
        logging.error(f"Error in fuzzy matching: {e}", exc_info=True)
        return 0.0

def normalize_text(text):
    '''Normalize text by removing punctuation and converting to lowercase.'''
    try:
        return re.sub(r'[^a-zA-Z0-9\s]', '', text).lower()
    except Exception as e:
        logging.error(f"Error normalizing text: {e}", exc_info=True)
        return text

def advanced_keyword_extraction(text, language='en'):
    '''Advanced keyword extraction with consideration of context and frequency.'''
    try:
        stopwords = set(ENGLISH_STOP_WORDS)
        words = re.findall(r'\b\w+\b', text.lower())
        filtered_words = [word for word in words if word not in stopwords and len(word) > 2]
        return Counter(filtered_words).most_common(10)
    except Exception as e:
        logging.error(f"Error in advanced keyword extraction: {e}", exc_info=True)
        return []
