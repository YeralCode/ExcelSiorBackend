"""
Paquete base para configuraciones reutilizables de proyectos.
Contiene clases y utilidades base que pueden ser extendidas por cada proyecto.
"""

from .config_base import ProjectConfigBase
from .values_manager import ValuesManager
from .validators import BaseValidator

__all__ = ['ProjectConfigBase', 'ValuesManager', 'BaseValidator'] 