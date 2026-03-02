"""
Multi-Language Configuration for Asset Management Q&A System
Updated for Google Gemini
Supports: English, Hindi, Telugu, Bengali, Spanish, Chinese, Russian
"""

import os
from pathlib import Path

# ==================== API CONFIGURATION (GOOGLE GEMINI) ====================
API_KEY_NAME = "GOOGLE_API_KEY"  # Changed from OPENROUTER_API_KEY

# Google Gemini Models - ALL FREE!
# Available free models:
# - "gemini-3-flash" - Fast, general purpose (250k tokens/min, 20 requests/day)
# - "gemini-2.5-flash" - More capable (250k tokens/min, 20 requests/day)
# - "gemma-3-27b-it" - Google's open model (15k tokens/min, 14,400 requests/day)
# - "gemma-3-12b-it" - Smaller/faster open model
# - "gemma-3-4b-it" - Tiny model for testing

LLM_MODEL_NAME = "gemini-2.5-flash"  # Start with this, change if needed

LLM_TEMPERATURE = 0.0
LLM_MAX_TOKENS = 4096

# ==================== MULTI-LANGUAGE SUPPORT ====================
# Supported languages with their codes
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'hi': 'Hindi (हिन्दी)',
    'te': 'Telugu (తెలుగు)',
    'bn': 'Bengali (বাংলা)',
    'es': 'Spanish (Español)',
    'zh-cn': 'Chinese (中文)',
    'ru': 'Russian (Русский)'
}

DEFAULT_LANGUAGE = 'en'
AUTO_DETECT_LANGUAGE = True

# Language detection confidence threshold
LANGUAGE_CONFIDENCE_THRESHOLD = 0.7

# Translation settings
ENABLE_TRANSLATION = True
TRANSLATION_CACHE_SIZE = 1000
TRANSLATION_CACHE_TTL = 86400  # 24 hours

# Language-specific prompts
LANGUAGE_PROMPTS = {
    'en': """You are a professional asset management expert. Answer based on the provided context.
If information is not in context, say "Information not found in available documents".
Be concise and professional.""",
    
    'hi': """आप एक पेशेवर एसेट प्रबंधन विशेषज्ञ हैं। प्रदान किए गए संदर्भ के आधार पर उत्तर दें।
यदि जानकारी संदर्भ में नहीं है, तो कहें "उपलब्ध दस्तावेज़ों में जानकारी नहीं मिली"।
संक्षिप्त और पेशेवर बनें।""",
    
    'te': """మీరు ప్రొఫెషనల్ అసెట్ మేనేజ్మెంట్ నిపుణులు. అందించిన సందర్భం ఆధారంగా సమాధానం ఇవ్వండి.
సమాచారం సందర్భంలో లేకపోతే, "అందుబాటులో ఉన్న పత్రాలలో సమాచారం లభించలేదు" అని చెప్పండి.
సంక్షిప్తంగా మరియు ప్రొఫెషనల్‌గా ఉండండి.""",
    
    'bn': """আপনি একজন পেশাদার সম্পদ ব্যবস্থাপনা বিশেষজ্ঞ। প্রদত্ত প্রসঙ্গের উপর ভিত্তি করে উত্তর দিন।
যদি তথ্য প্রসঙ্গে না থাকে, তাহলে বলুন "উপলব্ধ ডকুমেন্টে তথ্য পাওয়া যায়নি"।
সংক্ষিপ্ত এবং পেশাদার হোন।""",
    
    'es': """Eres un experto profesional en gestión de activos. Responde basándote en el contexto proporcionado.
Si la información no está en el contexto, di "Información no encontrada en los documentos disponibles".
Sé conciso y profesional.""",
    
    'zh-cn': """您是一位专业的资产管理专家。请根据提供的上下文回答。
如果上下文中没有信息，请说"在可用文档中未找到信息"。
请保持简洁和专业。""",
    
    'ru': """Вы профессиональный эксперт по управлению активами. Отвечайте на основе предоставленного контекста.
Если информация отсутствует в контексте, скажите "Информация не найдена в доступных документах".
Будьте кратки и профессиональны."""
}

# ==================== LANGUAGE-SPECIFIC FIELD MAPPINGS ====================
# Common asset management terms in all supported languages
FIELD_TRANSLATIONS = {
    # English to other languages
    'company name': {'hi': 'कंपनी का नाम', 'te': 'కంపెనీ పేరు', 'bn': 'কোম্পানির নাম', 
                     'es': 'nombre de la empresa', 'zh-cn': '公司名称', 'ru': 'название компании'},
    
    'legal representative': {'hi': 'कानूनी प्रतिनिधि', 'te': 'చట్టపరమైన ప్రతినిధి', 
                             'bn': 'আইনি প্রতিনিধি', 'es': 'representante legal', 
                             'zh-cn': '法定代表人', 'ru': 'юридический представитель'},
    
    'registered capital': {'hi': 'पंजीकृत पूंजी', 'te': 'నమోదిత మూలధనం', 
                           'bn': 'নিবন্ধিত মূলধন', 'es': 'capital registrado',
                           'zh-cn': '注册资本', 'ru': 'уставный капитал'},
    
    'shareholder': {'hi': 'शेयरधारक', 'te': 'వాటాదారు', 'bn': 'শেয়ারহোল্ডার',
                    'es': 'accionista', 'zh-cn': '股东', 'ru': 'акционер'},
    
    'fund': {'hi': 'फंड', 'te': 'ఫండ్', 'bn': 'তহবিল',
             'es': 'fondo', 'zh-cn': '基金', 'ru': 'фонд'},
    
    'investment': {'hi': 'निवेश', 'te': 'పెట్టుబడి', 'bn': 'বিনিয়োগ',
                   'es': 'inversión', 'zh-cn': '投资', 'ru': 'инвестиция'},
    
    'performance': {'hi': 'प्रदर्शन', 'te': 'పనితీరు', 'bn': 'কর্মক্ষমতা',
                    'es': 'rendimiento', 'zh-cn': '业绩', 'ru': 'производительность'},
    
    'risk': {'hi': 'जोखिम', 'te': 'రిస్క్', 'bn': 'ঝুঁকি',
             'es': 'riesgo', 'zh-cn': '风险', 'ru': 'риск'},
}

# ==================== DATABASE PATHS ====================
DB_DIRECTORY = "./chroma_db_multilang"
COLLECTION_NAME = "asset_management_multilang"
TRAINING_DATA_DIR = "training_data"
INPUT_DOC_PATH = "questions_input.docx"
OUTPUT_DOC_PATH = "answers_output.docx"
LOGS_DIR = "logs"
EXPORTS_DIR = "exports"
ANALYTICS_DIR = "analytics"
TRANSLATION_CACHE_DIR = "translation_cache"

# Create directories
for dir_path in [TRAINING_DATA_DIR, LOGS_DIR, EXPORTS_DIR, ANALYTICS_DIR, TRANSLATION_CACHE_DIR]:
    Path(dir_path).mkdir(exist_ok=True)

# ==================== RETRIEVAL SETTINGS ====================
RETRIEVER_SEARCH_K = 8
RETRIEVER_FETCH_K = 20
CHUNK_SIZE = 800
CHUNK_OVERLAP = 200

# ==================== ENHANCED FEATURE FLAGS ====================
ENABLE_CONVERSATION_MEMORY = True
ENABLE_CONFIDENCE_SCORING = True
ENABLE_MULTI_LANGUAGE = True
ENABLE_TRANSLATION = True
ENABLE_WEB_INTERFACE = True
ENABLE_EMAIL = False
ENABLE_ANALYTICS = True
ENABLE_TRANSLATION_CACHE = True

# ==================== EMBEDDINGS SETTINGS ====================
# Use HuggingFace embeddings (completely free!)
USE_HUGGINGFACE_EMBEDDINGS = True  # Set to True to use free embeddings
HUGGINGFACE_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"