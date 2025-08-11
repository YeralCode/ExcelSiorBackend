"""
Paquete repository para ExcelSior API.

Este paquete contiene todos los procesadores y transformadores
de archivos específicos para diferentes proyectos y formatos.
"""

from .processors.csv_processor import CSVProcessor
from .processors.excel_processor import ExcelProcessor
from .processors.consolidation_processor import ConsolidationProcessor
from .transformers.format_transformer import FormatTransformer
from .transformers.encoding_transformer import EncodingTransformer

__version__ = "1.0.0"
__author__ = "ExcelSior Team"

__all__ = [
    "CSVProcessor",
    "ExcelProcessor", 
    "ConsolidationProcessor",
    "FormatTransformer",
    "EncodingTransformer"
] 