"""
Configuración centralizada para ExcelSior API.

Este módulo contiene todas las configuraciones del proyecto,
incluyendo constantes, configuraciones de archivos y validaciones.
"""

import os
from typing import Dict, List, Set
from dataclasses import dataclass
from pathlib import Path

# Configuración de la aplicación
APP_NAME = "ExcelSior API"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "API para procesamiento y transformación de archivos Excel y CSV"

# Configuración de archivos
DEFAULT_ENCODING = 'utf-8'
DEFAULT_DELIMITER = '|'
TEMP_COMMA_REPLACEMENT = '\uE000'
TEMP_NEWLINE = '⏎'
TEMP_COMMA = '\uE000'

# Valores nulos reconocidos
NULL_VALUES: Set[str] = {
    "$null$", "nan", "null", "n.a", "n.a.", "n/a", "n/a.", 
    "none", "sin registro", "desconocido", "no aplica", "na"
}

# Formatos de fecha soportados
DATE_FORMATS = {
    'date': "%Y-%m-%d",
    'date_YY': "%Y/%m/%d",
    'date_dd_mm_yyyy': "%d/%m/%Y",
    'datetime': "%Y-%m-%d %H:%M:%S",
    'date_dd_mon_yy': "%d-%b-%y"
}

# Configuración de archivos temporales
TEMP_DIR = Path("/tmp/excelsior")
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
ALLOWED_EXTENSIONS = {'.csv', '.xlsx', '.xls', '.sav', '.txt'}

# Configuración de logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Configuración de CORS
# Permite leer desde variable de entorno o usar valores por defecto
_cors_origins_env = os.getenv("CORS_ORIGINS")
if _cors_origins_env:
    # Si viene como string JSON, parsearlo
    import json
    try:
        CORS_ORIGINS = json.loads(_cors_origins_env)
    except json.JSONDecodeError:
        # Si no es JSON válido, intentar como lista separada por comas
        CORS_ORIGINS = [origin.strip() for origin in _cors_origins_env.split(",")]
else:
    # Valores por defecto - incluye todos los puertos comunes de desarrollo
    CORS_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:5176",
        "http://localhost:5177",
        "http://localhost:5178",
        "http://localhost:5179",
        "http://localhost:5180",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5175",
        "http://127.0.0.1:5176",
        "http://127.0.0.1:5177",
        "http://127.0.0.1:5178",
        "http://127.0.0.1:5179",
        "http://127.0.0.1:5180",
    ]

# Configuración de validación
VALIDATION_CONFIG = {
    'max_rows_per_file': 1000000,
    'max_columns_per_file': 100,
    'timeout_seconds': 300,
}

@dataclass
class ProjectConfig:
    """Configuración específica para cada proyecto."""
    name: str
    headers: List[str]
    replacement_map: Dict[str, str]
    validators: Dict[str, str]
    
# Configuraciones específicas por proyecto
PROJECT_CONFIGS = {
    'DIAN': ProjectConfig(
        name="DIAN-Notificaciones",
        headers=[
            "PLAN_IDENTIF_ACTO", "CODIGO_ADMINISTRACION", "SECCIONAL",
            "CODIGO_DEPENDENCIA", "DEPENDENCIA", "ANO_CALENDARIO",
            "CODIGO_ACTO", "DESCRIPCION_ACTO", "ANO_ACTO", "CONSECUTIVO_ACTO",
            "FECHA_ACTO", "CUANTIA_ACTO", "NIT", "RAZON_SOCIAL", "DIRECCION",
            "PLANILLA_REMISION", "FECHA_PLANILLA_REMISION", "FUNCIONARIO_ENVIA",
            "FECHA_CITACION", "PLANILLA_CORR", "FECHA_PLANILLA_CORR",
            "FECHA_NOTIFICACION", "FECHA_EJECUTORIA", "GUIA", "COD_ESTADO",
            "ESTADO_NOTIFICACION", "COD_NOTIFICACION", "MEDIO_NOTIFICACION",
            "NUMERO_EXPEDIENTE", "TIPO_DOCUMENTO", "PERI_IMPUESTO", "PERI_PERIODO",
            "NOMBRE_APLICACION", "PAIS_COD_NUM_PAIS", "PAIS", "MUNI_CODIGO_DEPART",
            "DEPARTAMENTO", "MUNI_CODIGO_MUNICI", "MUNICIPIO", "REGIMEN",
            "FECHA_LEVANTE", "MOTIVO_LEVANTE", "NORMATIVIDAD", "FUNCIONARIO_RECIBE",
            "PLANILLA_REMI_ARCHIVO", "FECHA_PLANILLA_REMI_ARCHIVO"
        ],
        replacement_map={
            "nombre_archivo": "NOMBRE_ARCHIVO",
            "mes_reporte": "MES_REPORTE",
            'COPL_PLANILLA_REMI': 'PLANILLA_REMISION',
            'COPL_PLANILLA_CORR': 'PLANILLA_CORR',
            'Seccional': 'SECCIONAL',
            'PIA': 'PLAN_IDENTIF_ACTO',
            'SECC': 'SECCIONAL',
            'DEP': 'CODIGO_DEPENDENCIA',
            'AÑO': 'ANO_CALENDARIO',
            'COD_ACTO': 'CODIGO_ACTO',
            'DESCRIPCION': 'DESCRIPCION_ACTO',
            'CONSECUTIVO': 'CONSECUTIVO_ACTO',
            'CUANTIA': 'CUANTIA_ACTO',
            'PLANILLA_REMI': 'PLANILLA_REMISION',
            'FECHA_PLANILLA_REMI': 'FECHA_PLANILLA_REMISION',
            'NUMERO_DE_GUIA': 'GUIA',
            'ESTADO': 'ESTADO_NOTIFICACION',
            'COD_NOTI': 'COD_NOTIFICACION',
            'DESC_NOTIFICACION': 'DESCRIPCION',
            'TIPO_DOC': 'TIPO_DOCUMENTO',
            'IMPUESTO': 'PERI_IMPUESTO',
            'PERIODO': 'PERI_PERIODO',
            'DEPTO': 'MUNI_CODIGO_DEPART',
            'NOMBRE_DEPTO': 'DEPARTAMENTO',
            'MUNICIPIO': 'MUNI_CODIGO_MUNICI',
        },
        validators={
            'NIT': 'nit',
            'CUANTIA_ACTO': 'flotante',
            'ANO_CALENDARIO': 'entero',
            'ANO_ACTO': 'entero',
            'CONSECUTIVO_ACTO': 'entero',
            'FECHA_ACTO': 'fecha',
            'FECHA_PLANILLA_REMISION': 'fecha',
            'FECHA_CITACION': 'fecha',
            'FECHA_PLANILLA_CORR': 'fecha',
            'FECHA_NOTIFICACION': 'fecha',
            'FECHA_EJECUTORIA': 'fecha',
            'FECHA_LEVANTE': 'fecha',
            'FECHA_PLANILLA_REMI_ARCHIVO': 'fecha',
        }
    ),
    'COLJUEGOS': ProjectConfig(
        name="COLJUEGOS",
        headers=[],  # Definir headers específicos para COLJUEGOS
        replacement_map={},
        validators={}
    ),
    'UGPP': ProjectConfig(
        name="UGPP", 
        headers=[],  # Definir headers específicos para UGPP
        replacement_map={},
        validators={}
    )
}

def get_project_config(project_name: str) -> ProjectConfig:
    """Obtiene la configuración para un proyecto específico."""
    return PROJECT_CONFIGS.get(project_name.upper())

def ensure_temp_dir():
    """Asegura que el directorio temporal existe."""
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    return TEMP_DIR 