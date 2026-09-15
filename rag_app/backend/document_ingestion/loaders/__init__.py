"""Document loaders for various file types."""

from .base import DocumentLoader
from .docx_loader import DOCXLoader
from .email_loader import EmailLoader
from .excel_loader import ExcelLoader
from .html_loader import HTMLLoader
from .image_loader import ImageLoader
from .pdf_loader import PDFLoader
from .pptx_loader import PPTXLoader
from .registry import FileTypeRegistry
from .scanned_doc_loader import ScannedDocLoader
from .webpage_loader import WebPageLoader

__all__ = [
    "DocumentLoader",
    "PDFLoader",
    "DOCXLoader",
    "PPTXLoader",
    "ExcelLoader",
    "HTMLLoader",
    "ImageLoader",
    "EmailLoader",
    "WebPageLoader",
    "ScannedDocLoader",
    "FileTypeRegistry",
]
