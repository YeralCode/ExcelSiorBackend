"""
Sistema dinámico para tipos de datos personalizables.

Permite agregar, modificar y gestionar tipos de datos personalizados
antes del análisis de CSV.
"""

import re
import json
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime

from utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class CustomDataType:
    """Define un tipo de datos personalizado."""
    name: str
    description: str
    pattern: Optional[str] = None  # Regex opcional
    validation_function: Optional[str] = None  # Nombre de función personalizada
    confidence_threshold: float = 0.7
    priority: int = 1  # Prioridad de detección (mayor = más prioridad)
    examples: List[str] = None
    
    def __post_init__(self):
        if self.examples is None:
            self.examples = []

class DynamicDataTypeManager:
    """Gestor de tipos de datos dinámicos."""
    
    def __init__(self):
        self.custom_types: Dict[str, CustomDataType] = {}
        self.validation_functions: Dict[str, Callable] = {}
        self._load_default_types()
        self._load_custom_functions()
    
    def _load_default_types(self):
        """Carga tipos de datos por defecto (solo los esenciales)."""
        default_types = [
            CustomDataType(
                name="nit",
                description="Número de Identificación Tributaria colombiano",
                pattern=r'^\d{9,15}$',
                confidence_threshold=0.9,
                priority=10,
                examples=["900123456-7", "800987654-3"]
            ),
            CustomDataType(
                name="email",
                description="Dirección de correo electrónico",
                pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
                confidence_threshold=0.85,
                priority=9,
                examples=["usuario@empresa.com", "contacto@dominio.co"]
            ),
            CustomDataType(
                name="telefono",
                description="Número de teléfono colombiano",
                pattern=r'^(\+?57)?[0-9]{7,10}$',
                confidence_threshold=0.8,
                priority=8,
                examples=["3001234567", "+573001234567"]
            ),
            CustomDataType(
                name="porcentaje",
                description="Valor porcentual",
                pattern=r'^\d+(\.\d+)?%$',
                confidence_threshold=0.9,
                priority=9,
                examples=["25%", "12.5%"]
            )
        ]
        
        for data_type in default_types:
            self.add_custom_type(data_type)
    
    def _load_custom_functions(self):
        """Carga funciones de validación personalizadas."""
        self.validation_functions = {
            "validate_nit": self._validate_nit,
            "validate_email": self._validate_email,
            "validate_phone": self._validate_phone,
            "validate_percentage": self._validate_percentage
        }
    
    def add_custom_type(self, data_type: CustomDataType) -> bool:
        """
        Agrega un tipo de datos personalizado.
        
        Args:
            data_type: Tipo de datos personalizado
            
        Returns:
            True si se agregó correctamente
        """
        try:
            # Validar que el patrón sea válido si se proporciona
            if data_type.pattern:
                re.compile(data_type.pattern)
            
            self.custom_types[data_type.name] = data_type
            logger.info(f"Tipo de datos personalizado agregado: {data_type.name}")
            return True
        except re.error as e:
            logger.error(f"Error en patrón regex para {data_type.name}: {e}")
            return False
    
    def remove_custom_type(self, type_name: str) -> bool:
        """
        Elimina un tipo de datos personalizado.
        
        Args:
            type_name: Nombre del tipo a eliminar
            
        Returns:
            True si se eliminó correctamente
        """
        if type_name in self.custom_types:
            del self.custom_types[type_name]
            logger.info(f"Tipo de datos eliminado: {type_name}")
            return True
        return False
    
    def get_custom_type(self, type_name: str) -> Optional[CustomDataType]:
        """Obtiene un tipo de datos personalizado."""
        return self.custom_types.get(type_name)
    
    def get_all_types(self) -> List[Dict[str, Any]]:
        """Obtiene todos los tipos de datos disponibles."""
        types = []
        for name, data_type in self.custom_types.items():
            type_dict = asdict(data_type)
            type_dict['name'] = name
            types.append(type_dict)
        
        # Ordenar por prioridad (mayor primero)
        types.sort(key=lambda x: x['priority'], reverse=True)
        return types
    
    def detect_type(self, column_data: List[str], column_name: str = "") -> Dict[str, Any]:
        """
        Detecta el tipo de datos de una columna usando tipos personalizados.
        
        Args:
            column_data: Lista de valores de la columna
            column_name: Nombre de la columna
            
        Returns:
            Diccionario con información del tipo detectado
        """
        if not column_data:
            return {"type": "string", "confidence": 0.0, "reason": "Sin datos"}
        
        # Ordenar tipos por prioridad
        sorted_types = sorted(self.custom_types.values(), key=lambda x: x.priority, reverse=True)
        
        for data_type in sorted_types:
            matches = 0
            total_valid = 0
            
            for value in column_data:
                if value and str(value).strip():
                    total_valid += 1
                    
                    # Si no hay patrón, usar función de validación
                    if data_type.pattern:
                        if re.match(data_type.pattern, str(value).strip()):
                            matches += 1
                    elif data_type.validation_function and data_type.validation_function in self.validation_functions:
                        if self.validation_functions[data_type.validation_function](value):
                            matches += 1
                    else:
                        # Si no hay patrón ni función, considerar como match si el nombre coincide
                        if data_type.name.lower() in column_name.lower():
                            matches += 1
            
            if total_valid > 0:
                confidence = matches / total_valid
                if confidence >= data_type.confidence_threshold:
                    return {
                        "type": data_type.name,
                        "confidence": confidence,
                        "reason": data_type.description,
                        "examples": data_type.examples
                    }
        
        # Si no se detecta ningún tipo personalizado, retornar string
        return {"type": "string", "confidence": 0.5, "reason": "Tipo no detectado"}
    
    def validate_value(self, value: str, type_name: str) -> bool:
        """
        Valida un valor contra un tipo de datos específico.
        
        Args:
            value: Valor a validar
            type_name: Nombre del tipo de datos
            
        Returns:
            True si el valor es válido
        """
        data_type = self.get_custom_type(type_name)
        if not data_type:
            return False
        
        # Validar con patrón regex si existe
        if data_type.pattern and not re.match(data_type.pattern, str(value).strip()):
            return False
        
        # Validar con función personalizada si existe
        if data_type.validation_function and data_type.validation_function in self.validation_functions:
            return self.validation_functions[data_type.validation_function](value)
        
        return True
    
    # Funciones de validación personalizadas
    def _validate_nit(self, value: str) -> bool:
        """Valida NIT colombiano."""
        nit = str(value).replace('-', '').replace('.', '')
        if len(nit) < 9 or len(nit) > 15:
            return False
        return True
    
    def _validate_email(self, value: str) -> bool:
        """Valida email."""
        return '@' in value and '.' in value.split('@')[1]
    
    def _validate_phone(self, value: str) -> bool:
        """Valida teléfono colombiano."""
        phone = str(value).replace('+57', '').replace(' ', '').replace('-', '')
        return len(phone) >= 7 and len(phone) <= 10 and phone.isdigit()
    
    def _validate_percentage(self, value: str) -> bool:
        """Valida porcentaje."""
        if not value.endswith('%'):
            return False
        try:
            float(value[:-1])
            return True
        except ValueError:
            return False

# Instancia global del gestor
data_type_manager = DynamicDataTypeManager() 