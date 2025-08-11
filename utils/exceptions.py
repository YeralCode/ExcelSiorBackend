"""
Excepciones personalizadas para ExcelSior API.

Define excepciones específicas para diferentes tipos de errores
que pueden ocurrir en el procesamiento de archivos.
"""

from typing import Optional, Dict, Any


class ExcelSiorException(Exception):
    """Excepción base para todas las excepciones de ExcelSior."""
    
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte la excepción a un diccionario para respuestas JSON."""
        return {
            "error": True,
            "message": self.message,
            "error_code": self.error_code,
            "details": self.details
        }


class FileProcessingError(ExcelSiorException):
    """Error durante el procesamiento de archivos."""
    
    def __init__(self, message: str, file_path: Optional[str] = None, **kwargs):
        super().__init__(message, error_code="FILE_PROCESSING_ERROR", **kwargs)
        self.file_path = file_path
        if file_path:
            self.details["file_path"] = file_path


class FileValidationError(ExcelSiorException):
    """Error de validación de archivos."""
    
    def __init__(self, message: str, validation_type: str, **kwargs):
        super().__init__(message, error_code="FILE_VALIDATION_ERROR", **kwargs)
        self.validation_type = validation_type
        self.details["validation_type"] = validation_type


class UnsupportedFileTypeError(FileValidationError):
    """Error cuando se intenta procesar un tipo de archivo no soportado."""
    
    def __init__(self, file_extension: str, supported_extensions: list):
        message = f"Tipo de archivo no soportado: {file_extension}. Tipos soportados: {', '.join(supported_extensions)}"
        super().__init__(message, validation_type="file_type")
        self.file_extension = file_extension
        self.supported_extensions = supported_extensions
        self.details.update({
            "file_extension": file_extension,
            "supported_extensions": supported_extensions
        })


class FileSizeError(FileValidationError):
    """Error cuando el archivo excede el tamaño máximo permitido."""
    
    def __init__(self, file_size: int, max_size: int):
        message = f"El archivo excede el tamaño máximo permitido. Tamaño: {file_size}, Máximo: {max_size}"
        super().__init__(message, validation_type="file_size")
        self.file_size = file_size
        self.max_size = max_size
        self.details.update({
            "file_size": file_size,
            "max_size": max_size
        })


class EncodingError(FileProcessingError):
    """Error de codificación de caracteres."""
    
    def __init__(self, message: str, encoding: str, **kwargs):
        super().__init__(message, error_code="ENCODING_ERROR", **kwargs)
        self.encoding = encoding
        self.details["encoding"] = encoding


class DelimiterDetectionError(FileProcessingError):
    """Error al detectar el delimitador del archivo."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, error_code="DELIMITER_DETECTION_ERROR", **kwargs)


class DataValidationError(ExcelSiorException):
    """Error de validación de datos."""
    
    def __init__(self, message: str, column: Optional[str] = None, row: Optional[int] = None, **kwargs):
        super().__init__(message, error_code="DATA_VALIDATION_ERROR", **kwargs)
        self.column = column
        self.row = row
        if column:
            self.details["column"] = column
        if row:
            self.details["row"] = row


class HeaderValidationError(DataValidationError):
    """Error de validación de encabezados."""
    
    def __init__(self, message: str, expected_headers: list, actual_headers: list, **kwargs):
        super().__init__(message, **kwargs)
        self.expected_headers = expected_headers
        self.actual_headers = actual_headers
        self.details.update({
            "expected_headers": expected_headers,
            "actual_headers": actual_headers
        })


class ConfigurationError(ExcelSiorException):
    """Error de configuración."""
    
    def __init__(self, message: str, config_key: Optional[str] = None, **kwargs):
        super().__init__(message, error_code="CONFIGURATION_ERROR", **kwargs)
        self.config_key = config_key
        if config_key:
            self.details["config_key"] = config_key


class ProjectNotFoundError(ConfigurationError):
    """Error cuando no se encuentra la configuración de un proyecto."""
    
    def __init__(self, project_name: str, available_projects: list):
        message = f"Proyecto '{project_name}' no encontrado. Proyectos disponibles: {', '.join(available_projects)}"
        super().__init__(message, config_key="project_name")
        self.project_name = project_name
        self.available_projects = available_projects
        self.details.update({
            "project_name": project_name,
            "available_projects": available_projects
        })


class TimeoutError(ExcelSiorException):
    """Error de timeout en operaciones largas."""
    
    def __init__(self, message: str, timeout_seconds: int, **kwargs):
        super().__init__(message, error_code="TIMEOUT_ERROR", **kwargs)
        self.timeout_seconds = timeout_seconds
        self.details["timeout_seconds"] = timeout_seconds


class MemoryError(ExcelSiorException):
    """Error por falta de memoria."""
    
    def __init__(self, message: str, memory_usage: Optional[int] = None, **kwargs):
        super().__init__(message, error_code="MEMORY_ERROR", **kwargs)
        self.memory_usage = memory_usage
        if memory_usage:
            self.details["memory_usage"] = memory_usage


def handle_exception(func):
    """Decorador para manejo centralizado de excepciones."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ExcelSiorException:
            # Re-lanzar excepciones personalizadas sin modificar
            raise
        except Exception as e:
            # Convertir excepciones genéricas a ExcelSiorException
            raise ExcelSiorException(
                message=f"Error inesperado: {str(e)}",
                error_code="UNEXPECTED_ERROR",
                details={"original_error": str(e), "error_type": type(e).__name__}
            )
    return wrapper 