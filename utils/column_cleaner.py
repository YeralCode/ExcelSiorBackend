"""
Utilidad para limpiar nombres de columnas CSV.

Convierte nombres de columnas a un formato estándar:
- Sin caracteres especiales
- Sin tildes
- En mayúsculas
- Espacios reemplazados por guiones bajos
"""

import re
import unicodedata
from typing import Dict, List
from utils.logger import get_logger

logger = get_logger(__name__)

class ColumnCleaner:
    """Limpia nombres de columnas para formato estándar."""
    
    def __init__(self):
        # Mapeo de caracteres especiales y tildes
        self.character_mapping = {
            'á': 'A', 'é': 'E', 'í': 'I', 'ó': 'O', 'ú': 'U', 'ü': 'U', 'ñ': 'N',
            'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U', 'Ü': 'U', 'Ñ': 'N',
            'à': 'A', 'è': 'E', 'ì': 'I', 'ò': 'O', 'ù': 'U',
            'À': 'A', 'È': 'E', 'Ì': 'I', 'Ò': 'O', 'Ù': 'U',
            'â': 'A', 'ê': 'E', 'î': 'I', 'ô': 'O', 'û': 'U',
            'Â': 'A', 'Ê': 'E', 'Î': 'I', 'Ô': 'O', 'Û': 'U',
            'ã': 'A', 'õ': 'O',
            'Ã': 'A', 'Õ': 'O',
            'ä': 'A', 'ë': 'E', 'ï': 'I', 'ö': 'O', 'ü': 'U',
            'Ä': 'A', 'Ë': 'E', 'Ï': 'I', 'Ö': 'O', 'Ü': 'U'
        }
        
        # Caracteres especiales a reemplazar
        self.special_chars = {
            '!': '', '@': '', '#': '', '$': '', '%': '', '^': '', '&': '', 
            '*': '', '(': '', ')': '', '-': '_', '=': '', '+': '', '[': '', 
            ']': '', '{': '', '}': '', '\\': '', '|': '', ';': '', ':': '', 
            '"': '', "'": '', '<': '', '>': '', ',': '', '.': '', '?': '', 
            '/': '', '`': '', '~': '', '°': '', '·': '', '¿': '', '¡': '',
            '´': '', '`': '', '¨': '', '^': '', '¸': '', '˝': '', '˛': '',
            'ˇ': '', '˘': '', '˙': '', '˚': '', '˛': '', '˜': '', '˝': ''
        }
    
    def clean_column_name(self, column_name: str) -> str:
        """
        Limpia un nombre de columna.
        
        Args:
            column_name: Nombre original de la columna
            
        Returns:
            Nombre limpio de la columna
        """
        if not column_name:
            return "COLUMNA_VACIA"
        
        # Convertir a string si no lo es
        column_name = str(column_name).strip()
        
        # Normalizar caracteres Unicode (quitar tildes)
        column_name = unicodedata.normalize('NFD', column_name)
        column_name = ''.join(c for c in column_name if not unicodedata.combining(c))
        
        # Reemplazar caracteres especiales
        for char, replacement in self.character_mapping.items():
            column_name = column_name.replace(char, replacement)
        
        # Reemplazar caracteres especiales con espacios
        for char, replacement in self.special_chars.items():
            column_name = column_name.replace(char, replacement)
        
        # Reemplazar múltiples espacios con un solo espacio
        column_name = re.sub(r'\s+', ' ', column_name)
        
        # Reemplazar espacios con guiones bajos
        column_name = column_name.replace(' ', '_')
        
        # Reemplazar múltiples guiones bajos con uno solo
        column_name = re.sub(r'_+', '_', column_name)
        
        # Convertir a mayúsculas
        column_name = column_name.upper()
        
        # Remover guiones bajos al inicio y final
        column_name = column_name.strip('_')
        
        # Si el resultado está vacío, usar nombre por defecto
        if not column_name:
            column_name = "COLUMNA_SIN_NOMBRE"
        
        # Si empieza con número, agregar prefijo
        if column_name[0].isdigit():
            column_name = "COL_" + column_name
        
        return column_name
    
    def clean_column_names(self, column_names: List[str]) -> Dict[str, str]:
        """
        Limpia una lista de nombres de columnas.
        
        Args:
            column_names: Lista de nombres originales
            
        Returns:
            Diccionario con mapeo {nombre_original: nombre_limpio}
        """
        cleaned_mapping = {}
        used_names = set()
        
        for original_name in column_names:
            cleaned_name = self.clean_column_name(original_name)
            
            # Si el nombre ya existe, agregar sufijo numérico
            counter = 1
            final_name = cleaned_name
            while final_name in used_names:
                final_name = f"{cleaned_name}_{counter}"
                counter += 1
            
            cleaned_mapping[original_name] = final_name
            used_names.add(final_name)
            
            logger.debug(f"Columna limpiada: '{original_name}' -> '{final_name}'")
        
        return cleaned_mapping
    
    def clean_data_types_dict(self, data_types: Dict[str, List[str]], column_mapping: Dict[str, str]) -> Dict[str, List[str]]:
        """
        Limpia un diccionario de tipos de datos usando el mapeo de columnas.
        
        Args:
            data_types: Diccionario original de tipos de datos
            column_mapping: Mapeo de nombres de columnas
            
        Returns:
            Diccionario limpio de tipos de datos
        """
        cleaned_data_types = {}
        
        for data_type, columns in data_types.items():
            cleaned_columns = []
            for column in columns:
                if column in column_mapping:
                    cleaned_columns.append(column_mapping[column])
                else:
                    # Si no está en el mapeo, limpiar directamente
                    cleaned_columns.append(self.clean_column_name(column))
            
            if cleaned_columns:  # Solo agregar si hay columnas
                cleaned_data_types[data_type] = cleaned_columns
        
        return cleaned_data_types

# Instancia global del limpiador
column_cleaner = ColumnCleaner() 