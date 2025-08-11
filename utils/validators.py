"""
Sistema de validación mejorado para ExcelSior API.

Proporciona validadores reutilizables para diferentes tipos de datos
con manejo de errores estructurado y logging.
"""

import re
import unicodedata
from datetime import datetime, time, timedelta
from typing import Tuple, Dict, Union, Optional, Any, List
from dataclasses import dataclass
from utils.logger import LoggerMixin
from utils.exceptions import DataValidationError
from config.settings import NULL_VALUES, DATE_FORMATS

@dataclass
class ValidationResult:
    """Resultado de una validación."""
    is_valid: bool
    value: str
    error_message: Optional[str] = None
    normalized_value: Optional[str] = None

class BaseValidator(LoggerMixin):
    """Clase base para todos los validadores."""
    
    def __init__(self):
        super().__init__()
        self.validation_errors: List[Dict[str, Any]] = []
    
    def validate(self, value: str, **kwargs) -> ValidationResult:
        """Método base de validación que debe ser implementado por subclases."""
        raise NotImplementedError("Subclases deben implementar este método")
    
    def is_null_value(self, value: str) -> bool:
        """Verifica si un valor es considerado nulo."""
        if not value:
            return True
        return str(value).strip().lower() in NULL_VALUES
    
    def normalize_string(self, value: str) -> str:
        """Normaliza una cadena eliminando acentos y caracteres especiales."""
        if not value:
            return ""
        return unicodedata.normalize('NFKD', value.strip()).encode('ASCII', 'ignore').decode('ASCII')
    
    def clean_numeric(self, value: str) -> str:
        """Limpia valores numéricos eliminando caracteres no deseados."""
        return re.sub(r"[^\d.-eE+]", "", str(value))
    
    def log_validation_error(self, value: str, error: str, **context):
        """Registra un error de validación."""
        self.validation_errors.append({
            "value": value,
            "error": error,
            **context
        })
        self.log_operation(
            "validation_error",
            f"Error de validación: {error} para valor '{value}'",
            level="warning",
            **context
        )

class IntegerValidator(BaseValidator):
    """Validador para números enteros."""
    
    def validate(self, value: str, **kwargs) -> ValidationResult:
        """Valida si un valor es un entero válido."""
        self.log_operation("validate_integer", f"Validando entero: {value}")
        
        # Verificar valores nulos
        if self.is_null_value(value):
            return ValidationResult(is_valid=True, value="", normalized_value="")
        
        value_str = str(value).strip()
        
        # Quitar ".0" si lo tiene
        value_str = value_str.replace(".0", "")
        
        # Verificar caracteres válidos
        valor_original_limpio = re.sub(r'[^\d\s\-\.\$\,\%eE\+]', '', value_str)
        if valor_original_limpio != value_str.replace(' ', ''):
            error_msg = f"El valor '{value}' contiene caracteres no válidos para un entero"
            self.log_validation_error(value, error_msg)
            return ValidationResult(is_valid=False, value=value, error_message=error_msg)
        
        # Limpiar caracteres no numéricos
        valor_limpio = self.clean_numeric(value_str)
        
        if not valor_limpio:
            error_msg = f"El valor '{value}' no es un entero válido"
            self.log_validation_error(value, error_msg)
            return ValidationResult(is_valid=False, value=value, error_message=error_msg)
        
        try:
            numero_float = float(valor_limpio)
            
            if numero_float.is_integer():
                normalized = str(int(numero_float))
                return ValidationResult(is_valid=True, value=value, normalized_value=normalized)
            else:
                error_msg = f"El valor '{value}' no es un entero"
                self.log_validation_error(value, error_msg)
                return ValidationResult(is_valid=False, value=value, error_message=error_msg)
                
        except (ValueError, TypeError) as e:
            error_msg = f"Error al convertir '{value}' a entero: {str(e)}"
            self.log_validation_error(value, error_msg)
            return ValidationResult(is_valid=False, value=value, error_message=error_msg)

class FloatValidator(BaseValidator):
    """Validador para números flotantes."""
    
    def validate(self, value: str, **kwargs) -> ValidationResult:
        """Valida si un valor es un flotante válido."""
        self.log_operation("validate_float", f"Validando flotante: {value}")
        
        # Verificar valores nulos
        if self.is_null_value(value):
            return ValidationResult(is_valid=True, value="", normalized_value="")
        
        value_str = str(value).strip()
        
        # Quitar ".0" si lo tiene
        value_str = value_str.replace(".0", "")
        
        # Limpiar caracteres no numéricos
        valor_limpio = self.clean_numeric(value_str)
        
        if not valor_limpio:
            error_msg = f"El valor '{value}' no es un flotante válido"
            self.log_validation_error(value, error_msg)
            return ValidationResult(is_valid=False, value=value, error_message=error_msg)
        
        try:
            numero_float = float(valor_limpio)
            normalized = str(numero_float)
            return ValidationResult(is_valid=True, value=value, normalized_value=normalized)
            
        except (ValueError, TypeError) as e:
            error_msg = f"Error al convertir '{value}' a flotante: {str(e)}"
            self.log_validation_error(value, error_msg)
            return ValidationResult(is_valid=False, value=value, error_message=error_msg)

class DateValidator(BaseValidator):
    """Validador para fechas."""
    
    def validate(self, value: str, format_name: str = 'date', **kwargs) -> ValidationResult:
        """Valida si un valor es una fecha válida."""
        self.log_operation("validate_date", f"Validando fecha: {value} con formato {format_name}")
        
        # Verificar valores nulos
        if self.is_null_value(value):
            return ValidationResult(is_valid=True, value="", normalized_value="")
        
        value_str = str(value).strip()
        
        # Obtener formato de fecha
        date_format = DATE_FORMATS.get(format_name)
        if not date_format:
            error_msg = f"Formato de fecha '{format_name}' no soportado"
            self.log_validation_error(value, error_msg, format_name=format_name)
            return ValidationResult(is_valid=False, value=value, error_message=error_msg)
        
        try:
            # Intentar parsear la fecha
            parsed_date = datetime.strptime(value_str, date_format)
            normalized = parsed_date.strftime(DATE_FORMATS['date'])
            return ValidationResult(is_valid=True, value=value, normalized_value=normalized)
            
        except ValueError as e:
            error_msg = f"El valor '{value}' no es una fecha válida en formato {format_name}"
            self.log_validation_error(value, error_msg, format_name=format_name)
            return ValidationResult(is_valid=False, value=value, error_message=error_msg)

class NITValidator(BaseValidator):
    """Validador específico para NIT."""
    
    def validate(self, value: str, **kwargs) -> ValidationResult:
        """Valida si un valor es un NIT válido."""
        self.log_operation("validate_nit", f"Validando NIT: {value}")
        
        # Verificar valores nulos
        if self.is_null_value(value):
            return ValidationResult(is_valid=True, value="", normalized_value="")
        
        value_str = str(value).strip()
        
        # Limpiar caracteres no numéricos excepto guiones
        nit_limpio = re.sub(r'[^\d\-]', '', value_str)
        
        # Verificar longitud mínima
        if len(nit_limpio) < 8:
            error_msg = f"El NIT '{value}' es demasiado corto (mínimo 8 dígitos)"
            self.log_validation_error(value, error_msg)
            return ValidationResult(is_valid=False, value=value, error_message=error_msg)
        
        # Verificar que solo contenga números y guiones
        if not re.match(r'^[\d\-]+$', nit_limpio):
            error_msg = f"El NIT '{value}' contiene caracteres no válidos"
            self.log_validation_error(value, error_msg)
            return ValidationResult(is_valid=False, value=value, error_message=error_msg)
        
        # Normalizar (quitar guiones y espacios)
        normalized = re.sub(r'[^\d]', '', nit_limpio)
        
        return ValidationResult(is_valid=True, value=value, normalized_value=normalized)

class StringValidator(BaseValidator):
    """Validador para cadenas de texto."""
    
    def validate(self, value: str, max_length: Optional[int] = None, **kwargs) -> ValidationResult:
        """Valida si un valor es una cadena válida."""
        self.log_operation("validate_string", f"Validando cadena: {value}")
        
        # Verificar valores nulos
        if self.is_null_value(value):
            return ValidationResult(is_valid=True, value="", normalized_value="")
        
        value_str = str(value).strip()
        
        # Verificar longitud máxima
        if max_length and len(value_str) > max_length:
            error_msg = f"La cadena '{value}' excede la longitud máxima de {max_length} caracteres"
            self.log_validation_error(value, error_msg, max_length=max_length)
            return ValidationResult(is_valid=False, value=value, error_message=error_msg)
        
        # Normalizar cadena
        normalized = self.normalize_string(value_str)
        
        return ValidationResult(is_valid=True, value=value, normalized_value=normalized)

class ValidatorFactory:
    """Factory para crear validadores según el tipo de dato."""
    
    _validators = {
        'entero': IntegerValidator,
        'flotante': FloatValidator,
        'fecha': DateValidator,
        'nit': NITValidator,
        'cadena': StringValidator,
        'string': StringValidator,
    }
    
    @classmethod
    def get_validator(cls, validator_type: str) -> BaseValidator:
        """Obtiene un validador por tipo."""
        validator_class = cls._validators.get(validator_type.lower())
        if not validator_class:
            raise ValueError(f"Tipo de validador '{validator_type}' no soportado")
        return validator_class()
    
    @classmethod
    def register_validator(cls, name: str, validator_class: type):
        """Registra un nuevo tipo de validador."""
        cls._validators[name.lower()] = validator_class

class ValidationManager:
    """Gestor centralizado de validaciones."""
    
    def __init__(self):
        self.factory = ValidatorFactory()
        self.logger = LoggerMixin().logger
    
    def validate_field(self, value: str, field_type: str, **kwargs) -> ValidationResult:
        """Valida un campo según su tipo."""
        try:
            validator = self.factory.get_validator(field_type)
            return validator.validate(value, **kwargs)
        except Exception as e:
            self.logger.error(f"Error en validación de campo: {str(e)}")
            return ValidationResult(
                is_valid=False,
                value=value,
                error_message=f"Error interno de validación: {str(e)}"
            )
    
    def validate_row(self, row: Dict[str, str], field_validations: Dict[str, str]) -> Tuple[bool, List[Dict[str, Any]]]:
        """Valida una fila completa de datos."""
        errors = []
        is_valid = True
        
        for field_name, field_type in field_validations.items():
            value = row.get(field_name, "")
            result = self.validate_field(value, field_type)
            
            if not result.is_valid:
                is_valid = False
                errors.append({
                    "field": field_name,
                    "value": value,
                    "error": result.error_message
                })
        
        return is_valid, errors 