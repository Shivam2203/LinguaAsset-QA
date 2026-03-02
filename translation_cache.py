"""
Translation Cache - Cache translations to avoid repeated API calls
"""

import os
import json
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict
from pathlib import Path

logger = logging.getLogger(__name__)


class TranslationCache:
    """Cache for translations with TTL and size limits"""
    
    def __init__(self, cache_dir: str = "translation_cache", 
                 max_size: int = 1000, ttl: int = 86400):
        """
        Initialize translation cache
        
        Args:
            cache_dir: Directory to store cache files
            max_size: Maximum number of cache entries
            ttl: Time to live in seconds (default 24 hours)
        """
        self.cache_dir = cache_dir
        self.max_size = max_size
        self.ttl = ttl
        
        # Create cache directory
        Path(cache_dir).mkdir(exist_ok=True)
        
        # Cache metadata
        self.metadata_file = os.path.join(cache_dir, "metadata.json")
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict:
        """Load cache metadata"""
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load cache metadata: {e}")
                return {}
        return {}
    
    def _save_metadata(self):
        """Save cache metadata"""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save cache metadata: {e}")
    
    def _get_cache_key(self, text: str, source_lang: str, target_lang: str) -> str:
        """Generate cache key"""
        content = f"{text}|{source_lang}|{target_lang}"
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def _get_cache_path(self, key: str) -> str:
        """Get cache file path"""
        return os.path.join(self.cache_dir, f"{key}.json")
    
    def get(self, text: str, source_lang: str, target_lang: str) -> Optional[str]:
        """
        Get cached translation
        
        Returns:
            Translated text if found and not expired, None otherwise
        """
        key = self._get_cache_key(text, source_lang, target_lang)
        
        if key in self.metadata:
            entry = self.metadata[key]
            
            # Check expiration
            expiry = datetime.fromisoformat(entry['expiry'])
            if expiry > datetime.now():
                cache_path = self._get_cache_path(key)
                if os.path.exists(cache_path):
                    try:
                        with open(cache_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            return data['translation']
                    except Exception as e:
                        logger.error(f"Failed to read cache file: {e}")
            
            # Remove expired entry
            del self.metadata[key]
            self._save_metadata()
        
        return None
    
    def set(self, text: str, source_lang: str, target_lang: str, 
            translation: str, ttl: Optional[int] = None):
        """
        Cache translation
        
        Args:
            text: Original text
            source_lang: Source language
            target_lang: Target language
            translation: Translated text
            ttl: Optional custom TTL
        """
        key = self._get_cache_key(text, source_lang, target_lang)
        
        # Check cache size and clean if needed
        if len(self.metadata) >= self.max_size:
            self._clean_oldest()
        
        # Calculate expiry
        ttl_value = ttl if ttl is not None else self.ttl
        expiry = datetime.now() + timedelta(seconds=ttl_value)
        
        # Save translation
        cache_path = self._get_cache_path(key)
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'text': text,
                    'source_lang': source_lang,
                    'target_lang': target_lang,
                    'translation': translation,
                    'created': datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to write cache file: {e}")
            return
        
        # Update metadata
        self.metadata[key] = {
            'expiry': expiry.isoformat(),
            'size': len(translation),
            'source_lang': source_lang,
            'target_lang': target_lang
        }
        
        self._save_metadata()
        
        logger.debug(f"Cached translation: {source_lang}->{target_lang} ({len(translation)} chars)")
    
    def _clean_oldest(self):
        """Remove oldest cache entries"""
        # Sort by expiry
        sorted_items = sorted(
            self.metadata.items(),
            key=lambda x: x[1].get('expiry', '')
        )
        
        # Remove oldest 20%
        remove_count = max(1, int(self.max_size * 0.2))
        for key, _ in sorted_items[:remove_count]:
            # Remove cache file
            cache_path = self._get_cache_path(key)
            if os.path.exists(cache_path):
                try:
                    os.remove(cache_path)
                except:
                    pass
            
            # Remove from metadata
            del self.metadata[key]
        
        logger.info(f"Cleaned {remove_count} oldest cache entries")
    
    def clear(self):
        """Clear all cache"""
        import shutil
        
        # Remove cache directory
        shutil.rmtree(self.cache_dir)
        
        # Recreate directory
        Path(self.cache_dir).mkdir(exist_ok=True)
        
        # Reset metadata
        self.metadata = {}
        
        logger.info("Translation cache cleared")
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        total_size = 0
        languages = set()
        
        for key, entry in self.metadata.items():
            total_size += entry.get('size', 0)
            languages.add(entry.get('source_lang', 'unknown'))
            languages.add(entry.get('target_lang', 'unknown'))
        
        return {
            'total_entries': len(self.metadata),
            'total_size_mb': total_size / (1024 * 1024),
            'languages': list(languages),
            'cache_dir': self.cache_dir,
            'max_size': self.max_size,
            'ttl_hours': self.ttl / 3600
        }


# Global cache instance
_translation_cache = None


def get_translation_cache() -> TranslationCache:
    """Get or create translation cache"""
    global _translation_cache
    if _translation_cache is None:
        _translation_cache = TranslationCache()
    return _translation_cache