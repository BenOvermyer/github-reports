import os
import pickle
import hashlib
from datetime import datetime, timezone

CACHE_DIR = os.path.join(os.path.dirname(__file__), '.cache')
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

def _get_cache_path(key):
    h = hashlib.sha256(key.encode('utf-8')).hexdigest()
    return os.path.join(CACHE_DIR, h + '.pkl')

def load_cache(key, max_age_seconds=3600):
    path = _get_cache_path(key)
    if not os.path.exists(path):
        return None
    try:
        with open(path, 'rb') as f:
            data = pickle.load(f)
        timestamp = data.get('timestamp')
        if not timestamp or (datetime.now(timezone.utc) - timestamp).total_seconds() > max_age_seconds:
            return None
        return data.get('value')
    except Exception:
        return None

def save_cache(key, value):
    path = _get_cache_path(key)
    data = {'timestamp': datetime.now(timezone.utc), 'value': value}
    with open(path, 'wb') as f:
        pickle.dump(data, f)
