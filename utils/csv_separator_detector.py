"""
Utilidad para detectar automáticamente el separador de archivos CSV.
"""

import csv
import re
from typing import List, Tuple, Optional
from utils.logger import get_logger

logger = get_logger(__name__)

class CSVSeparatorDetector:
    """Detector automático de separadores para archivos CSV."""
    
    def __init__(self):
        # Separadores comunes ordenados por frecuencia de uso
        # Separadores compuestos primero para evitar detección incorrecta
        self.common_separators = ['|@', '|', ',', ';', '\t', '@', '~', '^']
        
    def detect_separator(self, file_path: str, sample_lines: int = 10) -> Tuple[str, float]:
        """
        Detecta el separador más probable del archivo CSV.
        
        Args:
            file_path: Ruta al archivo CSV
            sample_lines: Número de líneas a analizar
            
        Returns:
            Tupla con (separador_detectado, confianza)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = []
                for i, line in enumerate(file):
                    if i >= sample_lines:
                        break
                    lines.append(line.strip())
                
                if not lines:
                    return ',', 0.0
                
                return self._analyze_lines(lines)
                
        except UnicodeDecodeError:
            # Intentar con otros encodings
            for encoding in ['latin-1', 'cp1252']:
                try:
                    with open(file_path, 'r', encoding=encoding) as file:
                        lines = []
                        for i, line in enumerate(file):
                            if i >= sample_lines:
                                break
                            lines.append(line.strip())
                        
                        if lines:
                            return self._analyze_lines(lines)
                except:
                    continue
            
            # Si no se puede leer, usar separador por defecto
            return ',', 0.0
    
    def _analyze_lines(self, lines: List[str]) -> Tuple[str, float]:
        """
        Analiza las líneas para detectar el separador más probable.
        
        Args:
            lines: Lista de líneas del archivo
            
        Returns:
            Tupla con (separador_detectado, confianza)
        """
        if not lines:
            return ',', 0.0
        
        # Contar ocurrencias de cada separador
        separator_counts = {}
        separator_consistency = {}
        
        for separator in self.common_separators:
            separator_counts[separator] = 0
            separator_consistency[separator] = []
        
        # Analizar cada línea
        for line in lines:
            if not line.strip():
                continue
                
            for separator in self.common_separators:
                # Contar campos en esta línea
                fields = line.split(separator)
                separator_counts[separator] += len(fields)
                separator_consistency[separator].append(len(fields))
        
        # Calcular métricas para cada separador
        separator_scores = {}
        
        for separator in self.common_separators:
            if separator_counts[separator] == 0:
                separator_scores[separator] = 0.0
                continue
            
            # Calcular consistencia (mismo número de campos en todas las líneas)
            field_counts = separator_consistency[separator]
            if len(field_counts) == 0:
                separator_scores[separator] = 0.0
                continue
            
            # Consistencia: qué tan uniforme es el número de campos
            unique_counts = len(set(field_counts))
            consistency_score = 1.0 / unique_counts if unique_counts > 0 else 0.0
            
            # Frecuencia: qué tan común es este separador
            frequency_score = separator_counts[separator] / len(lines)
            
            # Peso del separador (separadores más comunes tienen más peso)
            weight = self._get_separator_weight(separator)
            
            # Score final
            separator_scores[separator] = (consistency_score * 0.6 + frequency_score * 0.4) * weight
        
        # Encontrar el mejor separador
        best_separator = max(separator_scores.items(), key=lambda x: x[1])
        
        # Normalizar la confianza
        max_score = max(separator_scores.values())
        confidence = best_separator[1] / max_score if max_score > 0 else 0.0
        
        logger.info(f"Separador detectado: '{best_separator[0]}' con confianza {confidence:.2f}")
        
        return best_separator[0], confidence
    
    def _get_separator_weight(self, separator: str) -> float:
        """
        Obtiene el peso de un separador basado en su frecuencia de uso.
        
        Args:
            separator: Separador a evaluar
            
        Returns:
            Peso del separador (mayor = más común)
        """
        weights = {
            ',': 1.0,    # Coma (más común)
            ';': 0.9,    # Punto y coma
            '\t': 0.8,   # Tab
            '|': 0.7,    # Pipe
            '|@': 0.6,   # Pipe con arroba (separador compuesto)
            '@': 0.5,    # Arroba
            '~': 0.4,    # Tilde
            '^': 0.3     # Caret
        }
        
        return weights.get(separator, 0.1)
    
    def validate_separator(self, file_path: str, separator: str, sample_lines: int = 5) -> bool:
        """
        Valida si un separador funciona correctamente para el archivo.
        
        Args:
            file_path: Ruta al archivo CSV
            separator: Separador a validar
            sample_lines: Número de líneas a verificar
            
        Returns:
            True si el separador es válido
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = []
                for i, line in enumerate(file):
                    if i >= sample_lines:
                        break
                    lines.append(line.strip())
                
                if not lines:
                    return False
                
                # Verificar que todas las líneas tengan el mismo número de campos
                field_counts = []
                for line in lines:
                    if line.strip():
                        fields = line.split(separator)
                        field_counts.append(len(fields))
                
                if len(field_counts) == 0:
                    return False
                
                # Si hay más de un número único de campos, el separador no es válido
                unique_counts = len(set(field_counts))
                return unique_counts <= 2  # Permitir pequeñas variaciones
                
        except Exception as e:
            logger.warning(f"Error validando separador '{separator}': {str(e)}")
            return False
    
    def get_separator_info(self, file_path: str) -> dict:
        """
        Obtiene información completa sobre el separador del archivo.
        
        Args:
            file_path: Ruta al archivo CSV
            
        Returns:
            Diccionario con información del separador
        """
        separator, confidence = self.detect_separator(file_path)
        is_valid = self.validate_separator(file_path, separator)
        
        return {
            "detected_separator": separator,
            "confidence": confidence,
            "is_valid": is_valid,
            "common_separators": self.common_separators,
            "recommendation": separator if is_valid else ","
        }

# Instancia global del detector
separator_detector = CSVSeparatorDetector() 