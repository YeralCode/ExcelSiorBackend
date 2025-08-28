"""
Procesador CSV simple y mantenible para limpieza de archivos.
Sigue principios SOLID y es fácil de entender y mantener.
"""

import csv
import os
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

# Constantes
NULL_VALUES = {"$null$", "nan", "NULL", "N.A", "null", "N.A.", "n/a", "n/a."}
DEFAULT_DELIMITER = '|'
DEFAULT_ENCODING = 'utf-8'


@dataclass
class ValidationError:
    """Información de error de validación."""
    columna: str
    valor: str
    fila: int
    tipo_esperado: str
    mensaje: str


class DataValidator(ABC):
    """Interfaz abstracta para validadores de datos."""
    
    @abstractmethod
    def validate(self, value: str) -> Tuple[str, bool]:
        """
        Valida un valor.
        
        Returns:
            Tupla (valor_limpio, es_valido)
        """
        pass


class DateValidator(DataValidator):
    """Validador para fechas."""
    
    def validate(self, value: str) -> Tuple[str, bool]:
        if not value or value.strip() == "":
            return value, True
        
        # Validación simple de fecha (formato YYYY-MM-DD)
        try:
            if len(value) == 10 and value.count('-') == 2:
                year, month, day = value.split('-')
                if len(year) == 4 and len(month) == 2 and len(day) == 2:
                    if 1900 <= int(year) <= 2100 and 1 <= int(month) <= 12 and 1 <= int(day) <= 31:
                        return value, True
        except:
            pass
        
        return value, False


class NITValidator(DataValidator):
    """Validador para NIT."""
    
    def validate(self, value: str) -> Tuple[str, bool]:
        if not value or value.strip() == "":
            return value, True
        
        # Limpiar caracteres especiales
        clean_value = ''.join(c for c in value if c.isdigit())
        
        # Validar que tenga entre 8 y 15 dígitos
        if 8 <= len(clean_value) <= 15:
            return clean_value, True
        
        return value, False


class ChoiceValidator(DataValidator):
    """Validador para valores de elección."""
    
    def __init__(self, choices: List[str], replacement_map: Dict[str, str] = None):
        self.choices = [choice.upper() for choice in choices]
        self.replacement_map = replacement_map or {}
    
    def validate(self, value: str) -> Tuple[str, bool]:
        if not value or value.strip() == "":
            return value, True
        
        upper_value = value.upper().strip()
        
        # Verificar si el valor está en las opciones válidas
        if upper_value in self.choices:
            return value, True
        
        # Verificar si hay un reemplazo válido
        if upper_value in self.replacement_map:
            return self.replacement_map[upper_value], True
        
        return value, False


class StringValidator(DataValidator):
    """Validador para cadenas de texto."""
    
    def __init__(self, min_length: int = 0, max_length: int = None):
        self.min_length = min_length
        self.max_length = max_length
    
    def validate(self, value: str) -> Tuple[str, bool]:
        if value is None:
            return "", True
        
        clean_value = str(value).strip()
        
        if len(clean_value) < self.min_length:
            return clean_value, False
        
        if self.max_length and len(clean_value) > self.max_length:
            return clean_value, False
        
        return clean_value, True


class CSVProcessor:
    """
    Procesador CSV simple y mantenible.
    
    Responsabilidades:
    1. Leer archivo CSV
    2. Normalizar headers
    3. Validar datos según type_mapping
    4. Generar archivo limpio y archivo de errores
    """
    
    def __init__(self, 
                 reference_headers: List[str],
                 type_mapping: Dict[str, List[str]],
                 validators: Dict[str, DataValidator] = None,
                 delimiter: str = None,
                 encoding: str = DEFAULT_ENCODING):
        """
        Inicializa el procesador.
        
        Args:
            reference_headers: Headers de referencia para organizar las columnas
            type_mapping: Mapeo de tipos por nombre de columna
            validators: Diccionario de validadores por tipo
            delimiter: Delimitador del CSV (se auto-detecta si es None)
            encoding: Encoding del archivo
        """
        self.reference_headers = [h.upper().strip() for h in reference_headers]
        self.type_mapping = type_mapping
        self.validators = validators or self._create_default_validators()
        self.delimiter = delimiter
        self.encoding = encoding
        
        logger.info(f"CSVProcessor inicializado con {len(reference_headers)} headers de referencia")
    
    def _create_default_validators(self) -> Dict[str, DataValidator]:
        """Crea validadores por defecto."""
        return {
            'datetime': DateValidator(),
            'date': DateValidator(),
            'nit': NITValidator(),
            'string': StringValidator(),
            'str': StringValidator(),
        }
    
    def detect_delimiter(self, file_path: str) -> str:
        """Detecta automáticamente el delimitador del archivo."""
        try:
            with open(file_path, 'r', encoding=self.encoding) as f:
                first_line = f.readline().strip()
            
            delimiters = [',', ';', '|', '\t']
            counts = {delim: first_line.count(delim) for delim in delimiters}
            
            detected = max(counts, key=counts.get)
            if counts[detected] > 0:
                logger.info(f"Delimitador detectado: '{detected}'")
                return detected
        except Exception as e:
            logger.warning(f"Error detectando delimitador: {e}")
        
        logger.info(f"Usando delimitador por defecto: '{DEFAULT_DELIMITER}'")
        return DEFAULT_DELIMITER
    
    def normalize_column_name(self, column_name: str) -> str:
        """Normaliza nombres de columnas."""
        if not column_name:
            return ""
        
        # Convertir a mayúsculas y reemplazar caracteres especiales
        normalized = column_name.upper().strip()
        replacements = [
            (' ', '_'), ('-', '_'), ('Á', 'A'), ('É', 'E'), ('Í', 'I'),
            ('Ó', 'O'), ('Ú', 'U'), ('Ñ', 'N'), ('.', ''), ('/', '_')
        ]
        
        for old, new in replacements:
            normalized = normalized.replace(old, new)
        
        return normalized
    
    def organize_headers(self, actual_headers: List[str]) -> List[str]:
        """Organiza headers según la referencia y elimina duplicados."""
        # Normalizar headers actuales
        normalized_headers = [self.normalize_column_name(h) for h in actual_headers]
        
        # Eliminar duplicados manteniendo orden
        seen = set()
        unique_headers = []
        for h in normalized_headers:
            if h not in seen:
                seen.add(h)
                unique_headers.append(h)
        
        # Ordenar según headers de referencia
        ordered = []
        remaining = []
        
        for ref_header in self.reference_headers:
            if ref_header in unique_headers:
                ordered.append(ref_header)
        
        # Agregar headers que no están en la referencia
        remaining = [h for h in unique_headers if h not in ordered]
        
        return ordered + remaining
    
    def clean_value(self, value: str) -> str:
        """Limpia valores nulos y espacios."""
        if value is None:
            return ""
        
        clean_value = str(value).strip()
        return "" if clean_value.upper() in NULL_VALUES else clean_value
    
    def read_csv(self, file_path: str) -> Tuple[List[str], List[List[str]]]:
        """Lee el archivo CSV y retorna headers y filas."""
        delimiter = self.delimiter or self.detect_delimiter(file_path)
        
        with open(file_path, 'r', encoding=self.encoding) as f:
            reader = csv.reader(f, delimiter=delimiter, quotechar='"')
            data = list(reader)
            
            if not data:
                return [], []
            
            headers = data[0]
            rows = data[1:] if len(data) > 1 else []
            
            # Normalizar headers
            normalized_headers = [self.normalize_column_name(h) for h in headers]
            
            logger.info(f"Archivo leído: {len(normalized_headers)} headers, {len(rows)} filas")
            return normalized_headers, rows
    
    def validate_row(self, row: List[str], headers: List[str], row_number: int) -> Tuple[List[str], List[ValidationError]]:
        """
        Valida una fila completa.
        
        Returns:
            Tupla (fila_procesada, errores_encontrados)
        """
        processed_row = []
        errors = []
        
        for col_index, (value, header) in enumerate(zip(row, headers)):
            clean_value = self.clean_value(value)
            
            # Buscar el tipo esperado para esta columna
            expected_type = self._get_expected_type(header)
            
            if expected_type and clean_value:
                # Validar el valor
                validator = self.validators.get(expected_type)
                if validator:
                    validated_value, is_valid = validator.validate(clean_value)
                    
                    if is_valid:
                        processed_row.append(validated_value)
                    else:
                        # Crear error de validación
                        error = ValidationError(
                            columna=header,
                            valor=clean_value,
                            fila=row_number,
                            tipo_esperado=expected_type,
                            mensaje=f"Valor '{clean_value}' no es válido para tipo '{expected_type}'"
                        )
                        errors.append(error)
                        processed_row.append(clean_value)  # Mantener valor original
                    continue
            
            # Si no hay validador o el valor está vacío, usar valor limpio
            processed_row.append(clean_value)
        
        return processed_row, errors
    
    def _get_expected_type(self, column_name: str) -> Optional[str]:
        """Obtiene el tipo esperado para una columna."""
        for type_name, columns in self.type_mapping.items():
            if column_name in columns:
                return type_name
        return None
    
    def reorganize_row(self, row: List[str], original_headers: List[str], 
                      final_headers: List[str]) -> List[str]:
        """Reorganiza una fila según los headers finales."""
        header_map = {h: i for i, h in enumerate(original_headers)}
        reorganized_row = []
        
        for final_header in final_headers:
            if final_header in header_map:
                reorganized_row.append(row[header_map[final_header]])
            else:
                reorganized_row.append("")  # Valor por defecto
        
        return reorganized_row
    
    def process_csv(self, input_file: str, output_file: str, error_file: str = None) -> Dict[str, Any]:
        """
        Procesa el archivo CSV completo.
        
        Returns:
            Diccionario con estadísticas del procesamiento
        """
        logger.info(f"Iniciando procesamiento de {input_file}")
        
        try:
            # Leer archivo
            headers, rows = self.read_csv(input_file)
            if not headers:
                raise ValueError("El archivo CSV está vacío o no tiene headers")
            
            # Organizar headers
            organized_headers = self.organize_headers(headers)
            logger.info(f"Headers organizados: {len(organized_headers)}")
            
            # Procesar filas
            processed_rows = []
            all_errors = []
            
            for row_index, row in enumerate(rows, start=1):
                if len(row) != len(headers):
                    # Error de estructura
                    error = ValidationError(
                        columna="ESTRUCTURA",
                        valor=str(row),
                        fila=row_index,
                        tipo_esperado="ESTRUCTURA",
                        mensaje=f"Fila tiene {len(row)} columnas, se esperaban {len(headers)}"
                    )
                    all_errors.append(error)
                    continue
                
                # Validar fila
                processed_row, row_errors = self.validate_row(row, headers, row_index)
                all_errors.extend(row_errors)
                
                # Reorganizar según headers finales
                final_row = self.reorganize_row(processed_row, headers, organized_headers)
                processed_rows.append(final_row)
            
            # Guardar archivo procesado
            self._save_csv(output_file, organized_headers, processed_rows)
            
            # Guardar errores si los hay
            if all_errors and error_file:
                self._save_errors(error_file, all_errors)
            
            # Estadísticas
            stats = {
                'filas_procesadas': len(processed_rows),
                'filas_con_errores': len([e for e in all_errors if e.columna != "ESTRUCTURA"]),
                'errores_estructura': len([e for e in all_errors if e.columna == "ESTRUCTURA"]),
                'total_errores': len(all_errors),
                'headers_originales': len(headers),
                'headers_finales': len(organized_headers)
            }
            
            logger.info(f"Procesamiento completado: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Error procesando archivo: {str(e)}")
            raise
    
    def _save_csv(self, file_path: str, headers: List[str], rows: List[List[str]]) -> None:
        """Guarda datos en formato CSV."""
        with open(file_path, 'w', newline='', encoding=self.encoding) as f:
            writer = csv.writer(f, delimiter=self.delimiter or DEFAULT_DELIMITER)
            writer.writerow(headers)
            writer.writerows(rows)
        
        logger.info(f"Archivo guardado: {file_path}")
    
    def _save_errors(self, file_path: str, errors: List[ValidationError]) -> None:
        """Guarda errores en formato CSV."""
        if not errors:
            return
        
        with open(file_path, 'w', newline='', encoding=self.encoding) as f:
            fieldnames = ['columna', 'valor', 'fila', 'tipo_esperado', 'mensaje']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for error in errors:
                writer.writerow({
                    'columna': error.columna,
                    'valor': error.valor,
                    'fila': error.fila,
                    'tipo_esperado': error.tipo_esperado,
                    'mensaje': error.mensaje
                })
        
        logger.info(f"Archivo de errores guardado: {file_path}")


# Funciones de conveniencia para uso directo
def process_csv_simple(input_file: str, 
                      output_file: str, 
                      reference_headers: List[str],
                      type_mapping: Dict[str, List[str]],
                      error_file: str = None,
                      custom_validators: Dict[str, DataValidator] = None,
                      delimiter: str = None) -> Dict[str, Any]:
    """
    Función de conveniencia para procesar archivos CSV.
    
    Args:
        input_file: Archivo de entrada
        output_file: Archivo de salida
        reference_headers: Headers de referencia
        type_mapping: Mapeo de tipos por columna
        error_file: Archivo de errores (opcional)
        custom_validators: Validadores personalizados (opcional)
        delimiter: Delimitador específico (opcional)
    
    Returns:
        Estadísticas del procesamiento
    """
    processor = CSVProcessor(
        reference_headers=reference_headers,
        type_mapping=type_mapping,
        validators=custom_validators,
        delimiter=delimiter
    )
    
    return processor.process_csv(input_file, output_file, error_file)


# Ejemplo de uso
if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    
    # Ejemplo de configuración para DIAN disciplinarios
    reference_headers = [
        'NOMBRE_ARCHIVO', 'MES_REPORTE', 'EXPEDIENTE', 'FECHA_RADICACION',
        'FECHA_HECHOS', 'IMPLICADO', 'IDENTIFICACION', 'DEPARTAMENTO',
        'CIUDAD', 'DIRECCION_SECCIONAL', 'PROCESO', 'CARGO'
    ]
    
    type_mapping = {
        "datetime": ["FECHA_RADICACION", "FECHA_HECHOS"],
        "str": ["NOMBRE_ARCHIVO", "MES_REPORTE", "EXPEDIENTE", "IMPLICADO", "CARGO"],
        "nit": ["IDENTIFICACION"],
        "departamento": ["DEPARTAMENTO"],
        "ciudad": ["CIUDAD"],
        "direccion_seccional": ["DIRECCION_SECCIONAL"],
        "proceso": ["PROCESO"]
    }
    
    # Validadores personalizados para departamentos y ciudades
    custom_validators = {
        'departamento': ChoiceValidator([
            'ANTIOQUIA', 'ATLANTICO', 'BOGOTA', 'BOLIVAR', 'BOYACA', 'CALDAS'
        ]),
        'ciudad': ChoiceValidator([
            'MEDELLIN', 'BARRANQUILLA', 'BOGOTA', 'CARTAGENA', 'TUNJA', 'MANIZALES'
        ]),
        'direccion_seccional': ChoiceValidator([
            'nivel central', 'direccion seccional de impuestos de bogota'
        ]),
        'proceso': ChoiceValidator([
            'proceso 1', 'proceso 2', 'proceso 3'
        ])
    }
    
    # Procesar archivo
    try:
        stats = process_csv_simple(
            input_file="archivo_entrada.csv",
            output_file="archivo_salida.csv",
            reference_headers=reference_headers,
            type_mapping=type_mapping,
            error_file="archivo_errores.csv",
            custom_validators=custom_validators
        )
        
        print(f"Procesamiento completado: {stats}")
        
    except Exception as e:
        print(f"Error: {e}") 