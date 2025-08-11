"""
Procesador de archivos Excel para ExcelSior API.

Proporciona funcionalidades para procesar, validar y transformar
archivos Excel con manejo robusto de errores y logging.
"""

import pandas as pd
import os
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any, Union
from datetime import datetime

from utils.logger import LoggerMixin
from utils.exceptions import FileProcessingError
from config.settings import DEFAULT_ENCODING

class ExcelProcessor(LoggerMixin):
    """Procesador especializado para archivos Excel."""
    
    def __init__(self):
        super().__init__()
        self.max_rows_per_sheet = 1048576  # Límite de filas por hoja en Excel
        self.max_sheets_per_file = 255  # Límite de hojas por archivo Excel
        self.supported_formats = ['.xlsx', '.xls', '.xlsm']
    
    def read_excel_file(self, file_path: Path, sheet_name: Optional[str] = None) -> Tuple[List[str], List[List[str]]]:
        """
        Lee un archivo Excel y retorna headers y datos.
        
        Args:
            file_path: Ruta del archivo Excel
            sheet_name: Nombre de la hoja a leer (opcional)
            
        Returns:
            Tupla con headers y filas de datos
            
        Raises:
            FileProcessingError: Si hay error al procesar el archivo
        """
        self.log_operation("read_excel_file", f"Leyendo archivo Excel: {file_path}")
        
        if not file_path.exists():
            raise FileProcessingError(f"Archivo no encontrado: {file_path}")
        
        if file_path.suffix.lower() not in self.supported_formats:
            raise FileProcessingError(f"Formato de archivo no soportado: {file_path.suffix}")
        
        try:
            # Leer archivo Excel
            if sheet_name:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
            else:
                df = pd.read_excel(file_path)
            
            # Convertir a listas
            headers = df.columns.tolist()
            data = df.values.tolist()
            
            # Convertir todos los valores a string
            data = [[str(cell) if cell is not None else "" for cell in row] for row in data]
            
            self.log_operation("excel_read", f"Archivo Excel leído: {len(headers)} columnas, {len(data)} filas")
            return headers, data
            
        except Exception as e:
            raise FileProcessingError(f"Error al leer archivo Excel: {str(e)}", file_path=str(file_path))
    
    def write_excel_file(self, file_path: Path, data_dict: Dict[str, Tuple[List[str], List[List[str]]]], 
                        engine: str = 'openpyxl') -> None:
        """
        Escribe datos en un archivo Excel.
        
        Args:
            file_path: Ruta del archivo de salida
            data_dict: Diccionario con nombre de hoja y tupla (headers, data)
            engine: Motor de Excel a usar ('openpyxl' o 'xlsxwriter')
        """
        self.log_operation("write_excel_file", f"Escribiendo archivo Excel: {file_path}")
        
        try:
            # Crear directorio si no existe
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with pd.ExcelWriter(file_path, engine=engine) as writer:
                for sheet_name, (headers, data) in data_dict.items():
                    # Crear DataFrame
                    df = pd.DataFrame(data, columns=headers)
                    
                    # Escribir hoja
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                    
                    self.log_operation("sheet_written", f"Hoja '{sheet_name}' escrita: {len(headers)} columnas, {len(data)} filas")
            
            self.log_operation("excel_written", f"Archivo Excel escrito: {len(data_dict)} hojas")
            
        except Exception as e:
            raise FileProcessingError(f"Error al escribir archivo Excel: {str(e)}", file_path=str(file_path))
    
    def split_large_dataframe(self, headers: List[str], data: List[List[str]], 
                            base_sheet_name: str) -> Dict[str, Tuple[List[str], List[List[str]]]]:
        """
        Divide un DataFrame grande en múltiples hojas de Excel.
        
        Args:
            headers: Encabezados del DataFrame
            data: Datos del DataFrame
            base_sheet_name: Nombre base para las hojas
            
        Returns:
            Diccionario con hojas divididas
        """
        self.log_operation("split_dataframe", f"Dividiendo DataFrame: {len(data)} filas")
        
        sheets_dict = {}
        total_rows = len(data)
        
        if total_rows <= self.max_rows_per_sheet:
            # No necesita división
            sheets_dict[base_sheet_name] = (headers, data)
            return sheets_dict
        
        # Calcular número de partes necesarias
        num_parts = (total_rows // self.max_rows_per_sheet) + 1
        
        for i in range(num_parts):
            start_idx = i * self.max_rows_per_sheet
            end_idx = min((i + 1) * self.max_rows_per_sheet, total_rows)
            
            # Crear nombre de hoja
            if num_parts == 1:
                sheet_name = base_sheet_name
            else:
                sheet_name = f"{base_sheet_name}_part{i+1}"
            
            # Limitar nombre a 31 caracteres (límite de Excel)
            sheet_name = sheet_name[:31]
            
            # Extraer datos de la parte
            part_data = data[start_idx:end_idx]
            sheets_dict[sheet_name] = (headers, part_data)
            
            self.log_operation("part_created", f"Parte {i+1} creada: {len(part_data)} filas")
        
        return sheets_dict
    
    def merge_csv_files_to_excel(self, csv_files: List[Path], output_file: Path, 
                                delimiter: str = '|') -> Dict[str, Any]:
        """
        Combina múltiples archivos CSV en un archivo Excel.
        
        Args:
            csv_files: Lista de archivos CSV a combinar
            output_file: Archivo Excel de salida
            delimiter: Delimitador de los archivos CSV
            
        Returns:
            Diccionario con información del proceso
        """
        self.log_operation("merge_csv_to_excel", f"Combinando {len(csv_files)} archivos CSV")
        
        excel_data = {}
        processed_files = 0
        total_rows = 0
        
        for csv_file in csv_files:
            try:
                if not csv_file.exists():
                    self.log_operation("file_not_found", f"Archivo no encontrado: {csv_file}")
                    continue
                
                # Leer archivo CSV
                df = pd.read_csv(csv_file, delimiter=delimiter, dtype=str)
                
                # Limpiar datos
                df = df.applymap(self._clean_value)
                
                # Crear nombre de hoja
                base_name = csv_file.stem[:25]  # Limitar a 25 caracteres
                
                # Dividir si es necesario
                headers = df.columns.tolist()
                data = df.values.tolist()
                
                sheets = self.split_large_dataframe(headers, data, base_name)
                
                # Agregar a excel_data
                for sheet_name, (sheet_headers, sheet_data) in sheets.items():
                    excel_data[sheet_name] = (sheet_headers, sheet_data)
                    total_rows += len(sheet_data)
                
                processed_files += 1
                self.log_operation("file_processed", f"Archivo procesado: {csv_file.name}")
                
            except Exception as e:
                self.log_operation("file_error", f"Error procesando {csv_file}: {str(e)}", level="error")
        
        # Escribir archivo Excel
        if excel_data:
            self.write_excel_file(output_file, excel_data)
        
        return {
            "processed_files": processed_files,
            "total_sheets": len(excel_data),
            "total_rows": total_rows,
            "output_file": str(output_file)
        }
    
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
    
    def get_excel_info(self, file_path: Path) -> Dict[str, Any]:
        """
        Obtiene información detallada de un archivo Excel.
        
        Args:
            file_path: Ruta del archivo Excel
            
        Returns:
            Diccionario con información del archivo
        """
        self.log_operation("get_excel_info", f"Obteniendo información: {file_path}")
        
        try:
            # Leer todas las hojas
            excel_file = pd.ExcelFile(file_path)
            sheet_names = excel_file.sheet_names
            
            info = {
                "file_path": str(file_path),
                "file_size": file_path.stat().st_size,
                "sheet_count": len(sheet_names),
                "sheet_names": sheet_names,
                "sheets_info": {}
            }
            
            # Información de cada hoja
            for sheet_name in sheet_names:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                info["sheets_info"][sheet_name] = {
                    "rows": len(df),
                    "columns": len(df.columns),
                    "column_names": df.columns.tolist()
                }
            
            return info
            
        except Exception as e:
            raise FileProcessingError(f"Error al obtener información del Excel: {str(e)}", file_path=str(file_path))
    
    def validate_excel_structure(self, file_path: Path) -> bool:
        """
        Valida la estructura de un archivo Excel.
        
        Args:
            file_path: Ruta del archivo Excel
            
        Returns:
            True si la estructura es válida
        """
        try:
            excel_file = pd.ExcelFile(file_path)
            
            # Verificar número de hojas
            if len(excel_file.sheet_names) > self.max_sheets_per_file:
                return False
            
            # Verificar cada hoja
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                
                # Verificar número de filas
                if len(df) > self.max_rows_per_sheet:
                    return False
            
            return True
            
        except Exception:
            return False 