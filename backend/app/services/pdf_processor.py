"""
PDF Processing Service
Extract text from PDF files, preserve slide boundaries, and handle OCR
"""
from typing import List, Dict, Tuple
import PyPDF2
import pdfplumber
from pathlib import Path


class PDFProcessor:
    """Service for processing PDF lecture files"""

    def __init__(self):
        pass

    def extract_text_from_pdf(self, pdf_path: str) -> Tuple[List[Dict[str, any]], int]:
        """
        Extract text from PDF, preserving slide boundaries

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Tuple of (list of slides with content, total number of pages)
            Each slide dict contains: {"page_number": int, "content": str}
        """
        try:
            # Try pdfplumber first (better text extraction)
            slides = self._extract_with_pdfplumber(pdf_path)
            if slides and any(slide["content"].strip() for slide in slides):
                return slides, len(slides)

            # Fallback to PyPDF2
            print("pdfplumber failed, trying PyPDF2...")
            slides = self._extract_with_pypdf2(pdf_path)
            if slides and any(slide["content"].strip() for slide in slides):
                return slides, len(slides)

            # If both fail, return empty slides with page count
            print("Text extraction failed, might need OCR")
            return self._get_empty_slides(pdf_path), len(slides) if slides else 0

        except Exception as e:
            raise RuntimeError(f"PDF processing error: {str(e)}")

    def _extract_with_pdfplumber(self, pdf_path: str) -> List[Dict[str, any]]:
        """Extract text using pdfplumber (preferred method)"""
        slides = []

        try:
            with pdfplumber.open(pdf_path) as pdf:
                for i, page in enumerate(pdf.pages, start=1):
                    text = page.extract_text() or ""

                    # Clean up the text
                    text = self._clean_text(text)

                    slides.append({
                        "page_number": i,
                        "content": text
                    })

            return slides

        except Exception as e:
            print(f"pdfplumber extraction failed: {str(e)}")
            return []

    def _extract_with_pypdf2(self, pdf_path: str) -> List[Dict[str, any]]:
        """Extract text using PyPDF2 (fallback method)"""
        slides = []

        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)

                for i, page in enumerate(pdf_reader.pages, start=1):
                    text = page.extract_text() or ""

                    # Clean up the text
                    text = self._clean_text(text)

                    slides.append({
                        "page_number": i,
                        "content": text
                    })

            return slides

        except Exception as e:
            print(f"PyPDF2 extraction failed: {str(e)}")
            return []

    def _get_empty_slides(self, pdf_path: str) -> List[Dict[str, any]]:
        """Get empty slides when extraction fails (for OCR later)"""
        slides = []

        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)

                for i in range(1, num_pages + 1):
                    slides.append({
                        "page_number": i,
                        "content": "[OCR required - scanned image]"
                    })

            return slides

        except Exception:
            return []

    def _clean_text(self, text: str) -> str:
        """Clean extracted text"""
        if not text:
            return ""

        # Remove excessive whitespace
        text = " ".join(text.split())

        # Remove common PDF artifacts
        text = text.replace("\x00", "")

        return text.strip()

    def extract_text_with_ocr(self, pdf_path: str) -> Tuple[List[Dict[str, any]], int]:
        """
        Extract text using OCR (for scanned PDFs)
        NOTE: Requires tesseract-ocr to be installed on the system

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Tuple of (list of slides with OCR'd content, total number of pages)
        """
        try:
            import pytesseract
            from pdf2image import convert_from_path

            # Convert PDF pages to images
            images = convert_from_path(pdf_path)

            slides = []
            for i, image in enumerate(images, start=1):
                # Perform OCR on the image
                text = pytesseract.image_to_string(image)
                text = self._clean_text(text)

                slides.append({
                    "page_number": i,
                    "content": text
                })

            return slides, len(slides)

        except ImportError:
            raise RuntimeError(
                "OCR dependencies not installed. "
                "Install: pip install pytesseract pdf2image and install tesseract-ocr"
            )
        except Exception as e:
            raise RuntimeError(f"OCR processing error: {str(e)}")

    def validate_pdf(self, pdf_path: str) -> bool:
        """
        Validate that the file is a readable PDF

        Args:
            pdf_path: Path to the PDF file

        Returns:
            True if valid PDF, False otherwise
        """
        try:
            with open(pdf_path, 'rb') as file:
                PyPDF2.PdfReader(file)
            return True
        except Exception:
            return False

    def get_pdf_info(self, pdf_path: str) -> Dict[str, any]:
        """
        Get metadata about the PDF

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Dictionary with PDF metadata
        """
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                metadata = pdf_reader.metadata

                return {
                    "num_pages": len(pdf_reader.pages),
                    "author": metadata.get("/Author", "Unknown") if metadata else "Unknown",
                    "title": metadata.get("/Title", "Unknown") if metadata else "Unknown",
                    "subject": metadata.get("/Subject", "") if metadata else "",
                    "creator": metadata.get("/Creator", "") if metadata else "",
                }

        except Exception as e:
            return {
                "num_pages": 0,
                "author": "Unknown",
                "title": "Unknown",
                "error": str(e)
            }


# Singleton instance
pdf_processor = PDFProcessor()
