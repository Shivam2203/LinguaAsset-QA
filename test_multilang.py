"""
Test script for multi-language functionality
"""

import os
from dotenv import load_dotenv
import logging

from language_handler import language_processor, MultiLanguageProcessor
from qa_engine_multilang import get_qa_engine, answer_question
from translation_cache import get_translation_cache

# Load environment
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)


def test_language_detection():
    """Test language detection"""
    print("\n" + "="*60)
    print("🌐 TEST 1: Language Detection")
    print("="*60)
    
    test_texts = {
        'English': "What is the company's registered capital?",
        'Hindi': "कंपनी की पंजीकृत पूंजी क्या है?",
        'Telugu': "కంపెనీ నమోదిత మూలధనం ఎంత?",
        'Bengali': "কোম্পানির নিবন্ধিত মূলধন কত?",
        'Spanish': "¿Cuál es el capital registrado de la empresa?",
        'Chinese': "公司的注册资本是多少？",
        'Russian': "Какой уставный капитал компании?"
    }
    
    processor = MultiLanguageProcessor()
    
    for lang, text in test_texts.items():
        detected, confidence = processor.detector.detect_language(text)
        print(f"{lang:10} -> {detected} (confidence: {confidence:.2f})")


def test_translation():
    """Test translation between languages"""
    print("\n" + "="*60)
    print("🔄 TEST 2: Translation")
    print("="*60)
    
    processor = MultiLanguageProcessor()
    
    # Test translations
    test_cases = [
        ("English to Hindi", "Shareholder information", "hi"),
        ("English to Telugu", "Fund performance", "te"),
        ("English to Bengali", "Investment strategy", "bn"),
        ("English to Spanish", "Risk management", "es"),
        ("English to Chinese", "Asset allocation", "zh-cn"),
        ("English to Russian", "Portfolio returns", "ru"),
    ]
    
    for desc, text, target in test_cases:
        translated = processor.translator.translate(text, target)
        print(f"{desc:25}: {translated}")


def test_qa_engine():
    """Test Q&A engine with multiple languages"""
    print("\n" + "="*60)
    print("🤖 TEST 3: Multi-Language Q&A")
    print("="*60)
    
    # Initialize engine
    engine = get_qa_engine()
    
    # Test questions in different languages
    questions = [
        ("English", "What is the company's name?"),
        ("Hindi", "कंपनी का नाम क्या है?"),
        ("Telugu", "కంపెనీ పేరు ఏమిటి?"),
        ("Bengali", "কোম্পানির নাম কী?"),
        ("Spanish", "¿Cuál es el nombre de la empresa?"),
        ("Chinese", "公司名称是什么？"),
        ("Russian", "Какое название компании?")
    ]
    
    for lang, question in questions:
        print(f"\n📝 {lang}: {question}")
        result = engine.answer(question)
        
        if result['success']:
            print(f"✅ Answer: {result['answer'][:100]}...")
            print(f"   Language: {result['language']}")
            if result.get('translation_used'):
                print("   ⚡ Translation used")
        else:
            print(f"❌ Failed: {result.get('error')}")


def test_cache():
    """Test translation cache"""
    print("\n" + "="*60)
    print("💾 TEST 4: Translation Cache")
    print("="*60)
    
    cache = get_translation_cache()
    
    # Test caching
    test_text = "This is a test sentence for caching."
    
    # First translation (should cache)
    print("First translation (caching)...")
    translator = MultiLanguageProcessor().translator
    result1 = translator.translate(test_text, 'hi')
    print(f"Result: {result1}")
    
    # Second translation (should use cache)
    print("\nSecond translation (should use cache)...")
    result2 = translator.translate(test_text, 'hi')
    print(f"Result: {result2}")
    
    # Show cache stats
    stats = cache.get_stats()
    print(f"\nCache stats: {stats}")


def test_field_translations():
    """Test field name translations"""
    print("\n" + "="*60)
    print("📚 TEST 5: Field Name Translations")
    print("="*60)
    
    processor = MultiLanguageProcessor()
    
    fields = ['company name', 'shareholder', 'investment', 'performance']
    languages = ['hi', 'te', 'bn', 'es', 'zh-cn', 'ru']
    
    for field in fields:
        print(f"\n{field}:")
        for lang in languages:
            translated = processor.get_field_name(field, lang)
            print(f"  {lang}: {translated}")


def test_end_to_end():
    """End-to-end test with sample conversation"""
    print("\n" + "="*60)
    print("🎯 TEST 6: End-to-End Conversation")
    print("="*60)
    
    engine = get_qa_engine()
    
    # Simulate conversation switching languages
    conversation = [
        ("en", "Hello, what is this system about?"),
        ("hi", "कंपनी के शेयरधारक कौन हैं?"),
        ("te", "ఫండ్ పనితీరు ఎలా ఉంది?"),
        ("bn", "বিনিয়োগের কৌশল কী?"),
        ("es", "¿Cuál es el capital registrado?"),
        ("zh-cn", "风险管理流程是什么？"),
        ("ru", "Какова структура акционеров?")
    ]
    
    for i, (lang, question) in enumerate(conversation, 1):
        print(f"\n[{i}] {lang.upper()}: {question}")
        result = engine.answer(question)
        
        if result['success']:
            print(f"    → {result['answer'][:100]}...")
    
    # Show conversation summary
    history = engine.get_conversation_history()
    print(f"\n📊 Total conversations: {len(history)}")
    
    # Group by language
    lang_counts = {}
    for item in history:
        lang = item['language']
        lang_counts[lang] = lang_counts.get(lang, 0) + 1
    
    print("By language:")
    for lang, count in lang_counts.items():
        print(f"  {lang}: {count} exchanges")


if __name__ == "__main__":
    print("\n🌐 MULTI-LANGUAGE ASSET MANAGEMENT Q&A SYSTEM TEST")
    print("="*60)
    
    # Run all tests
    test_language_detection()
    test_translation()
    test_field_translations()
    test_cache()
    test_qa_engine()
    test_end_to_end()
    
    print("\n" + "="*60)
    print("✅ All tests completed!")
    print("="*60)