"""
Data Processor - Handles document loading, chunking, and vectorization
Updated with correct LangChain imports and CSV support
"""

import os
import pandas as pd
import json
import time
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Generator
import logging

# Updated imports for newer LangChain versions
from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from unstructured.partition.docx import partition_docx
from tqdm import tqdm

import config

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Enhanced document processor with progress tracking and validation"""
    
    def __init__(self):
        self.stats = {
            'total_files': 0,
            'processed_files': 0,
            'failed_files': 0,
            'total_chunks': 0,
            'skipped_chunks': 0,
            'processing_time': 0
        }
        
        # Initialize embeddings model (using free HuggingFace)
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
    
    def test_connection(self) -> bool:
        """Test if embeddings are working"""
        try:
            logger.info("Testing embeddings...")
            result = self.embeddings.embed_query("test connection")
            logger.info("✅ Embeddings working")
            return True
        except Exception as e:
            logger.error(f"❌ Embeddings failed: {e}")
            return False
    
    def process_csv_file(self, file_path: Path) -> List[Document]:
        """
        Process CSV file and convert to documents
        
        Args:
            file_path: Path to CSV file
        
        Returns:
            List of Document objects
        """
        documents = []
        file_name = file_path.name
        
        try:
            # Read CSV file
            df = pd.read_csv(file_path)
            
            if df.empty:
                logger.warning(f"  CSV file {file_name} is empty")
                return documents
            
            logger.info(f"  Processing CSV: {len(df)} rows, {len(df.columns)} columns")
            
            # Create summary document
            summary = f"""Source: {file_name}
Total rows: {len(df)}
Total columns: {len(df.columns)}
Columns: {', '.join(df.columns.tolist()[:10])}"""
            
            doc = Document(
                page_content=summary,
                metadata={
                    "source": file_name,
                    "type": "csv_summary",
                    "rows": len(df),
                    "columns": len(df.columns)
                }
            )
            documents.append(doc)
            
            # Process rows (limit to MAX_EXCEL_ROWS)
            rows_processed = 0
            for idx, row in df.head(config.MAX_EXCEL_ROWS).iterrows():
                row_items = []
                for col, value in row.items():
                    if pd.notna(value) and str(value).strip():
                        value_str = str(value)[:100]
                        row_items.append(f"{col}: {value_str}")
                
                if row_items:
                    row_text = f"Row {idx+1}: " + ", ".join(row_items[:10])
                    
                    doc = Document(
                        page_content=row_text,
                        metadata={
                            "source": file_name,
                            "type": "csv_row",
                            "row": int(idx)
                        }
                    )
                    documents.append(doc)
                    rows_processed += 1
            
            logger.info(f"  ✅ Processed {rows_processed} rows from {file_name}")
            return documents
            
        except Exception as e:
            logger.error(f"Error processing CSV file {file_name}: {e}")
            return documents
    
    def process_excel_file(self, file_path: Path) -> List[Document]:
        """
        Process Excel file and convert to documents
        
        Args:
            file_path: Path to Excel file
        
        Returns:
            List of Document objects
        """
        documents = []
        file_name = file_path.name
        
        try:
            excel_file = pd.ExcelFile(file_path)
            sheet_names = excel_file.sheet_names[:config.MAX_EXCEL_SHEETS]
            
            logger.info(f"  Processing {len(sheet_names)} sheets from {file_name}")
            
            for sheet_name in sheet_names:
                try:
                    df = pd.read_excel(file_path, sheet_name=sheet_name)
                    
                    if df.empty:
                        logger.debug(f"  Sheet {sheet_name} is empty, skipping")
                        continue
                    
                    # Convert datetime columns
                    for col in df.columns:
                        if df[col].dtype in ['datetime64[ns]', 'object']:
                            if df[col].apply(lambda x: isinstance(x, (datetime, pd.Timestamp))).any():
                                df[col] = df[col].apply(
                                    lambda x: x.isoformat() if isinstance(x, (datetime, pd.Timestamp)) else x
                                )
                    
                    # Create table summary
                    summary = f"""Source: {file_name}
Sheet: {sheet_name}
Total rows: {len(df)}
Total columns: {len(df.columns)}
Columns: {', '.join(df.columns.tolist()[:10])}"""
                    
                    doc = Document(
                        page_content=summary,
                        metadata={
                            "source": file_name,
                            "sheet": sheet_name,
                            "type": "excel_summary",
                            "rows": len(df),
                            "columns": len(df.columns)
                        }
                    )
                    documents.append(doc)
                    
                    # Process rows
                    rows_processed = 0
                    for idx, row in df.head(config.MAX_EXCEL_ROWS).iterrows():
                        row_items = []
                        for col, value in row.items():
                            if pd.notna(value) and str(value).strip():
                                value_str = str(value)[:100]
                                row_items.append(f"{col}: {value_str}")
                        
                        if row_items:
                            row_text = f"Sheet[{sheet_name}] Row {idx+1}: " + ", ".join(row_items[:10])
                            
                            doc = Document(
                                page_content=row_text,
                                metadata={
                                    "source": file_name,
                                    "sheet": sheet_name,
                                    "type": "excel_row",
                                    "row": int(idx)
                                }
                            )
                            documents.append(doc)
                            rows_processed += 1
                    
                    logger.info(f"    Sheet {sheet_name}: {rows_processed} rows processed")
                    
                except Exception as e:
                    logger.error(f"    Error processing sheet {sheet_name}: {e}")
                    continue
                
                # Small delay to avoid overwhelming
                time.sleep(0.1)
            
        except Exception as e:
            logger.error(f"Error processing Excel file {file_name}: {e}")
        
        return documents
    
    def process_word_file(self, file_path: Path) -> List[Document]:
        """
        Process Word file and convert to documents
        
        Args:
            file_path: Path to Word file
        
        Returns:
            List of Document objects
        """
        documents = []
        file_name = file_path.name
        
        try:
            logger.info(f"  Processing Word file: {file_name}")
            
            # Use unstructured for better parsing
            elements = partition_docx(filename=str(file_path), strategy="auto")
            
            # Extract text from elements
            full_text = []
            
            for element in elements:
                text = str(element).strip()
                if not text or len(text) < config.MIN_TEXT_LENGTH:
                    continue
                
                full_text.append(text)
            
            if not full_text:
                logger.warning(f"  No text extracted from {file_name}")
                return documents
            
            # Combine all text
            combined_text = "\n\n".join(full_text)
            
            # Split into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=config.TEXT_CHUNK_SIZE,
                chunk_overlap=config.TEXT_CHUNK_OVERLAP,
                separators=config.TEXT_SEPARATORS,
                length_function=len
            )
            
            chunks = text_splitter.create_documents([combined_text[:config.MAX_TEXT_LENGTH]])
            
            # Add metadata to chunks
            for i, chunk in enumerate(chunks[:config.MAX_CHUNK_COUNT]):
                chunk.metadata = {
                    "source": file_name,
                    "type": "word_chunk",
                    "chunk": i,
                    "total_chunks": min(len(chunks), config.MAX_CHUNK_COUNT)
                }
                documents.append(chunk)
            
            logger.info(f"  Created {len(documents)} chunks from {file_name}")
            
        except Exception as e:
            logger.error(f"Error processing Word file {file_name}: {e}")
        
        return documents
    
    def process_file(self, file_path: Path) -> List[Document]:
        """
        Process a single file based on its extension
        
        Args:
            file_path: Path to file
        
        Returns:
            List of Document objects
        """
        self.stats['total_files'] += 1
        
        ext = file_path.suffix.lower()
        
        try:
            if ext in ['.xlsx', '.xls']:
                docs = self.process_excel_file(file_path)
            elif ext == '.docx':
                docs = self.process_word_file(file_path)
            elif ext == '.csv':  # Added CSV support
                docs = self.process_csv_file(file_path)
            else:
                logger.warning(f"Unsupported file type: {ext}")
                return []
            
            self.stats['processed_files'] += 1
            self.stats['total_chunks'] += len(docs)
            
            return docs
            
        except Exception as e:
            logger.error(f"Failed to process {file_path.name}: {e}")
            self.stats['failed_files'] += 1
            return []
    
    def validate_document(self, doc: Document) -> bool:
        """
        Validate document before storing
        
        Args:
            doc: Document to validate
        
        Returns:
            True if valid, False otherwise
        """
        content = doc.page_content.strip()
        
        # Check length
        if len(content) < config.MIN_CONTENT_LENGTH:
            self.stats['skipped_chunks'] += 1
            return False
        
        if len(content) > config.MAX_CONTENT_LENGTH:
            # Truncate instead of skip
            doc.page_content = content[:config.MAX_CONTENT_LENGTH]
        
        # Check for garbage content (too many special characters)
        special_chars = sum(not c.isalnum() and not c.isspace() for c in content)
        if special_chars > len(content) * 0.3:  # More than 30% special chars
            self.stats['skipped_chunks'] += 1
            return False
        
        return True
    
    def store_documents(self, documents: List[Document]) -> int:
        """
        Store documents in vector database with batching
        
        Args:
            documents: List of documents to store
        
        Returns:
            Number of successfully stored documents
        """
        if not documents:
            return 0
        
        try:
            # Initialize vector database
            vector_db = Chroma(
                persist_directory=config.DB_DIRECTORY,
                embedding_function=self.embeddings,
                collection_name=config.COLLECTION_NAME
            )
            
            # Store in batches
            success_count = 0
            batch_size = config.BATCH_SIZE
            
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i+batch_size]
                
                try:
                    # Add batch to database
                    vector_db.add_documents(batch)
                    success_count += len(batch)
                    
                    logger.debug(f"  Stored batch {i//batch_size + 1}: {len(batch)} documents")
                    
                    # Small delay between batches
                    time.sleep(config.BATCH_DELAY)
                    
                except Exception as e:
                    logger.error(f"  Batch storage failed: {e}")
                    
                    # Try individual storage
                    for doc in batch:
                        try:
                            vector_db.add_documents([doc])
                            success_count += 1
                            time.sleep(config.SINGLE_DOC_DELAY)
                        except Exception as e2:
                            logger.error(f"    Individual document storage failed: {e2}")
            
            return success_count
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            return 0
    
    def process_all_files(self) -> Dict[str, Any]:
        """
        Process all files in training data directory
        
        Returns:
            Statistics dictionary
        """
        start_time = time.time()
        
        # Reset stats
        self.stats = {
            'total_files': 0,
            'processed_files': 0,
            'failed_files': 0,
            'total_chunks': 0,
            'skipped_chunks': 0,
            'processing_time': 0
        }
        
        # Find all supported files - INCLUDING CSV!
        data_files = []
        for ext in ['.xlsx', '.xls', '.docx', '.csv']:  # Added .csv
            data_files.extend(Path(config.TRAINING_DATA_DIR).glob(f"*{ext}"))
        
        # Filter temporary files
        data_files = [f for f in data_files if not f.name.startswith('~$')]
        
        if not data_files:
            logger.warning("No files found to process")
            return self.stats
        
        logger.info(f"Found {len(data_files)} files to process")
        
        # Process each file
        all_documents = []
        
        for file_path in tqdm(data_files, desc="Processing files"):
            logger.info(f"\n📄 Processing: {file_path.name}")
            
            docs = self.process_file(file_path)
            
            # Validate documents
            valid_docs = [doc for doc in docs if self.validate_document(doc)]
            
            if len(valid_docs) < len(docs):
                logger.info(f"  Filtered {len(docs) - len(valid_docs)} invalid documents")
            
            all_documents.extend(valid_docs)
            
            # Small delay between files
            time.sleep(1)
        
        if not all_documents:
            logger.warning("No valid documents to store")
            return self.stats
        
        logger.info(f"\n💾 Storing {len(all_documents)} documents in vector database...")
        
        # Store documents
        stored = self.store_documents(all_documents)
        
        # Update stats
        self.stats['processing_time'] = time.time() - start_time
        
        logger.info(f"\n✅ Processing complete!")
        logger.info(f"   Files processed: {self.stats['processed_files']}/{self.stats['total_files']}")
        logger.info(f"   Documents stored: {stored}")
        logger.info(f"   Time taken: {self.stats['processing_time']:.2f}s")
        
        return self.stats


def process_training_data() -> bool:
    """
    Main function to process all training data
    
    Returns:
        True if successful, False otherwise
    """
    processor = DocumentProcessor()
    
    # Test connection first
    if not processor.test_connection():
        logger.error("Embeddings test failed")
        return False
    
    # Process files
    stats = processor.process_all_files()
    
    return stats['processed_files'] > 0


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    success = process_training_data()
    print(f"\nProcessing {'successful' if success else 'failed'}")