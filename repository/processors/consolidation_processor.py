"""
Procesador de consolidación para ExcelSior API.

Proporciona funcionalidades para consolidar múltiples archivos
en diferentes formatos con validación y logging.
"""

import pandas as pd
import os
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any, Union
from datetime import datetime

from utils.logger import LoggerMixin
from utils.exceptions import FileProcessingError
from .csv_processor import CSVProcessor
from .excel_processor import ExcelProcessor

class ConsolidationProcessor(LoggerMixin):
    """Procesador especializado para consolidación de archivos."""
    
    def __init__(self):
        super().__init__()
        self.csv_processor = CSVProcessor()
        self.excel_processor = ExcelProcessor()
    
    def consolidate_csv_files(self, csv_files: List[Path], output_file: Path, 
                            delimiter: str = '|', add_metadata: bool = True) -> Dict[str, Any]:
        """
        Consolida múltiples archivos CSV en uno solo.
        
        Args:
            csv_files: Lista de archivos CSV a consolidar
            output_file: Archivo de salida consolidado
            delimiter: Delimitador a usar
            add_metadata: Si agregar columnas de metadatos
            
        Returns:
            Diccionario con información del proceso
        """
        self.log_operation("consolidate_csv", f"Consolidando {len(csv_files)} archivos CSV")
        
        dataframes = []
        processed_files = 0
        total_rows = 0
        
        for csv_file in csv_files:
            try:
                if not csv_file.exists():
                    self.log_operation("file_not_found", f"Archivo no encontrado: {csv_file}")
                    continue
                
                # Leer archivo CSV
                headers, data = self.csv_processor.read_csv_file(csv_file, delimiter=delimiter)
                
                # Limpiar datos
                cleaned_data = self.csv_processor.clean_data(data)
                
                # Agregar metadatos si se solicita
                if add_metadata:
                    date_info = self.csv_processor.extract_date_from_filename(csv_file.name)
                    headers, cleaned_data = self.csv_processor.add_metadata_columns(
                        headers, cleaned_data, csv_file.name, date_info
                    )
                
                # Crear DataFrame
                df = pd.DataFrame(cleaned_data, columns=headers)
                dataframes.append(df)
                
                processed_files += 1
                total_rows += len(cleaned_data)
                
                self.log_operation("file_processed", f"Archivo procesado: {csv_file.name} ({len(cleaned_data)} filas)")
                
            except Exception as e:
                self.log_operation("file_error", f"Error procesando {csv_file}: {str(e)}", level="error")
        
        # Consolidar DataFrames
        if not dataframes:
            raise FileProcessingError("No se pudo procesar ningún archivo válido")
        
        try:
            combined_df = pd.concat(dataframes, ignore_index=True)
            
            # Escribir archivo consolidado
            self.csv_processor.write_csv_file(output_file, combined_df.columns.tolist(), combined_df.values.tolist(), delimiter)
            
            result = {
                "processed_files": processed_files,
                "total_rows": total_rows,
                "consolidated_rows": len(combined_df),
                "output_file": str(output_file),
                "success": True
            }
            
            self.log_operation("consolidation_complete", f"Consolidación completada: {len(combined_df)} filas")
            return result
            
        except Exception as e:
            raise FileProcessingError(f"Error en la consolidación: {str(e)}")
    
    def consolidate_to_excel(self, csv_files: List[Path], output_file: Path, 
                           delimiter: str = '|') -> Dict[str, Any]:
        """
        Consolida archivos CSV en un archivo Excel.
        
        Args:
            csv_files: Lista de archivos CSV a consolidar
            output_file: Archivo Excel de salida
            delimiter: Delimitador de los archivos CSV
            
        Returns:
            Diccionario con información del proceso
        """
        self.log_operation("consolidate_to_excel", f"Consolidando {len(csv_files)} archivos CSV a Excel")
        
        return self.excel_processor.merge_csv_files_to_excel(csv_files, output_file, delimiter)
    
    def consolidate_mixed_files(self, files: List[Path], output_file: Path, 
                              output_format: str = 'csv') -> Dict[str, Any]:
        """
        Consolida archivos de diferentes formatos.
        
        Args:
            files: Lista de archivos a consolidar
            output_file: Archivo de salida
            output_format: Formato de salida ('csv' o 'excel')
            
        Returns:
            Diccionario con información del proceso
        """
        self.log_operation("consolidate_mixed", f"Consolidando {len(files)} archivos mixtos")
        
        dataframes = []
        processed_files = 0
        total_rows = 0
        
        for file_path in files:
            try:
                if not file_path.exists():
                    self.log_operation("file_not_found", f"Archivo no encontrado: {file_path}")
                    continue
                
                # Determinar tipo de archivo y procesar
                if file_path.suffix.lower() == '.csv':
                    headers, data = self.csv_processor.read_csv_file(file_path)
                    df = pd.DataFrame(data, columns=headers)
                elif file_path.suffix.lower() in ['.xlsx', '.xls']:
                    headers, data = self.excel_processor.read_excel_file(file_path)
                    df = pd.DataFrame(data, columns=headers)
                else:
                    self.log_operation("unsupported_format", f"Formato no soportado: {file_path.suffix}")
                    continue
                
                # Limpiar datos
                df = df.applymap(self._clean_value)
                dataframes.append(df)
                
                processed_files += 1
                total_rows += len(df)
                
                self.log_operation("file_processed", f"Archivo procesado: {file_path.name} ({len(df)} filas)")
                
            except Exception as e:
                self.log_operation("file_error", f"Error procesando {file_path}: {str(e)}", level="error")
        
        # Consolidar DataFrames
        if not dataframes:
            raise FileProcessingError("No se pudo procesar ningún archivo válido")
        
        try:
            combined_df = pd.concat(dataframes, ignore_index=True)
            
            # Escribir archivo de salida
            if output_format.lower() == 'csv':
                self.csv_processor.write_csv_file(output_file, combined_df.columns.tolist(), combined_df.values.tolist())
            elif output_format.lower() == 'excel':
                excel_data = {output_file.stem: (combined_df.columns.tolist(), combined_df.values.tolist())}
                self.excel_processor.write_excel_file(output_file, excel_data)
            else:
                raise FileProcessingError(f"Formato de salida no soportado: {output_format}")
            
            result = {
                "processed_files": processed_files,
                "total_rows": total_rows,
                "consolidated_rows": len(combined_df),
                "output_file": str(output_file),
                "output_format": output_format,
                "success": True
            }
            
            self.log_operation("consolidation_complete", f"Consolidación completada: {len(combined_df)} filas")
            return result
            
        except Exception as e:
            raise FileProcessingError(f"Error en la consolidación: {str(e)}")
    
    def _clean_value(self, value: Any) -> str:
        """
        Limpia un valor individual.
        
        Args:
            value: Valor a limpiar
            
        Returns:
            Valor limpio
        """
        if pd.isna(value):
            return ""
        
        value_str = str(value).strip()
        
        # Limpiar valores tipo '123.0' -> '123'
        if value_str.endswith('.0'):
            value_str = value_str[:-2]
        
        return value_str
    
    def validate_consolidation(self, files: List[Path]) -> Dict[str, Any]:
        """
        Valida archivos antes de la consolidación.
        
        Args:
            files: Lista de archivos a validar
            
        Returns:
            Diccionario con resultados de validación
        """
        self.log_operation("validate_consolidation", f"Validando {len(files)} archivos")
        
        validation_results = {
            "total_files": len(files),
            "valid_files": 0,
            "invalid_files": 0,
            "file_details": {},
            "errors": []
        }
        
        for file_path in files:
            try:
                if not file_path.exists():
                    validation_results["errors"].append(f"Archivo no encontrado: {file_path}")
                    validation_results["invalid_files"] += 1
                    continue
                
                # Validar según el tipo de archivo
                if file_path.suffix.lower() == '.csv':
                    headers, data = self.csv_processor.read_csv_file(file_path)
                    is_valid = self.csv_processor.validate_csv_structure(headers, data)
                    stats = self.csv_processor.get_csv_statistics(headers, data)
                elif file_path.suffix.lower() in ['.xlsx', '.xls']:
                    is_valid = self.excel_processor.validate_excel_structure(file_path)
                    stats = self.excel_processor.get_excel_info(file_path)
                else:
                    is_valid = False
                    stats = {"error": "Formato no soportado"}
                
                validation_results["file_details"][str(file_path)] = {
                    "valid": is_valid,
                    "stats": stats
                }
                
                if is_valid:
                    validation_results["valid_files"] += 1
                else:
                    validation_results["invalid_files"] += 1
                    validation_results["errors"].append(f"Archivo inválido: {file_path}")
                
            except Exception as e:
                validation_results["invalid_files"] += 1
                validation_results["errors"].append(f"Error validando {file_path}: {str(e)}")
        
        return validation_results
    
    def get_consolidation_summary(self, files: List[Path]) -> Dict[str, Any]:
        """
        Obtiene un resumen de la consolidación.
        
        Args:
            files: Lista de archivos a consolidar
            
        Returns:
            Diccionario con resumen de la consolidación
        """
        self.log_operation("get_summary", f"Generando resumen para {len(files)} archivos")
        
        summary = {
            "total_files": len(files),
            "file_types": {},
            "total_size": 0,
            "estimated_rows": 0,
            "estimated_columns": 0
        }
        
        for file_path in files:
            if file_path.exists():
                # Contar tipos de archivo
                file_type = file_path.suffix.lower()
                summary["file_types"][file_type] = summary["file_types"].get(file_type, 0) + 1
                
                # Sumar tamaño
                summary["total_size"] += file_path.stat().st_size
                
                # Estimaciones
                try:
                    if file_type == '.csv':
                        headers, data = self.csv_processor.read_csv_file(file_path)
                        summary["estimated_rows"] += len(data)
                        summary["estimated_columns"] = max(summary["estimated_columns"], len(headers))
                    elif file_type in ['.xlsx', '.xls']:
                        info = self.excel_processor.get_excel_info(file_path)
                        for sheet_info in info["sheets_info"].values():
                            summary["estimated_rows"] += sheet_info["rows"]
                            summary["estimated_columns"] = max(summary["estimated_columns"], sheet_info["columns"])
                except Exception:
                    pass
        
        return summary 