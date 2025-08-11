"""
Tests unitarios para el sistema de validación.

Pruebas exhaustivas para todos los validadores y el sistema de validación.
"""

import pytest
from datetime import datetime
from utils.validators import (
    IntegerValidator, FloatValidator, DateValidator, 
    NITValidator, StringValidator, ValidationManager,
    ValidatorFactory, ValidationResult
)
from utils.exceptions import DataValidationError

class TestIntegerValidator:
    """Tests para el validador de enteros."""
    
    def setup_method(self):
        """Configuración inicial para cada test."""
        self.validator = IntegerValidator()
    
    def test_valid_integers(self):
        """Prueba valores enteros válidos."""
        test_cases = [
            ("123", "123"),
            ("-456", "-456"),
            ("0", "0"),
            ("123.0", "123"),
            ("1,234", "1234"),
            ("$500", "500"),
            ("1e6", "1000000"),
        ]
        
        for input_val, expected in test_cases:
            result = self.validator.validate(input_val)
            assert result.is_valid, f"'{input_val}' debería ser válido"
            assert result.normalized_value == expected
    
    def test_invalid_integers(self):
        """Prueba valores enteros inválidos."""
        test_cases = [
            "abc",
            "123abc",
            "abc123",
            "12.34",
            "1.5",
            "1.2e3",
        ]
        
        for input_val in test_cases:
            result = self.validator.validate(input_val)
            assert not result.is_valid, f"'{input_val}' debería ser inválido"
            assert result.error_message is not None
    
    def test_null_values(self):
        """Prueba valores nulos."""
        null_values = ["", "null", "nan", "none", "n/a", "sin registro"]
        
        for null_val in null_values:
            result = self.validator.validate(null_val)
            assert result.is_valid, f"'{null_val}' debería ser considerado nulo"
            assert result.normalized_value == ""

class TestFloatValidator:
    """Tests para el validador de flotantes."""
    
    def setup_method(self):
        """Configuración inicial para cada test."""
        self.validator = FloatValidator()
    
    def test_valid_floats(self):
        """Prueba valores flotantes válidos."""
        test_cases = [
            ("123.45", "123.45"),
            ("-456.78", "-456.78"),
            ("0.0", "0.0"),
            ("123", "123.0"),
            ("1.23e4", "12300.0"),
            ("1.23E-2", "0.0123"),
        ]
        
        for input_val, expected in test_cases:
            result = self.validator.validate(input_val)
            assert result.is_valid, f"'{input_val}' debería ser válido"
            assert result.normalized_value == expected
    
    def test_invalid_floats(self):
        """Prueba valores flotantes inválidos."""
        test_cases = [
            "abc",
            "123abc",
            "abc123.45",
            "12.34.56",
        ]
        
        for input_val in test_cases:
            result = self.validator.validate(input_val)
            assert not result.is_valid, f"'{input_val}' debería ser inválido"
            assert result.error_message is not None

class TestDateValidator:
    """Tests para el validador de fechas."""
    
    def setup_method(self):
        """Configuración inicial para cada test."""
        self.validator = DateValidator()
    
    def test_valid_dates(self):
        """Prueba fechas válidas."""
        test_cases = [
            ("2023-12-25", "date", "2023-12-25"),
            ("2023/12/25", "date_YY", "2023-12-25"),
            ("25/12/2023", "date_dd_mm_yyyy", "2023-12-25"),
            ("2023-12-25 14:30:00", "datetime", "2023-12-25"),
        ]
        
        for input_val, format_name, expected in test_cases:
            result = self.validator.validate(input_val, format_name=format_name)
            assert result.is_valid, f"'{input_val}' debería ser válido con formato {format_name}"
            assert result.normalized_value == expected
    
    def test_invalid_dates(self):
        """Prueba fechas inválidas."""
        test_cases = [
            ("2023-13-01", "date"),  # Mes inválido
            ("2023-12-32", "date"),  # Día inválido
            ("abc", "date"),         # Formato inválido
            ("2023/12/25", "date"),  # Formato incorrecto
        ]
        
        for input_val, format_name in test_cases:
            result = self.validator.validate(input_val, format_name=format_name)
            assert not result.is_valid, f"'{input_val}' debería ser inválido con formato {format_name}"
            assert result.error_message is not None

class TestNITValidator:
    """Tests para el validador de NIT."""
    
    def setup_method(self):
        """Configuración inicial para cada test."""
        self.validator = NITValidator()
    
    def test_valid_nits(self):
        """Prueba NITs válidos."""
        test_cases = [
            ("12345678", "12345678"),
            ("12345678-9", "123456789"),
            ("900123456-7", "9001234567"),
            ("800-123-456", "800123456"),
        ]
        
        for input_val, expected in test_cases:
            result = self.validator.validate(input_val)
            assert result.is_valid, f"'{input_val}' debería ser un NIT válido"
            assert result.normalized_value == expected
    
    def test_invalid_nits(self):
        """Prueba NITs inválidos."""
        test_cases = [
            "1234567",      # Muy corto
            "12345678901234567890",  # Muy largo
            "abc12345",     # Contiene letras
            "123-45-678",   # Formato incorrecto
        ]
        
        for input_val in test_cases:
            result = self.validator.validate(input_val)
            assert not result.is_valid, f"'{input_val}' debería ser un NIT inválido"
            assert result.error_message is not None

class TestStringValidator:
    """Tests para el validador de cadenas."""
    
    def setup_method(self):
        """Configuración inicial para cada test."""
        self.validator = StringValidator()
    
    def test_valid_strings(self):
        """Prueba cadenas válidas."""
        test_cases = [
            ("Hola mundo", "Hola mundo"),
            ("Texto con acentos: áéíóú", "Texto con acentos: aeiou"),
            ("", ""),
            ("123", "123"),
        ]
        
        for input_val, expected in test_cases:
            result = self.validator.validate(input_val)
            assert result.is_valid, f"'{input_val}' debería ser válido"
            assert result.normalized_value == expected
    
    def test_string_length_validation(self):
        """Prueba validación de longitud de cadena."""
        # Cadena que excede la longitud máxima
        result = self.validator.validate("Esta es una cadena muy larga", max_length=10)
        assert not result.is_valid
        assert result.error_message is not None
        
        # Cadena dentro del límite
        result = self.validator.validate("Corta", max_length=10)
        assert result.is_valid

class TestValidatorFactory:
    """Tests para la factory de validadores."""
    
    def test_get_validator(self):
        """Prueba obtención de validadores por tipo."""
        # Validar que se pueden obtener todos los tipos de validadores
        validator_types = ['entero', 'flotante', 'fecha', 'nit', 'cadena']
        
        for validator_type in validator_types:
            validator = ValidatorFactory.get_validator(validator_type)
            assert validator is not None
            assert hasattr(validator, 'validate')
    
    def test_invalid_validator_type(self):
        """Prueba error al solicitar tipo de validador inválido."""
        with pytest.raises(ValueError, match="no soportado"):
            ValidatorFactory.get_validator("tipo_invalido")
    
    def test_register_custom_validator(self):
        """Prueba registro de validador personalizado."""
        class CustomValidator(IntegerValidator):
            pass
        
        ValidatorFactory.register_validator("custom", CustomValidator)
        validator = ValidatorFactory.get_validator("custom")
        assert isinstance(validator, CustomValidator)

class TestValidationManager:
    """Tests para el gestor de validaciones."""
    
    def setup_method(self):
        """Configuración inicial para cada test."""
        self.manager = ValidationManager()
    
    def test_validate_field(self):
        """Prueba validación de campo individual."""
        # Campo válido
        result = self.manager.validate_field("123", "entero")
        assert result.is_valid
        assert result.normalized_value == "123"
        
        # Campo inválido
        result = self.manager.validate_field("abc", "entero")
        assert not result.is_valid
        assert result.error_message is not None
    
    def test_validate_row(self):
        """Prueba validación de fila completa."""
        row = {
            "id": "123",
            "nombre": "Juan Pérez",
            "edad": "25",
            "email": "juan@example.com"
        }
        
        field_validations = {
            "id": "entero",
            "nombre": "cadena",
            "edad": "entero",
            "email": "cadena"
        }
        
        is_valid, errors = self.manager.validate_row(row, field_validations)
        assert is_valid
        assert len(errors) == 0
    
    def test_validate_row_with_errors(self):
        """Prueba validación de fila con errores."""
        row = {
            "id": "abc",  # Inválido para entero
            "nombre": "Juan Pérez",
            "edad": "25",
        }
        
        field_validations = {
            "id": "entero",
            "nombre": "cadena",
            "edad": "entero",
        }
        
        is_valid, errors = self.manager.validate_row(row, field_validations)
        assert not is_valid
        assert len(errors) == 1
        assert errors[0]["field"] == "id"
        assert errors[0]["value"] == "abc"

class TestValidationResult:
    """Tests para la clase ValidationResult."""
    
    def test_validation_result_creation(self):
        """Prueba creación de ValidationResult."""
        # Resultado válido
        result = ValidationResult(
            is_valid=True,
            value="test",
            normalized_value="test_normalized"
        )
        assert result.is_valid
        assert result.value == "test"
        assert result.normalized_value == "test_normalized"
        assert result.error_message is None
        
        # Resultado inválido
        result = ValidationResult(
            is_valid=False,
            value="test",
            error_message="Error de validación"
        )
        assert not result.is_valid
        assert result.value == "test"
        assert result.error_message == "Error de validación"
        assert result.normalized_value is None

if __name__ == "__main__":
    pytest.main([__file__]) 