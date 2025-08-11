"""
Transformador de formatos para ExcelSior API.

Proporciona funcionalidades para convertir archivos entre diferentes
formatos (CSV, Excel, TXT, SAV) con manejo robusto de errores.
"""

import pandas as pd
import os
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
import pyreadstat

from utils.logger import LoggerMixin
from utils.exceptions import FileProcessingError, UnsupportedFileTypeError
from config.settings import DEFAULT_ENCODING, DEFAULT_DELIMITER

class FormatTransformer(LoggerMixin):
    """Transformador especializado para conversiones de formato."""
    
    def __init__(self):
        super().__init__()
        self.supported_input_formats = ['.csv', '.xlsx', '.xls', '.txt', '.sav']
        self.supported_output_formats = ['.csv', '.xlsx', '.xls']
    
    def csv_to_csv_with_delimiter_change(self, input_file: Path, output_file: Path, 
                                       old_delimiter: str, new_delimiter: str,
                                       add_metadata: bool = True) -> Dict[str, Any]:
        """
        Convierte CSV cambiando delimitador y opcionalmente agregando metadatos.
        
        Args:
            input_file: Archivo CSV de entrada
            output_file: Archivo CSV de salida
            old_delimiter: Delimitador original
            new_delimiter: Nuevo delimitador
            add_metadata: Si agregar columnas de metadatos
            
        Returns:
            Diccionario con información del proceso
        """
        self.log_operation("csv_delimiter_change", f"Cambiando delimitador: {old_delimiter} -> {new_delimiter}")
        
        try:
            # Leer archivo CSV
            df = pd.read_csv(input_file, delimiter=old_delimiter, dtype=str)
            
            # Extraer información de fecha del nombre del archivo
            date_info = self._extract_date_from_filename(input_file.name)
            
            # Agregar metadatos si se solicita
            if add_metadata:
                df.insert(0, 'mes_reporte', date_info['mes_reporte'])
                df.insert(0, 'nombre_archivo', input_file.name)
            
            # Escribir archivo con nuevo delimitador
            df.to_csv(output_file, sep=new_delimiter, index=False, encoding=DEFAULT_ENCODING)
            
            result = {
                "input_file": str(input_file),
                "output_file": str(output_file),
                "old_delimiter": old_delimiter,
                "new_delimiter": new_delimiter,
                "rows_processed": len(df),
                "columns_processed": len(df.columns),
                "metadata_added": add_metadata,
                "success": True
            }
            
            self.log_operation("delimiter_change_complete", f"Conversión completada: {len(df)} filas")
            return result
            
        except Exception as e:
            raise FileProcessingError(f"Error en cambio de delimitador: {str(e)}", file_path=str(input_file))
    
    def sav_to_csv(self, input_file: Path, output_file: Path, delimiter: str = DEFAULT_DELIMITER) -> Dict[str, Any]:
        """
        Convierte archivo SAV (SPSS) a CSV.
        
        Args:
            input_file: Archivo SAV de entrada
            output_file: Archivo CSV de salida
            delimiter: Delimitador para el CSV
            
        Returns:
            Diccionario con información del proceso
        """
        self.log_operation("sav_to_csv", f"Convirtiendo SAV a CSV: {input_file}")
        
        try:
            # Leer archivo SAV
            df, meta = pyreadstat.read_sav(input_file)
            
            # Convertir todos los valores a string
            df = df.astype(str)
            
            # Escribir archivo CSV
            df.to_csv(output_file, sep=delimiter, index=False, encoding=DEFAULT_ENCODING)
            
            result = {
                "input_file": str(input_file),
                "output_file": str(output_file),
                "rows_processed": len(df),
                "columns_processed": len(df.columns),
                "variable_labels": meta.variable_labels if hasattr(meta, 'variable_labels') else {},
                "success": True
            }
            
            self.log_operation("sav_conversion_complete", f"Conversión SAV completada: {len(df)} filas")
            return result
            
        except Exception as e:
            raise FileProcessingError(f"Error en conversión SAV: {str(e)}", file_path=str(input_file))
    
    def txt_to_csv(self, input_file: Path, output_file: Path, 
                  input_delimiter: str, output_delimiter: str = DEFAULT_DELIMITER) -> Dict[str, Any]:
        """
        Convierte archivo TXT a CSV.
        
        Args:
            input_file: Archivo TXT de entrada
            output_file: Archivo CSV de salida
            input_delimiter: Delimitador del archivo TXT
            output_delimiter: Delimitador para el CSV
            
        Returns:
            Diccionario con información del proceso
        """
        self.log_operation("txt_to_csv", f"Convirtiendo TXT a CSV: {input_file}")
        
        try:
            # Leer archivo TXT
            df = pd.read_csv(input_file, delimiter=input_delimiter, dtype=str)
            
            # Escribir archivo CSV
            df.to_csv(output_file, sep=output_delimiter, index=False, encoding=DEFAULT_ENCODING)
            
            result = {
                "input_file": str(input_file),
                "output_file": str(output_file),
                "input_delimiter": input_delimiter,
                "output_delimiter": output_delimiter,
                "rows_processed": len(df),
                "columns_processed": len(df.columns),
                "success": True
            }
            
            self.log_operation("txt_conversion_complete", f"Conversión TXT completada: {len(df)} filas")
            return result
            
        except Exception as e:
            raise FileProcessingError(f"Error en conversión TXT: {str(e)}", file_path=str(input_file))
    
    def xlsx_to_csv(self, input_file: Path, output_file: Path, 
                   sheet_name: Optional[str] = None, delimiter: str = DEFAULT_DELIMITER,
                   add_month_column: bool = True) -> Dict[str, Any]:
        """
        Convierte archivo Excel a CSV.
        
        Args:
            input_file: Archivo Excel de entrada
            output_file: Archivo CSV de salida
            sheet_name: Nombre de la hoja a convertir (opcional)
            delimiter: Delimitador para el CSV
            add_month_column: Si agregar columna de mes de reporte
            
        Returns:
            Diccionario con información del proceso
        """
        self.log_operation("xlsx_to_csv", f"Convirtiendo Excel a CSV: {input_file}")
        
        try:
            # Leer archivo Excel
            if sheet_name:
                df = pd.read_excel(input_file, sheet_name=sheet_name)
            else:
                df = pd.read_excel(input_file)
            
            # Convertir todos los valores a string
            df = df.astype(str)
            
            # Agregar columna de mes de reporte si se solicita
            if add_month_column:
                date_info = self._extract_date_from_filename(input_file.name)
                df.insert(0, 'mes_reporte', date_info['mes_reporte'])
            
            # Escribir archivo CSV
            df.to_csv(output_file, sep=delimiter, index=False, encoding=DEFAULT_ENCODING)
            
            result = {
                "input_file": str(input_file),
                "output_file": str(output_file),
                "sheet_name": sheet_name,
                "rows_processed": len(df),
                "columns_processed": len(df.columns),
                "month_column_added": add_month_column,
                "success": True
            }
            
            self.log_operation("xlsx_conversion_complete", f"Conversión Excel completada: {len(df)} filas")
            return result
            
        except Exception as e:
            raise FileProcessingError(f"Error en conversión Excel: {str(e)}", file_path=str(input_file))
    
    def _extract_date_from_filename(self, filename: str) -> Dict[str, str]:
        """
        Extrae información de fecha del nombre del archivo.
        
        Args:
            filename: Nombre del archivo
            
        Returns:
            Diccionario con información de fecha extraída
        """
        # Patrón para archivos con formato IYYYYMMDD
        pattern = r"I(\d{8})"
        match = re.search(pattern, filename)
        
        if match:
            fecha_str = match.group(1)
            anio = fecha_str[:4]
            mes = fecha_str[4:6]
            dia = fecha_str[6:8]
            
            return {
                "anio": anio,
                "mes": mes,
                "dia": dia,
                "mes_reporte": f"{mes}_{anio}",
                "fecha_completa": f"{anio}-{mes}-{dia}"
            }
        
        return {
            "anio": "Desconocido",
            "mes": "Desconocido", 
            "dia": "Desconocido",
            "mes_reporte": "Desconocido",
            "fecha_completa": "Desconocido"
        }
    
    def batch_convert(self, input_files: List[Path], output_format: str, 
                     output_dir: Path, **kwargs) -> Dict[str, Any]:
        """
        Convierte múltiples archivos en lote.
        
        Args:
            input_files: Lista de archivos de entrada
            output_format: Formato de salida
            output_dir: Directorio de salida
            **kwargs: Parámetros adicionales para la conversión
            
        Returns:
            Diccionario con información del proceso
        """
        self.log_operation("batch_convert", f"Convirtiendo {len(input_files)} archivos a {output_format}")
        
        # Crear directorio de salida
        output_dir.mkdir(parents=True, exist_ok=True)
        
        results = {
            "total_files": len(input_files),
            "processed_files": 0,
            "failed_files": 0,
            "conversions": [],
            "errors": []
        }
        
        for input_file in input_files:
            try:
                # Determinar método de conversión según el formato
                if input_file.suffix.lower() == '.csv' and output_format == 'csv':
                    # Cambio de delimitador
                    output_file = output_dir / f"{input_file.stem}_converted.csv"
                    result = self.csv_to_csv_with_delimiter_change(
                        input_file, output_file, 
                        kwargs.get('old_delimiter', '|@'), 
                        kwargs.get('new_delimiter', '|'),
                        kwargs.get('add_metadata', True)
                    )
                elif input_file.suffix.lower() == '.sav' and output_format == 'csv':
                    # SAV a CSV
                    output_file = output_dir / f"{input_file.stem}.csv"
                    result = self.sav_to_csv(input_file, output_file, kwargs.get('delimiter', '|'))
                elif input_file.suffix.lower() == '.txt' and output_format == 'csv':
                    # TXT a CSV
                    output_file = output_dir / f"{input_file.stem}.csv"
                    result = self.txt_to_csv(
                        input_file, output_file,
                        kwargs.get('input_delimiter', '|'),
                        kwargs.get('output_delimiter', '|')
                    )
                elif input_file.suffix.lower() in ['.xlsx', '.xls'] and output_format == 'csv':
                    # Excel a CSV
                    output_file = output_dir / f"{input_file.stem}.csv"
                    result = self.xlsx_to_csv(
                        input_file, output_file,
                        kwargs.get('sheet_name'),
                        kwargs.get('delimiter', '|'),
                        kwargs.get('add_month_column', True)
                    )
                else:
                    raise UnsupportedFileTypeError(
                        f"Conversión no soportada: {input_file.suffix} -> {output_format}"
                    )
                
                results["conversions"].append(result)
                results["processed_files"] += 1
                
            except Exception as e:
                results["failed_files"] += 1
                results["errors"].append(f"Error procesando {input_file}: {str(e)}")
                self.log_operation("conversion_error", f"Error en conversión: {str(e)}", level="error")
        
        results["success"] = results["failed_files"] == 0
        return results
    
    def validate_conversion(self, input_file: Path, output_format: str) -> bool:
        """
        Valida si una conversión es posible.
        
        Args:
            input_file: Archivo de entrada
            output_format: Formato de salida deseado
            
        Returns:
            True si la conversión es posible
        """
        input_format = input_file.suffix.lower()
        
        # Verificar formatos soportados
        if input_format not in self.supported_input_formats:
            return False
        
        if output_format not in self.supported_output_formats:
            return False
        
        # Verificar combinaciones válidas
        valid_conversions = {
            '.csv': ['csv'],
            '.xlsx': ['csv'],
            '.xls': ['csv'],
            '.txt': ['csv'],
            '.sav': ['csv']
        }
        
        return output_format in valid_conversions.get(input_format, []) 