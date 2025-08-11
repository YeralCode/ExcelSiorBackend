"""
Transformador de columnas para archivos de notificaciones de DIAN.
Integrado con el sistema modular de configuraciones y validaciones.
"""

import csv
import os
from typing import Dict, List, Union, Optional, Tuple
from dataclasses import dataclass
import io
import logging

# Importar componentes del sistema modular
from ...base.config_base import ProjectConfigBase
from ...base.values_manager import ValuesManager
from ...base.validators import ValidatorFactory
from ...factory import get_project_config

logger = logging.getLogger(__name__)

# Constantes
NULL_VALUES = {"$null$", "nan", "null", "n.a", "null", "n.a.", "n/a", "n/a."}
DELIMITER = '|'
ENCODING = 'utf-8'
TEMP_COMMA_REPLACEMENT = '\uE000'
TEMP_NEWLINE = '⏎'
TEMP_COMMA = '\uE000'

# Encabezados de referencia mejorados para DIAN notificaciones
REFERENCE_HEADERS = [
    "PLAN_IDENTIF_ACTO",
    "CODIGO_ADMINISTRACION", 
    "SECCIONAL",
    "CODIGO_DEPENDENCIA",
    "DEPENDENCIA",
    "ANO_CALENDARIO",
    "CODIGO_ACTO",
    "DESCRIPCION_ACTO",
    "ANO_ACTO",
    "CONSECUTIVO_ACTO",
    "FECHA_ACTO",
    "CUANTIA_ACTO",
    "NIT",
    "RAZON_SOCIAL",
    "DIRECCION",
    "PLANILLA_REMISION",
    "FECHA_PLANILLA_REMISION",
    "FUNCIONARIO_ENVIA",
    "FECHA_CITACION",
    "PLANILLA_CORR",
    "FECHA_PLANILLA_CORR",
    "FECHA_NOTIFICACION",
    "FECHA_EJECUTORIA",
    "GUIA",
    "COD_ESTADO",
    "ESTADO_NOTIFICACION",
    "COD_NOTIFICACION",
    "MEDIO_NOTIFICACION",
    "NUMERO_EXPEDIENTE",
    "TIPO_DOCUMENTO",
    "PERI_IMPUESTO",
    "PERI_PERIODO",
    "NOMBRE_APLICACION",
    "PAIS_COD_NUM_PAIS",
    "PAIS",
    "MUNI_CODIGO_DEPART",
    "DEPARTAMENTO",
    "MUNI_CODIGO_MUNICI",
    "MUNICIPIO",
    "REGIMEN",
    "FECHA_LEVANTE",
    "MOTIVO_LEVANTE",
    "NORMATIVIDAD",
    "FUNCIONARIO_RECIBE",
    "PLANILLA_REMI_ARCHIVO",
    "FECHA_PLANILLA_REMI_ARCHIVO"
]

# Mapeo de reemplazo de columnas mejorado
REPLACEMENT_MAP = {
    # Mapeos básicos
    "nombre_archivo": "NOMBRE_ARCHIVO",
    "mes_reporte": "MES_REPORTE",
    'COPL_PLANILLA_REMI': 'PLANILLA_REMISION',
    'COPL_PLANILLA_CORR': 'PLANILLA_CORR',
    'Seccional': 'SECCIONAL',
    
    # Variaciones comunes de columnas
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
    'FECHA_CITACION': 'FECHA_CITACION',
    'PLANILLA_CORR': 'PLANILLA_CORR',
    'FECHA_PLANILLA_CORR': 'FECHA_PLANILLA_CORR',
    'FECHA_NOTIFICACION': 'FECHA_NOTIFICACION',
    'FECHA_EJECUTORIA': 'FECHA_EJECUTORIA',
    'NUMERO_DE_GUIA': 'GUIA',
    'ESTADO': 'ESTADO_NOTIFICACION',
    'COD_NOTI': 'COD_NOTIFICACION',
    'DESC_NOTIFICACION': 'DESCRIPCION',
    'NUMERO_EXPEDIENTE': 'NUMERO_EXPEDIENTE',
    'TIPO_DOC': 'TIPO_DOCUMENTO',
    'IMPUESTO': 'PERI_IMPUESTO',
    'PERIODO': 'PERI_PERIODO',
    'NOMBRE_APLICACION': 'NOMBRE_APLICACION',
    'DEPTO': 'MUNI_CODIGO_DEPART',
    'NOMBRE_DEPTO': 'DEPARTAMENTO',
    'MUNICIPIO': 'MUNI_CODIGO_MUNICI',
}


@dataclass
class ErrorInfo:
    """Información de error para el procesamiento."""
    columna: str
    numero_columna: int
    tipo: str
    valor: str
    fila: int
    error: str


class DIANNotificacionesProcessor:
    """
    Procesador específico para archivos de notificaciones de DIAN.
    Integrado con el sistema modular de configuraciones.
    """
    
    def __init__(self, config: Optional[ProjectConfigBase] = None):
        """
        Inicializa el procesador.
        
        Args:
            config: Configuración específica del proyecto (opcional)
        """
        # Obtener configuración del proyecto
        self.config = config or get_project_config('DIAN', 'notificaciones')
        
        # Inicializar gestor de valores
        self.values_manager = ValuesManager('DIAN', 'notificaciones')
        
        # Inicializar validadores
        self.validators = self._initialize_validators()
        
        # Mensajes de error
        self.error_messages = {
            'invalid_integer': "No es un entero válido",
            'invalid_float': "No es un flotante válido",
            'invalid_date': "No es una fecha válida",
            'invalid_datetime': "No es una fecha y hora válida",
            'invalid_nit': "No es un NIT válido",
            'invalid_estado_notificacion': "No se encuentra en estado de notificación",
            'invalid_proceso': "No se encuentra en proceso",
            'invalid_dependencia': "No se encuentra en dependencia"
        }
        
        logger.info(f"Procesador inicializado para {self.config.project_name}")
    
    def _initialize_validators(self) -> Dict[str, any]:
        """Inicializa los validadores específicos para DIAN notificaciones."""
        factory = ValidatorFactory()
        
        return {
            'integer': factory.create_validator('integer'),
            'float': factory.create_validator('float', min_value=0.0),
            'date': factory.create_validator('date'),
            'datetime': factory.create_validator('date'),
            'nit': factory.create_validator('nit'),
            'string': factory.create_validator('string', min_length=0),
            'estado_notificacion': self._get_estado_notificacion_validator(),
            'proceso': self._get_proceso_validator(),
            'dependencia': self._get_dependencia_validator()
        }
    
    def _get_estado_notificacion_validator(self):
        """Obtiene el validador para estados de notificación."""
        try:
            estados = self.values_manager.get_all_values('estado_notificacion')
            return ValidatorFactory.create_validator('choice', choices=estados)
        except Exception as e:
            logger.warning(f"No se pudieron cargar valores de estado_notificacion: {e}")
            # Valores por defecto
            return ValidatorFactory.create_validator('choice', choices=[
                'notificado', 'pendiente', 'devuelto', 'cancelado', 'en trámite'
            ])
    
    def _get_proceso_validator(self):
        """Obtiene el validador para procesos."""
        try:
            procesos = self.values_manager.get_all_values('proceso')
            return ValidatorFactory.create_validator('choice', choices=procesos)
        except Exception as e:
            logger.warning(f"No se pudieron cargar valores de proceso: {e}")
            # Valores por defecto
            return ValidatorFactory.create_validator('choice', choices=[
                'asistencia al cliente', 'fiscalización y liquidación', 'operación aduanera',
                'gestión masiva', 'administración de cartera', 'gestión jurídica'
            ])
    
    def _get_dependencia_validator(self):
        """Obtiene el validador para dependencias."""
        try:
            dependencias = self.values_manager.get_all_values('dependencia')
            return ValidatorFactory.create_validator('choice', choices=dependencias)
        except Exception as e:
            logger.warning(f"No se pudieron cargar valores de dependencia: {e}")
            # Valores por defecto
            return ValidatorFactory.create_validator('choice', choices=[
                'nivel central', 'dirección seccional'
            ])
    
    def normalize_column_name(self, column_name: str) -> str:
        """Normaliza nombres de columnas reemplazando espacios y caracteres especiales."""
        column_name = column_name.strip().upper()
        replacements = [
            (' ', '_'), ('-', '_'), ('Á', 'A'), ('É', 'E'), ('Í', 'I'),
            ('Ó', 'O'), ('Ú', 'U'), ('Ñ', 'N'), ('.', ''), ('/', '_'),
        ]
        for old, new in replacements:
            column_name = column_name.replace(old, new)
        return column_name
    
    def organize_headers(self, actual_headers: List[str]) -> List[str]:
        """Organiza headers según REFERENCE_HEADERS y aplica reemplazos."""
        normalized = [self.normalize_column_name(h) for h in actual_headers]

        # Aplicar reemplazos
        for i, header in enumerate(normalized):
            normalized[i] = REPLACEMENT_MAP.get(header, header)

        # Eliminar duplicados manteniendo orden
        seen = set()
        unique_headers = []
        for h in normalized:
            if h not in seen:
                seen.add(h)
                unique_headers.append(h)

        # Ordenar según REFERENCE_HEADERS
        ref_headers_normalized = [self.normalize_column_name(h) for h in REFERENCE_HEADERS]
        ordered = []
        remaining = []
        
        for ref_h in ref_headers_normalized:
            if ref_h in unique_headers:
                ordered.append(ref_h)
        remaining = [h for h in unique_headers if h not in ordered]
        return ordered + remaining
    
    def get_header_mapping(self, original_headers: List[str], organized_headers: List[str]) -> Dict[int, int]:
        """Obtiene el mapeo entre headers originales y organizados."""
        mapping = {}
        original_normalized = [self.normalize_column_name(h) for h in original_headers]
        
        for i, org_header in enumerate(organized_headers):
            try:
                orig_index = original_normalized.index(org_header)
                mapping[i] = orig_index
            except ValueError:
                # Buscar en reemplazos
                for orig, replacement in REPLACEMENT_MAP.items():
                    if replacement == org_header and orig in original_normalized:
                        mapping[i] = original_normalized.index(orig)
                        break
        
        return mapping
    
    def reorganize_row(self, row: List[str], original_headers: List[str], organized_headers: List[str]) -> List[str]:
        """Reorganiza una fila según los headers organizados."""
        mapping = self.get_header_mapping(original_headers, organized_headers)
        reorganized_row = []
        
        for i in range(len(organized_headers)):
            if i in mapping:
                reorganized_row.append(row[mapping[i]])
            else:
                reorganized_row.append("")
        
        return reorganized_row
    
    def validate_headers(self, actual_headers: List[str]) -> Tuple[bool, List[str]]:
        """Valida que los headers contengan las columnas requeridas."""
        required_columns = self.config.get_required_columns()
        missing_columns = []
        
        normalized_actual = [self.normalize_column_name(h) for h in actual_headers]
        
        for required in required_columns:
            if self.normalize_column_name(required) not in normalized_actual:
                missing_columns.append(required)
        
        return len(missing_columns) == 0, missing_columns
    
    def clean_value(self, value: str) -> str:
        """Limpia valores nulos y espacios."""
        if value is None:
            return ""
        value = str(value).strip()
        return "" if value.upper() in NULL_VALUES else value
    
    def preprocess_line(self, line: str) -> str:
        """Preprocesa línea para manejar comas y saltos internos."""
        if not line.strip():
            return line
            
        line = line.replace('\\n', TEMP_NEWLINE)
        in_quotes = False
        processed = []
        
        for char in line:
            if char == '"':
                in_quotes = not in_quotes
                processed.append(char)
            elif char == ',' and not in_quotes:
                processed.append(TEMP_COMMA)
            else:
                processed.append(char)
        
        return ''.join(processed)
    
    def postprocess_field(self, field: str) -> str:
        """Restaura caracteres especiales a su forma original."""
        return field.replace(TEMP_COMMA, ',').replace(TEMP_NEWLINE, '\n')
    
    def detect_delimiter(self, input_file: str) -> str:
        """Detecta el delimitador del archivo CSV."""
        try:
            with open(input_file, 'r', encoding=ENCODING) as f:
                first_line = f.readline().strip()
                
            # Contar diferentes delimitadores
            delimiters = [',', ';', '|', '\t']
            counts = {}
            
            for delim in delimiters:
                counts[delim] = first_line.count(delim)
            
            # Retornar el delimitador más frecuente
            detected_delimiter = max(counts, key=counts.get)
            
            if counts[detected_delimiter] > 0:
                logger.info(f"Delimitador detectado: '{detected_delimiter}'")
                return detected_delimiter
            else:
                logger.warning("No se pudo detectar delimitador, usando por defecto: '|'")
                return DELIMITER
                
        except Exception as e:
            logger.warning(f"Error detectando delimitador: {e}, usando por defecto: '|'")
            return DELIMITER
    
    def read_csv(self, input_file: str, delimiter: str = None) -> Tuple[List[str], List[List[str]]]:
        """Lee CSV con manejo de comas y saltos internos."""
        if delimiter is None:
            delimiter = self.detect_delimiter(input_file)
        
        with open(input_file, 'r', encoding=ENCODING) as f:
            processed_content = [self.preprocess_line(line) for line in f.read().splitlines()]
            reader = csv.reader(
                processed_content,
                delimiter=delimiter,
                quotechar='"',
                escapechar='\\'
            )
            
            data = [row for row in reader]
            return data[0], data[1:] if len(data) > 1 else []
    
    def _get_expected_type(self, col_name: str, type_mapping: Dict[str, List[str]]) -> str:
        """Obtiene el tipo esperado para una columna por nombre."""
        normalized_col_name = self.normalize_column_name(col_name)
        
        for type_name, columns in type_mapping.items():
            normalized_columns = [self.normalize_column_name(col) for col in columns]
            if normalized_col_name in normalized_columns:
                return type_name
        return "string"
    
    def _validate_value_modular(self, value: str, col_name: str, col_num: int, 
                               row_num: int, type_mapping: Dict[str, List[str]]) -> Tuple[str, Optional[ErrorInfo]]:
        """Valida un valor usando el sistema modular de validadores."""
        if not value:
            return value, None
        
        # Determinar el tipo esperado
        expected_type = self._get_expected_type(col_name, type_mapping)
        
        try:
            if expected_type in self.validators:
                validator = self.validators[expected_type]
                if not validator.is_valid(value):
                    error_msg = self.error_messages.get(f'invalid_{expected_type}', f"Valor inválido para tipo {expected_type}")
                    error = ErrorInfo(
                        columna=col_name, numero_columna=col_num,
                        tipo=expected_type, valor=value, fila=row_num,
                        error=error_msg
                    )
                    return value, error
            
            return value, None
            
        except Exception as e:
            error = ErrorInfo(
                columna=col_name, numero_columna=col_num,
                tipo=expected_type, valor=value, fila=row_num,
                error=str(e)
            )
            return value, error
    
    def process_csv(self, input_file: str, output_file: str, error_file: str = None, 
                   type_mapping: Dict[str, List[str]] = None, delimiter: str = None) -> None:
        """
        Procesa CSV completo con:
        - Normalización de headers
        - Validación de datos usando el sistema modular
        - Manejo de errores
        """
        try:
            logger.info(f"Iniciando procesamiento de {input_file}")
            
            header, rows = self.read_csv(input_file, delimiter)
            normalized_header = self.organize_headers(header)
            
            # Validar headers
            is_valid, missing_columns = self.validate_headers(header)
            if not is_valid:
                logger.warning(f"Columnas faltantes: {missing_columns}")
            
            errors = []
            processed_rows = []
            
            for row_num, row in enumerate(rows, start=1):
                try:
                    if len(row) != len(header):
                        raise ValueError(f"Columnas esperadas: {len(header)}, obtenidas: {len(row)}")
                    
                    processed_row = []
                    for col_num, (raw_val, col_name) in enumerate(zip(row, header), start=1):
                        value = self.postprocess_field(raw_val)
                        clean_val = self.clean_value(value)
                        
                        # Validación usando el sistema modular
                        if type_mapping:
                            clean_val, error = self._validate_value_modular(
                                clean_val, col_name, col_num, row_num, type_mapping
                            )
                            if error:
                                errors.append(error)
                        
                        processed_row.append(clean_val)
                    
                    # Reorganizar según headers normalizados
                    final_row = self.reorganize_row(processed_row, header, normalized_header)
                    processed_rows.append(final_row)
                
                except Exception as e:
                    errors.append(ErrorInfo(
                        columna="", numero_columna=0, tipo="processing",
                        valor=str(row), fila=row_num, error=str(e)
                    ))
            
            self._save_output(output_file, normalized_header, processed_rows)
            if errors and error_file:
                self._save_errors(error_file, errors)
            
            logger.info(f"Procesamiento completado. Filas procesadas: {len(processed_rows)}, Errores: {len(errors)}")
            
        except Exception as e:
            logger.error(f"Error procesando archivo: {str(e)}")
            raise Exception(f"Error procesando archivo: {str(e)}")
    
    def _save_output(self, file_path: str, header: List[str], data: List[List[str]]) -> None:
        """Guarda datos procesados en CSV."""
        with open(file_path, 'w', newline='', encoding=ENCODING) as f:
            writer = csv.writer(f, delimiter=DELIMITER)
            writer.writerow(header)
            writer.writerows(data)
    
    def _save_errors(self, file_path: str, errors: List[ErrorInfo]) -> None:
        """Guarda errores en CSV."""
        if errors:
            with open(file_path, 'w', newline='', encoding=ENCODING) as f:
                writer = csv.DictWriter(f, fieldnames=errors[0].__dict__.keys())
                writer.writeheader()
                writer.writerows([e.__dict__ for e in errors])


# Clase de compatibilidad para mantener la interfaz existente
class CSVProcessor(DIANNotificacionesProcessor):
    """
    Clase de compatibilidad que mantiene la interfaz original.
    Hereda de DIANNotificacionesProcessor para usar el nuevo sistema modular.
    """
    
    def __init__(self, validator=None):
        """
        Inicializa el procesador manteniendo compatibilidad con el código existente.
        
        Args:
            validator: Validador legacy (ignorado, usa el sistema modular)
        """
        super().__init__()
        logger.info("Usando CSVProcessor con sistema modular integrado")


# Ejemplo de uso
if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    
    # Crear procesador
    processor = DIANNotificacionesProcessor()
    
    # Mapeo de tipos para DIAN notificaciones usando nombres de columnas
    type_mapping = {
        # Columnas de tipo integer (números enteros)
        "integer": [
            "PLAN_IDENTIF_ACTO", "CODIGO_ADMINISTRACION", 
            "CODIGO_DEPENDENCIA", "ANO_CALENDARIO", "CODIGO_ACTO", 
            "ANO_ACTO", "CONSECUTIVO_ACTO", "PLANILLA_REMISION", 
            "PLANILLA_CORR", "NUMERO_EXPEDIENTE", "PERI_IMPUESTO",
            "PERI_PERIODO", "PAIS_COD_NUM_PAIS", "MUNI_CODIGO_DEPART", 
            "MUNI_CODIGO_MUNICI", "PLANILLA_REMI_ARCHIVO"
        ],
        
        # Columnas de tipo float (números decimales)
        "float": [
            "CUANTIA_ACTO"
        ],
        
        # Columnas de tipo date (fechas)
        "date": [
            "FECHA_ACTO", "FECHA_PLANILLA_REMISION", "FECHA_CITACION", 
            "FECHA_PLANILLA_CORR", "FECHA_NOTIFICACION", "FECHA_EJECUTORIA",
            "FECHA_LEVANTE", "FECHA_PLANILLA_REMI_ARCHIVO"
        ],
        
        # Columnas de tipo NIT
        "nit": ["NIT"],
        
        # Columnas de tipo string
        "string": [
            "SECCIONAL", "DEPENDENCIA", "DESCRIPCION_ACTO", "RAZON_SOCIAL",
            "DIRECCION", "FUNCIONARIO_ENVIA", "GUIA", "COD_ESTADO",
            "ESTADO_NOTIFICACION", "COD_NOTIFICACION", "MEDIO_NOTIFICACION",
            "TIPO_DOCUMENTO", "NOMBRE_APLICACION", "PAIS", "DEPARTAMENTO",
            "MUNICIPIO", "REGIMEN", "MOTIVO_LEVANTE", "NORMATIVIDAD",
            "FUNCIONARIO_RECIBE"
        ]
    }
    
    # Rutas de archivos
    base_path = os.path.expanduser("~/Documentos/ITRC/DOCUMENTOS_LIMPIAR/DIAN_NOTIFICACIONES/2024/CSV/")
    input_file = os.path.join(base_path, "consolidado_dian_notificaciones_2024.csv")
    output_file = os.path.join(base_path, "consolidado_dian_notificaciones_2024_procesado.csv")
    error_file = os.path.join(base_path, "consolidado_dian_notificaciones_2024_errores_procesamiento.csv")
    
    # Procesar archivo
    processor.process_csv(input_file, output_file, error_file, type_mapping) 