"""
Procesador de archivos CSV para ExcelSior API.

Proporciona funcionalidades para procesar, validar y transformar
archivos CSV con manejo robusto de errores y logging.
"""

import csv
import os
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime

from utils.logger import LoggerMixin
from utils.exceptions import FileProcessingError, EncodingError
from config.settings import DEFAULT_ENCODING, DEFAULT_DELIMITER, NULL_VALUES

class CSVProcessor(LoggerMixin):
    """Procesador especializado para archivos CSV."""
    
    def __init__(self):
        super().__init__()
        self.supported_encodings = ['utf-8', 'latin-1', 'cp1252']
        self.max_rows_per_file = 1048576  # Límite de Excel
    
    def detect_encoding(self, file_path: Path) -> str:
        """
        Detecta la codificación de un archivo CSV.
        
        Args:
            file_path: Ruta del archivo
            
        Returns:
            Codificación detectada
            
        Raises:
            EncodingError: Si no se puede detectar la codificación
        """
        self.log_operation("detect_encoding", f"Detectando codificación: {file_path}")
        
        for encoding in self.supported_encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    f.read(1024)  # Leer una pequeña muestra
                self.log_operation("encoding_detected", f"Codificación detectada: {encoding}")
                return encoding
            except UnicodeDecodeError:
                continue
        
        raise EncodingError(
            f"No se pudo detectar la codificación del archivo {file_path}",
            encoding="unknown"
        )
    
    def read_csv_file(self, file_path: Path, delimiter: str = None, encoding: str = None) -> Tuple[List[str], List[List[str]]]:
        """
        Lee un archivo CSV y retorna headers y datos.
        
        Args:
            file_path: Ruta del archivo CSV
            delimiter: Delimitador (se detecta automáticamente si no se proporciona)
            encoding: Codificación (se detecta automáticamente si no se proporciona)
            
        Returns:
            Tupla con headers y filas de datos
            
        Raises:
            FileProcessingError: Si hay error al procesar el archivo
        """
        self.log_operation("read_csv_file", f"Leyendo archivo CSV: {file_path}")
        
        if not file_path.exists():
            raise FileProcessingError(f"Archivo no encontrado: {file_path}")
        
        # Detectar codificación si no se proporciona
        if encoding is None:
            encoding = self.detect_encoding(file_path)
        
        # Detectar delimitador si no se proporciona
        if delimiter is None:
            delimiter = self._detect_delimiter(file_path, encoding)
        
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                reader = csv.reader(f, delimiter=delimiter)
                rows = list(reader)
            
            if not rows:
                raise FileProcessingError(f"Archivo CSV vacío: {file_path}")
            
            headers = rows[0]
            data_rows = rows[1:]
            
            self.log_operation("csv_read", f"Archivo leído: {len(headers)} columnas, {len(data_rows)} filas")
            return headers, data_rows
            
        except Exception as e:
            raise FileProcessingError(f"Error al leer archivo CSV: {str(e)}", file_path=str(file_path))
    
    def write_csv_file(self, file_path: Path, headers: List[str], data: List[List[str]], 
                      delimiter: str = DEFAULT_DELIMITER, encoding: str = DEFAULT_ENCODING) -> None:
        """
        Escribe datos en un archivo CSV.
        
        Args:
            file_path: Ruta del archivo de salida
            headers: Lista de encabezados
            data: Lista de filas de datos
            delimiter: Delimitador a usar
            encoding: Codificación a usar
        """
        self.log_operation("write_csv_file", f"Escribiendo archivo CSV: {file_path}")
        
        try:
            # Crear directorio si no existe
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', newline='', encoding=encoding) as f:
                writer = csv.writer(f, delimiter=delimiter, quotechar='"', quoting=csv.QUOTE_MINIMAL)
                writer.writerow(headers)
                writer.writerows(data)
            
            self.log_operation("csv_written", f"Archivo escrito: {len(headers)} columnas, {len(data)} filas")
            
        except Exception as e:
            raise FileProcessingError(f"Error al escribir archivo CSV: {str(e)}", file_path=str(file_path))
    
    def _detect_delimiter(self, file_path: Path, encoding: str) -> str:
        """
        Detecta el delimitador de un archivo CSV.
        
        Args:
            file_path: Ruta del archivo
            encoding: Codificación del archivo
            
        Returns:
            Delimitador detectado
        """
        delimiters = [',', ';', '|', '\t', '|@']
        
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                first_line = f.readline().strip()
            
            if not first_line:
                return DEFAULT_DELIMITER
            
            # Contar ocurrencias de cada delimitador
            delimiter_counts = {}
            for delimiter in delimiters:
                count = first_line.count(delimiter)
                if count > 0:
                    delimiter_counts[delimiter] = count
            
            if not delimiter_counts:
                return DEFAULT_DELIMITER
            
            # Seleccionar el delimitador con más ocurrencias
            detected_delimiter = max(delimiter_counts.items(), key=lambda x: x[1])[0]
            return detected_delimiter
            
        except Exception:
            return DEFAULT_DELIMITER
    
    def extract_date_from_filename(self, filename: str) -> Dict[str, str]:
        """
        Extrae información de fecha del nombre del archivo.
        
        Args:
            filename: Nombre del archivo
            
        Returns:
            Diccionario con información de fecha extraída
        """
        self.log_operation("extract_date", f"Extrayendo fecha de: {filename}")
        
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
    
    def add_metadata_columns(self, headers: List[str], data: List[List[str]], 
                           filename: str, date_info: Dict[str, str]) -> Tuple[List[str], List[List[str]]]:
        """
        Agrega columnas de metadatos al CSV.
        
        Args:
            headers: Encabezados originales
            data: Datos originales
            filename: Nombre del archivo
            date_info: Información de fecha extraída
            
        Returns:
            Tupla con headers y datos actualizados
        """
        self.log_operation("add_metadata", f"Agregando metadatos para: {filename}")
        
        # Agregar columnas de metadatos
        new_headers = ['nombre_archivo', 'mes_reporte'] + headers
        
        # Agregar datos de metadatos
        new_data = []
        for row in data:
            new_row = [filename, date_info['mes_reporte']] + row
            new_data.append(new_row)
        
        return new_headers, new_data
    
    def clean_data(self, data: List[List[str]]) -> List[List[str]]:
        """
        Limpia los datos eliminando valores nulos y normalizando.
        
        Args:
            data: Datos a limpiar
            
        Returns:
            Datos limpios
        """
        self.log_operation("clean_data", "Limpiando datos")
        
        cleaned_data = []
        for row in data:
            cleaned_row = []
            for cell in row:
                # Limpiar valores nulos
                if cell.strip().lower() in NULL_VALUES:
                    cleaned_row.append("")
                else:
                    # Limpiar valores tipo '123.0' -> '123'
                    if isinstance(cell, str) and cell.endswith('.0'):
                        cleaned_row.append(cell[:-2])
                    else:
                        cleaned_row.append(cell.strip())
            cleaned_data.append(cleaned_row)
        
        return cleaned_data
    
    def validate_csv_structure(self, headers: List[str], data: List[List[str]]) -> bool:
        """
        Valida la estructura del CSV.
        
        Args:
            headers: Encabezados del CSV
            data: Datos del CSV
            
        Returns:
            True si la estructura es válida
        """
        if not headers:
            return False
        
        for row in data:
            if len(row) != len(headers):
                return False
        
        return True
    
    def get_csv_statistics(self, headers: List[str], data: List[List[str]]) -> Dict[str, Any]:
        """
        Obtiene estadísticas del archivo CSV.
        
        Args:
            headers: Encabezados del CSV
            data: Datos del CSV
            
        Returns:
            Diccionario con estadísticas
        """
        return {
            "column_count": len(headers),
            "row_count": len(data),
            "headers": headers,
            "file_size_estimate": len(headers) * len(data) * 50  # Estimación aproximada
        } 