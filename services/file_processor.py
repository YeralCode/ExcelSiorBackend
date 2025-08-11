"""
Servicio mejorado para procesamiento de archivos.

Proporciona funcionalidades centralizadas para el procesamiento
de archivos CSV, Excel y otros formatos con validación y logging.
"""

import csv
import os
import tempfile
import zipfile
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any, Union
from fastapi import UploadFile
import pandas as pd

from utils.logger import LoggerMixin, log_function_call
from utils.exceptions import (
    FileProcessingError, FileValidationError, UnsupportedFileTypeError,
    FileSizeError, EncodingError, DelimiterDetectionError
)
from utils.validators import ValidationManager
from config.settings import (
    DEFAULT_ENCODING, DEFAULT_DELIMITER, MAX_FILE_SIZE, 
    ALLOWED_EXTENSIONS, TEMP_DIR, ensure_temp_dir
)

class FileProcessor(LoggerMixin):
    """Servicio centralizado para procesamiento de archivos."""
    
    def __init__(self):
        super().__init__()
        self.validation_manager = ValidationManager()
        self.temp_dir = ensure_temp_dir()
    
    def validate_file(self, file: UploadFile) -> None:
        """
        Valida un archivo antes del procesamiento.
        
        Args:
            file: Archivo a validar
            
        Raises:
            FileValidationError: Si el archivo no pasa las validaciones
        """
        self.log_operation("validate_file", f"Validando archivo: {file.filename}")
        
        # Validar extensión
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in ALLOWED_EXTENSIONS:
            raise UnsupportedFileTypeError(file_extension, list(ALLOWED_EXTENSIONS))
        
        # Validar tamaño
        if file.size and file.size > MAX_FILE_SIZE:
            raise FileSizeError(file.size, MAX_FILE_SIZE)
    
    @log_function_call
    def save_uploaded_file(self, file: UploadFile) -> Path:
        """
        Guarda un archivo subido en el directorio temporal.
        
        Args:
            file: Archivo subido
            
        Returns:
            Path del archivo guardado
        """
        self.log_operation("save_uploaded_file", f"Guardando archivo: {file.filename}")
        
        # Crear nombre único para el archivo
        temp_file = self.temp_dir / f"{os.urandom(8).hex()}_{file.filename}"
        
        try:
            with open(temp_file, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            self.log_operation("file_saved", f"Archivo guardado: {temp_file}")
            return temp_file
            
        except Exception as e:
            raise FileProcessingError(
                f"Error al guardar archivo: {str(e)}",
                file_path=str(temp_file)
            )
    
    def detect_delimiter(self, file_path: Path) -> str:
        """
        Detecta el delimitador de un archivo CSV.
        
        Args:
            file_path: Ruta del archivo
            
        Returns:
            Delimitador detectado
            
        Raises:
            DelimiterDetectionError: Si no se puede detectar el delimitador
        """
        self.log_operation("detect_delimiter", f"Detectando delimitador: {file_path}")
        
        delimiters = [',', ';', '|', '\t', '|@']
        
        try:
            with open(file_path, 'r', encoding=DEFAULT_ENCODING) as f:
                first_line = f.readline().strip()
            
            if not first_line:
                raise DelimiterDetectionError("Archivo vacío o primera línea sin contenido")
            
            # Contar ocurrencias de cada delimitador
            delimiter_counts = {}
            for delimiter in delimiters:
                count = first_line.count(delimiter)
                if count > 0:
                    delimiter_counts[delimiter] = count
            
            if not delimiter_counts:
                raise DelimiterDetectionError("No se pudo detectar ningún delimitador válido")
            
            # Seleccionar el delimitador con más ocurrencias
            detected_delimiter = max(delimiter_counts.items(), key=lambda x: x[1])[0]
            
            self.log_operation("delimiter_detected", f"Delimitador detectado: '{detected_delimiter}'")
            return detected_delimiter
            
        except UnicodeDecodeError:
            # Intentar con encoding alternativo
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    first_line = f.readline().strip()
                
                delimiter_counts = {}
                for delimiter in delimiters:
                    count = first_line.count(delimiter)
                    if count > 0:
                        delimiter_counts[delimiter] = count
                
                if not delimiter_counts:
                    raise DelimiterDetectionError("No se pudo detectar ningún delimitador válido")
                
                detected_delimiter = max(delimiter_counts.items(), key=lambda x: x[1])[0]
                return detected_delimiter
                
            except Exception as e:
                raise DelimiterDetectionError(f"Error al detectar delimitador: {str(e)}")
    
    def read_csv_file(self, file_path: Path, delimiter: Optional[str] = None) -> Tuple[List[str], List[List[str]]]:
        """
        Lee un archivo CSV y retorna headers y datos.
        
        Args:
            file_path: Ruta del archivo
            delimiter: Delimitador (se detecta automáticamente si no se proporciona)
            
        Returns:
            Tupla con headers y filas de datos
        """
        self.log_operation("read_csv_file", f"Leyendo archivo CSV: {file_path}")
        
        if delimiter is None:
            delimiter = self.detect_delimiter(file_path)
        
        try:
            with open(file_path, 'r', encoding=DEFAULT_ENCODING) as f:
                reader = csv.reader(f, delimiter=delimiter)
                rows = list(reader)
            
            if not rows:
                raise FileProcessingError("Archivo CSV vacío", file_path=str(file_path))
            
            headers = rows[0]
            data_rows = rows[1:]
            
            self.log_operation("csv_read", f"Archivo leído: {len(headers)} columnas, {len(data_rows)} filas")
            return headers, data_rows
            
        except UnicodeDecodeError:
            # Intentar con encoding alternativo
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    reader = csv.reader(f, delimiter=delimiter)
                    rows = list(reader)
                
                if not rows:
                    raise FileProcessingError("Archivo CSV vacío", file_path=str(file_path))
                
                headers = rows[0]
                data_rows = rows[1:]
                
                return headers, data_rows
                
            except Exception as e:
                raise EncodingError(f"Error de codificación: {str(e)}", encoding="latin-1")
    
    def write_csv_file(self, file_path: Path, headers: List[str], data: List[List[str]], delimiter: str = DEFAULT_DELIMITER) -> None:
        """
        Escribe datos en un archivo CSV.
        
        Args:
            file_path: Ruta del archivo de salida
            headers: Lista de encabezados
            data: Lista de filas de datos
            delimiter: Delimitador a usar
        """
        self.log_operation("write_csv_file", f"Escribiendo archivo CSV: {file_path}")
        
        try:
            with open(file_path, 'w', newline='', encoding=DEFAULT_ENCODING) as f:
                writer = csv.writer(f, delimiter=delimiter, quotechar='"', quoting=csv.QUOTE_MINIMAL)
                writer.writerow(headers)
                writer.writerows(data)
            
            self.log_operation("csv_written", f"Archivo escrito: {len(headers)} columnas, {len(data)} filas")
            
        except Exception as e:
            raise FileProcessingError(f"Error al escribir archivo CSV: {str(e)}", file_path=str(file_path))
    
    def process_excel_file(self, file_path: Path, sheet_name: Optional[str] = None) -> Tuple[List[str], List[List[str]]]:
        """
        Procesa un archivo Excel y retorna headers y datos.
        
        Args:
            file_path: Ruta del archivo Excel
            sheet_name: Nombre de la hoja a procesar (opcional)
            
        Returns:
            Tupla con headers y filas de datos
        """
        self.log_operation("process_excel_file", f"Procesando archivo Excel: {file_path}")
        
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
            
            self.log_operation("excel_processed", f"Archivo Excel procesado: {len(headers)} columnas, {len(data)} filas")
            return headers, data
            
        except Exception as e:
            raise FileProcessingError(f"Error al procesar archivo Excel: {str(e)}", file_path=str(file_path))
    
    def create_zip_file(self, files: List[Path], zip_name: str = "processed_files.zip") -> Path:
        """
        Crea un archivo ZIP con los archivos procesados.
        
        Args:
            files: Lista de archivos a incluir en el ZIP
            zip_name: Nombre del archivo ZIP
            
        Returns:
            Path del archivo ZIP creado
        """
        self.log_operation("create_zip_file", f"Creando ZIP: {zip_name} con {len(files)} archivos")
        
        zip_path = self.temp_dir / zip_name
        
        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in files:
                    if file_path.exists():
                        zipf.write(file_path, file_path.name)
            
            self.log_operation("zip_created", f"ZIP creado: {zip_path}")
            return zip_path
            
        except Exception as e:
            raise FileProcessingError(f"Error al crear archivo ZIP: {str(e)}", file_path=str(zip_path))
    
    def cleanup_temp_files(self, files: List[Path]) -> None:
        """
        Limpia archivos temporales.
        
        Args:
            files: Lista de archivos a eliminar
        """
        self.log_operation("cleanup_temp_files", f"Limpiando {len(files)} archivos temporales")
        
        for file_path in files:
            try:
                if file_path.exists():
                    file_path.unlink()
                    self.log_operation("file_deleted", f"Archivo eliminado: {file_path}")
            except Exception as e:
                self.log_operation("cleanup_error", f"Error al eliminar {file_path}: {str(e)}", level="warning")
    
    def validate_and_process_file(self, file: UploadFile, project_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Valida y procesa un archivo completo.
        
        Args:
            file: Archivo a procesar
            project_config: Configuración específica del proyecto (opcional)
            
        Returns:
            Diccionario con información del procesamiento
        """
        self.log_operation("validate_and_process_file", f"Procesando archivo: {file.filename}")
        
        try:
            # Validar archivo
            self.validate_file(file)
            
            # Guardar archivo temporal
            temp_file = self.save_uploaded_file(file)
            
            # Procesar según el tipo de archivo
            file_extension = Path(file.filename).suffix.lower()
            
            if file_extension == '.csv':
                delimiter = self.detect_delimiter(temp_file)
                headers, data = self.read_csv_file(temp_file, delimiter)
            elif file_extension in ['.xlsx', '.xls']:
                headers, data = self.process_excel_file(temp_file)
            else:
                raise UnsupportedFileTypeError(file_extension, list(ALLOWED_EXTENSIONS))
            
            result = {
                "filename": file.filename,
                "file_size": file.size,
                "headers": headers,
                "row_count": len(data),
                "column_count": len(headers),
                "temp_file": str(temp_file)
            }
            
            # Aplicar validaciones específicas del proyecto si se proporcionan
            if project_config:
                validation_errors = self._validate_with_project_config(data, headers, project_config)
                result["validation_errors"] = validation_errors
                result["validation_passed"] = len(validation_errors) == 0
            
            self.log_operation("file_processed", f"Archivo procesado exitosamente: {file.filename}")
            return result
            
        except Exception as e:
            self.log_operation("processing_error", f"Error al procesar archivo: {str(e)}", level="error")
            raise
    
    def _validate_with_project_config(self, data: List[List[str]], headers: List[str], project_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Valida datos usando la configuración específica del proyecto.
        
        Args:
            data: Datos a validar
            headers: Encabezados de las columnas
            project_config: Configuración del proyecto
            
        Returns:
            Lista de errores de validación
        """
        validation_errors = []
        field_validations = project_config.get('validators', {})
        
        for row_index, row in enumerate(data, start=1):
            # Crear diccionario de fila
            row_dict = dict(zip(headers, row))
            
            # Validar cada campo según la configuración
            for field_name, field_type in field_validations.items():
                if field_name in row_dict:
                    value = row_dict[field_name]
                    result = self.validation_manager.validate_field(value, field_type)
                    
                    if not result.is_valid:
                        validation_errors.append({
                            "row": row_index,
                            "field": field_name,
                            "value": value,
                            "error": result.error_message
                        })
        
        return validation_errors 