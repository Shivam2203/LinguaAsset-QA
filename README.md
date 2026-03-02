<div align="center">
  <h1>🌐 LinguaAsset-QA</h1>
  <h3>Multi-Language AI-Powered Asset Management Intelligence</h3>
  <p><i>Supporting English, Hindi, Telugu, Bengali, Spanish, Chinese & Russian</i></p>
  
  <div>
    <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python" alt="Python">
    <img src="https://img.shields.io/badge/Google%20Gemini-2.5%20Flash-green?style=for-the-badge&logo=google" alt="Gemini">
    <img src="https://img.shields.io/badge/Streamlit-1.28-red?style=for-the-badge&logo=streamlit" alt="Streamlit">
    <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" alt="License">
  </div>
  
  <div>
    <img src="https://img.shields.io/github/stars/Shivam2203/LinguaAsset-QA?style=social" alt="Stars">
    <img src="https://img.shields.io/github/forks/Shivam2203/LinguaAsset-QA?style=social" alt="Forks">
    <img src="https://img.shields.io/github/issues/Shivam2203/LinguaAsset-QA?style=social" alt="Issues">
  </div>
  
  <br>
  <img src="https://via.placeholder.com/800x400.png?text=LinguaAsset-QA+Dashboard+Preview" alt="Dashboard Preview" width="80%">
  <br>
  <br>
</div>

---

## 📋 **Table of Contents**
- [About The Project](#-about-the-project)
- [Key Features](#-key-features)
- [Tech Stack](#-tech-stack)
- [Live Demo](#-live-demo)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
- [Usage Guide](#-usage-guide)
  - [Command Line Interface](#command-line-interface)
  - [Web Interface](#web-interface)
  - [Sample Queries](#sample-queries)
- [Project Structure](#-project-structure)
- [How It Works](#-how-it-works)
- [Multi-Language Support](#-multi-language-support)
- [Deployment](#-deployment)
- [Contributing](#-contributing)
- [License](#-license)
- [Contact](#-contact)
- [FAQ](#-faq)
- [Star History](#-star-history)

---

## 🎯 **About The Project**

**LinguaAsset-QA** is a cutting-edge, production-ready intelligent Q&A system designed specifically for **asset management professionals, financial analysts, and investment firms**. It enables users to query asset management documents in **7 languages** and receive accurate, context-aware responses in real-time.

This system solves the critical problem of manual document searching across multilingual datasets, reducing research time from hours to seconds. Whether you're dealing with due diligence questionnaires, regulatory filings, or internal reports in different languages, LinguaAsset-QA provides instant answers.

---

## ✨ **Key Features**

| Feature | Description |
|---------|-------------|
| 🌍 **7 Languages Support** | English, Hindi, Telugu, Bengali, Spanish, Chinese, Russian |
| 🤖 **Google Gemini 2.5 Flash** | Free tier, no credit card required, 20 requests/day |
| 🔍 **Semantic Vector Search** | ChromaDB with HuggingFace embeddings for accurate retrieval |
| 📊 **Multi-Format Document Processing** | CSV, Excel, Word document ingestion |
| 💬 **Dual Interface** | CLI for power users, Web UI for everyone |
| 🔄 **Auto Language Detection** | Automatically detects and responds in query language |
| 🗃️ **Persistent Knowledge Base** | Vector database for fast, scalable retrieval |
| 📈 **Analytics Dashboard** | Track usage, languages, and performance metrics |
| 🔒 **Privacy First** | All processing local, your data never leaves your control |
| 🚀 **Production Ready** | Scalable architecture, easy deployment |

---

## 🛠️ **Tech Stack**

<div align="center">
  
| Layer | Technology |
|-------|------------|
| **Frontend** | Streamlit, Plotly, HTML/CSS |
| **Backend** | Python, LangChain |
| **AI/ML** | Google Gemini 2.5 Flash, Sentence Transformers |
| **Database** | ChromaDB (Vector Database) |
| **Language Processing** | LangDetect, GoogleTrans |
| **Deployment** | Streamlit Cloud, Docker, Azure/AWS |

</div>

---

## 🌐 **Live Demo**

Experience LinguaAsset-QA live without installation:

🔗 **https://linguaasset-qa.streamlit.app** (Coming Soon)

<div align="center">
  <img src="https://via.placeholder.com/600x300.png?text=Live+Demo+Preview" alt="Live Demo" width="70%">
</div>

---

## 🚀 **Getting Started**

### Prerequisites

Before you begin, ensure you have:

- ✅ **Python 3.10 or higher** installed
- ✅ **Google Gemini API key** (free from [Google AI Studio](https://aistudio.google.com))
- ✅ **Git** installed (for cloning)
- ✅ **8GB RAM minimum** (16GB recommended)
- ✅ **Windows/Mac/Linux** (cross-platform compatible)

### Installation

Follow these steps to get your local instance running:

```bash
# 1. Clone the repository
git clone https://github.com/Shivam2203/LinguaAsset-QA.git
cd LinguaAsset-QA

# 2. Create virtual environment (recommended)
# Windows:
python -m venv venv
venv\Scripts\activate

# Mac/Linux:
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4. Set up environment variables
# Create .env file and add your API key
echo "GOOGLE_API_KEY=your-gemini-api-key-here" > .env

# 5. Add your training data
# Place your CSV/Excel/Word files in the 'training_data' folder
# Sample files are provided to get started

# 6. Process your data (creates vector database)
python run_multilang.py --process

# 7. Launch the system
# For CLI interface:
python run_multilang.py --mode cli

# For Web interface:
streamlit run web_interface.py
