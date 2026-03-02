"""
Language Handler - Multi-language support for 6 languages
Supports: English, Hindi, Telugu, Bengali, Spanish, Chinese, Russian
"""

import os
import logging
from typing import Optional, Tuple, Dict, Any
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException
from googletrans import Translator
import hashlib
import json
from datetime import datetime, timedelta

# Fix random seed for consistent language detection
DetectorFactory.seed = 0

logger = logging.getLogger(__name__)


class LanguageDetector:
    """Detects language from text"""
    
    def __init__(self):
        # Map langdetect codes to our supported languages
        self.lang_map = {
            'en': 'en',
            'hi': 'hi',
            'te': 'te',
            'bn': 'bn',
            'es': 'es',
            'zh-cn': 'zh-cn',
            'zh-tw': 'zh-cn',
            'zh': 'zh-cn',
            'ru': 'ru'
        }
        
        # Scripts for different languages (for verification)
        self.scripts = {
            'hi': range(0x0900, 0x097F),  # Devanagari
            'te': range(0x0C00, 0x0C7F),  # Telugu
            'bn': range(0x0980, 0x09FF),  # Bengali
            'zh-cn': range(0x4E00, 0x9FFF),  # CJK
            'ru': range(0x0400, 0x04FF),  # Cyrillic
        }
        
        # Confidence thresholds
        self.confidence_threshold = 0.7
    
    def detect_language(self, text: str) -> Tuple[str, float]:
        """
        Detect language of text
        
        Returns:
            Tuple of (language_code, confidence)
        """
        if not text or len(text.strip()) < 10:
            return 'en', 0.0
        
        try:
            # Detect language
            detection = detect(text)
            confidence = 1.0  # langdetect doesn't provide confidence
            
            # Map to our supported languages
            lang = self.lang_map.get(detection, 'en')
            
            # Verify with script detection
            script_confidence = self._verify_with_script(text, lang)
            confidence = min(confidence, script_confidence)
            
            logger.debug(f"Detected language: {lang} (confidence: {confidence:.2f})")
            return lang, confidence
            
        except LangDetectException as e:
            logger.warning(f"Language detection failed: {e}")
            return 'en', 0.0
    
    def _verify_with_script(self, text: str, detected_lang: str) -> float:
        """Verify language by checking Unicode scripts"""
        if detected_lang not in self.scripts:
            return 1.0
        
        script_range = self.scripts[detected_lang]
        matches = 0
        total = 0
        
        for char in text[:500]:  # Check first 500 chars
            code = ord(char)
            if code > 127:  # Non-ASCII
                total += 1
                if code in script_range:
                    matches += 1
        
        if total == 0:
            return 0.5
        
        return matches / total
    
    def get_language_name(self, lang_code: str) -> str:
        """Get language name from code"""
        from config import SUPPORTED_LANGUAGES
        return SUPPORTED_LANGUAGES.get(lang_code, 'English')


class TranslationCache:
    """Cache translations to avoid repeated API calls"""
    
    def __init__(self, cache_dir: str = "translation_cache", max_size: int = 1000):
        self.cache_dir = cache_dir
        self.max_size = max_size
        os.makedirs(cache_dir, exist_ok=True)
        self.cache = self._load_cache()
    
    def _get_cache_key(self, text: str, source_lang: str, target_lang: str) -> str:
        """Generate cache key"""
        content = f"{text}|{source_lang}|{target_lang}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _get_cache_path(self, key: str) -> str:
        """Get cache file path"""
        return os.path.join(self.cache_dir, f"{key}.json")
    
    def _load_cache(self) -> Dict:
        """Load cache metadata"""
        cache_file = os.path.join(self.cache_dir, "cache_metadata.json")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_metadata(self):
        """Save cache metadata"""
        cache_file = os.path.join(self.cache_dir, "cache_metadata.json")
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save cache metadata: {e}")
    
    def get(self, text: str, source_lang: str, target_lang: str) -> Optional[str]:
        """Get cached translation"""
        key = self._get_cache_key(text, source_lang, target_lang)
        
        if key in self.cache:
            cache_entry = self.cache[key]
            # Check if expired
            expiry = datetime.fromisoformat(cache_entry['expiry'])
            if expiry > datetime.now():
                cache_path = self._get_cache_path(key)
                if os.path.exists(cache_path):
                    try:
                        with open(cache_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            return data['translation']
                    except:
                        pass
            
            # Remove expired entry
            del self.cache[key]
            self._save_metadata()
        
        return None
    
    def set(self, text: str, source_lang: str, target_lang: str, 
            translation: str, ttl: int = 86400):
        """Cache translation"""
        key = self._get_cache_key(text, source_lang, target_lang)
        
        # Manage cache size
        if len(self.cache) >= self.max_size:
            # Remove oldest entries
            sorted_items = sorted(
                self.cache.items(),
                key=lambda x: x[1].get('timestamp', '')
            )
            for old_key, _ in sorted_items[:100]:  # Remove 100 oldest
                del self.cache[old_key]
                old_path = self._get_cache_path(old_key)
                if os.path.exists(old_path):
                    try:
                        os.remove(old_path)
                    except:
                        pass
        
        # Save translation
        cache_path = self._get_cache_path(key)
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'text': text,
                    'source_lang': source_lang,
                    'target_lang': target_lang,
                    'translation': translation
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to cache translation: {e}")
            return
        
        # Update metadata
        self.cache[key] = {
            'timestamp': datetime.now().isoformat(),
            'expiry': (datetime.now() + timedelta(seconds=ttl)).isoformat(),
            'size': len(translation)
        }
        
        self._save_metadata()
    
    def clear(self):
        """Clear cache"""
        import shutil
        shutil.rmtree(self.cache_dir)
        os.makedirs(self.cache_dir, exist_ok=True)
        self.cache = {}


class LanguageTranslator:
    """Translate between languages"""
    
    def __init__(self, use_cache: bool = True):
        self.translator = Translator()
        self.use_cache = use_cache
        self.cache = TranslationCache() if use_cache else None
        
        # Language code mapping for Google Translate
        self.google_lang_map = {
            'en': 'en',
            'hi': 'hi',
            'te': 'te',
            'bn': 'bn',
            'es': 'es',
            'zh-cn': 'zh-cn',
            'ru': 'ru'
        }
    
    def translate(self, text: str, target_lang: str, 
                  source_lang: Optional[str] = None) -> str:
        """
        Translate text to target language
        
        Args:
            text: Text to translate
            target_lang: Target language code
            source_lang: Source language (auto-detect if None)
        
        Returns:
            Translated text
        """
        if not text or not text.strip():
            return text
        
        # Detect source language if not provided
        if source_lang is None:
            detector = LanguageDetector()
            source_lang, _ = detector.detect_language(text)
        
        # If same language, return original
        if source_lang == target_lang:
            return text
        
        # Check cache first
        if self.use_cache and self.cache:
            cached = self.cache.get(text, source_lang, target_lang)
            if cached:
                logger.debug(f"Cache hit for translation: {source_lang}->{target_lang}")
                return cached
        
        try:
            # Map language codes
            src = self.google_lang_map.get(source_lang, 'en')
            dest = self.google_lang_map.get(target_lang, 'en')
            
            # Translate
            logger.debug(f"Translating from {src} to {dest}")
            result = self.translator.translate(text, src=src, dest=dest)
            
            translated = result.text
            
            # Cache result
            if self.use_cache and self.cache:
                self.cache.set(text, source_lang, target_lang, translated)
            
            return translated
            
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return text
    
    def translate_batch(self, texts: list, target_lang: str,
                       source_lang: Optional[str] = None) -> list:
        """Translate multiple texts"""
        return [self.translate(t, target_lang, source_lang) for t in texts]


class MultiLanguageProcessor:
    """Main language processor combining detection and translation"""
    
    def __init__(self):
        self.detector = LanguageDetector()
        self.translator = LanguageTranslator()
        
        # Language-specific patterns for different scripts
        self.patterns = {
            'hi': r'[\u0900-\u097F]+',  # Devanagari
            'te': r'[\u0C00-\u0C7F]+',  # Telugu
            'bn': r'[\u0980-\u09FF]+',  # Bengali
            'zh-cn': r'[\u4E00-\u9FFF]+',  # Chinese
            'ru': r'[\u0400-\u04FF]+',  # Cyrillic
        }
    
    def process_input(self, text: str, target_lang: Optional[str] = None) -> Dict[str, Any]:
        """
        Process input text: detect language and prepare for processing
        
        Returns:
            Dict with language info and processed text
        """
        # Detect language
        detected_lang, confidence = self.detector.detect_language(text)
        
        # Determine target language
        if target_lang is None:
            target_lang = detected_lang
        
        result = {
            'original_text': text,
            'detected_lang': detected_lang,
            'detected_lang_name': self.detector.get_language_name(detected_lang),
            'confidence': confidence,
            'target_lang': target_lang,
            'needs_translation': detected_lang != target_lang
        }
        
        # Translate if needed for processing
        if result['needs_translation']:
            result['processed_text'] = self.translator.translate(
                text, 'en', detected_lang
            )
            result['translation_for_processing'] = True
        else:
            result['processed_text'] = text
            result['translation_for_processing'] = False
        
        return result
    
    def format_output(self, answer: str, original_lang: str, 
                     target_lang: str, question: str) -> Dict[str, Any]:
        """
        Format output in appropriate language
        
        Returns:
            Dict with formatted output in multiple languages
        """
        result = {
            'original_answer': answer,
            'original_lang': original_lang,
            'target_lang': target_lang
        }
        
        # Translate answer to target language if needed
        if original_lang != target_lang:
            result['translated_answer'] = self.translator.translate(
                answer, target_lang, original_lang
            )
            
            # Also provide English version for reference
            if original_lang != 'en':
                result['english_version'] = self.translator.translate(
                    answer, 'en', original_lang
                )
            else:
                result['english_version'] = answer
        
        return result
    
    def get_field_name(self, field: str, target_lang: str) -> str:
        """Get field name in target language"""
        from config import FIELD_TRANSLATIONS
        
        field_lower = field.lower()
        for eng_field, translations in FIELD_TRANSLATIONS.items():
            if eng_field in field_lower or field_lower in eng_field:
                if target_lang in translations:
                    return translations[target_lang]
        
        # If no translation found, try to translate the field name
        if target_lang != 'en':
            return self.translator.translate(field, target_lang, 'en')
        
        return field
    
    def is_rtl_language(self, lang_code: str) -> bool:
        """Check if language is RTL (Right-to-Left)"""
        # Currently supported languages are all LTR
        return False


# Global instance for easy access
language_processor = MultiLanguageProcessor()


def get_language_processor():
    """Get language processor instance"""
    return language_processor