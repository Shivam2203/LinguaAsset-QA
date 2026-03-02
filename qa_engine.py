"""
Multi-Language Q&A Engine - Supports 6 languages with Google Gemini
"""

import os
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
import hashlib

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain.memory import ConversationBufferMemory
from langchain.schema import Document

import config
from language_handler import language_processor, MultiLanguageProcessor
from translation_cache import TranslationCache

logger = logging.getLogger(__name__)


class MultiLangQAEngine:
    """Multi-language Q&A Engine with Google Gemini"""
    
    def __init__(self):
        self.qa_chain = None
        self.retriever = None
        self.vector_db = None
        self.embeddings = None
        self.llm = None
        self.memory = None
        self.lang_processor = MultiLanguageProcessor()
        self.translation_cache = TranslationCache()
        
        # Session tracking
        self.current_session_lang = None
        self.conversation_history = []
    
    def initialize(self) -> bool:
        """Initialize the Q&A engine with Google Gemini"""
        try:
            # Check API key
            api_key = os.getenv(config.API_KEY_NAME)
            if not api_key:
                logger.error(f"API key not found: {config.API_KEY_NAME}")
                print(f"\n❌ API key not found in .env file")
                print(f"Please add: {config.API_KEY_NAME}=your-gemini-api-key")
                return False
            
            # Initialize embeddings (using free HuggingFace)
            logger.info("Initializing embeddings model with HuggingFace...")
            
            if config.USE_HUGGINGFACE_EMBEDDINGS:
                # Use completely free HuggingFace embeddings
                self.embeddings = HuggingFaceEmbeddings(
                    model_name=config.HUGGINGFACE_EMBEDDING_MODEL,
                    model_kwargs={'device': 'cpu'},
                    encode_kwargs={'normalize_embeddings': True}
                )
                logger.info(f"✅ Using HuggingFace embeddings: {config.HUGGINGFACE_EMBEDDING_MODEL}")
            else:
                # Fallback to DashScope if needed (requires API key)
                from langchain_community.embeddings import DashScopeEmbeddings
                self.embeddings = DashScopeEmbeddings(
                    model=config.EMBEDDING_MODEL_NAME,
                    dashscope_api_key=api_key
                )
            
            # Load vector database
            logger.info(f"Loading vector database from {config.DB_DIRECTORY}...")
            self.vector_db = Chroma(
                persist_directory=config.DB_DIRECTORY,
                embedding_function=self.embeddings,
                collection_name=config.COLLECTION_NAME
            )
            
            # Create retriever
            self.retriever = self.vector_db.as_retriever(
                search_type="mmr",
                search_kwargs={
                    "k": config.RETRIEVER_SEARCH_K,
                    "fetch_k": config.RETRIEVER_FETCH_K
                }
            )
            
            # 🔥 Initialize Google Gemini LLM
            logger.info(f"Initializing Google Gemini with model: {config.LLM_MODEL_NAME}...")
            
            self.llm = ChatGoogleGenerativeAI(
                model=config.LLM_MODEL_NAME,
                google_api_key=api_key,
                temperature=config.LLM_TEMPERATURE,
                max_tokens=config.LLM_MAX_TOKENS,
                convert_system_message_to_human=True  # Important for Gemini
            )
            
            # Set up memory if enabled
            if config.ENABLE_CONVERSATION_MEMORY:
                self.memory = ConversationBufferMemory(
                    return_messages=True,
                    max_token_limit=10
                )
            
            logger.info("✅ Multi-language Q&A engine initialized successfully with Google Gemini!")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing Q&A engine: {e}", exc_info=True)
            return False
    
    def _create_language_prompt(self, question_lang: str) -> ChatPromptTemplate:
        """Create prompt in appropriate language"""
        
        # Get base prompt in detected language
        base_prompt = config.LANGUAGE_PROMPTS.get(
            question_lang,
            config.LANGUAGE_PROMPTS['en']
        )
        
        # Add language-specific instructions
        lang_instructions = {
            'hi': "कृपया हिंदी में उत्तर दें।",
            'te': "దయచేసి తెలుగులో సమాధానం ఇవ్వండి.",
            'bn': "অনুগ্রহ করে বাংলায় উত্তর দিন।",
            'es': "Por favor responda en español.",
            'zh-cn': "请用中文回答。",
            'ru': "Пожалуйста, ответьте на русском.",
            'en': "Please answer in English."
        }
        
        instruction = lang_instructions.get(question_lang, lang_instructions['en'])
        
        template = f"""{base_prompt}

{instruction}

Context:
{{context}}

Question: {{input}}

Answer:"""
        
        return ChatPromptTemplate.from_template(template)
    
    def answer(self, question: str, context: str = "") -> Dict[str, Any]:
        """
        Answer question in the language it was asked
        
        Returns:
            Dict with answer and metadata in multiple languages
        """
        start_time = datetime.now()
        
        result = {
            'success': False,
            'original_question': question,
            'answer': '',
            'answer_en': '',  # English version
            'answer_original_lang': '',  # Original language version
            'language': 'en',
            'confidence': 0.0,
            'sources': [],
            'processing_time': 0,
            'translation_used': False
        }
        
        try:
            # Process input language
            lang_info = self.lang_processor.process_input(question)
            question_lang = lang_info['detected_lang']
            processed_question = lang_info['processed_text']
            
            result['language'] = question_lang
            result['translation_used'] = lang_info['needs_translation']
            
            logger.info(f"Question language: {question_lang} (confidence: {lang_info['confidence']:.2f})")
            
            # Create prompt in detected language
            prompt = self._create_language_prompt(question_lang)
            combine_docs_chain = create_stuff_documents_chain(llm=self.llm, prompt=prompt)
            
            # Create temporary chain for this question
            rag_chain = create_retrieval_chain(
                retriever=self.retriever,
                combine_docs_chain=combine_docs_chain
            )
            
            # Get answer
            input_data = {"input": processed_question}
            if context:
                input_data["context"] = context
            
            response = rag_chain.invoke(input_data)
            answer = response.get("answer", "").strip()
            
            # Get retrieved documents for sources
            retrieved_docs = response.get("context", [])
            
            # Extract sources
            sources = []
            for doc in retrieved_docs[:3]:
                if hasattr(doc, 'metadata'):
                    source_info = {
                        'file': doc.metadata.get('source', 'Unknown'),
                        'sheet': doc.metadata.get('sheet', ''),
                        'type': doc.metadata.get('type', 'Unknown'),
                        'language': doc.metadata.get('language', 'unknown')
                    }
                    if source_info not in sources:
                        sources.append(source_info)
            
            # If answer is in English but question was in another language, translate back
            if question_lang != 'en' and config.ENABLE_TRANSLATION:
                # Translate answer back to question language
                translated_answer = self.lang_processor.translator.translate(
                    answer, question_lang, 'en'
                )
                result['answer'] = translated_answer
                result['answer_en'] = answer
                result['answer_original_lang'] = translated_answer
            else:
                result['answer'] = answer
                result['answer_en'] = answer if question_lang == 'en' else ''
                result['answer_original_lang'] = answer
            
            # Update result
            result.update({
                'success': True,
                'confidence': 0.85,  # Placeholder - implement actual confidence scoring
                'sources': sources,
                'processing_time': (datetime.now() - start_time).total_seconds()
            })
            
            # Update conversation history
            self.conversation_history.append({
                'question': question,
                'answer': result['answer'],
                'language': question_lang,
                'timestamp': datetime.now().isoformat()
            })
            
            logger.info(f"Answer generated in {result['processing_time']:.2f}s")
            
        except Exception as e:
            logger.error(f"Error answering question: {e}", exc_info=True)
            result['error'] = str(e)
            result['answer'] = "An error occurred while processing your question."
        
        return result
    
    def answer_with_context(self, question: str, context_docs: List[Document]) -> Dict[str, Any]:
        """Answer using provided context documents"""
        # Process language
        lang_info = self.lang_processor.process_input(question)
        question_lang = lang_info['detected_lang']
        
        # Create context string from documents
        context_text = "\n\n".join([doc.page_content for doc in context_docs])
        
        # Create prompt
        prompt = self._create_language_prompt(question_lang)
        chain = create_stuff_documents_chain(llm=self.llm, prompt=prompt)
        
        # Get answer
        response = chain.invoke({
            "input": lang_info['processed_text'],
            "context": context_text
        })
        
        answer = response
        
        # Translate back if needed
        if question_lang != 'en' and config.ENABLE_TRANSLATION:
            answer = self.lang_processor.translator.translate(answer, question_lang, 'en')
        
        return {
            'answer': answer,
            'language': question_lang,
            'context_used': len(context_docs)
        }
    
    def get_conversation_history(self, lang: Optional[str] = None) -> List[Dict]:
        """Get conversation history, optionally filtered by language"""
        if lang:
            return [h for h in self.conversation_history if h['language'] == lang]
        return self.conversation_history
    
    def clear_conversation(self):
        """Clear conversation history"""
        self.conversation_history = []
        if self.memory:
            self.memory.clear()


# Global instance
_qa_engine = None


def get_qa_engine() -> MultiLangQAEngine:
    """Get or create QA engine instance"""
    global _qa_engine
    if _qa_engine is None:
        _qa_engine = MultiLangQAEngine()
        _qa_engine.initialize()
    return _qa_engine


def answer_question(question: str, context: str = "") -> Dict[str, Any]:
    """Convenience function to answer question"""
    engine = get_qa_engine()
    return engine.answer(question, context)