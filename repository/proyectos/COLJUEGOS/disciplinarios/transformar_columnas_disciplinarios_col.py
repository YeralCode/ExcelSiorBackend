"""
Transformador de columnas para archivos disciplinarios de COLJUEGOS.
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
NULL_VALUES = {"$null$", "nan", "NULL", "N.A", "null", "N.A."}
DELIMITER = '|'
ENCODING = 'utf-8'
TEMP_COMMA_REPLACEMENT = '\uE000'
TEMP_NEWLINE = '⏎'
TEMP_COMMA = '\uE000'

# Encabezados de referencia para COLJUEGOS disciplinarios
REFERENCE_HEADERS = [
    "EXPEDIENTE",
    "FECHA_DE_RADICACION",
    "FECHA_DE_LOS_HECHOS",
    "FECHA_DE_INDAGACION_PRELIMINAR",
    "FECHA_DE_INVESTIGACION_DISCIPLINARIA",
    "IMPLICADO",
    "DOCUMENTO_DEL_IMPLICADO",
    "DEPARTAMENTO_DE_LOS_HECHOS",
    "CIUDAD_DE_LOS_HECHOS",
    "DIRECCION_SECCIONAL",
    "DEPENDENCIA",
    "PROCESO",
    "SUBPROCESO",
    "PROCEDIMIENTO",
    "CARGO",
    "ORIGEN",
    "CONDUCTA",
    "ETAPA_PROCESAL",
    "FECHA_DE_FALLO",
    "SANCION_IMPUESTA",
    "HECHOS",
    "DECISION_DE_LA_INVESTIGACION",
    "TIPO_DE_PROCESO_AFECTADO",
    "SENALADOS_O_VINCULADOS_CON_LA_INVESTIGACION",
    "ADECUACION_TIPICA",
    "ABOGADO",
    "SENTIDO_DEL_FALLO",
    "QUEJOSO",
    "DOC_QUEJOSO",
    "TIPO_DE_PROCESO",
    "FECHA_CITACION",
    "FECHA_DE_CARGOS",
    "FECHA_DE_CIERRE_INVESTIGACION"
]

# Mapeo de reemplazo de columnas
REPLACEMENT_MAP = {
    # Agregar mapeos específicos si es necesario
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


class COLJUEGOSDisciplinariosProcessor:
    """
    Procesador específico para archivos disciplinarios de COLJUEGOS.
    Integrado con el sistema modular de configuraciones.
    """
    
    def __init__(self, config: Optional[ProjectConfigBase] = None):
        """
        Inicializa el procesador.
        
        Args:
            config: Configuración específica del proyecto (opcional)
        """
        # Obtener configuración del proyecto
        self.config = config or get_project_config('COLJUEGOS', 'disciplinarios')
        
        # Inicializar gestor de valores
        self.values_manager = ValuesManager('COLJUEGOS', 'disciplinarios')
        
        # Inicializar validadores
        self.validators = self._initialize_validators()
        
        # Mensajes de error
        self.error_messages = {
            'invalid_integer': "No es un entero válido",
            'invalid_float': "No es un flotante válido",
            'invalid_date': "No es una fecha válida",
            'invalid_datetime': "No es una fecha y hora válida",
            'invalid_nit': "No es un NIT válido",
            'invalid_direccion_seccional': "No se encuentra en direccion seccional",
            'invalid_columns': "Número de columnas no coincide con el encabezado",
            "invalid_proceso": "No se encuentra en proceso"
        }
        
        logger.info(f"Procesador inicializado para {self.config.project_name}")
    
    def _initialize_validators(self) -> Dict[str, any]:
        """Inicializa los validadores específicos para COLJUEGOS disciplinarios."""
        factory = ValidatorFactory()
        
        return {
            'integer': factory.create_validator('integer'),
            'float': factory.create_validator('float', min_value=0.0),
            'date': factory.create_validator('date'),
            'datetime': factory.create_validator('date'),
            'nit': factory.create_validator('nit'),
            'string': factory.create_validator('string', min_length=0),
            'direccion_seccional': self._get_direccion_seccional_validator(),
            'proceso': self._get_proceso_validator()
        }
    
    def _get_direccion_seccional_validator(self):
        """Obtiene el validador para direcciones seccionales."""
        try:
            direcciones = self.values_manager.get_all_values('direccion_seccional')
            return ValidatorFactory.create_validator('choice', choices=direcciones)
        except Exception as e:
            logger.warning(f"No se pudieron cargar valores de direccion_seccional: {e}")
            # Valores por defecto
            return ValidatorFactory.create_validator('choice', choices=[
                "gerencia control a las operaciones ilegales",
                "gerencia de cobro",
                "gerencia financiera",
                "gerencia seguimiento contractual",
                "vicepresidencia de desarrollo organizacional",
                "vicepresidencia de operaciones",
                "vicepresidencia desarrollo comercial"
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
                "cobro coactivo",
                "contratacion misional",
                "control",
                "control operaciones ilegales",
                "gestion juridica",
                "incumplimiento contractual",
                "seguimiento contractual",
                "segunda instancia"
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
    
    def read_csv(self, input_file: str) -> Tuple[List[str], List[List[str]]]:
        """Lee CSV con manejo de comas y saltos internos."""
        with open(input_file, 'r', encoding=ENCODING) as f:
            processed_content = [self.preprocess_line(line) for line in f.read().splitlines()]
            reader = csv.reader(
                processed_content,
                delimiter=DELIMITER,
                quotechar='"',
                escapechar='\\'
            )
            
            data = [row for row in reader]
            return data[0], data[1:] if len(data) > 1 else []
    
    def process_csv(self, input_file: str, output_file: str, error_file: str = None, 
                   type_mapping: Dict[str, List[int]] = None) -> None:
        """
        Procesa CSV completo con:
        - Normalización de headers
        - Validación de datos usando el sistema modular
        - Manejo de errores
        """
        try:
            logger.info(f"Iniciando procesamiento de {input_file}")
            
            header, rows = self.read_csv(input_file)
            normalized_header = self.organize_headers(header)
            
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
                    final_row = self._reorganize_row(processed_row, header, normalized_header)
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
    
    def _validate_value_modular(self, value: str, col_name: str, col_num: int, 
                               row_num: int, type_mapping: Dict[str, List[int]]) -> Tuple[str, Optional[ErrorInfo]]:
        """Valida un valor usando el sistema modular de validadores."""
        if not value:
            return value, None
        
        # Determinar el tipo esperado
        expected_type = self._get_expected_type(col_num, type_mapping)
        
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
    
    def _get_expected_type(self, col_num: int, type_mapping: Dict[str, List[int]]) -> str:
        """Obtiene el tipo esperado para una columna."""
        for type_name, columns in type_mapping.items():
            if col_num in columns:
                return type_name
        return "string"
    
    def _reorganize_row(self, row: List[str], original_headers: List[str], 
                       final_headers: List[str]) -> List[str]:
        """Reorganiza una fila según los headers finales."""
        header_map = {self.normalize_column_name(h): i for i, h in enumerate(original_headers)}
        final_row = []
        for header in final_headers:
            norm_header = self.normalize_column_name(header)
            if norm_header in header_map:
                final_row.append(row[header_map[norm_header]])
            else:
                # Buscar posibles mapeos alternativos
                for orig, replacement in REPLACEMENT_MAP.items():
                    if replacement == header and orig in header_map:
                        final_row.append(row[header_map[orig]])
                        break
                else:
                    final_row.append("")

        return final_row
    
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
class CSVProcessor(COLJUEGOSDisciplinariosProcessor):
    """
    Clase de compatibilidad que mantiene la interfaz original.
    Hereda de COLJUEGOSDisciplinariosProcessor para usar el nuevo sistema modular.
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
    processor = COLJUEGOSDisciplinariosProcessor()
    
    # Mapeo de tipos para COLJUEGOS disciplinarios
    type_mapping = {
        "int": [],
        "float": [],
        "date": [],
        "datetime": [4, 5, 6, 7, 21, 33, 34, 35],
        "str": [
            1, 2, 3, 8, 10, 11, 13, 15, 16, 17, 18, 19, 20, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32,
        ],
        "str-sin-caracteres-especiales": [],
        "nit": [9],
        "choice_direccion_seccional": [12],
        "choice_proceso": [14]
    }
    
    # Rutas de archivos
    base_path = os.path.expanduser("~/Documentos/ITRC/DOCUMENTOS_LIMPIAR/copia_COLJUEGOS_DISCIPLINARIOS/2024/CSV/")
    input_file = os.path.join(base_path, "consolidado_coljuegos_disciplinarios_2024.csv")
    output_file = os.path.join(base_path, "consolidado_coljuegos_disciplinarios_2024_procesado.csv")
    error_file = os.path.join(base_path, "consolidado_coljuegos_disciplinarios_2024_errores_procesamiento.csv")
    
    # Procesar archivo
    processor.process_csv(input_file, output_file, error_file, type_mapping)


