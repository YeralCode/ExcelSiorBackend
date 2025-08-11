"""
Procesador CSV unificado que utiliza el patrón Abstract Factory.
Elimina la duplicación de código y proporciona una interfaz unificada para todos los proyectos.
"""

import csv
import os
from typing import Dict, List, Union, Optional, Tuple, Any
from dataclasses import dataclass
import logging

from .processor_factory import create_processor, CSVProcessorBase
from .factory import get_project_config

logger = logging.getLogger(__name__)

# Constantes
NULL_VALUES = {"$null$", "nan", "NULL", "N.A", "null", "N.A.", "n/a", "n/a."}
DELIMITER = '|'
ENCODING = 'utf-8'


@dataclass
class ErrorInfo:
    """Información de error para el procesamiento."""
    columna: str
    numero_columna: int
    tipo: str
    valor: str
    fila: int
    error: str


class UnifiedCSVProcessor:
    """
    Procesador CSV unificado que utiliza el patrón Abstract Factory.
    Proporciona una interfaz única para procesar archivos CSV de cualquier proyecto.
    """
    
    def __init__(self, project_code: str, module_name: str, config: Optional[Any] = None):
        """
        Inicializa el procesador unificado.
        
        Args:
            project_code: Código del proyecto (DIAN, COLJUEGOS, UGPP)
            module_name: Nombre del módulo (disciplinarios, pqr, notificaciones, etc.)
            config: Configuración opcional del proyecto
        """
        logger.info(f"UnifiedCSVProcessor.__init__ - project_code: {project_code}, module_name: {module_name}")
        
        self.project_code = project_code.upper()
        self.module_name = module_name.lower()
        
        # Crear el procesador específico del proyecto
        try:
            self.processor = create_processor(self.project_code, self.module_name, config)
            logger.info(f"Procesador creado exitosamente para {self.project_code}:{self.module_name}")
        except Exception as e:
            logger.error(f"Error creando procesador para {self.project_code}:{self.module_name}: {str(e)}")
            raise
        
        logger.info(f"Procesador unificado inicializado para {project_code}:{module_name}")
    
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
            processed_content = [self.processor.preprocess_line(line) for line in f.read().splitlines()]
            reader = csv.reader(
                processed_content,
                delimiter=delimiter,
                quotechar='"',
                escapechar='\\'
            )
            
            data = [row for row in reader]
            if len(data) > 0:
                # Limpiar los headers usando normalize_column_name
                cleaned_headers = [self.processor.normalize_column_name(header) for header in data[0]]
                return cleaned_headers, data[1:] if len(data) > 1 else []
            else:
                return [], []
    
    def validate_headers(self, actual_headers: List[str]) -> Tuple[bool, List[str]]:
        """Valida que los headers contengan las columnas requeridas."""
        if not self.processor.config:
            return True, []
        
        required_columns = self.processor.config.get_required_columns()
        missing_columns = []

        # Los headers ya vienen normalizados desde read_csv
        normalized_actual = actual_headers
        
        for required in required_columns:
            normalized_required = self.processor.normalize_column_name(required)
            if normalized_required not in normalized_actual:
                missing_columns.append(required)
        
        return len(missing_columns) == 0, missing_columns
    
    def get_header_mapping(self, original_headers: List[str], organized_headers: List[str]) -> Dict[int, int]:
        """Obtiene el mapeo entre headers originales y organizados."""
        mapping = {}
        # Los headers originales ya vienen normalizados desde read_csv
        original_normalized = original_headers
        
        for i, org_header in enumerate(organized_headers):
            try:
                orig_index = original_normalized.index(org_header)
                mapping[i] = orig_index
            except ValueError:
                # Buscar en reemplazos
                replacement_map = self.processor.get_replacement_map()
                for orig, replacement in replacement_map.items():
                    normalized_replacement = self.processor.normalize_column_name(replacement)
                    if normalized_replacement == org_header and orig in original_normalized:
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
    
    def process_csv(self, input_file: str, output_file: str, error_file: str = None, 
                   type_mapping: Dict[str, List[Union[int, str]]] = None, delimiter: str = None) -> None:
        """
        Procesa CSV completo usando el procesador específico del proyecto.
        
        Args:
            input_file: Archivo de entrada
            output_file: Archivo de salida
            error_file: Archivo de errores (opcional)
            type_mapping: Mapeo de tipos por columna
            delimiter: Delimitador específico (opcional)
        """
        logger.info(f"process_csv iniciado - input: {input_file}, output: {output_file}")
        
        try:
            logger.info(f"Iniciando procesamiento de {input_file}")
            
            # Leer archivo
            logger.info("Leyendo archivo CSV...")
            header, rows = self.read_csv(input_file, delimiter)
            logger.info(f"Archivo leído - headers: {len(header)}, rows: {len(rows)}")
            
            normalized_header = self.processor.organize_headers(header)
            logger.info(f"Headers normalizados: {len(normalized_header)}")
            
            # Validar headers
            is_valid, missing_columns = self.validate_headers(header)
            if not is_valid:
                logger.warning(f"Columnas faltantes: {missing_columns}")
            
            errors = []
            processed_rows = []
            
            logger.info("Procesando filas...")
            for row_num, row in enumerate(rows, start=1):
                try:
                    if len(row) != len(header):
                        raise ValueError(f"Columnas esperadas: {len(header)}, obtenidas: {len(row)}")
                    
                    processed_row = []
                    for col_num, (raw_val, col_name) in enumerate(zip(row, header), start=1):
                        value = self.processor.postprocess_field(raw_val)
                        clean_val = self.processor.clean_value(value)
                        
                        # Validación usando el sistema modular
                        if type_mapping:
                            clean_val, error = self._validate_value_modular(
                                clean_val, col_name, col_num, row_num, type_mapping
                            )
                            if error:
                                errors.append(error)
                                # Reemplazar valor inválido por None o cadena vacía
                                clean_val = None
                        
                        processed_row.append(clean_val)
                    
                    # Reorganizar según headers normalizados
                    final_row = self.reorganize_row(processed_row, header, normalized_header)
                    processed_rows.append(final_row)
                
                except Exception as e:
                    errors.append(ErrorInfo(
                        columna="", numero_columna=0, tipo="processing",
                        valor=str(row), fila=row_num, error=str(e)
                    ))
            
            logger.info(f"Filas procesadas: {len(processed_rows)}, Errores: {len(errors)}")
            
            # Guardar resultados
            logger.info("Guardando archivo de salida...")
            self._save_output(output_file, normalized_header, processed_rows)
            
            if errors and error_file:
                logger.info("Guardando archivo de errores...")
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
    
    def get_project_info(self) -> Dict[str, Any]:
        """Obtiene información del proyecto y módulo."""
        return {
            'project_code': self.project_code,
            'module_name': self.module_name,
            'project_name': self.processor.config.project_name if self.processor.config else None,
            'reference_headers': self.processor.get_reference_headers(),
            'replacement_map': self.processor.get_replacement_map(),
            'available_validators': list(self.processor.validators.keys()) if self.processor.validators else []
        }

    def _validate_value_modular(self, value: str, col_name: str, col_num: int, 
                               row_num: int, type_mapping: Dict[str, List[str]]) -> tuple[str, Optional[Any]]:
        """
        Valida un valor usando el sistema modular con nombres de columnas.
        
        Args:
            value: Valor a validar
            col_name: Nombre de la columna
            col_num: Número de columna (para compatibilidad)
            row_num: Número de fila
            type_mapping: Mapeo de tipos por nombre de columna
            
        Returns:
            Tupla (valor_limpio, error_info)
        """
        # Normalizar nombre de columna
        normalized_col_name = self.processor.normalize_column_name(col_name)
        
        # Buscar el tipo esperado por nombre de columna
        expected_type = self._get_expected_type_by_name(normalized_col_name, type_mapping)
        
        if not expected_type:
            return value, None
        
        # Obtener validador
        validator = self.processor.validators.get(expected_type)
        if not validator:
            return value, None
        
        # Validar valor
        try:
            validated_value = validator.validate(value)
            
            # Si el validador devuelve None, verificar si hay errores
            if validated_value is None:
                # Obtener los errores del validador
                errors = validator.get_errors()
                
                # Si hay errores, crear objeto de error
                if errors:
                    error_msg = errors[0] if errors else f"Error de validación en {expected_type}"
                    error = self._create_error(col_name, col_num, expected_type, value, row_num, error_msg)
                    return value, error
                else:
                    # Si no hay errores, significa que el validador retornó None intencionalmente
                    # (como en el caso de NITValidator para frases inválidas)
                    # No generar error, usar None como valor válido
                    return None, None
            
            # Si la validación fue exitosa, devolver el valor limpio
            return validated_value, None
            
        except Exception as e:
            error = self._create_error(col_name, col_num, expected_type, value, row_num, str(e))
            return value, error
    
    def _get_expected_type_by_name(self, col_name: str, type_mapping: Dict[str, List[str]]) -> str:
        """
        Obtiene el tipo esperado para una columna por su nombre.
        
        Args:
            col_name: Nombre de la columna normalizado
            type_mapping: Mapeo de tipos por nombre de columna
            
        Returns:
            Tipo esperado o cadena vacía si no se encuentra
        """
        for type_name, column_names in type_mapping.items():
            if col_name in column_names:
                return type_name
        return ""
    
    def _create_error(self, col_name: str, col_num: int, expected_type: str, 
                     value: str, row_num: int, error_msg: str) -> ErrorInfo:
        """
        Crea un objeto ErrorInfo para reportar errores de validación.
        
        Args:
            col_name: Nombre de la columna
            col_num: Número de columna
            expected_type: Tipo esperado
            value: Valor que causó el error
            row_num: Número de fila
            error_msg: Mensaje de error
            
        Returns:
            Objeto ErrorInfo
        """
        return ErrorInfo(
            columna=col_name,
            numero_columna=col_num,
            tipo=expected_type,
            valor=value,
            fila=row_num,
            error=error_msg
        )


# Clase de compatibilidad para mantener la interfaz existente
class CSVProcessor(UnifiedCSVProcessor):
    """
    Clase de compatibilidad que mantiene la interfaz original.
    Hereda de UnifiedCSVProcessor para usar el nuevo sistema unificado.
    """
    
    def __init__(self, project_code: str, module_name: str, validator=None):
        """
        Inicializa el procesador manteniendo compatibilidad con el código existente.
        
        Args:
            project_code: Código del proyecto
            module_name: Nombre del módulo
            validator: Validador legacy (ignorado, usa el sistema modular)
        """
        super().__init__(project_code, module_name)
        logger.info(f"Usando CSVProcessor unificado para {project_code}:{module_name}")


# Funciones de conveniencia para uso directo
def process_csv_file(project_code: str, module_name: str, input_file: str, 
                    output_file: str, error_file: str = None, 
                    type_mapping: Dict[str, List[Union[int, str]]] = None) -> None:
    """
    Función de conveniencia para procesar archivos CSV.
    
    Args:
        project_code: Código del proyecto
        module_name: Nombre del módulo
        input_file: Archivo de entrada
        output_file: Archivo de salida
        error_file: Archivo de errores (opcional)
        type_mapping: Mapeo de tipos por columna
    """
    logger.info(f"process_csv_file iniciado - project_code: {project_code}, module_name: {module_name}")
    logger.info(f"Archivos - input: {input_file}, output: {output_file}, error: {error_file}")
    
    try:
        processor = UnifiedCSVProcessor(project_code, module_name)
        logger.info("UnifiedCSVProcessor creado exitosamente")
        
        processor.process_csv(input_file, output_file, error_file, type_mapping)
        logger.info("process_csv completado exitosamente")
        
    except Exception as e:
        logger.error(f"Error en process_csv_file: {str(e)}")
        raise


def get_processor_info(project_code: str, module_name: str) -> Dict[str, Any]:
    """
    Función de conveniencia para obtener información del procesador.
    
    Args:
        project_code: Código del proyecto
        module_name: Nombre del módulo
        
    Returns:
        Información del procesador
    """
    processor = UnifiedCSVProcessor(project_code, module_name)
    return processor.get_project_info()


# Ejemplo de uso
if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    
    # Ejemplo de procesamiento de DIAN notificaciones
    print("=== Procesamiento de DIAN Notificaciones ===")
    processor_dian = UnifiedCSVProcessor('DIAN', 'notificaciones')
    info_dian = processor_dian.get_project_info()
    print(f"Proyecto: {info_dian['project_name']}")
    print(f"Headers de referencia: {len(info_dian['reference_headers'])}")
    print(f"Validadores disponibles: {info_dian['available_validators']}")
    
    # Ejemplo de procesamiento de COLJUEGOS disciplinarios
    print("\n=== Procesamiento de COLJUEGOS Disciplinarios ===")
    processor_coljuegos = UnifiedCSVProcessor('COLJUEGOS', 'disciplinarios')
    info_coljuegos = processor_coljuegos.get_project_info()
    print(f"Proyecto: {info_coljuegos['project_name']}")
    print(f"Headers de referencia: {len(info_coljuegos['reference_headers'])}")
    print(f"Validadores disponibles: {info_coljuegos['available_validators']}")
    
    # Ejemplo de procesamiento de DIAN disciplinarios
    print("\n=== Procesamiento de DIAN Disciplinarios ===")
    processor_dian_disc = UnifiedCSVProcessor('DIAN', 'disciplinarios')
    info_dian_disc = processor_dian_disc.get_project_info()
    print(f"Proyecto: {info_dian_disc['project_name']}")
    print(f"Headers de referencia: {len(info_dian_disc['reference_headers'])}")
    print(f"Validadores disponibles: {info_dian_disc['available_validators']}") 