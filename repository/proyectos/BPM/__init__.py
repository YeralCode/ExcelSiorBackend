"""
Módulo BPM para procesamiento de archivos
Implementa validación, transformación y limpieza de datos para archivos BPM
"""

from .config import BPMConfig

from .validadores.validadores_bpm import bpm_validator, BPMValidators
from .transformar_columnas_bpm import bpm_transformer, BPMColumnTransformer
from .processor_bpm import bpm_processor, BPMProcessor

__version__ = "1.0.0"
__author__ = "ExcelSior Team"
__description__ = "Procesador especializado para archivos BPM"

# Exportar componentes principales
__all__ = [
    # Configuración
    'BPMConfig',
    
    # Validadores
    'bpm_validator',
    'BPMValidators',
    
    # Transformadores
    'bpm_transformer',
    'BPMColumnTransformer',
    
    # Procesador principal
    'bpm_processor',
    'BPMProcessor'
] 