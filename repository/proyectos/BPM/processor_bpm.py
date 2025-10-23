"""
Procesador principal para BPM
Implementa la lógica de procesamiento completo para archivos BPM
"""

import pandas as pd
import logging
import os
import tempfile
from typing import Dict, Any, Optional
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

# Configuración de procesamiento para BPM
PROCESSING_CONFIG = {
    "batch_size": 1000,
    "max_workers": 4,
    "timeout": 300,
    "retry_attempts": 3,
    "cleanup_temp_files": True
}
from .transformar_columnas_bpm import bpm_transformer
from .validadores.validadores_bpm import bpm_validator

# Configurar logger
logger = logging.getLogger(__name__)

class BPMProcessor:
    """Procesador principal para archivos BPM"""
    
    def __init__(self):
        """Inicializar procesador de BPM"""
        self.logger = logging.getLogger(__name__)
        self.logger.info("Inicializando procesador BPM")
        
        # Configuración del procesador
        self.config = PROCESSING_CONFIG
        self.type_mapping = {}
        self.reference_headers = REFERENCE_HEADERS
        
        # Estadísticas del procesamiento
        self.stats = {
            'total_rows_processed': 0,
            'total_columns_processed': 0,
            'validation_errors': 0,
            'transformation_errors': 0,
            'processing_time': 0,
            'file_size_input': 0,
            'file_size_output': 0
        }
        
        self.logger.info("Procesador BPM inicializado exitosamente")
    
    def process_csv(self, input_file: str, output_file: str, error_file: str) -> Dict[str, Any]:
        """
        Procesa un archivo CSV completo según las reglas de BPM
        
        Args:
            input_file: Ruta del archivo de entrada
            output_file: Ruta del archivo de salida
            error_file: Ruta del archivo de errores
            
        Returns:
            Dict: Estadísticas del procesamiento
        """
        import time
        start_time = time.time()
        
        self.logger.info(f"=== INICIANDO PROCESAMIENTO BPM ===")
        self.logger.info(f"Archivo de entrada: {input_file}")
        self.logger.info(f"Archivo de salida: {output_file}")
        self.logger.info(f"Archivo de errores: {error_file}")
        
        try:
            # 1. Verificar archivo de entrada
            self._verify_input_file(input_file)
            
            # 2. Leer archivo CSV
            df = self._read_csv_file(input_file)
            
            # 3. Procesar DataFrame
            df_processed = self._process_dataframe(df)
            
            # 4. Guardar archivo procesado
            self._save_processed_file(df_processed, output_file)
            
            # 5. Generar reporte de errores
            self._generate_error_report(error_file)
            
            # 6. Calcular estadísticas finales
            processing_time = time.time() - start_time
            self._calculate_final_stats(input_file, output_file, processing_time)
            
            self.logger.info("=== PROCESAMIENTO BPM COMPLETADO EXITOSAMENTE ===")
            return self.stats
            
        except Exception as e:
            self.logger.error(f"Error en procesamiento BPM: {str(e)}")
            self.logger.error("Traceback completo:", exc_info=True)
            raise
    
    def _verify_input_file(self, input_file: str) -> None:
        """
        Verifica que el archivo de entrada exista y sea válido
        
        Args:
            input_file: Ruta del archivo de entrada
            
        Raises:
            FileNotFoundError: Si el archivo no existe
            ValueError: Si el archivo está vacío
        """
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"El archivo de entrada no existe: {input_file}")
        
        file_size = os.path.getsize(input_file)
        if file_size == 0:
            raise ValueError(f"El archivo de entrada está vacío: {input_file}")
        
        self.stats['file_size_input'] = file_size
        self.logger.info(f"Archivo de entrada verificado: {file_size:,} bytes")
    
    def _read_csv_file(self, input_file: str) -> pd.DataFrame:
        """
        Lee el archivo CSV con manejo robusto de errores
        
        Args:
            input_file: Ruta del archivo CSV
            
        Returns:
            pd.DataFrame: DataFrame leído del archivo
            
        Raises:
            Exception: Si no se puede leer el archivo
        """
        self.logger.info("Leyendo archivo CSV...")
        
        # Intentar diferentes estrategias de lectura
        reading_strategies = [
            # Estrategia 1: UTF-8 con separador automático
            {'encoding': 'utf-8', 'sep': None, 'engine': 'python'},
            # Estrategia 2: Latin-1 con separador automático
            {'encoding': 'latin-1', 'sep': None, 'engine': 'python'},
            # Estrategia 3: UTF-8 con separador específico
            {'encoding': 'utf-8', 'sep': ';', 'engine': 'python'},
            # Estrategia 4: UTF-8 con separador específico
            {'encoding': 'utf-8', 'sep': ',', 'engine': 'python'},
            # Estrategia 5: Sin encoding específico
            {'sep': None, 'engine': 'python'}
        ]
        
        df = None
        last_error = None
        
        for i, strategy in enumerate(reading_strategies):
            try:
                self.logger.info(f"Intentando estrategia de lectura {i+1}: {strategy}")
                
                df = pd.read_csv(
                    input_file,
                    dtype=str,  # Leer todo como string inicialmente
                    **strategy
                )
                
                self.logger.info(f"✅ Archivo leído exitosamente con estrategia {i+1}")
                self.logger.info(f"   - Filas: {len(df):,}")
                self.logger.info(f"   - Columnas: {len(df.columns)}")
                self.logger.info(f"   - Separador detectado: {getattr(df, '_engine', 'unknown')}")
                
                break
                
            except Exception as e:
                last_error = e
                self.logger.warning(f"❌ Estrategia {i+1} falló: {str(e)}")
                continue
        
        if df is None:
            raise Exception(f"No se pudo leer el archivo CSV con ninguna estrategia. Último error: {str(last_error)}")
        
        # Verificar que el DataFrame tenga contenido
        if len(df) == 0:
            raise ValueError("El archivo CSV no contiene datos")
        
        if len(df.columns) == 0:
            raise ValueError("El archivo CSV no contiene columnas")
        
        self.stats['total_rows_processed'] = len(df)
        self.stats['total_columns_processed'] = len(df.columns)
        
        self.logger.info(f"Archivo CSV leído exitosamente: {len(df):,} filas × {len(df.columns)} columnas")
        return df
    
    def _process_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Procesa el DataFrame completo según las reglas de BPM
        
        Args:
            df: DataFrame original a procesar
            
        Returns:
            pd.DataFrame: DataFrame procesado
        """
        self.logger.info("Procesando DataFrame...")
        
        try:
            # 1. Aplicar transformaciones de columnas
            df_transformed = bpm_transformer.transform_dataframe(df)
            
            # 2. Validar datos finales
            df_validated = self._validate_final_data(df_transformed)
            
            # 3. Aplicar limpieza final
            df_final = self._apply_final_cleaning(df_validated)
            
            self.logger.info("DataFrame procesado exitosamente")
            return df_final
            
        except Exception as e:
            self.logger.error(f"Error procesando DataFrame: {str(e)}")
            raise
    
    def _validate_final_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Valida los datos finales del DataFrame
        
        Args:
            df: DataFrame a validar
            
        Returns:
            pd.DataFrame: DataFrame validado
        """
        self.logger.info("Validando datos finales...")
        
        validation_errors = []
        
        # Validar solo una muestra para no ralentizar el proceso
        sample_size = min(1000, len(df))
        sample_df = df.head(sample_size)
        
        for column in sample_df.columns:
            column_type = self.type_mapping.get(column, 'string')
            
            # Validar muestra de la columna
            sample_values = sample_df[column].dropna().head(100)
            
            for value in sample_values:
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
                            'value': value,
                            'error': error_msg,
                            'type': column_type
                        })
                        
                except Exception as e:
                    validation_errors.append({
                        'column': column,
                        'value': value,
                        'error': f"Error interno: {str(e)}",
                        'type': column_type
                    })
        
        # Actualizar estadísticas
        self.stats['validation_errors'] = len(validation_errors)
        
        if validation_errors:
            self.logger.warning(f"Se encontraron {len(validation_errors)} errores de validación en la muestra")
            # Guardar errores para el reporte
            self._validation_errors = validation_errors
        else:
            self.logger.info("No se encontraron errores de validación en la muestra")
            self._validation_errors = []
        
        return df
    
    def _apply_final_cleaning(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aplica limpieza final al DataFrame
        
        Args:
            df: DataFrame a limpiar
            
        Returns:
            pd.DataFrame: DataFrame limpio
        """
        self.logger.info("Aplicando limpieza final...")
        
        df_clean = df.copy()
        
        # 1. Reemplazar valores NaN con strings vacíos
        df_clean = df_clean.fillna("")
        
        # 2. Limpiar strings de caracteres problemáticos
        for col in df_clean.select_dtypes(include=['object']).columns:
            df_clean[col] = df_clean[col].astype(str).str.replace(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', regex=True)
        
        # 3. Normalizar espacios en strings
        for col in df_clean.select_dtypes(include=['object']).columns:
            df_clean[col] = df_clean[col].astype(str).str.strip()
        
        # 4. Limpiar strings vacíos
        for col in df_clean.select_dtypes(include=['object']).columns:
            df_clean[col] = df_clean[col].replace(['nan', 'NaN', 'NULL', 'null', ''], '')
        
        self.logger.info("Limpieza final completada")
        return df_clean
    
    def _save_processed_file(self, df: pd.DataFrame, output_file: str) -> None:
        """
        Guarda el DataFrame procesado en el archivo de salida
        
        Args:
            df: DataFrame procesado
            output_file: Ruta del archivo de salida
        """
        self.logger.info(f"Guardando archivo procesado: {output_file}")
        
        try:
            # Crear directorio si no existe
            output_dir = os.path.dirname(output_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # Guardar como CSV
            df.to_csv(
                output_file,
                index=False,
                sep=';',  # Separador estándar para BPM
                encoding='utf-8',
                quoting=1,  # QUOTE_ALL para evitar problemas con separadores
                escapechar='\\'  # Carácter de escape para separadores en texto
            )
            
            # Verificar que se guardó correctamente
            if not os.path.exists(output_file):
                raise Exception("El archivo de salida no se creó correctamente")
            
            file_size = os.path.getsize(output_file)
            self.stats['file_size_output'] = file_size
            
            self.logger.info(f"Archivo procesado guardado exitosamente: {file_size:,} bytes")
            
        except Exception as e:
            self.logger.error(f"Error guardando archivo procesado: {str(e)}")
            raise
    
    def _generate_error_report(self, error_file: str) -> None:
        """
        Genera un reporte de errores de validación
        
        Args:
            error_file: Ruta del archivo de errores
        """
        self.logger.info(f"Generando reporte de errores: {error_file}")
        
        try:
            if not hasattr(self, '_validation_errors') or not self._validation_errors:
                # No hay errores, crear archivo vacío
                with open(error_file, 'w', encoding='utf-8') as f:
                    f.write("No se encontraron errores de validación en el procesamiento.\n")
                    f.write("Todos los datos fueron procesados exitosamente.\n")
                
                self.logger.info("Reporte de errores generado: Sin errores")
                return
            
            # Crear directorio si no existe
            error_dir = os.path.dirname(error_file)
            if error_dir and not os.path.exists(error_dir):
                os.makedirs(error_dir)
            
            # Generar reporte detallado
            with open(error_file, 'w', encoding='utf-8') as f:
                f.write("REPORTE DE ERRORES DE VALIDACIÓN BPM\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Total de errores encontrados: {len(self._validation_errors)}\n")
                f.write(f"Archivo procesado: {self.stats['total_rows_processed']:,} filas\n")
                f.write(f"Columnas procesadas: {self.stats['total_columns_processed']}\n\n")
                
                f.write("DETALLE DE ERRORES:\n")
                f.write("-" * 30 + "\n")
                
                for i, error in enumerate(self._validation_errors, 1):
                    f.write(f"{i}. Columna: {error['column']}\n")
                    f.write(f"   Tipo esperado: {error['type']}\n")
                    f.write(f"   Valor problemático: {error['value']}\n")
                    f.write(f"   Error: {error['error']}\n")
                    f.write("\n")
            
            self.logger.info(f"Reporte de errores generado: {len(self._validation_errors)} errores documentados")
            
        except Exception as e:
            self.logger.error(f"Error generando reporte de errores: {str(e)}")
            # No fallar el proceso por errores en el reporte
    
    def _calculate_final_stats(self, input_file: str, output_file: str, processing_time: float) -> None:
        """
        Calcula estadísticas finales del procesamiento
        
        Args:
            input_file: Ruta del archivo de entrada
            output_file: Ruta del archivo de salida
            processing_time: Tiempo de procesamiento en segundos
        """
        self.stats['processing_time'] = processing_time
        
        # Calcular tasas de procesamiento
        if self.stats['total_rows_processed'] > 0:
            rows_per_second = self.stats['total_rows_processed'] / processing_time
            self.stats['rows_per_second'] = round(rows_per_second, 2)
        
        # Calcular eficiencia de compresión
        if self.stats['file_size_input'] > 0:
            compression_ratio = self.stats['file_size_output'] / self.stats['file_size_input']
            self.stats['compression_ratio'] = round(compression_ratio, 3)
        
        self.logger.info("=== ESTADÍSTICAS FINALES DEL PROCESAMIENTO ===")
        self.logger.info(f"Tiempo total: {processing_time:.2f} segundos")
        self.logger.info(f"Filas procesadas: {self.stats['total_rows_processed']:,}")
        self.logger.info(f"Columnas procesadas: {self.stats['total_columns_processed']}")
        self.logger.info(f"Errores de validación: {self.stats['validation_errors']}")
        self.logger.info(f"Tamaño archivo entrada: {self.stats['file_size_input']:,} bytes")
        self.logger.info(f"Tamaño archivo salida: {self.stats['file_size_output']:,} bytes")
        
        if 'rows_per_second' in self.stats:
            self.logger.info(f"Velocidad: {self.stats['rows_per_second']} filas/segundo")
        
        if 'compression_ratio' in self.stats:
            self.logger.info(f"Ratio de compresión: {self.stats['compression_ratio']}")
    
    def get_processor_info(self) -> Dict[str, Any]:
        """
        Obtiene información del procesador
        
        Returns:
            Dict: Información del procesador
        """
        return {
            "name": "BPM Processor",
            "version": "1.0.0",
            "description": "Procesador especializado para archivos BPM",
            "supported_types": list(self.type_mapping.keys()),
            "total_columns": sum(len(cols) for cols in self.type_mapping.values()),
            "reference_headers": len(self.reference_headers),
            "config": self.config
        }

# Instancia global del procesador
bpm_processor = BPMProcessor() 