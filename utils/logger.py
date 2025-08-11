"""
Sistema de logging centralizado para ExcelSior API.

Proporciona logging estructurado con diferentes niveles
y formateo consistente para toda la aplicación.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from config.settings import LOG_LEVEL, LOG_FORMAT, TEMP_DIR

class StructuredFormatter(logging.Formatter):
    """Formateador personalizado para logs estructurados."""
    
    def format(self, record):
        # Agregar información adicional al record
        if not hasattr(record, 'component'):
            record.component = 'general'
        
        if not hasattr(record, 'operation'):
            record.operation = 'unknown'
            
        return super().format(record)

def setup_logger(
    name: str = "excelsior",
    level: Optional[str] = None,
    log_file: Optional[Path] = None
) -> logging.Logger:
    """
    Configura y retorna un logger estructurado.
    
    Args:
        name: Nombre del logger
        level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Archivo donde escribir los logs (opcional)
    
    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)
    
    # Evitar duplicar handlers
    if logger.handlers:
        return logger
    
    # Configurar nivel
    log_level = level or LOG_LEVEL
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Crear formateador
    formatter = StructuredFormatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - [%(component)s:%(operation)s] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler para archivo (si se especifica)
    if log_file:
        ensure_temp_dir()
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def get_logger(name: str = "excelsior") -> logging.Logger:
    """Obtiene un logger configurado."""
    return setup_logger(name)

class LoggerMixin:
    """Mixin para agregar logging a las clases."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = get_logger(f"{self.__class__.__module__}.{self.__class__.__name__}")
    
    def log_operation(self, operation: str, message: str, level: str = "info", **kwargs):
        """
        Registra una operación con contexto adicional.
        
        Args:
            operation: Nombre de la operación
            message: Mensaje a registrar
            level: Nivel de logging
            **kwargs: Datos adicionales para el contexto
        """
        extra = {
            'component': self.__class__.__name__,
            'operation': operation,
            **kwargs
        }
        
        log_method = getattr(self.logger, level.lower())
        log_method(message, extra=extra)

def log_function_call(func):
    """Decorador para logging automático de llamadas a funciones."""
    def wrapper(*args, **kwargs):
        logger = get_logger(f"{func.__module__}.{func.__name__}")
        
        logger.info(
            f"Llamando función {func.__name__}",
            extra={
                'component': func.__module__,
                'operation': 'function_call',
                'function': func.__name__,
                'args_count': len(args),
                'kwargs_count': len(kwargs)
            }
        )
        
        try:
            result = func(*args, **kwargs)
            logger.info(
                f"Función {func.__name__} completada exitosamente",
                extra={
                    'component': func.__module__,
                    'operation': 'function_success',
                    'function': func.__name__
                }
            )
            return result
        except Exception as e:
            logger.error(
                f"Error en función {func.__name__}: {str(e)}",
                extra={
                    'component': func.__module__,
                    'operation': 'function_error',
                    'function': func.__name__,
                    'error': str(e)
                }
            )
            raise
    
    return wrapper 