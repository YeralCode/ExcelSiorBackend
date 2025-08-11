"""
Sistema de validadores base reutilizable.
Proporciona validadores comunes que pueden ser extendidos por cada proyecto.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, Callable
from datetime import datetime
import re
import logging
import unicodedata

logger = logging.getLogger(__name__)


class BaseValidator(ABC):
    """
    Clase base para validadores.
    Define la interfaz común que todos los validadores deben implementar.
    """
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.errors: List[str] = []
    
    @abstractmethod
    def validate(self, value: Any) -> Any:
        """
        Valida y limpia un valor.
        
        Args:
            value: Valor a validar
            
        Returns:
            Valor limpio si es válido, valor original si no es válido
        """
        pass
    
    def add_error(self, error: str) -> None:
        """Agrega un error a la lista de errores."""
        self.errors.append(f"{self.name}: {error}")
    
    def get_errors(self) -> List[str]:
        """Retorna la lista de errores."""
        return self.errors.copy()
    
    def clear_errors(self) -> None:
        """Limpia la lista de errores."""
        self.errors.clear()
    
    def is_valid(self, value: Any) -> bool:
        """
        Verifica si un valor es válido y limpia errores previos.
        
        Args:
            value: Valor a validar
            
        Returns:
            True si el valor es válido
        """
        self.clear_errors()
        try:
            cleaned_value = self.validate(value)
            return cleaned_value != value or len(self.errors) == 0
        except:
            return False


class StringValidator(BaseValidator):
    """Validador para strings."""
    
    def __init__(self, min_length: int = 0, max_length: Optional[int] = None, 
                 pattern: Optional[str] = None, allowed_values: Optional[List[str]] = None):
        super().__init__("StringValidator", "Valida strings con restricciones opcionales")
        self.min_length = min_length
        self.max_length = max_length
        self.pattern = pattern
        self.allowed_values = allowed_values
    
    def validate(self, value: Any) -> Any:
        # Omitir valores None, vacíos o con solo espacios en blanco
        if value is None or value == "" or (isinstance(value, str) and value.strip() == ""):
            return value
        
        if not isinstance(value, str):
            self.add_error(f"El valor debe ser un string, se recibió: {type(value)}")
            return None
        
        # Validar longitud mínima
        if len(value) < self.min_length:
            self.add_error(f"La longitud mínima es {self.min_length}, se recibió: {len(value)}")
            return None
        
        # Validar longitud máxima
        if self.max_length and len(value) > self.max_length:
            self.add_error(f"La longitud máxima es {self.max_length}, se recibió: {len(value)}")
            return None
        
        # Validar patrón regex
        if self.pattern and not re.match(self.pattern, value):
            self.add_error(f"El valor no coincide con el patrón requerido: {self.pattern}")
            return None
        
        # Validar valores permitidos
        if self.allowed_values and value not in self.allowed_values:
            self.add_error(f"El valor debe estar en: {self.allowed_values}")
            return None
        
        return value


class IntegerValidator(BaseValidator):
    """Validador para enteros."""
    
    def __init__(self, min_value: Optional[int] = None, max_value: Optional[int] = None):
        super().__init__("IntegerValidator", "Valida enteros con rango opcional")
        self.min_value = min_value
        self.max_value = max_value
    
    def validate(self, value: Any) -> Any:
        # Omitir valores None, vacíos o con solo espacios en blanco
        if value is None or value == "" or (isinstance(value, str) and value.strip() == ""):
            return value
        
        try:
            int_value = int(value)
        except (ValueError, TypeError):
            self.add_error(f"El valor debe ser un entero, se recibió: {value}")
            return None
        
        # Validar valor mínimo
        if self.min_value is not None and int_value < self.min_value:
            self.add_error(f"El valor mínimo es {self.min_value}, se recibió: {int_value}")
            return None
        
        # Validar valor máximo
        if self.max_value is not None and int_value > self.max_value:
            self.add_error(f"El valor máximo es {self.max_value}, se recibió: {int_value}")
            return None
        
        return int_value


class FloatValidator(BaseValidator):
    """Validador para números flotantes."""
    
    def __init__(self, min_value: Optional[float] = None, max_value: Optional[float] = None, 
                 decimal_places: Optional[int] = None):
        super().__init__("FloatValidator", "Valida flotantes con rango y decimales opcionales")
        self.min_value = min_value
        self.max_value = max_value
        self.decimal_places = decimal_places
    
    def validate(self, value: Any) -> Any:
        # Omitir valores None, vacíos o con solo espacios en blanco
        if value is None or value == "" or (isinstance(value, str) and value.strip() == ""):
            return value
        
        try:
            float_value = float(value)
        except (ValueError, TypeError):
            self.add_error(f"El valor debe ser un número, se recibió: {value}")
            return None
        
        # Validar valor mínimo
        if self.min_value is not None and float_value < self.min_value:
            self.add_error(f"El valor mínimo es {self.min_value}, se recibió: {float_value}")
            return None
        
        # Validar valor máximo
        if self.max_value is not None and float_value > self.max_value:
            self.add_error(f"El valor máximo es {self.max_value}, se recibió: {float_value}")
            return None
        
        # Validar decimales
        if self.decimal_places is not None:
            str_value = str(float_value)
            if '.' in str_value:
                decimal_part = str_value.split('.')[1]
                if len(decimal_part) > self.decimal_places:
                    self.add_error(f"El valor debe tener máximo {self.decimal_places} decimales, se recibió: {len(decimal_part)}")
                    return None
        
        return float_value


class DateValidator(BaseValidator):
    """Validador para fechas."""
    
    def __init__(self, date_formats: Optional[List[str]] = None, 
                 min_date: Optional[datetime] = None, max_date: Optional[datetime] = None):
        super().__init__("DateValidator", "Valida fechas con formato y rango opcionales")
        self.date_formats = date_formats or [
            '%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%Y/%m/%d',
            '%d/%m/%y', '%d-%m-%y', '%y/%m/%d', '%Y-%m-%d %H:%M:%S'
        ]
        self.min_date = min_date
        self.max_date = max_date
    
    def validate(self, value: Any) -> Any:
        # Omitir valores None, vacíos o con solo espacios en blanco
        if value is None or value == "" or (isinstance(value, str) and value.strip() == ""):
            return value
        
        if not isinstance(value, str):
            self.add_error(f"El valor debe ser un string, se recibió: {type(value)}")
            return None
        
        # Intentar parsear la fecha con diferentes formatos
        parsed_date = None
        for date_format in self.date_formats:
            try:
                parsed_date = datetime.strptime(value, date_format)
                break
            except ValueError:
                continue
        
        if parsed_date is None:
            self.add_error(f"No se pudo parsear la fecha: {value}. Formatos soportados: {self.date_formats}")
            return None
        
        if self.min_date and parsed_date < self.min_date:
            self.add_error(f"La fecha mínima es {self.min_date.strftime('%Y-%m-%d')}, se recibió: {parsed_date.strftime('%Y-%m-%d')}")
            return None
        
        if self.max_date and parsed_date > self.max_date:
            self.add_error(f"La fecha máxima es {self.max_date.strftime('%Y-%m-%d')}, se recibió: {parsed_date.strftime('%Y-%m-%d')}")
            return None
        
        return parsed_date


class NITValidator(BaseValidator):
    """Validador para NIT (Número de Identificación Tributaria)."""
    
    def __init__(self):
        super().__init__("NITValidator", "Valida formato de NIT colombiano")
        # Frases que indican que no hay NIT válido
        self.invalid_phrases = [
            "por establecer", "no aplica", "n/a", "na", "sin nit", 
            "sin número", "no tiene", "pendiente", "por definir"
        ]
    
    def validate(self, value: Any) -> Any:
        # Omitir valores None, vacíos o con solo espacios en blanco
        if value is None or value == "" or (isinstance(value, str) and value.strip() == ""):
            return value
        
        if not isinstance(value, str):
            self.add_error(f"El valor debe ser un string, se recibió: {type(value)}")
            return None
        
        # Limpiar el valor de espacios y convertir a minúsculas para comparación
        clean_value_lower = value.strip().lower()
        
        # Verificar si es una frase inválida - NO agregar error, solo retornar None
        if clean_value_lower in self.invalid_phrases:
            # No agregar error, simplemente retornar None para que se omita
            return None
        
        # Verificar si contiene letras (excepto en frases válidas)
        if any(char.isalpha() for char in clean_value_lower):
            self.add_error(f"El NIT no puede contener letras: {value}")
            return None
        
        # Limpiar el valor de espacios, guiones y puntos para procesamiento numérico
        clean_value_numeric = re.sub(r'[\s\-\.]', '', value)
        
        # Manejar casos especiales con guiones
        original_value = value.strip()
        if '-' in original_value:
            parts = original_value.split('-')
            
            # Si hay más de 2 partes separadas por guiones, es inválido
            if len(parts) > 2:
                self.add_error(f"El NIT tiene demasiados guiones: {value}")
                return None
            
            # Si hay exactamente 2 partes
            if len(parts) == 2:
                main_part = parts[0].strip()
                suffix = parts[1].strip()
                
                # Verificar que ambas partes sean numéricas
                if not main_part.isdigit() or not suffix.isdigit():
                    self.add_error(f"Las partes del NIT deben ser numéricas: {value}")
                    return None
                
                # Si el sufijo tiene exactamente 2 dígitos, usar solo la parte principal
                if len(suffix) == 2:
                    clean_value_numeric = main_part
                else:
                    # Si el sufijo tiene más de 2 dígitos, es inválido
                    self.add_error(f"El sufijo del NIT debe tener máximo 2 dígitos: {value}")
                    return None
        
        # Verificar que solo contenga dígitos después de la limpieza y manejo de guiones
        if not clean_value_numeric.isdigit():
            self.add_error(f"El NIT solo debe contener dígitos: {value}")
            return None
        
        # Verificar longitud mínima (al menos 3 dígitos)
        if len(clean_value_numeric) < 3:
            self.add_error(f"El NIT debe tener al menos 3 dígitos, se recibió: {len(clean_value_numeric)}")
            return None
        
        # No hay límite máximo de dígitos (pueden ser NITs muy largos)
        
        return clean_value_numeric


class EmailValidator(BaseValidator):
    """Validador para emails."""
    
    def __init__(self):
        super().__init__("EmailValidator", "Valida formato de email")
        self.email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    def validate(self, value: Any) -> Any:
        # Omitir valores None, vacíos o con solo espacios en blanco
        if value is None or value == "" or (isinstance(value, str) and value.strip() == ""):
            return value
        
        if not isinstance(value, str):
            self.add_error(f"El valor debe ser un string, se recibió: {type(value)}")
            return None
        
        if not self.email_pattern.match(value):
            self.add_error(f"El formato de email no es válido: {value}")
            return None
        
        return value


class PhoneValidator(BaseValidator):
    """Validador para números de teléfono."""
    
    def __init__(self, country_code: str = "CO"):
        super().__init__("PhoneValidator", "Valida números de teléfono")
        self.country_code = country_code
    
    def validate(self, value: Any) -> Any:
        # Omitir valores None, vacíos o con solo espacios en blanco
        if value is None or value == "" or (isinstance(value, str) and value.strip() == ""):
            return value
        
        if not isinstance(value, str):
            self.add_error(f"El valor debe ser un string, se recibió: {type(value)}")
            return None
        
        # Limpiar el valor de espacios y caracteres especiales
        clean_value = re.sub(r'[\s\-\(\)\+]', '', value)
        
        # Verificar que solo contenga dígitos
        if not clean_value.isdigit():
            self.add_error(f"El número de teléfono solo debe contener dígitos: {value}")
            return None
        
        # Validar longitud mínima (al menos 7 dígitos)
        if len(clean_value) < 7:
            self.add_error(f"El número de teléfono debe tener al menos 7 dígitos, se recibió: {len(clean_value)}")
            return None
        
        return clean_value


class PercentageValidator(BaseValidator):
    """Validador para porcentajes."""
    
    def __init__(self, min_percentage: float = 0.0, max_percentage: float = 100.0):
        super().__init__("PercentageValidator", "Valida porcentajes con rango opcional")
        self.min_percentage = min_percentage
        self.max_percentage = max_percentage
    
    def validate(self, value: Any) -> Any:
        # Omitir valores None, vacíos o con solo espacios en blanco
        if value is None or value == "" or (isinstance(value, str) and value.strip() == ""):
            return value
        
        try:
            # Remover el símbolo % si está presente
            if isinstance(value, str):
                value = value.replace('%', '').strip()
            
            float_value = float(value)
        except (ValueError, TypeError):
            self.add_error(f"El valor debe ser un número, se recibió: {value}")
            return None
        
        # Validar rango
        if float_value < self.min_percentage:
            self.add_error(f"El porcentaje mínimo es {self.min_percentage}%, se recibió: {float_value}%")
            return None
        
        if float_value > self.max_percentage:
            self.add_error(f"El porcentaje máximo es {self.max_percentage}%, se recibió: {float_value}%")
            return None
        
        return float_value


class BooleanValidator(BaseValidator):
    """Validador para valores booleanos."""
    
    def __init__(self, true_values: Optional[List[str]] = None, false_values: Optional[List[str]] = None):
        super().__init__("BooleanValidator", "Valida valores booleanos")
        self.true_values = true_values or ['true', '1', 'yes', 'si', 'sí', 'verdadero', 'on']
        self.false_values = false_values or ['false', '0', 'no', 'falso', 'off']
    
    def validate(self, value: Any) -> Any:
        # Omitir valores None, vacíos o con solo espacios en blanco
        if value is None or value == "" or (isinstance(value, str) and value.strip() == ""):
            return value
        
        if isinstance(value, bool):
            return value
        
        if not isinstance(value, str):
            self.add_error(f"El valor debe ser un string o boolean, se recibió: {type(value)}")
            return None
        
        value_lower = value.lower().strip()
        
        if value_lower in self.true_values:
            return True
        elif value_lower in self.false_values:
            return False
        else:
            self.add_error(f"El valor debe ser uno de: {self.true_values + self.false_values}")
            return None


class ChoiceValidator(BaseValidator):
    """Validador para valores de una lista de opciones."""
    
    def __init__(self, choices: List[str], case_sensitive: bool = False):
        super().__init__("ChoiceValidator", "Valida valores de una lista de opciones")
        self.choices = choices
        self.case_sensitive = case_sensitive
    
    def validate(self, value: Any) -> Any:
        # Omitir valores None, vacíos o con solo espacios en blanco
        if value is None or value == "" or (isinstance(value, str) and value.strip() == ""):
            return value
        
        if not isinstance(value, str):
            self.add_error(f"El valor debe ser un string, se recibió: {type(value)}")
            return None
        
        if self.case_sensitive:
            if value not in self.choices:
                self.add_error(f"El valor debe estar en: {self.choices}")
                return None
        else:
            if value.lower() not in [choice.lower() for choice in self.choices]:
                self.add_error(f"El valor debe estar en: {self.choices}")
                return None
        
        return value


class FlexibleChoiceValidator(BaseValidator):
    """Validador para valores de una lista de opciones con búsqueda flexible."""
    
    def __init__(self, choices: List[str], case_sensitive: bool = False, 
                 normalizer: Optional[Callable[[str], str]] = None,
                 replacement_map: Optional[Dict[str, str]] = None):
        super().__init__("FlexibleChoiceValidator", "Valida valores de una lista de opciones con búsqueda flexible")
        
        # Normalizar las opciones quitando tildes y aplicando casos especiales
        self.original_choices = choices
        self.choices = normalize_choices_for_validator(choices)
        
        self.case_sensitive = case_sensitive
        self.normalizer = normalizer if normalizer else normalize_location_name
        self.replacement_map = replacement_map or {}
    
    def validate(self, value: Any) -> Any:
        # Omitir validation for None or empty/whitespace-only strings
        if value is None or (isinstance(value, str) and not value.strip()):
            return value
        
        if not isinstance(value, str):
            self.add_error(f"El valor debe ser un string, se recibió: {type(value)}")
            return None
        
        # PASO 1: Normalizar el valor de entrada (quitar tildes, convertir a minúsculas)
        normalized_value = self.normalizer(value)
        logger.info(f"Valor original: '{value}' -> Normalizado: '{normalized_value}'")
        
        # PASO 2: Convertir a uppercase para buscar en el replacement_map
        normalized_uppercase = normalized_value.upper()
        logger.info(f"Normalizado uppercase: '{normalized_uppercase}'")
        
        # PASO 3: Verificar si hay un reemplazo directo en el mapa
        if normalized_uppercase in self.replacement_map:
            replacement_value = self.replacement_map[normalized_uppercase]
            logger.info(f"Reemplazo encontrado: '{normalized_uppercase}' -> '{replacement_value}'")
            # Normalizar el valor reemplazado para la búsqueda final
            normalized_value = self.normalizer(replacement_value)
            logger.info(f"Valor reemplazado normalizado: '{normalized_value}'")
        
        # PASO 4: Buscar en las opciones normalizadas
        found_match = False
        matched_choice = None
        
        for i, choice in enumerate(self.choices):
            normalized_choice = self.normalizer(choice)
            if normalized_value == normalized_choice:
                found_match = True
                # Usar el choice original para mantener el formato correcto
                matched_choice = self.original_choices[i]
                logger.info(f"Coincidencia encontrada: '{normalized_value}' -> '{matched_choice}'")
                break
        
        if found_match:
            # Retornar el valor original de la lista en uppercase
            return matched_choice.upper()
        else:
            # Si no se encuentra, devolver el dato original normalizado en uppercase
            logger.info(f"No se encontró coincidencia para '{normalized_value}'. Devolviendo valor original normalizado.")
            return normalized_value.upper()


def normalize_location_name(text: str) -> str:
    """
    Normaliza nombres de ubicaciones (departamentos, ciudades) para búsqueda flexible.
    
    Args:
        text: Texto a normalizar
        
    Returns:
        Texto normalizado para búsqueda
    """
    if not isinstance(text, str):
        return ""
    
    # Convertir a minúsculas primero para normalizar
    normalized = text.lower()
    
    # Quitar tildes y caracteres especiales
    normalized = unicodedata.normalize('NFD', normalized)
    normalized = ''.join(c for c in normalized if not unicodedata.combining(c))
    
    # Reemplazar caracteres especiales (solo minúsculas ya que convertimos arriba)
    replacements = {
        'ñ': 'n',
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'ü': 'u',
        'ç': 'c',
        'ã': 'a', 'õ': 'o',
        'à': 'a', 'è': 'e', 'ì': 'i', 'ò': 'o', 'ù': 'u'
    }
    
    for old, new in replacements.items():
        normalized = normalized.replace(old, new)
    
    # Normalizar espacios múltiples y quitar espacios al inicio y final
    normalized = re.sub(r'\s+', ' ', normalized)
    normalized = normalized.strip()
    
    return normalized


def normalize_choices_for_validator(choices: List[str]) -> List[str]:
    """
    Normaliza las opciones de un validador quitando tildes y aplicando casos especiales.
    
    Args:
        choices: Lista de opciones originales
        
    Returns:
        Lista de opciones normalizadas
    """
    normalized_choices = []
    
    for choice in choices:
        if isinstance(choice, str):
            # Normalizar el choice
            normalized = normalize_location_name(choice)
            # Convertir a uppercase para mantener consistencia
            normalized_choices.append(normalized.upper())
        else:
            # Mantener valores no string tal como están
            normalized_choices.append(choice)
    
    return normalized_choices


def create_location_validator(choices: List[str], name: str = "LocationValidator") -> FlexibleChoiceValidator:
    """
    Crea un validador específico para ubicaciones (departamentos, ciudades).
    
    Args:
        choices: Lista de opciones válidas
        name: Nombre del validador
        
    Returns:
        FlexibleChoiceValidator configurado para ubicaciones
    """
    validator = FlexibleChoiceValidator(
        choices=choices,
        case_sensitive=False,
        normalizer=normalize_location_name
    )
    validator.name = name
    validator.description = f"Valida {name.lower()} con búsqueda flexible"
    
    return validator


def create_location_validator_with_replacements(choices: List[str], validator_name: str, 
                                               replacement_map: Optional[Dict[str, str]] = None) -> FlexibleChoiceValidator:
    """
    Crea un validador de ubicación con diccionario de reemplazos.
    
    Args:
        choices: Lista de opciones válidas
        validator_name: Nombre del validador
        replacement_map: Diccionario de reemplazos {valor_entrada: valor_correcto}
        
    Returns:
        FlexibleChoiceValidator configurado con reemplazos
    """
    return FlexibleChoiceValidator(
        choices=choices,
        case_sensitive=False,
        normalizer=normalize_location_name,
        replacement_map=replacement_map
    )


class ValidatorFactory:
    """Factory para crear validadores."""
    
    @staticmethod
    def create_validator(validator_type: str, **kwargs) -> BaseValidator:
        """
        Crea un validador del tipo especificado.
        
        Args:
            validator_type: Tipo de validador a crear
            **kwargs: Argumentos específicos del validador
            
        Returns:
            Instancia del validador creado
        """
        validator_map = {
            'string': StringValidator,
            'integer': IntegerValidator,
            'float': FloatValidator,
            'date': DateValidator,
            'datetime': DateValidator,
            'nit': NITValidator,
            'email': EmailValidator,
            'phone': PhoneValidator,
            'percentage': PercentageValidator,
            'boolean': BooleanValidator,
            'choice': FlexibleChoiceValidator,
            'flexible_choice': FlexibleChoiceValidator
        }
        
        validator_class = validator_map.get(validator_type)
        if not validator_class:
            raise ValueError(f"Tipo de validador no soportado: {validator_type}")
        
        # Para FlexibleChoiceValidator, asegurar que se pase el normalizer si no se proporciona
        if validator_class == FlexibleChoiceValidator and 'normalizer' not in kwargs:
            kwargs['normalizer'] = normalize_location_name
        
        return validator_class(**kwargs)
    
    @staticmethod
    def get_available_validators() -> List[str]:
        """Retorna la lista de validadores disponibles."""
        return ['string', 'integer', 'float', 'date', 'nit', 'email', 'phone', 'percentage', 'boolean', 'choice', 'flexible_choice'] 