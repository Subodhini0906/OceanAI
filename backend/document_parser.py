"""
Document parsing utilities for various file types
"""
import os
from pathlib import Path
from typing import Dict, List
import json
import PyPDF2
try:
    import fitz  # PyMuPDF (optional)
except ImportError:
    fitz = None
from bs4 import BeautifulSoup

class DocumentParser:
    """Parse various document types and extract text"""
    
    @staticmethod
    def parse_file(file_path: str, file_type: str = None) -> str:
        """
        Parse a file and extract text content
        
        Args:
            file_path: Path to the file
            file_type: Optional file type hint
            
        Returns:
            Extracted text content
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Auto-detect file type if not provided
        if not file_type:
            file_type = Path(file_path).suffix.lower()
        
        # Parse based on file type
        if file_type in ['.txt', '.md']:
            return DocumentParser.parse_text(file_path)
        elif file_type == '.json':
            return DocumentParser.parse_json(file_path)
        elif file_type == '.pdf':
            return DocumentParser.parse_pdf(file_path)
        elif file_type in ['.html', '.htm']:
            return DocumentParser.parse_html(file_path)
        else:
            # Try text parsing as fallback
            return DocumentParser.parse_text(file_path)
    
    @staticmethod
    def parse_text(file_path: str) -> str:
        """Parse plain text or markdown file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()
    
    @staticmethod
    def parse_json(file_path: str) -> str:
        """Parse JSON file and convert to readable text"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Convert JSON to readable format
                return json.dumps(data, indent=2)
        except Exception as e:
            return f"Error parsing JSON: {str(e)}"
    
    @staticmethod
    def parse_pdf(file_path: str) -> str:
        """Parse PDF file using PyMuPDF (fitz) or PyPDF2"""
        try:
            # Try PyMuPDF first (better quality) if available
            try:
                import fitz
                doc = fitz.open(file_path)
                text = ""
                for page in doc:
                    text += page.get_text()
                doc.close()
                return text
            except ImportError:
                # PyMuPDF not available, use PyPDF2
                pass
        except Exception:
            pass
        
        # Fallback to PyPDF2
        try:
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            return f"Error parsing PDF: {str(e)}"
    
    @staticmethod
    def parse_html(file_path: str) -> str:
        """Parse HTML file and extract text content"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                # Get text
                text = soup.get_text()
                # Clean up whitespace
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = ' '.join(chunk for chunk in chunks if chunk)
                return text
        except Exception as e:
            return f"Error parsing HTML: {str(e)}"
    
    @staticmethod
    def parse_uploaded_file(content: bytes, filename: str) -> str:
        """
        Parse uploaded file content
        
        Args:
            content: File content as bytes
            filename: Original filename
            
        Returns:
            Extracted text content
        """
        file_type = Path(filename).suffix.lower()
        
        if file_type in ['.txt', '.md']:
            return content.decode('utf-8', errors='ignore')
        elif file_type == '.json':
            try:
                data = json.loads(content.decode('utf-8'))
                return json.dumps(data, indent=2)
            except:
                return content.decode('utf-8', errors='ignore')
        elif file_type == '.pdf':
            # Save temporarily and parse
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                tmp.write(content)
                tmp_path = tmp.name
            try:
                text = DocumentParser.parse_pdf(tmp_path)
            finally:
                os.unlink(tmp_path)
            return text
        elif file_type in ['.html', '.htm']:
            soup = BeautifulSoup(content.decode('utf-8', errors='ignore'), 'html.parser')
            for script in soup(["script", "style"]):
                script.decompose()
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            return ' '.join(chunk for chunk in chunks if chunk)
        else:
            return content.decode('utf-8', errors='ignore')

