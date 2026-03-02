"""
Simplified Q&A Engine using Google GenerativeAI directly
"""

import os
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

import google.generativeai as genai

import config
from language_handler import language_processor

logger = logging.getLogger(__name__)


class SimpleQAEngine:
    """Simplified Q&A Engine using Google GenerativeAI"""
    
    def __init__(self):
        self.model = None
        self.lang_processor = language_processor
        self.conversation_history = []
    
    def initialize(self) -> bool:
        """Initialize with Google GenerativeAI"""
        try:
            api_key = os.getenv(config.API_KEY_NAME)
            if not api_key:
                logger.error("API key not found")
                print("\n❌ API key not found in .env file")
                return False
            
            genai.configure(api_key=api_key)
            
            # Use the working model with fallback
            try:
                self.model = genai.GenerativeModel('gemini-2.5-flash')
            except:
                try:
                    self.model = genai.GenerativeModel('gemini-1.5-flash')
                except:
                    self.model = genai.GenerativeModel('gemini-pro')
            
            logger.info("✅ QA Engine initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing: {e}")
            return False
    
    def answer(self, question: str) -> Dict[str, Any]:
        """Answer question directly"""
        start_time = datetime.now()
        
        try:
            # Process language
            lang_info = self.lang_processor.process_input(question)
            question_lang = lang_info['detected_lang']
            
            logger.info(f"Question language: {question_lang}")
            
            # Generate response
            response = self.model.generate_content(question)
            
            result = {
                'success': True,
                'answer': response.text,
                'language': question_lang,
                'processing_time': (datetime.now() - start_time).total_seconds(),
                'sources': []
            }
            
            # Update conversation history
            self.conversation_history.append({
                'question': question,
                'answer': response.text,
                'language': question_lang,
                'timestamp': datetime.now().isoformat()
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Error answering question: {e}")
            return {
                'success': False,
                'answer': f"Error: {str(e)}",
                'language': 'en',
                'processing_time': (datetime.now() - start_time).total_seconds()
            }
    
    def get_conversation_history(self, lang: Optional[str] = None) -> List[Dict]:
        """Get conversation history"""
        if lang:
            return [h for h in self.conversation_history if h['language'] == lang]
        return self.conversation_history
    
    def clear_conversation(self):
        """Clear conversation history"""
        self.conversation_history = []


# Global instance
_qa_engine = None


def get_qa_engine() -> SimpleQAEngine:
    """Get or create QA engine instance"""
    global _qa_engine
    if _qa_engine is None:
        _qa_engine = SimpleQAEngine()
        _qa_engine.initialize()
    return _qa_engine


def answer_question(question: str) -> Dict[str, Any]:
    """Convenience function to answer question"""
    engine = get_qa_engine()
    return engine.answer(question)