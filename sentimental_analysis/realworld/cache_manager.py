import json
import os
import time
from functools import lru_cache

class AnalysisCache:
    def __init__(self, cache_file="analysis_cache.json", cache_duration=3600):
        self.cache_file = cache_file
        self.cache_duration = cache_duration
        self.cache = self._load_cache()

    def _load_cache(self):
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    print('Loaded analytics cache')
                    return json.load(f)
            except:
                return {}
        return {}

    def _save_cache(self):
        with open(self.cache_file, 'w') as f:
            print('saved analytics cache')
            json.dump(self.cache, f)

    def get_analysis(self, topic_name, news_text):
        # Create a unique key combining topic and news content
        cache_key = f"{topic_name}_{hash(str(news_text))}"
        
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            if time.time() - cached_data['timestamp'] <= self.cache_duration:
                return cached_data['sentiment'], cached_data['text']
        return None, None

    def set_analysis(self, topic_name, news_text, sentiment_result, final_text):
        cache_key = f"{topic_name}_{hash(str(news_text))}"
        self.cache[cache_key] = {
            'timestamp': time.time(),
            'sentiment': sentiment_result,
            'text': final_text
        }
        self._save_cache()


class NewsCache:
    def __init__(self, cache_file="news_cache.json", cache_duration=3600):
        self.cache_file = cache_file
        self.cache_duration = cache_duration
        self.cache = self._load_cache()

    def _load_cache(self):
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _save_cache(self):
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f)

    def get(self, key):
        if key in self.cache:
            timestamp = self.cache[key]['timestamp']
            if time.time() - timestamp <= self.cache_duration:
                return self.cache[key]['data']
        return None

    def set(self, key, value):
        self.cache[key] = {
            'timestamp': time.time(),
            'data': value
        }
        self._save_cache()