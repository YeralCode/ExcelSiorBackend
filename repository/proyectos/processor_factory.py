"""
Abstract Factory para procesadores de CSV.
Implementa el patrón Abstract Factory para crear procesadores específicos de cada proyecto
de manera unificada y reutilizable.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Type, List
import logging
from pathlib import Path

from .base.config_base import ProjectConfigBase
from .base.values_manager import ValuesManager
from .base.validators import ValidatorFactory
from .factory import get_project_config

logger = logging.getLogger(__name__)


class CSVProcessorBase(ABC):
    """
    Clase base abstracta para todos los procesadores de CSV.
    Define la interfaz común que deben implementar todos los procesadores.
    """
    
    def __init__(self, config: Optional[ProjectConfigBase] = None):
        """
        Inicializa el procesador base.
        
        Args:
            config: Configuración específica del proyecto (opcional)
        """
        self.config = config
        self.values_manager = None
        self.validators = {}
        self.error_messages = {}
        
        if config:
            self._initialize_components()
    
    @abstractmethod
    def _initialize_components(self) -> None:
        """Inicializa los componentes específicos del procesador."""
        pass
    
    @abstractmethod
    def _get_validators(self) -> Dict[str, Any]:
        """Retorna los validadores específicos del procesador."""
        pass
    
    @abstractmethod
    def _get_error_messages(self) -> Dict[str, str]:
        """Retorna los mensajes de error específicos del procesador."""
        pass
    
    @abstractmethod
    def get_reference_headers(self) -> List[str]:
        """Retorna los headers de referencia para el procesador."""
        pass
    
    @abstractmethod
    def get_replacement_map(self) -> Dict[str, str]:
        """Retorna el mapeo de reemplazo de columnas."""
        pass
    
    def normalize_column_name(self, column_name: str) -> str:
        """Normaliza nombres de columnas reemplazando espacios y caracteres especiales."""
        column_name = column_name.strip().upper()
        replacements = [
            (' ', '_'), ('-', '_'), ('Á', 'A'), ('É', 'E'), ('Í', 'I'),
            ('Ó', 'O'), ('Ú', 'U'), ('Ñ', 'N'), ('.', ''), ('/', '_'),
        ]
        for old, new in replacements:
            column_name = column_name.replace(old, new)
        return column_name
    
    def organize_headers(self, actual_headers: List[str]) -> List[str]:
        """Organiza headers según REFERENCE_HEADERS y aplica reemplazos."""
        normalized = [self.normalize_column_name(h) for h in actual_headers]
        replacement_map = self.get_replacement_map()

        # Aplicar reemplazos
        for i, header in enumerate(normalized):
            normalized[i] = replacement_map.get(header, header)

        # Eliminar duplicados manteniendo orden
        seen = set()
        unique_headers = []
        for h in normalized:
            if h not in seen:
                seen.add(h)
                unique_headers.append(h)

        # Ordenar según REFERENCE_HEADERS
        ref_headers_normalized = [self.normalize_column_name(h) for h in self.get_reference_headers()]
        ordered = []
        remaining = []
        
        for ref_h in ref_headers_normalized:
            if ref_h in unique_headers:
                ordered.append(ref_h)
        remaining = [h for h in unique_headers if h not in ordered]
        return ordered + remaining
    
    def clean_value(self, value: str, null_values: set = None) -> str:
        """Limpia valores nulos y espacios."""
        if null_values is None:
            null_values = {"$null$", "nan", "NULL", "N.A", "null", "N.A.", "n/a", "n/a."}
        
        if value is None:
            return ""
        value = str(value).strip()
        return "" if value.upper() in null_values else value
    
    def preprocess_line(self, line: str) -> str:
        """Preprocesa línea para manejar comas y saltos internos."""
        if not line.strip():
            return line
            
        temp_newline = '⏎'
        temp_comma = '\uE000'
        
        line = line.replace('\\n', temp_newline)
        in_quotes = False
        processed = []
        
        for char in line:
            if char == '"':
                in_quotes = not in_quotes
                processed.append(char)
            elif char == ',' and not in_quotes:
                processed.append(temp_comma)
            else:
                processed.append(char)
        
        return ''.join(processed)
    
    def postprocess_field(self, field: str) -> str:
        """Restaura caracteres especiales a su forma original."""
        return field.replace('\uE000', ',').replace('⏎', '\n')
    
    def _validate_value_modular(self, value: str, col_name: str, col_num: int, 
                               row_num: int, type_mapping: Dict[str, List[int]]) -> tuple[str, Optional[Any]]:
        """Valida un valor usando el sistema modular de validadores."""
        if not value:
            return value, None
        
        # Determinar el tipo esperado
        expected_type = self._get_expected_type(col_num, type_mapping)
        
        try:
            if expected_type in self.validators:
                validator = self.validators[expected_type]
                if not validator.is_valid(value):
                    error_msg = self.error_messages.get(f'invalid_{expected_type}', f"Valor inválido para tipo {expected_type}")
                    return value, self._create_error(col_name, col_num, expected_type, value, row_num, error_msg)
            
            return value, None
            
        except Exception as e:
            return value, self._create_error(col_name, col_num, expected_type, value, row_num, str(e))
    
    def _get_expected_type(self, col_num: int, type_mapping: Dict[str, List[int]]) -> str:
        """Obtiene el tipo esperado para una columna."""
        for type_name, columns in type_mapping.items():
            if col_num in columns:
                return type_name
        return "string"
    
    def _create_error(self, col_name: str, col_num: int, expected_type: str, 
                     value: str, row_num: int, error_msg: str) -> Any:
        """Crea un objeto de error estandarizado."""
        from dataclasses import dataclass
        
        @dataclass
        class ErrorInfo:
            columna: str
            numero_columna: int
            tipo: str
            valor: str
            fila: int
            error: str
        
        return ErrorInfo(
            columna=col_name, numero_columna=col_num,
            tipo=expected_type, valor=value, fila=row_num,
            error=error_msg
        )


class ProcessorFactory:
    """
    Abstract Factory para crear procesadores de CSV específicos de cada proyecto.
    Implementa el patrón Abstract Factory para centralizar la creación de procesadores.
    """
    
    # Registro de procesadores disponibles
    _processors: Dict[str, Type[CSVProcessorBase]] = {}
    
    @classmethod
    def register_processor(cls, project_code: str, module_name: str, 
                          processor_class: Type[CSVProcessorBase]) -> None:
        """
        Registra un nuevo procesador.
        
        Args:
            project_code: Código del proyecto (DIAN, COLJUEGOS, UGPP)
            module_name: Nombre del módulo (notificaciones, disciplinarios, pqr)
            processor_class: Clase del procesador
        """
        key = f"{project_code.upper()}:{module_name.lower()}"
        cls._processors[key] = processor_class
        logger.info(f"Procesador registrado: {key}")
    
    @classmethod
    def create_processor(cls, project_code: str, module_name: str, 
                        config: Optional[ProjectConfigBase] = None) -> CSVProcessorBase:
        """
        Crea un procesador específico para el proyecto y módulo.
        
        Args:
            project_code: Código del proyecto
            module_name: Nombre del módulo
            config: Configuración específica (opcional)
            
        Returns:
            Instancia del procesador específico
            
        Raises:
            ValueError: Si el procesador no está registrado
        """
        key = f"{project_code.upper()}:{module_name.lower()}"
        
        if key not in cls._processors:
            available_processors = list(cls._processors.keys())
            raise ValueError(f"Procesador '{key}' no está registrado. Procesadores disponibles: {available_processors}")
        
        processor_class = cls._processors[key]
        
        # Si no se proporciona config, obtenerla automáticamente
        if config is None:
            config = get_project_config(project_code, module_name)
        
        processor = processor_class(config=config)
        logger.info(f"Procesador creado: {key}")
        return processor
    
    @classmethod
    def get_available_processors(cls) -> List[str]:
        """
        Retorna la lista de procesadores disponibles.
        
        Returns:
            Lista de procesadores disponibles
        """
        return list(cls._processors.keys())
    
    @classmethod
    def clear_registry(cls) -> None:
        """Limpia el registro de procesadores."""
        cls._processors.clear()
        logger.info("Registro de procesadores limpiado")


# Procesadores específicos implementados como clases concretas

class DIANNotificacionesProcessor(CSVProcessorBase):
    """Procesador específico para archivos de notificaciones de DIAN."""
    
    def _initialize_components(self) -> None:
        """Inicializa los componentes específicos del procesador."""
        self.values_manager = ValuesManager('DIAN', 'notificaciones')
        self.validators = self._get_validators()
        self.error_messages = self._get_error_messages()
        logger.info(f"Procesador inicializado para {self.config.project_name}")
    
    def _get_validators(self) -> Dict[str, Any]:
        """Retorna los validadores específicos del procesador."""
        factory = ValidatorFactory()
        
        return {
            'integer': factory.create_validator('integer'),
            'float': factory.create_validator('float', min_value=0.0),
            'date': factory.create_validator('date'),
            'datetime': factory.create_validator('date'),
            'nit': factory.create_validator('nit'),
            'string': factory.create_validator('string', min_length=0),
            'estado_notificacion': self._get_estado_notificacion_validator(),
            'proceso': self._get_proceso_validator(),
            'dependencia': self._get_dependencia_validator()
        }
    
    def _get_error_messages(self) -> Dict[str, str]:
        """Retorna los mensajes de error específicos del procesador."""
        return {
            'invalid_integer': "No es un entero válido",
            'invalid_float': "No es un flotante válido",
            'invalid_date': "No es una fecha válida",
            'invalid_datetime': "No es una fecha y hora válida",
            'invalid_nit': "No es un NIT válido",
            'invalid_estado_notificacion': "No se encuentra en estado de notificación",
            'invalid_proceso': "No se encuentra en proceso",
            'invalid_dependencia': "No se encuentra en dependencia"
        }
    
    def get_reference_headers(self) -> List[str]:
        """Retorna los headers de referencia para DIAN notificaciones."""
        return [
            "PLAN_IDENTIF_ACTO", "CODIGO_ADMINISTRACION", "SECCIONAL", "CODIGO_DEPENDENCIA",
            "DEPENDENCIA", "ANO_CALENDARIO", "CODIGO_ACTO", "DESCRIPCION_ACTO", "ANO_ACTO",
            "CONSECUTIVO_ACTO", "FECHA_ACTO", "CUANTIA_ACTO", "NIT", "RAZON_SOCIAL",
            "DIRECCION", "PLANILLA_REMISION", "FECHA_PLANILLA_REMISION", "FUNCIONARIO_ENVIA",
            "FECHA_CITACION", "PLANILLA_CORR", "FECHA_PLANILLA_CORR", "FECHA_NOTIFICACION",
            "FECHA_EJECUTORIA", "GUIA", "COD_ESTADO", "ESTADO_NOTIFICACION", "COD_NOTIFICACION",
            "MEDIO_NOTIFICACION", "NUMERO_EXPEDIENTE", "TIPO_DOCUMENTO", "PERI_IMPUESTO",
            "PERI_PERIODO", "NOMBRE_APLICACION", "PAIS_COD_NUM_PAIS", "PAIS",
            "MUNI_CODIGO_DEPART", "DEPARTAMENTO", "MUNI_CODIGO_MUNICI", "MUNICIPIO",
            "REGIMEN", "FECHA_LEVANTE", "MOTIVO_LEVANTE", "NORMATIVIDAD", "FUNCIONARIO_RECIBE",
            "PLANILLA_REMI_ARCHIVO", "FECHA_PLANILLA_REMI_ARCHIVO"
        ]
    
    def get_replacement_map(self) -> Dict[str, str]:
        """Retorna el mapeo de reemplazo de columnas para DIAN notificaciones."""
        return {
            "nombre_archivo": "NOMBRE_ARCHIVO",
            "mes_reporte": "MES_REPORTE",
            'COPL_PLANILLA_REMI': 'PLANILLA_REMISION',
            'COPL_PLANILLA_CORR': 'PLANILLA_CORR',
            'Seccional': 'SECCIONAL',
            'PIA': 'PLAN_IDENTIF_ACTO',
            'SECC': 'SECCIONAL',
            'DEP': 'CODIGO_DEPENDENCIA',
            'AÑO': 'ANO_CALENDARIO',
            'COD_ACTO': 'CODIGO_ACTO',
            'DESCRIPCION': 'DESCRIPCION_ACTO',
            'CONSECUTIVO': 'CONSECUTIVO_ACTO',
            'CUANTIA': 'CUANTIA_ACTO',
            'PLANILLA_REMI': 'PLANILLA_REMISION',
            'FECHA_PLANILLA_REMI': 'FECHA_PLANILLA_REMISION',
            'NUMERO_DE_GUIA': 'GUIA',
            'ESTADO': 'ESTADO_NOTIFICACION',
            'COD_NOTI': 'COD_NOTIFICACION',
            'DESC_NOTIFICACION': 'DESCRIPCION',
            'TIPO_DOC': 'TIPO_DOCUMENTO',
            'IMPUESTO': 'PERI_IMPUESTO',
            'PERIODO': 'PERI_PERIODO',
            'DEPTO': 'MUNI_CODIGO_DEPART',
            'NOMBRE_DEPTO': 'DEPARTAMENTO',
            'MUNICIPIO': 'MUNI_CODIGO_MUNICI',
        }
    
    def _get_estado_notificacion_validator(self):
        """Obtiene el validador para estados de notificación."""
        try:
            estados = self.values_manager.get_all_values('estado_notificacion')
            return ValidatorFactory.create_validator('choice', choices=estados)
        except Exception as e:
            logger.warning(f"No se pudieron cargar valores de estado_notificacion: {e}")
            return ValidatorFactory.create_validator('choice', choices=[
                'notificado', 'pendiente', 'devuelto', 'cancelado', 'en trámite'
            ])
    
    def _get_proceso_validator(self):
        """Obtiene el validador para procesos."""
        try:
            procesos = self.values_manager.get_all_values('proceso')
            return ValidatorFactory.create_validator('choice', choices=procesos)
        except Exception as e:
            logger.warning(f"No se pudieron cargar valores de proceso: {e}")
            return ValidatorFactory.create_validator('choice', choices=[
                'asistencia al cliente', 'fiscalización y liquidación', 'operación aduanera',
                'gestión masiva', 'administración de cartera', 'gestión jurídica'
            ])
    
    def _get_dependencia_validator(self):
        """Obtiene el validador para dependencias."""
        try:
            dependencias = self.values_manager.get_all_values('dependencia')
            return ValidatorFactory.create_validator('choice', choices=dependencias)
        except Exception as e:
            logger.warning(f"No se pudieron cargar valores de dependencia: {e}")
            return ValidatorFactory.create_validator('choice', choices=[
                'nivel central', 'dirección seccional'
            ])


class DIANDisciplinariosProcessor(CSVProcessorBase):
    """Procesador específico para archivos disciplinarios de DIAN."""
    
    def _initialize_components(self) -> None:
        """Inicializa los componentes específicos del procesador."""
        self.values_manager = ValuesManager('DIAN', 'disciplinarios')
        self.validators = self._get_validators()
        self.error_messages = self._get_error_messages()
        logger.info(f"Procesador inicializado para {self.config.project_name}")
    
    def _get_validators(self) -> Dict[str, Any]:
        """Retorna los validadores específicos del procesador."""
        factory = ValidatorFactory()
        
        return {
            'integer': factory.create_validator('integer'),
            'float': factory.create_validator('float', min_value=0.0),
            'date': factory.create_validator('date'),
            'datetime': factory.create_validator('date'),
            'nit': factory.create_validator('nit'),
            'string': factory.create_validator('string', min_length=0),
            'departamento': self._get_departamento_validator(),
            'ciudad': self._get_ciudad_validator(),
            'direccion_seccional': self._get_direccion_seccional_validator(),
            'expediente': factory.create_validator('string', min_length=1, max_length=50)
        }
    
    def _get_error_messages(self) -> Dict[str, str]:
        """Retorna los mensajes de error específicos del procesador."""
        return {
            'invalid_integer': "No es un entero válido",
            'invalid_float': "No es un flotante válido",
            'invalid_date': "No es una fecha válida",
            'invalid_datetime': "No es una fecha y hora válida",
            'invalid_nit': "No es un NIT válido",
            'invalid_departamento': "No se encuentra en departamento",
            'invalid_ciudad': "No se encuentra en ciudad",
            'invalid_direccion_seccional': "No se encuentra en direccion seccional",
            'invalid_expediente': "No es un expediente valido"
        }
    
    def get_reference_headers(self) -> List[str]:
        """Retorna los headers de referencia para DIAN disciplinarios."""
        return [
            'NOMBRE_ARCHIVO', 'MES_REPORTE', "NO_EXPEDIENTE", "FECHA_RADICACION",
            "FECHA_HECHOS", "INDAGACION_PRELIMINAR", "INVESTIGACION_DISCIPLINARIA",
            "IMPLICADO", "IDENTIFICACION", "DEPARTAMENTO", "CIUDAD",
            "DIRECCION_SECCIONAL_O_EQUIVALENTE", "DEPENDENCIA", "PROCESO",
            "SUBPROCESO", "PROCEDIMIENTO", "CARGO", "ORIGEN", "CONDUCTA",
            "ETAPA_PROCESAL", "FECHA_FALLO", "SANCION_IMPUESTA", "HECHO",
            "DECISION", "PROCESO_AFECTADO", "SENALADOS_O_VINCULADOS",
            "ADECUACION_TIPICA", "ABOGADO", "SENTIDO_DEL_FALLO", "QUEJOSO",
            "IDENTIFICACION_QUEJOSO", "TIPO_DE_PROCESO", "FECHA_PLIEGO_DE_CARGOS",
            "FECHA_CITACION", "FECHA_CIERRE_DE_INVESTIGACION"
        ]
    
    def get_replacement_map(self) -> Dict[str, str]:
        """Retorna el mapeo de reemplazo de columnas para DIAN disciplinarios."""
        return {}
    
    def _get_departamento_validator(self):
        """Obtiene el validador para departamentos."""
        try:
            departamentos = self.values_manager.get_all_values('departamento')
            return ValidatorFactory.create_validator('choice', choices=departamentos)
        except Exception as e:
            logger.warning(f"No se pudieron cargar valores de departamento: {e}")
            return ValidatorFactory.create_validator('choice', choices=[
                'antioquia', 'atlantico', 'bogota', 'bolivar', 'boyaca',
                'caldas', 'caqueta', 'cauca', 'cesar', 'cordoba',
                'cundinamarca', 'choco', 'huila', 'la guajira', 'magdalena',
                'meta', 'nariño', 'norte de santander', 'quindio', 'risaralda',
                'santander', 'sucre', 'tolima', 'valle del cauca', 'vaupes',
                'vichada', 'amazonas', 'guainia', 'guaviare', 'putumayo',
                'san andres y providencia', 'arauca', 'casanare'
            ])
    
    def _get_ciudad_validator(self):
        """Obtiene el validador para ciudades."""
        try:
            ciudades = self.values_manager.get_all_values('ciudad')
            return ValidatorFactory.create_validator('choice', choices=ciudades)
        except Exception as e:
            logger.warning(f"No se pudieron cargar valores de ciudad: {e}")
            return ValidatorFactory.create_validator('choice', choices=[
                'medellin', 'barranquilla', 'bogota', 'cartagena', 'tunja',
                'manizales', 'florencia', 'popayan', 'valledupar', 'monteria',
                'bogota', 'quibdo', 'neiva', 'riohacha', 'santa marta',
                'villavicencio', 'pasto', 'cucuta', 'armenia', 'pereira',
                'bucaramanga', 'sincelejo', 'ibague', 'cali', 'mitu',
                'puerto carreno', 'leticia', 'inirida', 'san jose del guaviare',
                'mocoa', 'san andres'
            ])
    
    def _get_direccion_seccional_validator(self):
        """Obtiene el validador para direcciones seccionales."""
        try:
            direcciones = self.values_manager.get_all_values('direccion_seccional')
            return ValidatorFactory.create_validator('choice', choices=direcciones)
        except Exception as e:
            logger.warning(f"No se pudieron cargar valores de direccion_seccional: {e}")
            return ValidatorFactory.create_validator('choice', choices=[
                'nivel central',
                'direccion seccional de impuestos y aduanas de armenia',
                'direccion seccional de impuestos de barranquilla',
                'direccion seccional de aduanas de bogota',
                'direccion seccional de impuestos y aduanas de bucaramanga',
                'direccion seccional de impuestos de cali',
                'direccion seccional de impuestos de cartagena',
                'direccion seccional de impuestos de cucuta',
                'direccion seccional de impuestos de medellin',
                'direccion seccional de impuestos de grandes contribuyentes',
                'direccion seccional de impuestos de bogota'
            ])


class COLJUEGOSDisciplinariosProcessor(CSVProcessorBase):
    """Procesador específico para archivos disciplinarios de COLJUEGOS."""
    
    def _initialize_components(self) -> None:
        """Inicializa los componentes específicos del procesador."""
        self.values_manager = ValuesManager('COLJUEGOS', 'disciplinarios')
        self.validators = self._get_validators()
        self.error_messages = self._get_error_messages()
        logger.info(f"Procesador inicializado para {self.config.project_name}")
    
    def _get_validators(self) -> Dict[str, Any]:
        """Retorna los validadores específicos del procesador."""
        factory = ValidatorFactory()
        
        return {
            'integer': factory.create_validator('integer'),
            'float': factory.create_validator('float', min_value=0.0),
            'date': factory.create_validator('date'),
            'datetime': factory.create_validator('date'),
            'nit': factory.create_validator('nit'),
            'string': factory.create_validator('string', min_length=0),
            'direccion_seccional': self._get_direccion_seccional_validator(),
            'proceso': self._get_proceso_validator()
        }
    
    def _get_error_messages(self) -> Dict[str, str]:
        """Retorna los mensajes de error específicos del procesador."""
        return {
            'invalid_integer': "No es un entero válido",
            'invalid_float': "No es un flotante válido",
            'invalid_date': "No es una fecha válida",
            'invalid_datetime': "No es una fecha y hora válida",
            'invalid_nit': "No es un NIT válido",
            'invalid_direccion_seccional': "No se encuentra en direccion seccional",
            'invalid_proceso': "No se encuentra en proceso"
        }
    
    def get_reference_headers(self) -> List[str]:
        """Retorna los headers de referencia para COLJUEGOS disciplinarios."""
        return [
            "EXPEDIENTE", "FECHA_DE_RADICACION", "FECHA_DE_LOS_HECHOS",
            "FECHA_DE_INDAGACION_PRELIMINAR", "FECHA_DE_INVESTIGACION_DISCIPLINARIA",
            "IMPLICADO", "DOCUMENTO_DEL_IMPLICADO", "DEPARTAMENTO_DE_LOS_HECHOS",
            "CIUDAD_DE_LOS_HECHOS", "DIRECCION_SECCIONAL", "DEPENDENCIA",
            "PROCESO", "SUBPROCESO", "PROCEDIMIENTO", "CARGO", "ORIGEN",
            "CONDUCTA", "ETAPA_PROCESAL", "FECHA_DE_FALLO", "SANCION_IMPUESTA",
            "HECHOS", "DECISION_DE_LA_INVESTIGACION", "TIPO_DE_PROCESO_AFECTADO",
            "SENALADOS_O_VINCULADOS_CON_LA_INVESTIGACION", "ADECUACION_TIPICA",
            "ABOGADO", "SENTIDO_DEL_FALLO", "QUEJOSO", "DOC_QUEJOSO",
            "TIPO_DE_PROCESO", "FECHA_CITACION", "FECHA_DE_CARGOS",
            "FECHA_DE_CIERRE_INVESTIGACION"
        ]
    
    def get_replacement_map(self) -> Dict[str, str]:
        """Retorna el mapeo de reemplazo de columnas para COLJUEGOS disciplinarios."""
        return {}
    
    def _get_direccion_seccional_validator(self):
        """Obtiene el validador para direcciones seccionales."""
        try:
            direcciones = self.values_manager.get_all_values('direccion_seccional')
            return ValidatorFactory.create_validator('choice', choices=direcciones)
        except Exception as e:
            logger.warning(f"No se pudieron cargar valores de direccion_seccional: {e}")
            return ValidatorFactory.create_validator('choice', choices=[
                "gerencia control a las operaciones ilegales",
                "gerencia de cobro",
                "gerencia financiera",
                "gerencia seguimiento contractual",
                "vicepresidencia de desarrollo organizacional",
                "vicepresidencia de operaciones",
                "vicepresidencia desarrollo comercial"
            ])
    
    def _get_proceso_validator(self):
        """Obtiene el validador para procesos."""
        try:
            procesos = self.values_manager.get_all_values('proceso')
            return ValidatorFactory.create_validator('choice', choices=procesos)
        except Exception as e:
            logger.warning(f"No se pudieron cargar valores de proceso: {e}")
            return ValidatorFactory.create_validator('choice', choices=[
                "cobro coactivo",
                "contratacion misional",
                "control",
                "control operaciones ilegales",
                "gestion juridica",
                "incumplimiento contractual",
                "seguimiento contractual",
                "segunda instancia"
            ])


# Registrar todos los procesadores disponibles
ProcessorFactory.register_processor('DIAN', 'notificaciones', DIANNotificacionesProcessor)
ProcessorFactory.register_processor('DIAN', 'disciplinarios', DIANDisciplinariosProcessor)
ProcessorFactory.register_processor('COLJUEGOS', 'disciplinarios', COLJUEGOSDisciplinariosProcessor)


# Funciones de conveniencia para uso directo
def create_processor(project_code: str, module_name: str, 
                    config: Optional[ProjectConfigBase] = None) -> CSVProcessorBase:
    """
    Función de conveniencia para crear procesadores.
    
    Args:
        project_code: Código del proyecto
        module_name: Nombre del módulo
        config: Configuración específica (opcional)
        
    Returns:
        Instancia del procesador específico
    """
    return ProcessorFactory.create_processor(project_code, module_name, config)


def get_available_processors() -> List[str]:
    """
    Función de conveniencia para obtener procesadores disponibles.
    
    Returns:
        Lista de procesadores disponibles
    """
    return ProcessorFactory.get_available_processors() 