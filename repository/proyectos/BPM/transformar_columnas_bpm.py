"""
Transformadores de columnas para BPM
Implementa la lógica de transformación y limpieza de datos para BPM
"""

import pandas as pd
import logging
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
from .validadores.validadores_bpm import bpm_validator
# Configuración de referencia para BPM
REFERENCE_HEADERS = [
    "ORDEN",
    "EXPEDIENTE_(ANTIGUO)",
    "TIPO_EXPEDIENTE",
    "ID_EXPEDIENTE_ECM",
    "NOMBRE_ARCHIVO",
    "MES_REPORTE",
    "FECHA_REPARTO",
    "ANO_REPARTO",
    "ANO_GESTION",
    "TIPO_DOC_IDENTIFICACION_APORTANTE",
    "NO_CC_O_NIT_APORTANTE",
    "NOMBRES_Y_O_RAZON_SOCIAL_APORTANTE",
    "TIPO_APORTANTE",
    "DIRECCION_RUT",
    "MUNICIPIO_RUT",
    "DPTO_RUT",
    "TELEFONO",
    "EMAIL",
    "NOMBRES_Y_APELLIDOS_REP_LEGAL",
    "CC_O_NIT_REP_LEGAL",
    "TELEFONO_REP_LEGAL",
    "NOMBRE_REMITENTE",
    "DENUNCIANTE___NOMBRES_Y_APELLIDOS_Y_O_RAZON_SOCIAL",
    "HALLAZGO___DENUNCIA",
    "PROGRAMA",
    "ANO_PROGRAMA",
    "NOMBRE_ACTIVIDAD_CIIU",
    "NOMBRE_SECCION_CIIU",
    "ESTADO"
]

# Configurar logger
logger = logging.getLogger(__name__)

class BPMColumnTransformer:
    """Transformador de columnas para archivos BPM"""
    
    def __init__(self):
        """Inicializar transformador de BPM"""
        self.logger = logging.getLogger(__name__)
        self.logger.info("Inicializando transformador de columnas BPM")
        
        # Crear mapeo inverso de tipos
        self.column_type_mapping = {}
        # Mapeo básico de tipos para BPM
        self.column_type_mapping = {
            "ORDEN": "integer",
            "ANO_REPARTO": "integer",
            "ANO_GESTION": "integer",
            "#_EMPLEADOS": "integer",
            "MES_REPORTE": "date",
            "FECHA_REPARTO": "date",
            "FECHA_NACIMIENTO___CONSTITUCION_EMPRESA": "date",
            "NO_CC_O_NIT_APORTANTE": "nit",
            "CC_O_NIT_REP_LEGAL": "nit",
            "CC_O_NIT_DENUNCIANTE": "nit"
        }
        self.logger.info(f"Mapeo de tipos creado para {len(self.column_type_mapping)} columnas")
    
    def transform_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Transforma un DataFrame completo según las reglas de BPM
        
        Args:
            df: DataFrame a transformar
            
        Returns:
            DataFrame: DataFrame transformado
        """
        self.logger.info(f"Iniciando transformación de DataFrame con {len(df)} filas y {len(df.columns)} columnas")
        
        try:
            # Crear copia para no modificar el original
            df_transformed = df.copy()
            
            # 1. Limpiar nombres de columnas
            df_transformed = self._clean_column_names(df_transformed)
            
            # 2. Aplicar transformaciones por tipo de columna
            df_transformed = self._apply_type_transformations(df_transformed)
            
            # 3. Validar datos según tipos asignados
            df_transformed = self._validate_data(df_transformed)
            
            # 4. Aplicar limpieza general
            df_transformed = self._apply_general_cleaning(df_transformed)
            
            # 5. Reordenar columnas según referencia
            df_transformed = self._reorder_columns(df_transformed)
            
            self.logger.info("Transformación de DataFrame completada exitosamente")
            return df_transformed
            
        except Exception as e:
            self.logger.error(f"Error transformando DataFrame: {str(e)}")
            raise
    
    def _clean_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Limpia y normaliza nombres de columnas
        
        Args:
            df: DataFrame con nombres de columnas a limpiar
            
        Returns:
            DataFrame: DataFrame con nombres de columnas limpios
        """
        self.logger.info("Limpiando nombres de columnas...")
        
        # Crear mapeo de nombres originales a limpios
        column_mapping = {}
        for col in df.columns:
            clean_name = self._clean_column_name(col)
            column_mapping[col] = clean_name
        
        # Renombrar columnas
        df_renamed = df.rename(columns=column_mapping)
        
        self.logger.info(f"Columnas renombradas: {len(column_mapping)}")
        return df_renamed
    
    def _clean_column_name(self, column_name: str) -> str:
        """
        Limpia un nombre de columna individual
        
        Args:
            column_name: Nombre de columna a limpiar
            
        Returns:
            str: Nombre de columna limpio
        """
        if pd.isna(column_name):
            return "COLUMNA_DESCONOCIDA"
        
        # Convertir a string y limpiar
        clean_name = str(column_name).strip()
        
        # Remover caracteres problemáticos
        clean_name = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', clean_name)
        
        # Normalizar espacios y caracteres especiales
        clean_name = re.sub(r'\s+', '_', clean_name)
        clean_name = re.sub(r'[^\w\-_]', '', clean_name)
        
        # Asegurar que no esté vacío
        if not clean_name:
            clean_name = "COLUMNA_VACIA"
        
        return clean_name
    
    def _apply_type_transformations(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aplica transformaciones específicas según el tipo de columna
        
        Args:
            df: DataFrame a transformar
            
        Returns:
            DataFrame: DataFrame con transformaciones aplicadas
        """
        self.logger.info("Aplicando transformaciones por tipo de columna...")
        
        df_transformed = df.copy()
        
        for column in df_transformed.columns:
            column_type = self.column_type_mapping.get(column, 'string')
            
            try:
                if column_type == 'date':
                    df_transformed[column] = self._transform_date_column(df_transformed[column])
                elif column_type == 'integer':
                    df_transformed[column] = self._transform_integer_column(df_transformed[column])
                elif column_type == 'telefono':
                    df_transformed[column] = self._transform_telefono_column(df_transformed[column])
                elif column_type == 'email':
                    df_transformed[column] = self._transform_email_column(df_transformed[column])
                elif column_type == 'boolean':
                    df_transformed[column] = self._transform_boolean_column(df_transformed[column])
                elif column_type == 'string':
                    df_transformed[column] = self._transform_string_column(df_transformed[column])
                
            except Exception as e:
                self.logger.warning(f"Error transformando columna '{column}' ({column_type}): {str(e)}")
                # Mantener columna original en caso de error
        
        self.logger.info("Transformaciones por tipo aplicadas")
        return df_transformed
    
    def _transform_date_column(self, series: pd.Series) -> pd.Series:
        """
        Transforma columna de fechas
        
        Args:
            series: Serie de fechas a transformar
            
        Returns:
            pd.Series: Serie transformada
        """
        def convert_date(value):
            if pd.isna(value) or value == '':
                return ""
            
            try:
                # Usar el validador de BPM
                is_valid, error_msg, converted_value = bpm_validator.validate_date(value)
                if is_valid and converted_value:
                    return converted_value
                else:
                    return str(value)  # Mantener valor original si no se puede convertir
            except:
                return str(value)
        
        return series.apply(convert_date)
    
    def _transform_integer_column(self, series: pd.Series) -> pd.Series:
        """
        Transforma columna de enteros
        
        Args:
            series: Serie de enteros a transformar
            
        Returns:
            pd.Series: Serie transformada
        """
        def convert_integer(value):
            if pd.isna(value) or value == '':
                return None
            
            try:
                # Usar el validador de BPM
                is_valid, error_msg, converted_value = bpm_validator.validate_integer(value)
                if is_valid and converted_value is not None:
                    return converted_value
                else:
                    return None  # Valor no válido
            except:
                return None
        
        return series.apply(convert_integer)
    
    def _transform_telefono_column(self, series: pd.Series) -> pd.Series:
        """
        Transforma columna de teléfonos/NIT
        
        Args:
            series: Serie de teléfonos a transformar
            
        Returns:
            pd.Series: Serie transformada
        """
        def convert_telefono(value):
            if pd.isna(value) or value == '':
                return ""
            
            try:
                # Usar el validador de BPM
                is_valid, error_msg, converted_value = bpm_validator.validate_telefono(value)
                if is_valid:
                    return converted_value
                else:
                    return str(value)  # Mantener valor original
            except:
                return str(value)
        
        return series.apply(convert_telefono)
    
    def _transform_email_column(self, series: pd.Series) -> pd.Series:
        """
        Transforma columna de emails
        
        Args:
            series: Serie de emails a transformar
            
        Returns:
            pd.Series: Serie transformada
        """
        def convert_email(value):
            if pd.isna(value) or value == '':
                return ""
            
            try:
                # Usar el validador de BPM
                is_valid, error_msg, converted_value = bpm_validator.validate_email(value)
                if is_valid:
                    return converted_value
                else:
                    return str(value)  # Mantener valor original
            except:
                return str(value)
        
        return series.apply(convert_email)
    
    def _transform_boolean_column(self, series: pd.Series) -> pd.Series:
        """
        Transforma columna de booleanos
        
        Args:
            series: Serie de booleanos a transformar
            
        Returns:
            pd.Series: Serie transformada
        """
        def convert_boolean(value):
            if pd.isna(value) or value == '':
                return ""
            
            try:
                # Usar el validador de BPM
                is_valid, error_msg, converted_value = bpm_validator.validate_boolean(value)
                if is_valid and converted_value:
                    return converted_value
                else:
                    return str(value)  # Mantener valor original
            except:
                return str(value)
        
        return series.apply(convert_boolean)
    
    def _transform_string_column(self, series: pd.Series) -> pd.Series:
        """
        Transforma columna de strings
        
        Args:
            series: Serie de strings a transformar
            
        Returns:
            pd.Series: Serie transformada
        """
        def convert_string(value):
            if pd.isna(value):
                return ""
            
            try:
                # Usar el validador de BPM
                is_valid, error_msg, converted_value = bpm_validator.validate_string(value)
                if is_valid:
                    return converted_value
                else:
                    return str(value)  # Mantener valor original
            except:
                return str(value)
        
        return series.apply(convert_string)
    
    def _validate_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Valida todos los datos según los tipos asignados
        
        Args:
            df: DataFrame a validar
            
        Returns:
            DataFrame: DataFrame validado
        """
        self.logger.info("Validando datos según tipos asignados...")
        
        # Crear DataFrame de errores para logging
        validation_errors = []
        
        for column in df.columns:
            column_type = self.column_type_mapping.get(column, 'string')
            
            # Validar solo las primeras filas para logging (no todas para evitar lentitud)
            sample_data = df[column].head(100).to_dict()
            
            for idx, value in sample_data.items():
                try:
                    if column_type == 'date':
                        is_valid, error_msg, _ = bpm_validator.validate_date(value)
                    elif column_type == 'integer':
                        is_valid, error_msg, _ = bpm_validator.validate_integer(value)
                    elif column_type == 'telefono':
                        is_valid, error_msg, _ = bpm_validator.validate_telefono(value)
                    elif column_type == 'email':
                        is_valid, error_msg, _ = bpm_validator.validate_email(value)
                    elif column_type == 'boolean':
                        is_valid, error_msg, _ = bpm_validator.validate_boolean(value)
                    else:
                        is_valid, error_msg, _ = bpm_validator.validate_string(value)
                    
                    if not is_valid:
                        validation_errors.append({
                            'column': column,
                            'row': idx,
                            'value': value,
                            'error': error_msg,
                            'type': column_type
                        })
                        
                except Exception as e:
                    validation_errors.append({
                        'column': column,
                        'row': idx,
                        'value': value,
                        'error': f"Error interno: {str(e)}",
                        'type': column_type
                    })
        
        # Log de errores de validación
        if validation_errors:
            self.logger.warning(f"Se encontraron {len(validation_errors)} errores de validación en la muestra")
            for error in validation_errors[:10]:  # Solo los primeros 10 errores
                self.logger.warning(f"  {error['column']}[{error['row']}]: {error['error']}")
        else:
            self.logger.info("No se encontraron errores de validación en la muestra")
        
        return df
    
    def _apply_general_cleaning(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aplica limpieza general a todo el DataFrame
        
        Args:
            df: DataFrame a limpiar
            
        Returns:
            DataFrame: DataFrame limpio
        """
        self.logger.info("Aplicando limpieza general...")
        
        df_clean = df.copy()
        
        # 1. Reemplazar valores NaN con strings vacíos
        df_clean = df_clean.fillna("")
        
        # 2. Limpiar strings de caracteres problemáticos
        for col in df_clean.select_dtypes(include=['object']).columns:
            df_clean[col] = df_clean[col].astype(str).str.replace(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', regex=True)
        
        # 3. Normalizar espacios en strings
        for col in df_clean.select_dtypes(include=['object']).columns:
            df_clean[col] = df_clean[col].astype(str).str.strip()
        
        self.logger.info("Limpieza general completada")
        return df_clean
    
    def _reorder_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Reordena las columnas según el orden de referencia
        
        Args:
            df: DataFrame a reordenar
            
        Returns:
            DataFrame: DataFrame con columnas reordenadas
        """
        self.logger.info("Reordenando columnas según referencia...")
        
        # Obtener columnas que están en la referencia
        reference_cols = [col for col in REFERENCE_HEADERS if col in df.columns]
        
        # Obtener columnas que no están en la referencia
        other_cols = [col for col in df.columns if col not in REFERENCE_HEADERS]
        
        # Crear orden final: primero las de referencia, luego las demás
        final_order = reference_cols + other_cols
        
        # Reordenar DataFrame
        df_reordered = df[final_order]
        
        self.logger.info(f"Columnas reordenadas: {len(reference_cols)} de referencia + {len(other_cols)} adicionales")
        return df_reordered
    
    def get_transformation_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de la transformación
        
        Returns:
            Dict: Estadísticas de transformación
        """
        return {
            "total_columns": len(self.column_type_mapping),
            "column_types": {
                "integer": len([col for col, type_val in self.column_type_mapping.items() if type_val == "integer"]),
                "date": len([col for col, type_val in self.column_type_mapping.items() if type_val == "date"]),
                "nit": len([col for col, type_val in self.column_type_mapping.items() if type_val == "nit"]),
                "string": len([col for col, type_val in self.column_type_mapping.items() if type_val == "string"])
            },
            "reference_headers": len(REFERENCE_HEADERS),
            "transformer_name": "BPM Column Transformer",
            "version": "1.0.0"
        }

# Instancia global del transformador
bpm_transformer = BPMColumnTransformer() 