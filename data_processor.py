"""
Multi-Language Data Processor - Handles documents in multiple languages
"""

import os
import pandas as pd
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from unstructured.partition.docx import partition_docx

import config
from language_handler import language_processor

logger = logging.getLogger(__name__)


class MultiLangDocumentProcessor:
    """Process documents in multiple languages"""
    
    def __init__(self):
        self.stats = {
            'total_files': 0,
            'processed_files': 0,
            'failed_files': 0,
            'total_chunks': 0,
            'languages_detected': {}
        }
    
    def detect_document_language(self, text: str) -> str:
        """Detect language of document content"""
        if not text or len(text) < 50:
            return 'unknown'
        
        # Sample first 1000 characters
        sample = text[:1000]
        lang, confidence = language_processor.detector.detect_language(sample)
        
        if confidence >= 0.5:
            return lang
        return 'unknown'
    
    def process_excel_file(self, file_path: Path) -> List[Document]:
        """Process Excel file with language detection"""
        documents = []
        file_name = file_path.name
        
        try:
            excel_file = pd.ExcelFile(file_path)
            sheet_names = excel_file.sheet_names[:config.MAX_EXCEL_SHEETS]
            
            for sheet_name in sheet_names:
                try:
                    df = pd.read_excel(file_path, sheet_name=sheet_name)
                    
                    if df.empty:
                        continue
                    
                    # Convert dataframe to text for language detection
                    sample_text = " ".join(df.iloc[0].astype(str).tolist())
                    doc_lang = self.detect_document_language(sample_text)
                    
                    # Update language stats
                    self.stats['languages_detected'][doc_lang] = \
                        self.stats['languages_detected'].get(doc_lang, 0) + 1
                    
                    # Create document with language metadata
                    doc = Document(
                        page_content=f"Excel File: {file_name}\nSheet: {sheet_name}\n"
                                   f"Rows: {len(df)}\nColumns: {len(df.columns)}",
                        metadata={
                            "source": file_name,
                            "sheet": sheet_name,
                            "type": "excel",
                            "language": doc_lang,
                            "rows": len(df),
                            "columns": len(df.columns)
                        }
                    )
                    documents.append(doc)
                    
                    # Process rows
                    for idx, row in df.head(config.MAX_EXCEL_ROWS).iterrows():
                        row_text = f"Sheet[{sheet_name}] Row {idx+1}: "
                        row_items = []
                        
                        for col, value in row.items():
                            if pd.notna(value) and str(value).strip():
                                row_items.append(f"{col}: {value}")
                        
                        if row_items:
                            row_text += " | ".join(row_items[:10])
                            
                            doc = Document(
                                page_content=row_text,
                                metadata={
                                    "source": file_name,
                                    "sheet": sheet_name,
                                    "type": "excel_row",
                                    "language": doc_lang,
                                    "row": int(idx)
                                }
                            )
                            documents.append(doc)
                    
                except Exception as e:
                    logger.error(f"Error processing sheet {sheet_name}: {e}")
                    continue
            
            self.stats['processed_files'] += 1
            
        except Exception as e:
            logger.error(f"Error processing Excel file {file_name}: {e}")
            self.stats['failed_files'] += 1
        
        return documents
    
    def process_word_file(self, file_path: Path) -> List[Document]:
        """Process Word file with language detection"""
        documents = []
        file_name = file_path.name
        
        try:
            # Extract text
            elements = partition_docx(filename=str(file_path), strategy="auto")
            
            # Combine text for language detection
            full_text = "\n".join([str(el) for el in elements if str(el).strip()])
            
            if not full_text:
                return documents
            
            # Detect document language
            doc_lang = self.detect_document_language(full_text)
            
            # Update stats
            self.stats['languages_detected'][doc_lang] = \
                self.stats['languages_detected'].get(doc_lang, 0) + 1
            
            # Split into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=config.TEXT_CHUNK_SIZE,
                chunk_overlap=config.TEXT_CHUNK_OVERLAP,
                separators=config.TEXT_SEPARATORS
            )
            
            chunks = text_splitter.create_documents([full_text])
            
            # Add metadata
            for i, chunk in enumerate(chunks):
                chunk.metadata = {
                    "source": file_name,
                    "type": "word_chunk",
                    "language": doc_lang,
                    "chunk": i,
                    "total_chunks": len(chunks)
                }
                documents.append(chunk)
            
            self.stats['processed_files'] += 1
            logger.info(f"Processed {file_name}: {len(chunks)} chunks, language: {doc_lang}")
            
        except Exception as e:
            logger.error(f"Error processing Word file {file_name}: {e}")
            self.stats['failed_files'] += 1
        
        return documents
    
    def process_all_files(self) -> Dict[str, Any]:
        """Process all files in training directory"""
        self.stats = {
            'total_files': 0,
            'processed_files': 0,
            'failed_files': 0,
            'total_chunks': 0,
            'languages_detected': {}
        }
        
        # Find all files
        data_files = []
        for ext in ['.xlsx', '.xls', '.docx']:
            data_files.extend(Path(config.TRAINING_DATA_DIR).glob(f"*{ext}"))
        
        data_files = [f for f in data_files if not f.name.startswith('~$')]
        self.stats['total_files'] = len(data_files)
        
        if not data_files:
            logger.warning("No files found to process")
            return self.stats
        
        logger.info(f"Found {len(data_files)} files to process")
        
        all_documents = []
        
        for file_path in data_files:
            logger.info(f"Processing: {file_path.name}")
            
            if file_path.suffix.lower() in ['.xlsx', '.xls']:
                docs = self.process_excel_file(file_path)
            elif file_path.suffix.lower() == '.docx':
                docs = self.process_word_file(file_path)
            else:
                continue
            
            all_documents.extend(docs)
            self.stats['total_chunks'] += len(docs)
        
        # Store in vector database
        if all_documents:
            self._store_documents(all_documents)
        
        # Print language statistics
        logger.info("\n📊 Language Distribution:")
        for lang, count in self.stats['languages_detected'].items():
            lang_name = language_processor.detector.get_language_name(lang)
            logger.info(f"  {lang_name}: {count} files")
        
        return self.stats
    
    def _store_documents(self, documents: List[Document]):
        """Store documents in vector database"""
        from langchain_community.embeddings import DashScopeEmbeddings
        from langchain_chroma import Chroma
        
        api_key = os.getenv(config.API_KEY_NAME)
        embeddings = DashScopeEmbeddings(
            model=config.EMBEDDING_MODEL_NAME,
            dashscope_api_key=api_key
        )
        
        vector_db = Chroma(
            persist_directory=config.DB_DIRECTORY,
            embedding_function=embeddings,
            collection_name=config.COLLECTION_NAME
        )
        
        # Store in batches
        batch_size = config.BATCH_SIZE
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i+batch_size]
            vector_db.add_documents(batch)
            logger.info(f"Stored batch {i//batch_size + 1}: {len(batch)} documents")


# Convenience function
def process_training_data() -> bool:
    """Process all training data"""
    processor = MultiLangDocumentProcessor()
    stats = processor.process_all_files()
    return stats['processed_files'] > 0