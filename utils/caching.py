import hashlib
import pickle
import os
import json
from datetime import datetime, timedelta
from config import get_provider

# Create cache directory
CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def generate_cache_key(model, messages, temperature, max_tokens=None):
    """
    Generate a unique cache key based on request parameters
    
    Args:
        model (str): The model name
        messages (list): The messages list
        temperature (float): The temperature setting
        max_tokens (int, optional): Maximum tokens limit
        
    Returns:
        str: A hexadecimal cache key
    """
    # Include the provider in the cache key to differentiate between providers
    provider = get_provider()
    
    # Convert messages to a string representation
    message_str = json.dumps(messages, sort_keys=True)
    
    # Create a unique identifier from all parameters
    params_str = f"{provider}_{model}_{message_str}_{temperature}_{max_tokens}"
    
    # Generate MD5 hash
    return hashlib.md5(params_str.encode('utf-8')).hexdigest()

def get_cached_response(cache_key, max_age_hours=24):
    """
    Retrieve a cached response if it exists and is not expired
    
    Args:
        cache_key (str): The cache key to look up
        max_age_hours (int): Maximum age of the cache in hours
        
    Returns:
        object or None: The cached response or None if not found/expired
    """
    cache_file = os.path.join(CACHE_DIR, f"{cache_key}.pickle")
    
    # Check if cache file exists
    if not os.path.exists(cache_file):
        return None
    
    # Check if cache is expired
    file_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
    if datetime.now() - file_time > timedelta(hours=max_age_hours):
        # Cache expired, delete it
        os.remove(cache_file)
        return None
    
    # Load and return cached response
    try:
        with open(cache_file, 'rb') as f:
            return pickle.load(f)
    except (pickle.PickleError, EOFError):
        # Invalid cache file
        os.remove(cache_file)
        return None

def cache_response(cache_key, response):
    """
    Cache an API response
    
    Args:
        cache_key (str): The cache key
        response: The response object to cache
        
    Returns:
        None
    """
    cache_file = os.path.join(CACHE_DIR, f"{cache_key}.pickle")
    
    try:
        with open(cache_file, 'wb') as f:
            pickle.dump(response, f)
    except (pickle.PickleError, IOError) as e:
        print(f"Warning: Failed to cache response: {e}")