"""
Factory para gestionar las configuraciones de todos los proyectos.
Proporciona una interfaz unificada para acceder a las configuraciones específicas de cada proyecto.
"""

from typing import Dict, Any, Optional, Type
from pathlib import Path
import logging

from .base.config_base import ProjectConfigBase
from .DIAN.config import DIANConfig
from .COLJUEGOS.config import COLJUEGOSConfig
from .UGPP.config import UGPPConfig
from .BPM.config import BPMConfig

logger = logging.getLogger(__name__)


class ProjectConfigFactory:
    """
    Factory para crear y gestionar configuraciones de proyectos.
    Proporciona una interfaz unificada para acceder a las configuraciones específicas.
    """
    
    # Registro de configuraciones disponibles
    _configs: Dict[str, Type[ProjectConfigBase]] = {
        'DIAN': DIANConfig,
        'COLJUEGOS': COLJUEGOSConfig,
        'UGPP': UGPPConfig,
        'BPM': BPMConfig
    }
    
    # Cache de instancias de configuración
    _instances: Dict[str, ProjectConfigBase] = {}
    
    @classmethod
    def register_config(cls, project_code: str, config_class: Type[ProjectConfigBase]) -> None:
        """
        Registra una nueva configuración de proyecto.
        
        Args:
            project_code: Código del proyecto
            config_class: Clase de configuración
        """
        cls._configs[project_code.upper()] = config_class
        logger.info(f"Configuración registrada para el proyecto: {project_code}")
    
    @classmethod
    def get_config(cls, project_code: str, module_path: str = "") -> ProjectConfigBase:
        """
        Obtiene la configuración para un proyecto específico.
        
        Args:
            project_code: Código del proyecto (DIAN, COLJUEGOS, UGPP)
            module_path: Ruta del módulo (opcional)
            
        Returns:
            Instancia de la configuración del proyecto
            
        Raises:
            ValueError: Si el proyecto no está registrado
        """
        project_code = project_code.upper()
        
        # Crear clave única para el cache
        cache_key = f"{project_code}:{module_path}"
        
        # Verificar cache
        if cache_key in cls._instances:
            return cls._instances[cache_key]
        
        # Verificar si el proyecto está registrado
        if project_code not in cls._configs:
            available_projects = list(cls._configs.keys())
            raise ValueError(f"Proyecto '{project_code}' no está registrado. Proyectos disponibles: {available_projects}")
        
        # Crear nueva instancia
        config_class = cls._configs[project_code]
        config_instance = config_class(module_path)
        
        # Cachear la instancia
        cls._instances[cache_key] = config_instance
        
        logger.info(f"Configuración creada para {project_code} con módulo: {module_path}")
        return config_instance
    
    @classmethod
    def get_available_projects(cls) -> list[str]:
        """
        Retorna la lista de proyectos disponibles.
        
        Returns:
            Lista de códigos de proyectos disponibles
        """
        return list(cls._configs.keys())
    
    @classmethod
    def validate_project_data(cls, project_code: str, data: Dict[str, Any], 
                            module_name: str = "") -> Dict[str, Any]:
        """
        Valida datos para un proyecto específico.
        
        Args:
            project_code: Código del proyecto
            data: Datos a validar
            module_name: Nombre del módulo (opcional)
            
        Returns:
            Resultado de la validación
        """
        config = cls.get_config(project_code, module_name)
        return config.validate_module_data(data, module_name)
    
    @classmethod
    def get_project_summary(cls, project_code: str, module_path: str = "") -> str:
        """
        Obtiene un resumen de la configuración de un proyecto.
        
        Args:
            project_code: Código del proyecto
            module_path: Ruta del módulo (opcional)
            
        Returns:
            Resumen de la configuración
        """
        config = cls.get_config(project_code, module_path)
        return config.get_config_summary()
    
    @classmethod
    def get_all_configs_summary(cls) -> str:
        """
        Obtiene un resumen de todas las configuraciones disponibles.
        
        Returns:
            Resumen de todas las configuraciones
        """
        summary = "Resumen de Configuraciones de Proyectos\n"
        summary += "=" * 50 + "\n\n"
        
        for project_code in cls.get_available_projects():
            try:
                config = cls.get_config(project_code)
                summary += f"Proyecto: {project_code}\n"
                summary += f"  Nombre: {config.project_name}\n"
                summary += f"  Descripción: {config.description}\n"
                summary += f"  Columnas requeridas: {len(config.get_required_columns())}\n"
                summary += f"  Columnas opcionales: {len(config.get_optional_columns())}\n"
                summary += f"  Validadores: {len(config.get_validators())}\n"
                summary += "\n"
            except Exception as e:
                summary += f"Proyecto: {project_code} - Error: {str(e)}\n\n"
        
        return summary
    
    @classmethod
    def clear_cache(cls) -> None:
        """Limpia el cache de configuraciones."""
        cls._instances.clear()
        logger.info("Cache de configuraciones limpiado")
    
    @classmethod
    def reload_config(cls, project_code: str, module_path: str = "") -> ProjectConfigBase:
        """
        Recarga la configuración de un proyecto (ignora cache).
        
        Args:
            project_code: Código del proyecto
            module_path: Ruta del módulo (opcional)
            
        Returns:
            Nueva instancia de la configuración
        """
        project_code = project_code.upper()
        cache_key = f"{project_code}:{module_path}"
        
        # Remover del cache si existe
        if cache_key in cls._instances:
            del cls._instances[cache_key]
        
        # Crear nueva instancia
        return cls.get_config(project_code, module_path)


class ProjectManager:
    """
    Gestor de proyectos que proporciona funcionalidades avanzadas.
    """
    
    def __init__(self):
        self.factory = ProjectConfigFactory()
    
    def process_file(self, project_code: str, file_path: str, module_name: str = "") -> Dict[str, Any]:
        """
        Procesa un archivo para un proyecto específico.
        
        Args:
            project_code: Código del proyecto
            file_path: Ruta del archivo
            module_name: Nombre del módulo (opcional)
            
        Returns:
            Resultado del procesamiento
        """
        config = self.factory.get_config(project_code, module_name)
        
        # Aquí se implementaría la lógica de procesamiento
        # Por ahora retornamos información básica
        return {
            'project_code': project_code,
            'file_path': file_path,
            'module_name': module_name,
            'config_summary': config.get_config_summary(),
            'required_columns': config.get_required_columns(),
            'optional_columns': config.get_optional_columns(),
            'validators': list(config.get_validators().keys())
        }
    
    def validate_data(self, project_code: str, data: Dict[str, Any], 
                     module_name: str = "") -> Dict[str, Any]:
        """
        Valida datos para un proyecto específico.
        
        Args:
            project_code: Código del proyecto
            data: Datos a validar
            module_name: Nombre del módulo (opcional)
            
        Returns:
            Resultado de la validación
        """
        return self.factory.validate_project_data(project_code, data, module_name)
    
    def get_project_info(self, project_code: str, module_path: str = "") -> Dict[str, Any]:
        """
        Obtiene información detallada de un proyecto.
        
        Args:
            project_code: Código del proyecto
            module_path: Ruta del módulo (opcional)
            
        Returns:
            Información del proyecto
        """
        config = self.factory.get_config(project_code, module_path)
        
        return {
            'project_code': config.project_code,
            'project_name': config.project_name,
            'description': config.description,
            'required_columns': config.get_required_columns(),
            'optional_columns': config.get_optional_columns(),
            'column_mappings': config.get_column_mappings(),
            'validators': list(config.get_validators().keys()),
            'supported_formats': config.supported_formats,
            'encoding': config.encoding,
            'delimiter': config.delimiter
        }
    
    def list_projects(self) -> Dict[str, Dict[str, Any]]:
        """
        Lista todos los proyectos disponibles con información básica.
        
        Returns:
            Diccionario con información de todos los proyectos
        """
        projects = {}
        
        for project_code in self.factory.get_available_projects():
            try:
                config = self.factory.get_config(project_code)
                projects[project_code] = {
                    'name': config.project_name,
                    'description': config.description,
                    'required_columns_count': len(config.get_required_columns()),
                    'optional_columns_count': len(config.get_optional_columns()),
                    'validators_count': len(config.get_validators())
                }
            except Exception as e:
                projects[project_code] = {
                    'error': str(e)
                }
        
        return projects


# Instancia global del gestor de proyectos
project_manager = ProjectManager()


def get_project_config(project_code: str, module_path: str = "") -> ProjectConfigBase:
    """
    Función de conveniencia para obtener la configuración de un proyecto.
    
    Args:
        project_code: Código del proyecto
        module_path: Ruta del módulo (opcional)
        
    Returns:
        Configuración del proyecto
    """
    return ProjectConfigFactory.get_config(project_code, module_path)


def validate_project_data(project_code: str, data: Dict[str, Any], 
                         module_name: str = "") -> Dict[str, Any]:
    """
    Función de conveniencia para validar datos de un proyecto.
    
    Args:
        project_code: Código del proyecto
        data: Datos a validar
        module_name: Nombre del módulo (opcional)
        
    Returns:
        Resultado de la validación
    """
    return ProjectConfigFactory.validate_project_data(project_code, data, module_name) 