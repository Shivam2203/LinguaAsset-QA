#!/usr/bin/env python3
"""
Multi-Language Asset Management Q&A System with Google Gemini
Main entry point with language selection
"""

import os
import sys
import argparse
from dotenv import load_dotenv
import logging
from pathlib import Path

import config
from language_handler import language_processor
from qa_engine import get_qa_engine, answer_question
from data_processor import process_training_data

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_banner():
    """Print welcome banner with language support"""
    banner = f"""
    ╔════════════════════════════════════════════════════════════╗
    ║     Multi-Language Asset Management Intelligent Q&A        ║
    ║                 (Google Gemini Powered)                    ║
    ╠════════════════════════════════════════════════════════════╣
    ║  Supported Languages:                                       ║
    ║  🇬🇧 English  🇮🇳 हिन्दी  🇮🇳 తెలుగు  🇮🇳 বাংলা              ║
    ║  🇪🇸 Español  🇨🇳 中文      🇷🇺 Русский                       ║
    ╚════════════════════════════════════════════════════════════╝
    """
    print(banner)


def interactive_mode(target_lang: str = None):
    """Run interactive Q&A in specified language"""
    engine = get_qa_engine()
    
    print(f"\n💬 Interactive Mode - Language: {config.SUPPORTED_LANGUAGES.get(target_lang, 'Auto-detect')}")
    print("="*60)
    print("Commands:")
    print("  /lang <code>  - Switch language (en/hi/te/bn/es/zh-cn/ru)")
    print("  /stats        - Show language statistics")
    print("  /clear        - Clear conversation")
    print("  /exit         - Exit")
    print("="*60)
    
    current_lang = target_lang
    
    while True:
        try:
            # Get input
            prompt = input(f"\n[{current_lang or 'auto'}] You: ").strip()
            
            # Handle commands
            if prompt.lower() == '/exit':
                print("👋 Goodbye!")
                break
            
            if prompt.lower() == '/clear':
                os.system('cls' if os.name == 'nt' else 'clear')
                engine.clear_conversation()
                print_banner()
                continue
            
            if prompt.lower() == '/stats':
                history = engine.get_conversation_history()
                print(f"\n📊 Total conversations: {len(history)}")
                
                lang_counts = {}
                for item in history:
                    lang = item['language']
                    lang_counts[lang] = lang_counts.get(lang, 0) + 1
                
                for lang, count in lang_counts.items():
                    print(f"  {config.SUPPORTED_LANGUAGES.get(lang, lang)}: {count}")
                continue
            
            if prompt.lower().startswith('/lang'):
                parts = prompt.split()
                if len(parts) > 1:
                    new_lang = parts[1]
                    if new_lang in config.SUPPORTED_LANGUAGES:
                        current_lang = new_lang
                        print(f"✅ Language switched to: {config.SUPPORTED_LANGUAGES[new_lang]}")
                    else:
                        print(f"❌ Unsupported language. Use: {', '.join(config.SUPPORTED_LANGUAGES.keys())}")
                continue
            
            if not prompt:
                continue
            
            # Get answer
            print("🤔 Thinking...", end="", flush=True)
            result = answer_question(prompt)
            print("\r", end="", flush=True)
            
            # Display result
            print(f"\n🤖 Assistant: {result['answer']}")
            
            # Show language info
            if result['language'] != current_lang and current_lang:
                print(f"   (Answered in {config.SUPPORTED_LANGUAGES[result['language']]})")
            
            # Show confidence
            if result.get('confidence'):
                confidence = result['confidence'] * 100
                print(f"   Confidence: {confidence:.1f}%")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            logger.error(f"Error: {e}")
            print(f"❌ Error: {e}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Multi-Language Asset Management Q&A System")
    parser.add_argument('--mode', '-m', choices=['cli', 'web'], default='cli',
                       help='Run mode (cli or web)')
    parser.add_argument('--lang', '-l', choices=list(config.SUPPORTED_LANGUAGES.keys()),
                       help='Default language')
    parser.add_argument('--rebuild', '-r', action='store_true',
                       help='Rebuild vector database')
    parser.add_argument('--process', '-p', action='store_true',
                       help='Process training data')
    args = parser.parse_args()
    
    print_banner()
    
    # Process training data if requested
    if args.process or args.rebuild:
        print("\n📚 Processing training data...")
        if process_training_data():
            print("✅ Training data processed successfully")
        else:
            print("❌ Failed to process training data")
            return 1
    
    # Run in selected mode
    if args.mode == 'web':
        try:
            from web_interface import main as web_main
            web_main()
        except ImportError as e:
            logger.error(f"Failed to start web interface: {e}")
            print("❌ Web interface dependencies not installed. Run: pip install streamlit")
            return 1
    else:
        interactive_mode(args.lang)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())