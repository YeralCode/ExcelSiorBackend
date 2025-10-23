"""
Validadores específicos para BPM
Implementa validaciones y transformaciones para los tipos de datos de BPM
"""

import re
import logging
import pandas as pd
from datetime import datetime
from typing import Any, Dict, List, Optional, Union, Tuple

# Configurar logger
logger = logging.getLogger(__name__)

class BPMValidators:
    """Clase de validadores específicos para BPM"""
    
    def __init__(self):
        """Inicializar validadores de BPM"""
        self.logger = logging.getLogger(__name__)
        self.logger.info("Inicializando validadores de BPM")
    
    def validate_date(self, value: Any) -> Tuple[bool, str, Optional[str]]:
        """
        Valida y convierte fechas a formato DD/MM/YYYY
        
        Args:
            value: Valor a validar
            
        Returns:
            tuple: (es_valido, mensaje_error, valor_convertido)
        """
        if pd.isna(value) or value == '' or str(value).strip() == '':
            return True, "", ""
        
        try:
            value_str = str(value).strip()
            
            # Patrones de fecha comunes en BPM
            patterns = [
                # DD/MM/YYYY
                (r'^(\d{1,2})/(\d{1,2})/(\d{4})$', '%d/%m/%Y'),
                # DD-MM-YYYY
                (r'^(\d{1,2})-(\d{1,2})-(\d{4})$', '%d-%m-%Y'),
                # YYYY-MM-DD
                (r'^(\d{4})-(\d{1,2})-(\d{1,2})$', '%Y-%m-%d'),
                # DD.MM.YYYY
                (r'^(\d{1,2})\.(\d{1,2})\.(\d{4})$', '%d.%m.%Y'),
                # Excel date number
                (r'^\d{5,6}$', 'excel'),
                # ISO format
                (r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', 'iso')
            ]
            
            for pattern, date_format in patterns:
                if re.match(pattern, value_str):
                    if date_format == 'excel':
                        # Convertir fecha de Excel
                        try:
                            excel_date = int(float(value_str))
                            if 1 <= excel_date <= 999999:  # Rango válido de Excel
                                # Convertir desde 1900-01-01
                                from datetime import datetime, timedelta
                                base_date = datetime(1900, 1, 1)
                                converted_date = base_date + timedelta(days=excel_date - 2)
                                return True, "", converted_date.strftime('%d/%m/%Y')
                        except (ValueError, OverflowError):
                            pass
                    elif date_format == 'iso':
                        # Convertir fecha ISO
                        try:
                            dt = datetime.fromisoformat(value_str.replace('Z', '+00:00'))
                            return True, "", dt.strftime('%d/%m/%Y')
                        except ValueError:
                            pass
                    else:
                        # Convertir otros formatos
                        try:
                            dt = datetime.strptime(value_str, date_format)
                            return True, "", dt.strftime('%d/%m/%Y')
                        except ValueError:
                            pass
            
            # Si no coincide con ningún patrón, intentar parseo automático
            try:
                from dateutil import parser
                dt = parser.parse(value_str, dayfirst=True)
                return True, "", dt.strftime('%d/%m/%Y')
            except:
                pass
            
            return False, f"Formato de fecha no válido: {value_str}", None
            
        except Exception as e:
            self.logger.warning(f"Error validando fecha '{value}': {str(e)}")
            return False, f"Error procesando fecha: {str(e)}", None
    
    def validate_string(self, value: Any) -> Tuple[bool, str, str]:
        """
        Valida y limpia strings
        
        Args:
            value: Valor a validar
            
        Returns:
            tuple: (es_valido, mensaje_error, valor_convertido)
        """
        try:
            if pd.isna(value):
                return True, "", ""
            
            # Convertir a string y limpiar
            value_str = str(value).strip()
            
            # Limpiar caracteres problemáticos
            value_str = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', value_str)
            
            # Normalizar espacios múltiples
            value_str = re.sub(r'\s+', ' ', value_str)
            
            return True, "", value_str
            
        except Exception as e:
            self.logger.warning(f"Error validando string '{value}': {str(e)}")
            return False, f"Error procesando string: {str(e)}", str(value) if value else ""
    
    def validate_integer(self, value: Any) -> Tuple[bool, str, Optional[int]]:
        """
        Valida y convierte a entero
        
        Args:
            value: Valor a validar
            
        Returns:
            tuple: (es_valido, mensaje_error, valor_convertido)
        """
        if pd.isna(value) or value == '' or str(value).strip() == '':
            return True, "", None
        
        try:
            value_str = str(value).strip()
            
            # Remover caracteres no numéricos excepto signos
            clean_value = re.sub(r'[^\d\-+]', '', value_str)
            
            # Validar que sea un entero válido
            if re.match(r'^[+-]?\d+$', clean_value):
                return True, "", int(clean_value)
            
            return False, f"Valor no es un entero válido: {value_str}", None
            
        except Exception as e:
            self.logger.warning(f"Error validando entero '{value}': {str(e)}")
            return False, f"Error procesando entero: {str(e)}", None
    
    def validate_telefono(self, value: Any) -> Tuple[bool, str, str]:
        """
        Valida y formatea números telefónicos y NIT
        
        Args:
            value: Valor a validar
            
        Returns:
            tuple: (es_valido, mensaje_error, valor_convertido)
        """
        if pd.isna(value) or value == '' or str(value).strip() == '':
            return True, "", ""
        
        try:
            value_str = str(value).strip()
            
            # Limpiar caracteres no válidos
            clean_value = re.sub(r'[^\d\-\(\)\s\.]', '', value_str)
            
            # Validar formato básico
            if re.match(r'^[\d\-\(\)\s\.]+$', clean_value):
                # Formatear NIT (debe tener 9-10 dígitos)
                digits_only = re.sub(r'[^\d]', '', clean_value)
                if len(digits_only) >= 9 and len(digits_only) <= 10:
                    # Formatear como NIT: XXX.XXX.XXX-X
                    if len(digits_only) == 9:
                        formatted = f"{digits_only[:3]}.{digits_only[3:6]}.{digits_only[6:8]}-{digits_only[8]}"
                    else:
                        formatted = f"{digits_only[:3]}.{digits_only[3:6]}.{digits_only[6:9]}-{digits_only[9]}"
                    return True, "", formatted
                elif len(digits_only) >= 7:  # Teléfono
                    # Formatear como teléfono: XXX XXX XXXX
                    if len(digits_only) == 7:
                        formatted = f"{digits_only[:3]} {digits_only[3:5]} {digits_only[5:7]}"
                    elif len(digits_only) == 10:
                        formatted = f"{digits_only[:3]} {digits_only[3:6]} {digits_only[6:10]}"
                    else:
                        formatted = clean_value
                    return True, "", formatted
                else:
                    return True, "", clean_value
            
            return False, f"Formato de teléfono/NIT no válido: {value_str}", value_str
            
        except Exception as e:
            self.logger.warning(f"Error validando teléfono/NIT '{value}': {str(e)}")
            return False, f"Error procesando teléfono/NIT: {str(e)}", str(value) if value else ""
    
    def validate_email(self, value: Any) -> Tuple[bool, str, str]:
        """
        Valida y limpia correos electrónicos
        
        Args:
            value: Valor a validar
            
        Returns:
            tuple: (es_valido, mensaje_error, valor_convertido)
        """
        if pd.isna(value) or value == '' or str(value).strip() == '':
            return True, "", ""
        
        try:
            value_str = str(value).strip().lower()
            
            # Patrón básico de email
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            
            if re.match(email_pattern, value_str):
                return True, "", value_str
            
            return False, f"Formato de email no válido: {value_str}", value_str
            
        except Exception as e:
            self.logger.warning(f"Error validando email '{value}': {str(e)}")
            return False, f"Error procesando email: {str(e)}", str(value) if value else ""
    
    def validate_boolean(self, value: Any) -> Tuple[bool, str, Optional[str]]:
        """
        Valida y convierte valores booleanos
        
        Args:
            value: Valor a validar
            
        Returns:
            tuple: (es_valido, mensaje_error, valor_convertido)
        """
        if pd.isna(value) or value == '' or str(value).strip() == '':
            return True, "", ""
        
        try:
            value_str = str(value).strip().upper()
            
            # Mapeo de valores booleanos
            true_values = ['SI', 'VERDADERO', 'TRUE', '1', 'SÍ', 'V']
            false_values = ['NO', 'FALSO', 'FALSE', '0', 'N', 'F']
            
            if value_str in true_values:
                return True, "", "SI"
            elif value_str in false_values:
                return True, "", "NO"
            
            return False, f"Valor booleano no válido: {value_str}", None
            
        except Exception as e:
            self.logger.warning(f"Error validando booleano '{value}': {str(e)}")
            return False, f"Error procesando booleano: {str(e)}", None
    
    def validate_all(self, data: Dict[str, Any], column_types: Dict[str, str]) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Valida todos los campos según sus tipos asignados
        
        Args:
            data: Diccionario con los datos a validar
            column_types: Diccionario con el tipo de cada columna
            
        Returns:
            Tuple: (datos_validados, errores_validacion)
        """
        validated_data = {}
        validation_errors = []
        
        for column, value in data.items():
            column_type = column_types.get(column, 'string')
            
            try:
                if column_type == 'date':
                    is_valid, error_msg, converted_value = self.validate_date(value)
                elif column_type == 'string':
                    is_valid, error_msg, converted_value = self.validate_string(value)
                elif column_type == 'integer':
                    is_valid, error_msg, converted_value = self.validate_integer(value)
                elif column_type == 'telefono':
                    is_valid, error_msg, converted_value = self.validate_telefono(value)
                elif column_type == 'email':
                    is_valid, error_msg, converted_value = self.validate_email(value)
                elif column_type == 'boolean':
                    is_valid, error_msg, converted_value = self.validate_boolean(value)
                else:
                    # Tipo desconocido, tratar como string
                    is_valid, error_msg, converted_value = self.validate_string(value)
                
                if is_valid:
                    validated_data[column] = converted_value
                else:
                    validated_data[column] = value  # Mantener valor original
                    validation_errors.append({
                        'column': column,
                        'value': value,
                        'error': error_msg,
                        'type': column_type
                    })
                    
            except Exception as e:
                self.logger.error(f"Error validando columna '{column}': {str(e)}")
                validated_data[column] = value  # Mantener valor original
                validation_errors.append({
                    'column': column,
                    'value': value,
                    'error': f"Error interno: {str(e)}",
                    'type': column_type
                })
        
        # Log de errores de validación
        if validation_errors:
            self.logger.warning(f"Se encontraron {len(validation_errors)} errores de validación")
            for error in validation_errors[:5]:  # Solo los primeros 5 errores
                self.logger.warning(f"  {error['column']}: {error['error']}")
        
        return validated_data, validation_errors

# Instancia global del validador
bpm_validator = BPMValidators() 