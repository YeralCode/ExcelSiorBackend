"""
Gestor de valores para manejar valores_choice de manera reutilizable.
Proporciona funcionalidades para cargar, validar y gestionar valores específicos de cada proyecto.
"""

from typing import Dict, List, Set, Any, Optional, Union
from pathlib import Path
import importlib
import inspect
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ValuesConfig:
    """Configuración para un conjunto de valores."""
    name: str
    values: Union[List[str], Set[str], Dict[str, str]]
    replacement_map: Optional[Dict[str, str]] = None
    description: str = ""
    validation_rules: Optional[Dict[str, Any]] = None


class ValuesManager:
    """
    Gestor de valores para manejar valores_choice de manera reutilizable.
    Permite cargar y gestionar valores específicos de cada proyecto.
    """
    
    def __init__(self, project_code: str, module_path: str = ""):
        """
        Inicializa el gestor de valores.
        
        Args:
            project_code: Código del proyecto (ej: 'DIAN', 'COLJUEGOS')
            module_path: Ruta del módulo de valores (ej: 'defensoria/valores_choice')
        """
        self.project_code = project_code.upper()
        self.module_path = module_path
        self.values_cache: Dict[str, ValuesConfig] = {}
        self.base_path = Path(f"repository/proyectos/{self.project_code}")
        
        if module_path:
            self.full_path = self.base_path / module_path
        else:
            self.full_path = self.base_path
    
    def load_values_from_module(self, module_name: str) -> ValuesConfig:
        """
        Carga valores desde un módulo Python.
        
        Args:
            module_name: Nombre del módulo (sin extensión .py)
            
        Returns:
            ValuesConfig con los valores cargados
        """
        try:
            # Construir la ruta del módulo
            module_path = self.full_path / "valores_choice" / f"{module_name}.py"
            
            if not module_path.exists():
                raise FileNotFoundError(f"No se encontró el módulo: {module_path}")
            
            # Importar el módulo dinámicamente
            spec = importlib.util.spec_from_file_location(
                f"{self.project_code}.{module_name}", 
                module_path
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Extraer valores del módulo
            values = self._extract_values_from_module(module, module_name)
            
            # Crear configuración
            config = ValuesConfig(
                name=module_name,
                values=values.get('values', []),
                replacement_map=values.get('replacement_map', {}),
                description=values.get('description', f"Valores de {module_name} para {self.project_code}"),
                validation_rules=values.get('validation_rules', {})
            )
            
            # Cachear la configuración
            self.values_cache[module_name] = config
            
            logger.info(f"Valores cargados exitosamente desde {module_name} para {self.project_code}")
            return config
            
        except Exception as e:
            logger.error(f"Error cargando valores desde {module_name}: {str(e)}")
            raise
    
    def _extract_values_from_module(self, module: Any, module_name: str) -> Dict[str, Any]:
        """
        Extrae valores de un módulo importado.
        
        Args:
            module: Módulo importado
            module_name: Nombre del módulo
            
        Returns:
            Diccionario con los valores extraídos
        """
        values = {}
        
        # Buscar variables que contengan 'VALORES'
        for attr_name in dir(module):
            if attr_name.startswith('VALORES_'):
                attr_value = getattr(module, attr_name)
                
                if isinstance(attr_value, (list, set, dict)):
                    values['values'] = attr_value
                
                # Buscar mapa de reemplazo correspondiente
                replacement_name = attr_name.replace('VALORES_', 'VALORES_REEMPLAZO_')
                if hasattr(module, replacement_name):
                    values['replacement_map'] = getattr(module, replacement_name)
        
        # Si no se encontraron valores con el patrón, buscar variables específicas
        if 'values' not in values:
            common_names = ['VALORES', 'VALUES', 'CHOICES', 'OPTIONS']
            for name in common_names:
                if hasattr(module, name):
                    values['values'] = getattr(module, name)
                    break
        
        return values
    
    def get_values(self, module_name: str, force_reload: bool = False) -> ValuesConfig:
        """
        Obtiene valores de un módulo, usando cache si está disponible.
        
        Args:
            module_name: Nombre del módulo
            force_reload: Si True, recarga el módulo ignorando el cache
            
        Returns:
            ValuesConfig con los valores
        """
        if not force_reload and module_name in self.values_cache:
            return self.values_cache[module_name]
        
        return self.load_values_from_module(module_name)
    
    def validate_value(self, module_name: str, value: str) -> bool:
        """
        Valida si un valor está en la lista de valores permitidos.
        
        Args:
            module_name: Nombre del módulo de valores
            value: Valor a validar
            
        Returns:
            True si el valor es válido
        """
        config = self.get_values(module_name)
        
        if isinstance(config.values, dict):
            return value in config.values.values() or value in config.values.keys()
        elif isinstance(config.values, (list, set)):
            return value in config.values
        
        return False
    
    def get_replacement(self, module_name: str, value: str) -> str:
        """
        Obtiene el valor de reemplazo para un valor dado.
        
        Args:
            module_name: Nombre del módulo de valores
            value: Valor original
            
        Returns:
            Valor de reemplazo o el valor original si no hay reemplazo
        """
        config = self.get_values(module_name)
        
        if config.replacement_map and value in config.replacement_map:
            return config.replacement_map[value]
        
        return value
    
    def get_all_values(self, module_name: str) -> List[str]:
        """
        Obtiene todos los valores de un módulo como lista.
        
        Args:
            module_name: Nombre del módulo
            
        Returns:
            Lista con todos los valores
        """
        config = self.get_values(module_name)
        
        if isinstance(config.values, dict):
            return list(config.values.values())
        elif isinstance(config.values, set):
            return list(config.values)
        elif isinstance(config.values, list):
            return config.values
        
        return []
    
    def add_value(self, module_name: str, value: str, replacement: Optional[str] = None) -> None:
        """
        Agrega un nuevo valor al módulo especificado.
        
        Args:
            module_name: Nombre del módulo
            value: Nuevo valor
            replacement: Valor de reemplazo (opcional)
        """
        config = self.get_values(module_name)
        
        # Agregar el valor
        if isinstance(config.values, list):
            if value not in config.values:
                config.values.append(value)
        elif isinstance(config.values, set):
            config.values.add(value)
        elif isinstance(config.values, dict):
            # Para diccionarios, asumimos que el valor es la clave
            config.values[value] = value
        
        # Agregar reemplazo si se especifica
        if replacement and config.replacement_map is not None:
            config.replacement_map[value] = replacement
        
        logger.info(f"Valor '{value}' agregado al módulo {module_name}")
    
    def remove_value(self, module_name: str, value: str) -> bool:
        """
        Remueve un valor del módulo especificado.
        
        Args:
            module_name: Nombre del módulo
            value: Valor a remover
            
        Returns:
            True si el valor fue removido
        """
        config = self.get_values(module_name)
        
        if isinstance(config.values, list):
            if value in config.values:
                config.values.remove(value)
                return True
        elif isinstance(config.values, set):
            if value in config.values:
                config.values.remove(value)
                return True
        elif isinstance(config.values, dict):
            if value in config.values:
                del config.values[value]
                return True
        
        # Remover del mapa de reemplazo también
        if config.replacement_map and value in config.replacement_map:
            del config.replacement_map[value]
        
        logger.info(f"Valor '{value}' removido del módulo {module_name}")
        return False
    
    def save_values_to_file(self, module_name: str, file_path: Optional[Path] = None) -> None:
        """
        Guarda los valores en un archivo Python.
        
        Args:
            module_name: Nombre del módulo
            file_path: Ruta del archivo (opcional)
        """
        config = self.get_values(module_name)
        
        if file_path is None:
            file_path = self.full_path / "valores_choice" / f"{module_name}.py"
        
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f'"""\nValores para {module_name} del proyecto {self.project_code}\n"""\n\n')
            
            # Escribir valores principales
            if isinstance(config.values, list):
                f.write(f"{module_name.upper()} = [\n")
                for value in config.values:
                    f.write(f'    "{value}",\n')
                f.write("]\n\n")
            elif isinstance(config.values, set):
                f.write(f"{module_name.upper()} = {{\n")
                for value in config.values:
                    f.write(f'    "{value}",\n')
                f.write("}\n\n")
            elif isinstance(config.values, dict):
                f.write(f"{module_name.upper()} = {{\n")
                for key, value in config.values.items():
                    f.write(f'    "{key}": "{value}",\n')
                f.write("}\n\n")
            
            # Escribir mapa de reemplazo si existe
            if config.replacement_map:
                f.write(f"{module_name.upper()}_REEMPLAZO = {{\n")
                for key, value in config.replacement_map.items():
                    f.write(f'    "{key}": "{value}",\n')
                f.write("}\n\n")
        
        logger.info(f"Valores guardados en {file_path}")
    
    def get_available_modules(self) -> List[str]:
        """
        Obtiene la lista de módulos disponibles.
        
        Returns:
            Lista de nombres de módulos disponibles
        """
        values_path = self.full_path / "valores_choice"
        
        if not values_path.exists():
            return []
        
        modules = []
        for file_path in values_path.glob("*.py"):
            if file_path.name != "__init__.py":
                modules.append(file_path.stem)
        
        return modules
    
    def get_summary(self) -> str:
        """
        Obtiene un resumen de todos los valores cargados.
        
        Returns:
            String con el resumen
        """
        summary = f"Resumen de valores para {self.project_code}\n"
        summary += "=" * 50 + "\n"
        
        for module_name, config in self.values_cache.items():
            summary += f"\nMódulo: {module_name}\n"
            summary += f"  Descripción: {config.description}\n"
            summary += f"  Valores: {len(self.get_all_values(module_name))}\n"
            if config.replacement_map:
                summary += f"  Reemplazos: {len(config.replacement_map)}\n"
        
        return summary 