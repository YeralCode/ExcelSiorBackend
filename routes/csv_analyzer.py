"""
Ruta para el analizador interactivo de archivos CSV.

Proporciona endpoints para analizar archivos CSV y generar
diccionarios de tipos de datos automáticamente.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import re
import os
import shutil
import tempfile

from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from utils.logger import get_logger
from utils.exceptions import handle_exception
from utils.dynamic_data_types import data_type_manager
from utils.csv_separator_detector import separator_detector
from utils.column_cleaner import column_cleaner
from repository.processors.csv_processor import CSVProcessor
from config.settings import get_project_config

logger = get_logger(__name__)
router = APIRouter(prefix="/csv-analyzer", tags=["CSV Analyzer"])

class CSVAnalysisRequest(BaseModel):
    """Modelo para solicitudes de análisis de CSV."""
    project_name: Optional[str] = None
    include_metadata: bool = True
    sample_size: int = 1000
    auto_detect_types: bool = True
    use_dynamic_types: bool = True  # Nuevo campo para usar tipos dinámicos

class CSVAnalysisResponse(BaseModel):
    """Modelo para respuestas de análisis de CSV."""
    success: bool
    file_info: Dict[str, Any]
    column_analysis: Dict[str, Any]
    data_types: Dict[str, List[str]]
    recommendations: Dict[str, Any]
    sample_data: List[Dict[str, Any]]
    validation_results: Dict[str, Any]
    available_types: List[Dict[str, Any]]  # Nuevo campo para tipos disponibles

def normalize_column_name(column_name: str) -> str:
    """Normaliza nombres de columnas reemplazando espacios y caracteres especiales."""
    column_name = column_name.strip().upper()
    replacements = [
        (' ', '_'), ('-', '_'), ('Á', 'A'), ('É', 'E'), ('Í', 'I'),
        ('Ó', 'O'), ('Ú', 'U'), ('Ñ', 'N'), ('.', ''), ('/', '_'),
    ]
    for old, new in replacements:
        column_name = column_name.replace(old, new)
    return column_name

class DataTypeDetector:
    """Detector automático de tipos de datos para columnas CSV."""
    
    def __init__(self, use_dynamic_types: bool = True):
        self.use_dynamic_types = use_dynamic_types
        self.null_values = {"", "nan", "null", "n/a", "none", "undefined"}
        self.date_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
            r'\d{2}-\d{2}-\d{4}',  # MM-DD-YYYY
            r'\d{4}/\d{2}/\d{2}',  # YYYY/MM/DD
            r'\d{2}/\d{2}/\d{2}',  # DD/MM/YY
            r'\d{2}-\d{2}-\d{2}',  # DD-MM-YY
        ]
        
    def detect_column_type(self, column_data: pd.Series, column_name: str) -> Dict[str, Any]:
        """
        Detecta el tipo de datos de una columna.
        
        Args:
            column_data: Serie de pandas con los datos de la columna
            column_name: Nombre de la columna
            
        Returns:
            Diccionario con información del tipo detectado
        """
        # Limpiar datos nulos
        clean_data = column_data.dropna()
        if len(clean_data) == 0:
            return {"type": "string", "confidence": 0.0, "reason": "Solo valores nulos"}
        
        # Convertir a string para análisis
        str_data = clean_data.astype(str).str.strip()
        
        # Si se usan tipos dinámicos, intentar detectar primero
        if self.use_dynamic_types:
            dynamic_result = data_type_manager.detect_type(str_data.tolist(), column_name)
            if dynamic_result["confidence"] > 0.7:
                return dynamic_result
        
        # Detectar tipos básicos
        return self._detect_basic_types(str_data, column_name)
    
    def _detect_basic_types(self, str_data: pd.Series, column_name: str) -> Dict[str, Any]:
        """Detecta tipos básicos de datos."""
        
        # Detectar fechas
        if self._detect_date_type(str_data):
            return {"type": "date", "confidence": 0.8, "reason": "Patrones de fecha detectados"}
        
        # Detectar números enteros
        if self._detect_integer_type(str_data):
            return {"type": "integer", "confidence": 0.9, "reason": "Números enteros detectados"}
        
        # Detectar números decimales
        if self._detect_float_type(str_data):
            return {"type": "float", "confidence": 0.85, "reason": "Números decimales detectados"}
        
        # Detectar booleanos
        if self._detect_boolean_type(str_data):
            return {"type": "boolean", "confidence": 0.9, "reason": "Valores booleanos detectados"}
        
        # Por defecto, es string
        return {"type": "string", "confidence": 0.5, "reason": "Texto detectado"}
    
    def _detect_date_type(self, str_data: pd.Series) -> bool:
        """Detecta si la columna contiene fechas."""
        date_count = 0
        total_valid = 0
        
        for value in str_data:
            if value and str(value).strip():
                total_valid += 1
                for pattern in self.date_patterns:
                    if re.search(pattern, str(value)):
                        date_count += 1
                        break
        
        return total_valid > 0 and (date_count / total_valid) > 0.7
    
    def _detect_integer_type(self, str_data: pd.Series) -> bool:
        """Detecta si la columna contiene números enteros."""
        int_count = 0
        total_valid = 0
        
        for value in str_data:
            if value and str(value).strip():
                total_valid += 1
                try:
                    int(str(value).replace(',', '').replace('.', ''))
                    int_count += 1
                except ValueError:
                    pass
        
        return total_valid > 0 and (int_count / total_valid) > 0.8
    
    def _detect_float_type(self, str_data: pd.Series) -> bool:
        """Detecta si la columna contiene números decimales."""
        float_count = 0
        total_valid = 0
        
        for value in str_data:
            if value and str(value).strip():
                total_valid += 1
                try:
                    float(str(value).replace(',', ''))
                    float_count += 1
                except ValueError:
                    pass
        
        return total_valid > 0 and (float_count / total_valid) > 0.8
    
    def _detect_boolean_type(self, str_data: pd.Series) -> bool:
        """Detecta si la columna contiene valores booleanos."""
        boolean_values = {'true', 'false', 'yes', 'no', '1', '0', 'si', 'no', 'verdadero', 'falso'}
        bool_count = 0
        total_valid = 0
        
        for value in str_data:
            if value and str(value).strip():
                total_valid += 1
                if str(value).lower().strip() in boolean_values:
                    bool_count += 1
        
        return total_valid > 0 and (bool_count / total_valid) > 0.8

def extract_unique_values(column_data: pd.Series, max_values: Optional[int] = None) -> List[str]:
    """
    Extrae valores únicos de una columna.
    
    Args:
        column_data: Serie de pandas con los datos de la columna
        max_values: Máximo número de valores únicos a retornar (None para sin límite)
        
    Returns:
        Lista de valores únicos
    """
    try:
        # Limpiar datos nulos y vacíos
        clean_data = column_data.dropna()
        clean_data = clean_data[clean_data.astype(str).str.strip() != '']
        
        if len(clean_data) == 0:
            return []
        
        # Obtener valores únicos
        unique_values = clean_data.astype(str).str.strip().unique()
        
        # Ordenar y limitar solo si se especifica un límite
        if max_values is not None and max_values > 0:
            unique_values = sorted(unique_values)[:max_values]
        else:
            # Sin límite - ordenar todos los valores únicos
            unique_values = sorted(unique_values)
        
        # Convertir a lista de strings
        return [str(value) for value in unique_values]
    except Exception as e:
        logger.warning(f"Error extrayendo valores únicos: {str(e)}")
        return []

@router.post("/analyze")
async def analyze_csv(
    file: UploadFile = File(...),
    use_dynamic_types: bool = Form(True),
    extract_choices: bool = Form(True)  # Nuevo parámetro para extraer choices
):
    try:
        # Crear directorio temporal
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, file.filename)
        
        # Guardar archivo temporalmente
        with open(temp_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        # Detectar separador automáticamente
        separator_info = separator_detector.get_separator_info(temp_path)
        detected_separator = separator_info["detected_separator"]
        separator_confidence = separator_info["confidence"]
        
        logger.info(f"Separador detectado: '{detected_separator}' (confianza: {separator_confidence:.2f})")
        
        try:
            # Intentar leer con diferentes configuraciones usando el separador detectado
            df = None
            error_messages = []
            
            # Configuración 1: Lectura básica con separador detectado
            try:
                df = pd.read_csv(temp_path, dtype=str, encoding='utf-8', sep=detected_separator)
                logger.info(f"CSV leído exitosamente con separador '{detected_separator}'")
            except Exception as e1:
                error_messages.append(f"Separador '{detected_separator}' falló: {str(e1)}")
                
                # Configuración 2: Con encoding latin-1
                try:
                    df = pd.read_csv(temp_path, dtype=str, encoding='latin-1', sep=detected_separator)
                    logger.info(f"CSV leído exitosamente con separador '{detected_separator}' y encoding latin-1")
                except Exception as e2:
                    error_messages.append(f"Encoding latin-1 falló: {str(e2)}")
                    
                    # Configuración 3: Con encoding cp1252
                    try:
                        df = pd.read_csv(temp_path, dtype=str, encoding='cp1252', sep=detected_separator)
                        logger.info(f"CSV leído exitosamente con separador '{detected_separator}' y encoding cp1252")
                    except Exception as e3:
                        error_messages.append(f"Encoding cp1252 falló: {str(e3)}")
                        
                        # Configuración 4: Con engine python
                        try:
                            df = pd.read_csv(temp_path, dtype=str, engine='python', sep=detected_separator)
                            logger.info(f"CSV leído exitosamente con separador '{detected_separator}' y engine python")
                        except Exception as e4:
                            error_messages.append(f"Engine python falló: {str(e4)}")
                            
                            # Configuración 5: Ignorar líneas problemáticas
                            try:
                                df = pd.read_csv(temp_path, dtype=str, on_bad_lines='skip', sep=detected_separator)
                                logger.info(f"CSV leído exitosamente con separador '{detected_separator}' ignorando líneas problemáticas")
                            except Exception as e5:
                                error_messages.append(f"Ignorar líneas problemáticas falló: {str(e5)}")
                                
                                # Configuración 6: Último intento con separador automático
                                try:
                                    df = pd.read_csv(temp_path, dtype=str, sep=None, engine='python')
                                    logger.info("CSV leído exitosamente con separador automático")
                                except Exception as e6:
                                    error_messages.append(f"Separador automático falló: {str(e6)}")
                                    raise Exception(f"No se pudo leer el archivo CSV. Errores: {'; '.join(error_messages)}")
            
            if df is None or df.empty:
                raise Exception("El archivo CSV está vacío o no se pudo leer correctamente")
            
            # Limpiar columnas con nombres problemáticos
            df.columns = [str(col).strip() for col in df.columns]
            
            # Eliminar columnas completamente vacías
            df = df.dropna(axis=1, how='all')
            
            # Si no hay columnas después de la limpieza
            if df.empty or len(df.columns) == 0:
                raise Exception("No se encontraron columnas válidas en el archivo CSV")
            
            # Crear mapeo de nombres de columnas limpios
            column_mapping = column_cleaner.clean_column_names(list(df.columns))
            
            logger.info(f"CSV procesado exitosamente: {len(df)} filas, {len(df.columns)} columnas")
            logger.info(f"Mapeo de columnas: {column_mapping}")
            
        except Exception as e:
            logger.error(f"Error leyendo CSV: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Error leyendo archivo CSV: {str(e)}")
        
        # Inicializar detector
        detector = DataTypeDetector(use_dynamic_types=use_dynamic_types)
        
        # Analizar cada columna
        column_analysis = {}
        column_choices = {}  # Nuevo diccionario para almacenar choices
        
        for column in df.columns:
            try:
                analysis = detector.detect_column_type(df[column], column)
                column_analysis[column] = analysis
                
                # Extraer valores únicos si se solicita - SIN LÍMITE MÁXIMO
                if extract_choices:
                    unique_values = extract_unique_values(df[column], max_values=None)  # Sin límite
                    column_choices[column] = unique_values
                    logger.info(f"Columna '{column}': {len(unique_values)} valores únicos extraídos (sin límite)")
                
            except Exception as e:
                logger.warning(f"Error analizando columna {column}: {str(e)}")
                # Usar tipo por defecto si hay error
                column_analysis[column] = {
                    "type": "string",
                    "confidence": 0.0,
                    "reason": f"Error en análisis: {str(e)}"
                }
                column_choices[column] = []
        
        # Normalizar nombres de columnas para el JSON de respuesta
        normalized_column_analysis = {}
        normalized_column_choices = {}
        
        for original_name, analysis in column_analysis.items():
            normalized_name = normalize_column_name(original_name)
            normalized_column_analysis[normalized_name] = analysis
            if extract_choices and original_name in column_choices:
                normalized_column_choices[normalized_name] = column_choices[original_name]
        
        # Información del archivo
        file_info = {
            "filename": file.filename,
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "sample_size": min(1000, len(df)),
            "detected_separator": detected_separator,
            "separator_confidence": separator_confidence,
            "column_mapping": column_mapping
        }
        
        # Obtener tipos disponibles si se usan tipos dinámicos
        available_types = []
        if use_dynamic_types:
            available_types = data_type_manager.get_all_types()
        
        # Preparar respuesta
        response_data = {
            "success": True,
            "file_info": file_info,
            "column_analysis": normalized_column_analysis,  # Usar nombres normalizados
            "column_choices": normalized_column_choices,  # Nuevo campo con choices
            "available_types": available_types,
            "separator_info": separator_info,
            "column_mapping": column_mapping,
            "original_columns": list(df.columns),  # Agregar nombres originales de columnas
            "normalized_columns": [normalize_column_name(col) for col in df.columns],  # Agregar nombres normalizados
            "recommendations": {
                "total_columns_analyzed": len(df.columns),
                "types_detected": len(set(analysis["type"] for analysis in column_analysis.values())),
                "use_dynamic_types": use_dynamic_types,
                "recommended_separator": detected_separator,
                "choices_extracted": extract_choices
            }
        }
        
        # Limpiar archivo temporal
        try:
            os.remove(temp_path)
            os.rmdir(temp_dir)
        except:
            pass  # Ignorar errores de limpieza
        
        logger.info(f"Análisis completado para {file.filename}")
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analizando CSV: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error analizando archivo: {str(e)}")

@router.post("/get-column-choices")
async def get_column_choices(
    file: UploadFile = File(...),
    column_name: str = Form(...),
    max_values: Optional[int] = Form(None)
):
    try:
        # Crear directorio temporal
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, file.filename)
        
        # Guardar archivo temporalmente
        with open(temp_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        # Detectar separador automáticamente
        separator_info = separator_detector.get_separator_info(temp_path)
        detected_separator = separator_info["detected_separator"]
        
        # Leer CSV
        try:
            df = pd.read_csv(temp_path, dtype=str, encoding='utf-8', sep=detected_separator)
        except:
            try:
                df = pd.read_csv(temp_path, dtype=str, encoding='latin-1', sep=detected_separator)
            except:
                df = pd.read_csv(temp_path, dtype=str, sep=None, engine='python')
        
        # Crear mapeo de nombres normalizados a nombres originales
        normalized_to_original = {}
        for original_col in df.columns:
            normalized_col = normalize_column_name(original_col)
            normalized_to_original[normalized_col] = original_col
        
        # Buscar la columna (puede ser nombre original o normalizado)
        target_column = None
        
        # Primero buscar por nombre original
        if column_name in df.columns:
            target_column = column_name
            logger.info(f"Columna encontrada por nombre original: {column_name}")
        # Luego buscar por nombre normalizado
        elif column_name in normalized_to_original:
            target_column = normalized_to_original[column_name]
            logger.info(f"Columna encontrada por nombre normalizado: {column_name} -> {target_column}")
        else:
            # Si no se encuentra, mostrar todas las columnas disponibles para debugging
            available_columns = list(df.columns)
            available_normalized = [normalize_column_name(col) for col in df.columns]
            logger.error(f"Columna '{column_name}' no encontrada. Columnas disponibles:")
            logger.error(f"  Originales: {available_columns}")
            logger.error(f"  Normalizadas: {available_normalized}")
            raise HTTPException(
                status_code=400, 
                detail=f"La columna '{column_name}' no existe en el archivo. Columnas disponibles: {available_columns}"
            )
        
        # Extraer valores únicos - SIN LÍMITE por defecto
        logger.info(f"🔍 Extrayendo valores únicos para columna '{target_column}'")
        logger.info(f"🔍 Parámetro max_values recibido: {max_values} (tipo: {type(max_values)})")
        logger.info(f"🔍 Total de filas en la columna: {len(df[target_column])}")
        
        unique_values = extract_unique_values(df[target_column], max_values=max_values)
        
        logger.info(f"🔍 Valores únicos extraídos: {len(unique_values)}")
        logger.info(f"🔍 Primeros 5 valores únicos: {unique_values[:5] if unique_values else 'Ninguno'}")
        
        # Limpiar archivo temporal
        try:
            os.remove(temp_path)
            os.rmdir(temp_dir)
        except:
            pass
        
        return {
            "success": True,
            "column_name": target_column,  # Nombre original de la columna
            "normalized_column_name": normalize_column_name(target_column),
            "unique_values": unique_values,
            "total_unique_values": len(unique_values),
            "max_values_requested": max_values if max_values else "Sin límite"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error extrayendo choices de columna: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error extrayendo choices: {str(e)}")

@router.post("/detect-separator")
async def detect_csv_separator(file: UploadFile = File(...)):
    try:
        # Crear directorio temporal
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, file.filename)
        
        # Guardar archivo temporalmente
        with open(temp_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        # Detectar separador
        separator_info = separator_detector.get_separator_info(temp_path)
        
        # Limpiar archivo temporal
        try:
            os.remove(temp_path)
            os.rmdir(temp_dir)
        except:
            pass
        
        return {
            "success": True,
            "separator_info": separator_info
        }
        
    except Exception as e:
        logger.error(f"Error detectando separador: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error detectando separador: {str(e)}")

@router.get("/generate-type-dictionary")
async def generate_type_dictionary():
    """Genera un diccionario de tipos de datos basado en los tipos disponibles."""
    try:
        types = data_type_manager.get_all_types()
        
        # Crear diccionario de tipos
        type_dictionary = {}
        for type_info in types:
            type_dictionary[type_info['name']] = {
                "description": type_info['description'],
                "pattern": type_info['pattern'],
                "examples": type_info['examples'],
                "confidence_threshold": type_info['confidence_threshold']
            }
        
        return {
            "success": True,
            "type_dictionary": type_dictionary,
            "total_types": len(types)
        }
        
    except Exception as e:
        logger.error(f"Error generando diccionario: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generando diccionario: {str(e)}") 