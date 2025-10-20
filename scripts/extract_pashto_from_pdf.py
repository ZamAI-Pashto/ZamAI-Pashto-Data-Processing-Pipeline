#!/usr/bin/env python3
"""
Pashto PDF Text Extractor

This script extracts text from PDF files containing Pashto content, cleans it,
and saves it in formats suitable for model fine-tuning.
"""

import os
import glob
import re
import argparse
import pandas as pd
import numpy as np
import json
from tqdm import tqdm
import logging
from datetime import datetime
import concurrent.futures
import sys
import shutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pdf_extraction.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Try to import PDF extraction libraries with robust fallbacks
try:
    import pdfplumber  # Primary PDF extraction tool
    PDF_EXTRACTOR = "pdfplumber"
except ImportError:
    try:
        from pdfminer.high_level import extract_text
        PDF_EXTRACTOR = "pdfminer"
    except ImportError:
        try:
            import PyPDF2
            PDF_EXTRACTOR = "pypdf2"
        except ImportError:
            try:
                import fitz  # PyMuPDF
                PDF_EXTRACTOR = "pymupdf"
            except ImportError:
                logger.error("No PDF extraction library found. Please install one of: pdfplumber, pdfminer.six, PyPDF2, or PyMuPDF (fitz)")
                sys.exit(1)

# Try to import OCR libraries (optional, for scanned PDFs)
try:
    import pytesseract
    from PIL import Image
    HAS_OCR = True
except ImportError:
    HAS_OCR = False
    logger.warning("OCR libraries (pytesseract, Pillow) not found. OCR functionality will be disabled.")

# Load stopwords for text cleaning
def load_stopwords():
        """Load Pashto stopwords from file"""
    stopwords_path = '/workspaces/ZamAI-Pashto-Data-Processing-Pipeline/stopwords.csv'
    
    if not os.path.exists(stopwords_path):
            stopwords = pd.read_csv(stopwords_path, header=None)[0].tolist()
            return set(stopwords)
        else:
            # If stopwords file doesn't exist, run the script to create it
            logger.info("Stopwords file not found. Creating it...")
            stopwords_script = '/workspaces/pashto-text-dataset/ZamAI_Pashto_Datasets/scripts/create_stopwords.py'
            
            if os.path.exists(stopwords_script):
                import subprocess
                subprocess.run(['python', stopwords_script])
                
                # Try loading again
                if os.path.exists(stopwords_path):
                    stopwords = pd.read_csv(stopwords_path, header=None)[0].tolist()
                    return set(stopwords)
            
            # If still not available, return minimal set
            logger.warning("Couldn't create or find stopwords file. Using minimal stopwords set.")
            return set(['د', 'په', 'او', 'چې', 'له', 'نه'])
    except Exception as e:
        logger.error(f"Error loading stopwords: {e}")
        return set(['د', 'په', 'او', 'چې', 'له', 'نه'])

# Text cleaning functions
def is_pashto_text(text):
    """Check if text contains Pashto characters."""
    # Pattern for Pashto/Arabic script characters
    pashto_pattern = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]')
    
    # Check if the text contains Pashto characters and meets minimum length
    return bool(pashto_pattern.search(text)) and len(text.strip()) > 10

def normalize_text(text):
    """Normalize and clean Pashto text."""
    if not text:
        return ""
    
    # Replace multiple spaces, newlines, tabs with single space
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters except Pashto script
    text = re.sub(r'[^\s\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]', ' ', text)
    
    # Remove extra spaces again after special character removal
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def preprocess_text(text, stopwords_set, remove_stopwords=True):
    """Preprocess text including stopword removal."""
    # First normalize
    text = normalize_text(text)
    
    # If we don't want to remove stopwords
    if not remove_stopwords:
        return text
    
    # Split words and remove stopwords
    words = text.split()
    meaningful_words = [w for w in words if w not in stopwords_set]
    
    # Join back into text
    return " ".join(meaningful_words)

# PDF text extraction functions
def extract_text_with_pdfplumber(pdf_path):
    """Extract text from PDF using pdfplumber."""
    try:
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                text += page_text + "\n\n"
        return text
    except Exception as e:
        logger.error(f"Error extracting text from {pdf_path} with pdfplumber: {e}")
        return ""

def extract_text_with_pdfminer(pdf_path):
    """Extract text from PDF using pdfminer."""
    try:
        return extract_text(pdf_path)
    except Exception as e:
        logger.error(f"Error extracting text from {pdf_path} with pdfminer: {e}")
        return ""

def extract_text_with_pypdf2(pdf_path):
    """Extract text from PDF using PyPDF2."""
    try:
        text = ""
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() or ""
                text += "\n\n"
        return text
    except Exception as e:
        logger.error(f"Error extracting text from {pdf_path} with PyPDF2: {e}")
        return ""

def extract_text_with_pymupdf(pdf_path):
    """Extract text from PDF using PyMuPDF (fitz)."""
    try:
        text = ""
        doc = fitz.open(pdf_path)
        for page in doc:
            text += page.get_text() + "\n\n"
        return text
    except Exception as e:
        logger.error(f"Error extracting text from {pdf_path} with PyMuPDF: {e}")
        return ""

def extract_text_from_pdf(pdf_path, use_ocr=False, ocr_lang='eng'):
    """Extract text from PDF using available library."""
    if PDF_EXTRACTOR == "pdfplumber":
        text = extract_text_with_pdfplumber(pdf_path)
    elif PDF_EXTRACTOR == "pdfminer":
        text = extract_text_with_pdfminer(pdf_path)
    elif PDF_EXTRACTOR == "pypdf2":
        text = extract_text_with_pypdf2(pdf_path)
    elif PDF_EXTRACTOR == "pymupdf":
        text = extract_text_with_pymupdf(pdf_path)
    else:
        logger.error("No PDF extraction method available")
        return ""
    
    # If text extraction yielded little text and OCR is available, try OCR
    if use_ocr and HAS_OCR and (not text.strip() or len(text.strip()) < 100):
        logger.info(f"Attempting OCR on {pdf_path}")
        try:
            text = perform_ocr(pdf_path, ocr_lang)
        except Exception as e:
            logger.error(f"OCR failed on {pdf_path}: {e}")
    
    return text

def perform_ocr(pdf_path, lang='eng+ara'):
    """Perform OCR on PDF using Tesseract."""
    if not HAS_OCR:
        logger.error("OCR libraries not available")
        return ""
    
    try:
        # Convert PDF to images
        doc = fitz.open(pdf_path)
        text = ""
        
        for i, page in enumerate(doc):
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            text += pytesseract.image_to_string(img, lang=lang) + "\n\n"
        
        return text
    except Exception as e:
        logger.error(f"OCR error: {e}")
        return ""

class PashtoPdfExtractor:
    """Main class for extracting Pashto text from PDFs."""
    
    def __init__(self, input_dir=None, output_dir=None, use_ocr=False, 
                 ocr_lang='eng+ara', min_length=50, extract_sections=True):
        """Initialize the PDF extractor."""
        self.input_dir = input_dir or '/workspaces/pashto-text-dataset/ZamAI_Pashto_Datasets/pdf_documents'
        self.output_dir = output_dir or '/workspaces/pashto-text-dataset/ZamAI_Pashto_Datasets/extracted_pdf_data'
        self.use_ocr = use_ocr and HAS_OCR
        self.ocr_lang = ocr_lang
        self.min_length = min_length
        self.extract_sections = extract_sections
        self.stopwords = load_stopwords()
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
        
        # PDF extraction method
        logger.info(f"Using {PDF_EXTRACTOR} for PDF text extraction")
    
    def find_pdf_files(self):
        """Find all PDF files in the input directory."""
        # Check if directory exists
        if not os.path.exists(self.input_dir):
            logger.warning(f"Input directory {self.input_dir} does not exist.")
            return []
        
        # Find all PDFs
        pdf_pattern = os.path.join(self.input_dir, "**", "*.pdf")
        pdf_files = glob.glob(pdf_pattern, recursive=True)
        
        logger.info(f"Found {len(pdf_files)} PDF files in {self.input_dir}")
        return pdf_files
    
    def extract_sections_from_text(self, text):
        """Extract sections from text based on common patterns."""
        sections = []
        
        # Pattern for potential section titles
        section_pattern = re.compile(r'\n\s*([A-Za-z\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]{2,50})\s*\n', re.MULTILINE)
        
        # Find potential section headings
        matches = list(section_pattern.finditer(text))
        
        if not matches:
            # If no sections found, return the whole text as one section
            if is_pashto_text(text):
                sections.append({"title": "", "content": text})
            return sections
        
        # Extract sections
        for i, match in enumerate(matches):
            title = match.group(1).strip()
            start_pos = match.end()
            
            # Calculate end position (start of next section or end of text)
            end_pos = matches[i+1].start() if i < len(matches)-1 else len(text)
            
            # Extract section content
            content = text[start_pos:end_pos].strip()
            
            # Only add if it contains Pashto text and meets minimum length
            if is_pashto_text(content) and len(content) >= self.min_length:
                sections.append({"title": title, "content": content})
        
        return sections
    
    def extract_text_from_pdf_file(self, pdf_file):
        """Process a single PDF file."""
        try:
            # Extract raw text
            raw_text = extract_text_from_pdf(pdf_file, self.use_ocr, self.ocr_lang)
            
            # If text is too short, skip
            if not raw_text or len(raw_text) < self.min_length:
                logger.warning(f"Insufficient text extracted from {pdf_file}")
                return None
            
            # Normalize the text
            normalized_text = normalize_text(raw_text)
            
            # Extract filename as document title
            filename = os.path.basename(pdf_file)
            title = os.path.splitext(filename)[0].replace('_', ' ')
            
            # Extract sections if enabled, otherwise use the whole document
            results = []
            
            if self.extract_sections:
                sections = self.extract_sections_from_text(normalized_text)
                
                for i, section in enumerate(sections):
                    section_title = section["title"] if section["title"] else f"{title} - Section {i+1}"
                    section_content = section["content"]
                    
                    # Process text (with and without stopword removal)
                    processed_content = preprocess_text(section_content, self.stopwords, remove_stopwords=True)
                    
                    results.append({
                        "source_file": filename,
                        "title": section_title,
                        "content": section_content,
                        "processed_content": processed_content,
                        "extracted_at": datetime.now().isoformat()
                    })
            else:
                # Process text (with and without stopword removal)
                processed_text = preprocess_text(normalized_text, self.stopwords, remove_stopwords=True)
                
                results.append({
                    "source_file": filename,
                    "title": title,
                    "content": normalized_text,
                    "processed_content": processed_text,
                    "extracted_at": datetime.now().isoformat()
                })
            
            return results
        except Exception as e:
            logger.error(f"Error processing {pdf_file}: {e}")
            return None
    
    def extract_and_save(self):
        """Extract text from all PDF files and save results."""
        pdf_files = self.find_pdf_files()
        
        if not pdf_files:
            logger.warning("No PDF files found to process.")
            return []
        
        all_extracted_data = []
        
        # Process PDFs with parallel execution
        with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
            # Submit all extraction tasks
            future_to_pdf = {executor.submit(self.extract_text_from_pdf_file, pdf): pdf for pdf in pdf_files}
            
            # Process as they complete
            for future in tqdm(concurrent.futures.as_completed(future_to_pdf), 
                            total=len(future_to_pdf), 
                            desc="Extracting text from PDFs"):
                pdf = future_to_pdf[future]
                try:
                    results = future.result()
                    if results:
                        all_extracted_data.extend(results)
                except Exception as e:
                    logger.error(f"Error processing {pdf}: {e}")
        
        # Save the results
        if all_extracted_data:
            self.save_results(all_extracted_data)
        else:
            logger.warning("No valid data extracted from PDFs.")
        
        return all_extracted_data
    
    def save_results(self, data):
        """Save extracted data to CSV and JSON formats."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Save to CSV
        csv_filename = f"{self.output_dir}/{timestamp}_extracted_pdf_text.csv"
        df.to_csv(csv_filename, index=False, encoding='utf-8')
        logger.info(f"Saved {len(data)} extracted texts to {csv_filename}")
        
        # Save to JSON
        json_filename = f"{self.output_dir}/{timestamp}_extracted_pdf_text.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"Saved {len(data)} extracted texts to {json_filename}")
        
        # Save in JSONL format for model fine-tuning
        jsonl_filename = f"{self.output_dir}/{timestamp}_extracted_pdf_text.jsonl"
        with open(jsonl_filename, 'w', encoding='utf-8') as f:
            for item in data:
                # Format for model fine-tuning
                entry = {
                    "prompt": item["title"],
                    "completion": item["content"]
                }
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        logger.info(f"Saved JSONL format for model fine-tuning to {jsonl_filename}")
        
        # Create symbolic links to the latest files
        self._create_symbolic_links(csv_filename, json_filename, jsonl_filename)
    
    def _create_symbolic_links(self, csv_file, json_file, jsonl_file):
        """Create symbolic links to the latest files."""
        try:
            # Define link names
            csv_link = f"{self.output_dir}/latest_extracted_pdf_text.csv"
            json_link = f"{self.output_dir}/latest_extracted_pdf_text.json"
            jsonl_link = f"{self.output_dir}/latest_extracted_pdf_text.jsonl"
            
            # Remove existing links
            for link in [csv_link, json_link, jsonl_link]:
                if os.path.exists(link):
                    os.unlink(link)
            
            # Create new links
            os.symlink(os.path.basename(csv_file), csv_link)
            os.symlink(os.path.basename(json_file), json_link)
            os.symlink(os.path.basename(jsonl_file), jsonl_link)
            
            logger.info(f"Created symbolic links to latest extracted files")
        except Exception as e:
            logger.error(f"Error creating symbolic links: {e}")

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Extract Pashto text from PDF files")
    parser.add_argument('--input-dir', type=str, default='/workspaces/ZamAI-Pashto-Data-Processing-Pipeline/pdf_documents',
                        help='Directory containing PDF files')
    parser.add_argument('--output-dir', type=str, default='/workspaces/ZamAI-Pashto-Data-Processing-Pipeline/extracted_pdf_data',
                        help='Directory to save extracted text')
    parser.add_argument('--use-ocr', action='store_true', 
                        help='Use OCR for scanned PDFs (requires tesseract)')
    parser.add_argument('--ocr-lang', type=str, default='eng+ara',
                        help='Tesseract language(s) for OCR')
    parser.add_argument('--min-length', type=int, default=50,
                        help='Minimum length for extracted text sections')
    parser.add_argument('--no-sections', action='store_true',
                        help='Do not attempt to extract sections from text')
    parser.add_argument('--install-deps', action='store_true',
                        help='Install dependencies before running')
    
    args = parser.parse_args()
    
    # Install dependencies if requested
    if args.install_deps:
        logger.info("Installing dependencies...")
        try:
            import subprocess
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'pdfplumber', 'pandas', 'tqdm', 'pymupdf'])
            if args.use_ocr:
                subprocess.run([sys.executable, '-m', 'pip', 'install', 'pytesseract', 'pillow'])
                logger.info("Note: You may need to install Tesseract OCR separately on your system")
                logger.info("For Linux: apt-get install tesseract-ocr")
                logger.info("For macOS: brew install tesseract")
            logger.info("Dependencies installed")
        except Exception as e:
            logger.error(f"Error installing dependencies: {e}")
    
    # Ensure input directory exists
    if not os.path.exists(args.input_dir):
        os.makedirs(args.input_dir, exist_ok=True)
        logger.info(f"Created input directory: {args.input_dir}")
    
    # Create and run the extractor
    extractor = PashtoPdfExtractor(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        use_ocr=args.use_ocr,
        ocr_lang=args.ocr_lang,
        min_length=args.min_length,
        extract_sections=not args.no_sections
    )
    
    logger.info("Starting PDF text extraction process...")
    extracted_data = extractor.extract_and_save()
    
    # Print summary
    logger.info("PDF text extraction complete!")
    logger.info(f"Extracted {len(extracted_data)} text segments from PDFs in {args.input_dir}")
    logger.info(f"Results saved to {args.output_dir}")

if __name__ == "__main__":
    main()
