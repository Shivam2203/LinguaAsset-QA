"""
Multi-Language Web Interface - Streamlit UI with language selection
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 🔥 IMPORTANT: Load .env FIRST before any other imports that need API key
from dotenv import load_dotenv
load_dotenv()  # This loads the .env file

# Verify API key is loaded (optional debug)
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    st.error("❌ GOOGLE_API_KEY not found in .env file!")
    st.info(f"Current directory: {os.getcwd()}")
    st.stop()
else:
    # Show success (you can comment this out later)
    st.sidebar.success(f"✅ API key loaded: {api_key[:10]}...")

# Now import your modules
import config
from qa_engine import get_qa_engine, answer_question
from language_handler import language_processor

logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Multi-Language Asset Management Q&A",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for RTL support
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #2563EB;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    .language-badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        background-color: #E5E7EB;
        border-radius: 0.25rem;
        font-size: 0.875rem;
        margin-right: 0.5rem;
    }
    .rtl-text {
        direction: rtl;
        text-align: right;
        font-family: 'Arial', sans-serif;
    }
    /* Language-specific fonts */
    .lang-hi { font-family: 'Nirmala UI', 'Arial', sans-serif; }
    .lang-te { font-family: 'Gautami', 'Nirmala UI', sans-serif; }
    .lang-bn { font-family: 'Vrinda', 'Nirmala UI', sans-serif; }
    .lang-zh { font-family: 'Microsoft YaHei', 'SimSun', sans-serif; }
    .lang-ru { font-family: 'Arial', 'Helvetica', sans-serif; }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state"""
    if 'qa_engine' not in st.session_state:
        st.session_state.qa_engine = get_qa_engine()
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'selected_language' not in st.session_state:
        st.session_state.selected_language = 'en'
    
    if 'translation_enabled' not in st.session_state:
        st.session_state.translation_enabled = True


def get_language_selector():
    """Create language selector sidebar"""
    st.sidebar.markdown("### 🌐 Language / भाषा / భాష / ভাষা / Idioma / 语言 / Язык")
    
    # Create language selection grid
    cols = st.sidebar.columns(2)
    
    lang_options = {
        'en': '🇬🇧 English',
        'hi': '🇮🇳 हिन्दी (Hindi)',
        'te': '🇮🇳 తెలుగు (Telugu)',
        'bn': '🇮🇳 বাংলা (Bengali)',
        'es': '🇪🇸 Español',
        'zh-cn': '🇨🇳 中文 (Chinese)',
        'ru': '🇷🇺 Русский (Russian)'
    }
    
    for i, (code, name) in enumerate(lang_options.items()):
        with cols[i % 2]:
            if st.button(
                name,
                use_container_width=True,
                type="primary" if st.session_state.selected_language == code else "secondary"
            ):
                st.session_state.selected_language = code
                st.rerun()
    
    st.sidebar.markdown("---")
    
    # Translation toggle
    st.session_state.translation_enabled = st.sidebar.toggle(
        "Enable Translation",
        value=st.session_state.translation_enabled,
        help="Automatically translate responses to selected language"
    )
    
    # Show current language
    current_lang_name = config.SUPPORTED_LANGUAGES[st.session_state.selected_language]
    st.sidebar.info(f"Current: {current_lang_name}")


def display_message(message, lang_code):
    """Display message with proper language formatting"""
    role = message["role"]
    content = message["content"]
    
    # Add language-specific class
    lang_class = f"lang-{lang_code.split('-')[0]}"
    
    with st.chat_message(role):
        if lang_code != 'en' and lang_code in ['hi', 'te', 'bn', 'zh-cn', 'ru']:
            # Apply RTL/LTR based on language
            if lang_code in ['hi', 'te', 'bn']:  # Indic scripts - LTR
                st.markdown(f'<div class="{lang_class}">{content}</div>', unsafe_allow_html=True)
            elif lang_code == 'zh-cn':  # Chinese - LTR
                st.markdown(f'<div class="{lang_class}">{content}</div>', unsafe_allow_html=True)
            elif lang_code == 'ru':  # Russian - LTR
                st.markdown(f'<div class="{lang_class}">{content}</div>', unsafe_allow_html=True)
            else:
                st.markdown(content)
        else:
            st.markdown(content)
        
        # Show language badge
        if message.get("language") and message["language"] != st.session_state.selected_language:
            st.caption(f"🌐 {config.SUPPORTED_LANGUAGES[message['language']]}")


def qa_interface():
    """Main Q&A interface with multi-language support"""
    st.markdown('<p class="sub-header">💬 Ask in Any Language</p>', unsafe_allow_html=True)
    
    # Language selector in main area
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown(f"**Current Language:** {config.SUPPORTED_LANGUAGES[st.session_state.selected_language]}")
    
    # Display chat history with proper language formatting
    for message in st.session_state.messages:
        display_message(message, message.get("language", "en"))
    
    # Language-specific input placeholder
    placeholders = {
        'en': "Ask a question about your assets...",
        'hi': "अपनी संपत्तियों के बारे में प्रश्न पूछें...",
        'te': "మీ ఆస్తుల గురించి ప్రశ్న అడగండి...",
        'bn': "আপনার সম্পদ সম্পর্কে প্রশ্ন জিজ্ঞাসা করুন...",
        'es': "Haga una pregunta sobre sus activos...",
        'zh-cn': "询问关于您的资产的问题...",
        'ru': "Задайте вопрос о своих активах..."
    }
    
    placeholder = placeholders.get(st.session_state.selected_language, placeholders['en'])
    
    # Chat input
    if prompt := st.chat_input(placeholder):
        # Add user message
        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
            "language": st.session_state.selected_language
        })
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get response
        with st.chat_message("assistant"):
            with st.spinner("Thinking... / सोच रहा हूँ... / ఆలోచిస్తున్నాను... / ভাবছি... / Pensando... / 思考中... / Думаю..."):
                # Get answer from QA engine
                result = answer_question(prompt)
                
                if result['success']:
                    # Display answer
                    if result['language'] != st.session_state.selected_language:
                        # Show both original and translated
                        st.markdown(f"**In {config.SUPPORTED_LANGUAGES[result['language']]}:**")
                        st.markdown(result['answer_original_lang'])
                        st.markdown(f"**In {config.SUPPORTED_LANGUAGES[st.session_state.selected_language]}:**")
                        st.markdown(result['answer'])
                        
                        # Add to messages
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": result['answer'],
                            "language": st.session_state.selected_language,
                            "original_language": result['language'],
                            "original_content": result['answer_original_lang']
                        })
                    else:
                        st.markdown(result['answer'])
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": result['answer'],
                            "language": result['language']
                        })
                    
                    # Show confidence
                    if result.get('confidence'):
                        confidence = result['confidence'] * 100
                        color = "🟢" if confidence >= 70 else "🟡" if confidence >= 40 else "🔴"
                        st.caption(f"{color} Confidence: {confidence:.1f}%")
                    
                    # Show sources
                    if result.get('sources'):
                        with st.expander("📚 Sources / स्रोत / మూలాలు / উৎস / Fuentes / 来源 / Источники"):
                            for source in result['sources']:
                                lang_name = config.SUPPORTED_LANGUAGES.get(
                                    source.get('language', 'en'), 
                                    'Unknown'
                                )
                                st.write(f"• {source['file']} ({lang_name})")
                                if source.get('sheet'):
                                    st.write(f"  Sheet: {source['sheet']}")
                else:
                    st.error(f"Error: {result.get('error', 'Unknown error')}")


def document_translation_interface():
    """Interface for translating documents"""
    st.markdown('<p class="sub-header">📄 Document Translation</p>', unsafe_allow_html=True)
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Upload a document to translate",
        type=['txt', 'docx', 'pdf'],
        help="Upload a document to translate to your selected language"
    )
    
    if uploaded_file:
        st.info(f"File uploaded: {uploaded_file.name}")
        
        # Detect language
        content_sample = "Sample text"  # In real implementation, read file
        detected_lang, confidence = language_processor.detector.detect_language(content_sample)
        
        st.write(f"**Detected Language:** {config.SUPPORTED_LANGUAGES.get(detected_lang, 'Unknown')}")
        st.write(f"**Confidence:** {confidence:.1%}")
        
        # Translation options
        target_lang = st.session_state.selected_language
        
        if st.button("🔄 Translate Document", type="primary"):
            with st.spinner("Translating..."):
                st.success("Translation complete! (Demo - implement actual file translation)")
                # In real implementation: translate and offer download


def language_stats_interface():
    """Show language statistics"""
    st.markdown('<p class="sub-header">📊 Language Statistics</p>', unsafe_allow_html=True)
    
    # Get QA engine
    engine = st.session_state.qa_engine
    
    # Get conversation history by language
    history = engine.get_conversation_history()
    
    if history:
        # Count by language
        lang_counts = {}
        for item in history:
            lang = item.get('language', 'en')
            lang_counts[lang] = lang_counts.get(lang, 0) + 1
        
        # Create dataframe
        df = pd.DataFrame([
            {"Language": config.SUPPORTED_LANGUAGES.get(lang, lang), "Questions": count}
            for lang, count in lang_counts.items()
        ])
        
        # Show chart
        fig = px.pie(df, values='Questions', names='Language', 
                     title="Questions by Language")
        st.plotly_chart(fig, use_container_width=True)
        
        # Show table
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No conversation history yet. Ask some questions in different languages!")


def settings_interface():
    """Settings interface"""
    st.markdown('<p class="sub-header">⚙️ Settings</p>', unsafe_allow_html=True)
    
    # Language settings
    st.markdown("### 🌐 Language Settings")
    
    # Default language
    default_lang = st.selectbox(
        "Default Language",
        options=list(config.SUPPORTED_LANGUAGES.keys()),
        format_func=lambda x: config.SUPPORTED_LANGUAGES[x],
        index=list(config.SUPPORTED_LANGUAGES.keys()).index(st.session_state.selected_language)
    )
    
    if default_lang != st.session_state.selected_language:
        st.session_state.selected_language = default_lang
        st.rerun()
    
    # Translation settings
    st.markdown("### 🔄 Translation Settings")
    
    enable_translation = st.toggle(
        "Enable Translation",
        value=st.session_state.translation_enabled
    )
    
    if enable_translation != st.session_state.translation_enabled:
        st.session_state.translation_enabled = enable_translation
        st.rerun()
    
    # Cache settings
    st.markdown("### 💾 Cache Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Clear Translation Cache"):
            from translation_cache import TranslationCache
            cache = TranslationCache()
            cache.clear()
            st.success("Translation cache cleared!")
    
    with col2:
        if st.button("Clear Conversation"):
            engine = st.session_state.qa_engine
            engine.clear_conversation()
            st.session_state.messages = []
            st.success("Conversation cleared!")
            st.rerun()


def main():
    """Main web interface"""
    init_session_state()
    
    # Sidebar with language selector
    with st.sidebar:
        st.markdown('<p class="main-header" style="font-size: 1.5rem;">🌐 Multi-Language Asset Q&A</p>', 
                   unsafe_allow_html=True)
        
        get_language_selector()
        
        st.markdown("---")
        
        # Navigation
        st.markdown("### Navigation")
        page = st.radio(
            "Go to",
            ["💬 Q&A", "📄 Translate Document", "📊 Language Stats", "⚙️ Settings"]
        )
    
    # Main content
    st.markdown('<p class="main-header">Multi-Language Asset Management Q&A System</p>', 
               unsafe_allow_html=True)
    
    # Show supported languages
    st.markdown("**Supported Languages:** " + " | ".join([
        f"🇬🇧 English", "🇮🇳 हिन्दी", "🇮🇳 తెలుగు", "🇮🇳 বাংলা", 
        "🇪🇸 Español", "🇨🇳 中文", "🇷🇺 Русский"
    ]))
    
    st.markdown("---")
    
    # Show selected page
    if "💬 Q&A" in page:
        qa_interface()
    elif "📄 Translate Document" in page:
        document_translation_interface()
    elif "📊 Language Stats" in page:
        language_stats_interface()
    elif "⚙️ Settings" in page:
        settings_interface()


if __name__ == "__main__":
    main()