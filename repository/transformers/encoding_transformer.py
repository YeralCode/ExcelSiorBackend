"""
Transformador de codificación para ExcelSior API.

Proporciona funcionalidades para detectar y convertir codificaciones
de archivos con manejo robusto de errores.
"""

import chardet
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import codecs

from utils.logger import LoggerMixin
from utils.exceptions import FileProcessingError, EncodingError
from config.settings import DEFAULT_ENCODING

class EncodingTransformer(LoggerMixin):
    """Transformador especializado para conversiones de codificación."""
    
    def __init__(self):
        super().__init__()
        self.supported_encodings = [
            'utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1',
            'ascii', 'utf-16', 'utf-16le', 'utf-16be'
        ]
        self.common_encodings = ['utf-8', 'latin-1', 'cp1252']
    
    def detect_encoding(self, file_path: Path, sample_size: int = 10000) -> Dict[str, Any]:
        """
        Detecta la codificación de un archivo.
        
        Args:
            file_path: Ruta del archivo
            sample_size: Tamaño de la muestra para detección
            
        Returns:
            Diccionario con información de la codificación detectada
        """
        self.log_operation("detect_encoding", f"Detectando codificación: {file_path}")
        
        try:
            # Leer muestra del archivo
            with open(file_path, 'rb') as f:
                sample = f.read(sample_size)
            
            # Detectar codificación
            result = chardet.detect(sample)
            
            detection_info = {
                "encoding": result['encoding'],
                "confidence": result['confidence'],
                "file_path": str(file_path),
                "sample_size": len(sample)
            }
            
            self.log_operation("encoding_detected", f"Codificación detectada: {result['encoding']} (confianza: {result['confidence']:.2f})")
            return detection_info
            
        except Exception as e:
            raise EncodingError(f"Error al detectar codificación: {str(e)}", encoding="unknown")
    
    def validate_encoding(self, file_path: Path, encoding: str) -> bool:
        """
        Valida si un archivo puede ser leído con una codificación específica.
        
        Args:
            file_path: Ruta del archivo
            encoding: Codificación a validar
            
        Returns:
            True si la codificación es válida
        """
        self.log_operation("validate_encoding", f"Validando codificación {encoding}: {file_path}")
        
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                f.read(1024)  # Leer una pequeña muestra
            return True
        except UnicodeDecodeError:
            return False
        except Exception:
            return False
    
    def convert_encoding(self, input_file: Path, output_file: Path, 
                        target_encoding: str = DEFAULT_ENCODING,
                        source_encoding: Optional[str] = None) -> Dict[str, Any]:
        """
        Convierte la codificación de un archivo.
        
        Args:
            input_file: Archivo de entrada
            output_file: Archivo de salida
            target_encoding: Codificación de destino
            source_encoding: Codificación de origen (se detecta si no se proporciona)
            
        Returns:
            Diccionario con información del proceso
        """
        self.log_operation("convert_encoding", f"Convirtiendo codificación: {input_file}")
        
        try:
            # Detectar codificación de origen si no se proporciona
            if source_encoding is None:
                detection_info = self.detect_encoding(input_file)
                source_encoding = detection_info['encoding']
            
            # Validar codificación de origen
            if not self.validate_encoding(input_file, source_encoding):
                raise EncodingError(f"No se puede leer el archivo con codificación {source_encoding}", encoding=source_encoding)
            
            # Crear directorio de salida si no existe
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Convertir archivo
            with open(input_file, 'r', encoding=source_encoding) as infile, \
                 open(output_file, 'w', encoding=target_encoding) as outfile:
                content = infile.read()
                outfile.write(content)
            
            result = {
                "input_file": str(input_file),
                "output_file": str(output_file),
                "source_encoding": source_encoding,
                "target_encoding": target_encoding,
                "file_size": len(content),
                "success": True
            }
            
            self.log_operation("encoding_conversion_complete", f"Conversión completada: {source_encoding} -> {target_encoding}")
            return result
            
        except Exception as e:
            raise FileProcessingError(f"Error en conversión de codificación: {str(e)}", file_path=str(input_file))
    
    def batch_convert_encoding(self, input_files: List[Path], output_dir: Path,
                             target_encoding: str = DEFAULT_ENCODING) -> Dict[str, Any]:
        """
        Convierte la codificación de múltiples archivos en lote.
        
        Args:
            input_files: Lista de archivos de entrada
            output_dir: Directorio de salida
            target_encoding: Codificación de destino
            
        Returns:
            Diccionario con información del proceso
        """
        self.log_operation("batch_convert_encoding", f"Convirtiendo codificación de {len(input_files)} archivos")
        
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
                # Detectar codificación de origen
                detection_info = self.detect_encoding(input_file)
                source_encoding = detection_info['encoding']
                
                # Solo convertir si es necesario
                if source_encoding.lower() == target_encoding.lower():
                    self.log_operation("encoding_skip", f"Codificación ya es {target_encoding}, saltando: {input_file}")
                    results["processed_files"] += 1
                    continue
                
                # Crear archivo de salida
                output_file = output_dir / input_file.name
                
                # Convertir
                result = self.convert_encoding(input_file, output_file, target_encoding, source_encoding)
                results["conversions"].append(result)
                results["processed_files"] += 1
                
            except Exception as e:
                results["failed_files"] += 1
                results["errors"].append(f"Error procesando {input_file}: {str(e)}")
                self.log_operation("conversion_error", f"Error en conversión: {str(e)}", level="error")
        
        results["success"] = results["failed_files"] == 0
        return results
    
    def fix_encoding_issues(self, file_path: Path, output_file: Optional[Path] = None) -> Dict[str, Any]:
        """
        Intenta arreglar problemas de codificación automáticamente.
        
        Args:
            file_path: Archivo con problemas de codificación
            output_file: Archivo de salida (opcional)
            
        Returns:
            Diccionario con información del proceso
        """
        self.log_operation("fix_encoding", f"Arreglando problemas de codificación: {file_path}")
        
        if output_file is None:
            output_file = file_path.parent / f"{file_path.stem}_fixed{file_path.suffix}"
        
        # Probar diferentes codificaciones
        for encoding in self.common_encodings:
            try:
                if self.validate_encoding(file_path, encoding):
                    # Intentar convertir a UTF-8
                    result = self.convert_encoding(file_path, output_file, 'utf-8', encoding)
                    result["fixed_encoding"] = encoding
                    return result
            except Exception:
                continue
        
        # Si no se puede arreglar, intentar con detección automática
        try:
            detection_info = self.detect_encoding(file_path)
            if detection_info['confidence'] > 0.7:
                result = self.convert_encoding(file_path, output_file, 'utf-8', detection_info['encoding'])
                result["fixed_encoding"] = detection_info['encoding']
                result["confidence"] = detection_info['confidence']
                return result
        except Exception as e:
            pass
        
        raise EncodingError(f"No se pudieron arreglar los problemas de codificación: {file_path}", encoding="unknown")
    
    def get_encoding_statistics(self, files: List[Path]) -> Dict[str, Any]:
        """
        Obtiene estadísticas de codificación de múltiples archivos.
        
        Args:
            files: Lista de archivos a analizar
            
        Returns:
            Diccionario con estadísticas de codificación
        """
        self.log_operation("encoding_statistics", f"Analizando codificaciones de {len(files)} archivos")
        
        statistics = {
            "total_files": len(files),
            "encoding_counts": {},
            "confidence_stats": {
                "high": 0,    # > 0.8
                "medium": 0,  # 0.5-0.8
                "low": 0      # < 0.5
            },
            "file_details": {}
        }
        
        for file_path in files:
            try:
                detection_info = self.detect_encoding(file_path)
                encoding = detection_info['encoding']
                confidence = detection_info['confidence']
                
                # Contar codificaciones
                statistics["encoding_counts"][encoding] = statistics["encoding_counts"].get(encoding, 0) + 1
                
                # Clasificar por confianza
                if confidence > 0.8:
                    statistics["confidence_stats"]["high"] += 1
                elif confidence > 0.5:
                    statistics["confidence_stats"]["medium"] += 1
                else:
                    statistics["confidence_stats"]["low"] += 1
                
                # Detalles del archivo
                statistics["file_details"][str(file_path)] = detection_info
                
            except Exception as e:
                statistics["file_details"][str(file_path)] = {"error": str(e)}
        
        return statistics 