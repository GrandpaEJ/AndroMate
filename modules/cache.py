# modules/cache.py
import hashlib
import json
import os
import time

CACHE_DIR = os.path.expanduser("~/storage/shared/AndroMate/cache")
os.makedirs(CACHE_DIR, exist_ok=True)

def get_hash(text):
    """Generate a MD5 hash for the given text."""
    return hashlib.md5(text.encode('utf-8')).hexdigest()

def get_cached_response(prompt):
    """Retrieve a cached response if it exists and is not expired."""
    prompt_hash = get_hash(prompt)
    cache_file = os.path.join(CACHE_DIR, f"{prompt_hash}.json")
    
    if os.path.exists(cache_file):
        # Optional: check expiration (e.g., 24 hours)
        # For now, let's just return it if it exists
        with open(cache_file, 'r') as f:
            return json.load(f)
    return None

def set_cached_response(prompt, response):
    """Save a response to the cache."""
    prompt_hash = get_hash(prompt)
    cache_file = os.path.join(CACHE_DIR, f"{prompt_hash}.json")
    
    with open(cache_file, 'w') as f:
        json.dump(response, f)
