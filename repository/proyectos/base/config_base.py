"""
Clase base para configuraciones de proyectos.
Proporciona una estructura común que puede ser extendida por cada proyecto específico.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Set, Any, Optional
from pathlib import Path
import json
import yaml


@dataclass
class ProjectConfigBase(ABC):
    """
    Clase base abstracta para configuraciones de proyectos.
    Define la estructura común que todos los proyectos deben implementar.
    """
    
    # Información básica del proyecto
    project_name: str
    project_code: str
    description: str = ""
    
    # Configuraciones de archivos
    supported_formats: List[str] = field(default_factory=lambda: ['.csv', '.xlsx', '.xls'])
    encoding: str = 'utf-8'
    delimiter: str = ','
    
    # Configuraciones de procesamiento
    batch_size: int = 1000
    max_workers: int = 4
    timeout_seconds: int = 300
    
    # Configuraciones de validación
    strict_validation: bool = True
    allow_unknown_columns: bool = False
    
    # Configuraciones de logging
    log_level: str = 'INFO'
    log_file: Optional[str] = None
    
    # Rutas de archivos
    config_path: Optional[Path] = None
    data_path: Optional[Path] = None
    output_path: Optional[Path] = None
    
    def __post_init__(self):
        """Inicialización post-construcción del dataclass."""
        if self.config_path is None:
            self.config_path = Path(f"repository/proyectos/{self.project_code}")
        
        if self.data_path is None:
            self.data_path = self.config_path / "data"
        
        if self.output_path is None:
            self.output_path = self.config_path / "output"
    
    @abstractmethod
    def get_required_columns(self) -> List[str]:
        """Retorna las columnas requeridas para este proyecto."""
        pass
    
    @abstractmethod
    def get_optional_columns(self) -> List[str]:
        """Retorna las columnas opcionales para este proyecto."""
        pass
    
    @abstractmethod
    def get_column_mappings(self) -> Dict[str, str]:
        """Retorna los mapeos de columnas para este proyecto."""
        pass
    
    @abstractmethod
    def get_validators(self) -> Dict[str, Any]:
        """Retorna los validadores específicos para este proyecto."""
        pass
    
    def get_all_columns(self) -> List[str]:
        """Retorna todas las columnas (requeridas + opcionales)."""
        return self.get_required_columns() + self.get_optional_columns()
    
    def validate_config(self) -> bool:
        """Valida que la configuración sea correcta."""
        required_columns = self.get_required_columns()
        if not required_columns:
            raise ValueError(f"El proyecto {self.project_name} debe tener columnas requeridas")
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte la configuración a un diccionario."""
        return {
            'project_name': self.project_name,
            'project_code': self.project_code,
            'description': self.description,
            'supported_formats': self.supported_formats,
            'encoding': self.encoding,
            'delimiter': self.delimiter,
            'batch_size': self.batch_size,
            'max_workers': self.max_workers,
            'timeout_seconds': self.timeout_seconds,
            'strict_validation': self.strict_validation,
            'allow_unknown_columns': self.allow_unknown_columns,
            'log_level': self.log_level,
            'log_file': self.log_file,
            'required_columns': self.get_required_columns(),
            'optional_columns': self.get_optional_columns(),
            'column_mappings': self.get_column_mappings(),
            'validators': self.get_validators()
        }
    
    def save_config(self, file_path: Optional[Path] = None) -> None:
        """Guarda la configuración en un archivo JSON o YAML."""
        if file_path is None:
            file_path = self.config_path / f"{self.project_code}_config.json"
        
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        if file_path.suffix.lower() == '.yaml' or file_path.suffix.lower() == '.yml':
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.to_dict(), f, default_flow_style=False, allow_unicode=True)
        else:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
    
    @classmethod
    def load_config(cls, file_path: Path) -> 'ProjectConfigBase':
        """Carga una configuración desde un archivo."""
        if file_path.suffix.lower() in ['.yaml', '.yml']:
            with open(file_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
        
        return cls(**config_data)
    
    def get_config_summary(self) -> str:
        """Retorna un resumen de la configuración."""
        return f"""
Configuración del Proyecto: {self.project_name}
Código: {self.project_code}
Descripción: {self.description}
Columnas requeridas: {len(self.get_required_columns())}
Columnas opcionales: {len(self.get_optional_columns())}
Formatos soportados: {', '.join(self.supported_formats)}
Validación estricta: {self.strict_validation}
        """.strip() 