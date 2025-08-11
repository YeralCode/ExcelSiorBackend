"""
Transformador de columnas para archivos disciplinarios de DIAN.
Integrado con el sistema modular de configuraciones y validaciones.
"""

import csv
import os
from random import choice
from typing import Dict, List, Union, Optional, Tuple
from dataclasses import dataclass
import logging

# Importar componentes del sistema modular
from ...base.config_base import ProjectConfigBase
from ...base.values_manager import ValuesManager
from ...base.validators import ValidatorFactory
from ...factory import get_project_config
from repository.proyectos.DIAN.disciplinarios.valores_choice.departamento import VALORES_REEMPLAZO_DEPARTAMENTO, VALORES_DEPARTAMENTO
from repository.proyectos.DIAN.disciplinarios.valores_choice.ciudad import VALORES_REEMPLAZO_CIUDAD, VALORES_CIUDAD
from repository.proyectos.DIAN.disciplinarios.valores_choice.direccion_seccional import VALORES_REEMPLAZO_DIRECCION_SECCIONAL, VALORES_DIRECCION_SECCIONAL


logger = logging.getLogger(__name__)

# Constantes
NULL_VALUES = {"$null$", "nan", "NULL", "N.A", "null", "N.A."}
DELIMITER = '|'
ENCODING = 'utf-8'
TEMP_COMMA_REPLACEMENT = '\uE000'
TEMP_NEWLINE = '⏎'
TEMP_COMMA = '\uE000'

# Encabezados de referencia para DIAN disciplinarios
REFERENCE_HEADERS = [
    'NOMBRE_ARCHIVO',
    'MES_REPORTE',
    "EXPEDIENTE",
    "FECHA_RADICACION",
    "FECHA_HECHOS",
    "INDAGACION_PRELIMINAR",
    "INVESTIGACION_DISCIPLINARIA",
    "IMPLICADO",
    "IDENTIFICACION",
    "DEPARTAMENTO",
    "CIUDAD",
    "DIRECCION_SECCIONAL_O_EQUIVALENTE",
    "DEPENDENCIA",
    "PROCESO",
    "SUBPROCESO",
    "PROCEDIMIENTO",
    "CARGO",
    "ORIGEN",
    "CONDUCTA",
    "ETAPA_PROCESAL",
    "FECHA_FALLO",
    "SANCION_IMPUESTA",
    "HECHO",
    "DECISION",
    "PROCESO_AFECTADO",
    "SENALADOS_O_VINCULADOS",
    "ADECUACION_TIPICA",
    "ABOGADO",
    "SENTIDO_DEL_FALLO",
    "QUEJOSO",
    "IDENTIFICACION_QUEJOSO",
    "TIPO_DE_PROCESO",
    "FECHA_PLIEGO_DE_CARGOS",
    "FECHA_CITACION",
    "FECHA_CIERRE_DE_INVESTIGACION"
]

# Mapeo de reemplazo de columnas
REPLACEMENT_MAP = {
    # Agregar mapeos específicos si es necesario
}


@dataclass
class ErrorInfo:
    """Información de error para el procesamiento."""
    columna: str
    numero_columna: int
    tipo: str
    valor: str
    fila: int
    error: str


class DIANDisciplinariosProcessor:
    """
    Procesador específico para archivos disciplinarios de DIAN.
    Integrado con el sistema modular de configuraciones.
    """
    
    def __init__(self, config: Optional[ProjectConfigBase] = None):
        """
        Inicializa el procesador.
        
        Args:
            config: Configuración específica del proyecto (opcional)
        """
        # Obtener configuración del proyecto
        self.config = config or get_project_config('DIAN', 'disciplinarios')
        
        # Inicializar gestor de valores
        self.values_manager = ValuesManager('DIAN', 'disciplinarios')
        
        # Inicializar validadores
        self.validators = self._initialize_validators()
        
        # Mensajes de error
        self.error_messages = {
            'invalid_integer': "No es un entero válido",
            'invalid_float': "No es un flotante válido",
            'invalid_date': "No es una fecha válida",
            'invalid_datetime': "No es una fecha y hora válida",
            'invalid_nit': "No es un NIT válido",
            'invalid_departamento': "No se encuentra en departamento",
            'invalid_ciudad': "No se encuentra en ciudad",
            'invalid_direccion_seccional': "No se encuentra en direccion seccional",
            'invalid_expediente': "No es un expediente valido",
            'invalid_columns': "Número de columnas no coincide con el encabezado"
        }
        
        logger.info(f"Procesador inicializado para {self.config.project_name}")
    
    def _initialize_validators(self) -> Dict[str, any]:
        """Inicializa los validadores específicos para DIAN disciplinarios."""
        factory = ValidatorFactory()
        
        # Verificar que las variables estén disponibles
        logger.info(f"VALORES_CIUDAD disponible: {len(VALORES_CIUDAD) if 'VALORES_CIUDAD' in globals() else 'NO'}")
        logger.info(f"VALORES_REEMPLAZO_CIUDAD disponible: {len(VALORES_REEMPLAZO_CIUDAD) if 'VALORES_REEMPLAZO_CIUDAD' in globals() else 'NO'}")
        
        return {
            'integer': factory.create_validator('integer'),
            'float': factory.create_validator('float', min_value=0.0),
            'date': factory.create_validator('date'),
            'datetime': factory.create_validator('date'),
            'nit': factory.create_validator('nit'),
            'string': factory.create_validator('string', min_length=0),
            'departamento': factory.create_validator('flexible_choice', 
                                                   choices=[
'AMAZONAS',
'ANTIOQUIA',
'ANTIOQUIA',
'ANTIOQUIA',
'ARAUCA',
'ARAUCA',
'ATLANTICO',
'BOGOTA',
'BOLIVAR',
'BOYACA',
'BOYACA',
'CALDAS',
'CAQUETA',
'CASANARE',
'CAUCA',
'CESAR',
'CHOCO',
'CORDOBA',
'CUNDINAMARCA',
'GUAINIA',
'GUAVIARE',
'HUILA',
'LA GUAJIRA',
'MAGDALENA',
'META',
'NARINO',
'NORTE DE SANTANDER',
'POR DETERMINAR',
'PUTUMAYO',
'PUTUMAYO',
'QUINDIO',
'QUINDIO',
'RISARALDA',
'SAN ANDRES Y PROVIDENCIA',
'SANTANDER',
'SUCRE',
'TOLIMA',
'VALLE DEL CAUCA',
'VICHADA',
], 
                                                   replacement_map= {
    # Reemplazos de Guajira
    "GUAJIRA": "LA GUAJIRA",
    
    # Reemplazos de Norte de Santander
    "N.SANTANDER": "NORTE DE SANTANDER",
    "NORTE SANTANDER": "NORTE DE SANTANDER",
    "NSANTANDER": "NORTE DE SANTANDER",
    
    # Reemplazos de Valle del Cauca
    "VALLE": "VALLE DEL CAUCA",
    
    # Reemplazos de San Andrés y Providencia
    "SAN_ANDRES_Y_PROVIDENCIA": "SAN ANDRES Y PROVIDENCIA",
    "SAN ANDRES": "SAN ANDRES Y PROVIDENCIA",
    
    # Reemplazos de Bogotá D.C.
    "BOGOTA DC": "BOGOTA",
    "BOGOTA D.C.": "BOGOTA",
    "BOGOTÁ D.C.": "BOGOTA",
    "BOGOTÁ DC": "BOGOTA",
    "BOGOTÁ D C": "BOGOTA",
    "BOGOTÁ DISTRITO CAPITAL": "BOGOTA",
    "DISTRITO CAPITAL": "BOGOTA",
    "D.C.": "BOGOTA",
    "DC": "BOGOTA",
    "BOGOTÁ": "BOGOTA",
    
    # Reemplazos de Cundinamarca
    "CUNDINAMRCA": "CUNDINAMARCA",
    "CUNDINAMCA": "CUNDINAMARCA",
    "CUNDINAMRACA": "CUNDINAMARCA",
    "CUNDINAMARCA": "CUNDINAMARCA",  # Para casos donde ya está correcto
}),
            'ciudad': factory.create_validator('flexible_choice', 
                                             choices=[
'LETICIA',
'MEDELLIN',
'TURBO',
'URABA',
'ARAUCA',
'SARAVENA',
'BARRANQUILLA',
'BOGOTA',
'CARTAGENA',
'SOGAMOSO',
'TUNJA',
'MANIZALES',
'FLORENCIA',
'YOPAL',
'POPAYAN',
'VALLEDUPAR',
'QUIBDO',
'MONTERIA',
'GIRARDOT',
'INIRIDA',
'SAN JOSE DEL GUAVIARE',
'NEIVA',
'MAICAO',
'RIOHACHA',
'SANTA MARTA',
'VILLAVICENCIO',
'IPIALES',
'PASTO',
'TUMACO',
'CUCUTA',
'PAMPLONA',
'POR DETERMINAR',
'PUERTO ASIS',
'ARMENIA',
'LA TEBAIDA',
'PEREIRA',
'SAN ANDRES',
'BARRANCABERMEJA',
'BUCARAMANGA',
'SINCELEJO',
'BOGOTA',
'IBAGUE',
'BUENAVENTURA',
'CALI',
'PALMIRA',
'SINCELEJO',
'TULUA',
'PUERTO CARREÑO',

], 
                                             replacement_map={
    # Reemplazos de nombres de ciudades
    "MANIZALEZ": "MANIZALES",
    "BARRAQUILLA": "BARRANQUILLA",
    "SAN_JOSE": "SAN JOSE DEL GUAVIARE",
    "SANTAMARTA": "SANTA MARTA",
    "SAN_ANDRES": "SAN ANDRES",
    "SANTA_MARTA": "SANTA MARTA",
    "PUERTO_ASÍS": "PUERTO ASIS",
    
    # Reemplazos de Bogotá D.C.
    "BOGOTA D.C.": "BOGOTA",
    "BOGOTÁ D.C.": "BOGOTA",
    "BOGOTÁ DC": "BOGOTA",
    "BOGOTÁ D C": "BOGOTA",
    "BOGOTÁ DISTRITO CAPITAL": "BOGOTA",
    "DISTRITO CAPITAL": "BOGOTA",
    "D.C.": "BOGOTA",
    "DC": "BOGOTA",
    "BOGOTÁ": "BOGOTA",
}),
            'direccion_seccional': factory.create_validator('flexible_choice', 
                                                          choices= [
    'nivel central',
    'direccion seccional de impuestos y aduanas de armenia',
    'direccion seccional de impuestos de barranquilla',
    'direccion seccional de aduanas de bogota',
    'direccion seccional de impuestos y aduanas de bucaramanga',
    'direccion seccional de impuestos de cali',
    'direccion seccional de impuestos de cartagena',
    'direccion seccional de impuestos de cucuta',
    'direccion seccional de impuestos y aduanas de girardot',
    'direccion seccional de impuestos y aduanas de ibague',
    'direccion seccional de impuestos y aduanas de manizales',
    'direccion seccional de impuestos de medellin',
    'direccion seccional de impuestos y aduanas de monteria',
    'direccion seccional de impuestos y aduanas de neiva',
    'direccion seccional de impuestos y aduanas de pasto',
    'direccion seccional de impuestos y aduanas de palmira',
    'direccion seccional de impuestos y aduanas de pereira',
    'direccion seccional de impuestos y aduanas de popayan',
    'direccion seccional de impuestos y aduanas de quibdo',
    'direccion seccional de impuestos y aduanas de santa marta',
    'direccion seccional de impuestos y aduanas de tunja',
    'direccion seccional de impuestos y aduanas de tulua',
    'direccion seccional de impuestos y aduanas de villavicencio',
    'direccion seccional de impuestos y aduanas de sincelejo',
    'direccion seccional de impuestos y aduanas de valledupar',
    'direccion seccional de impuestos y aduanas de riohacha',
    'direccion seccional de impuestos y aduanas de sogamoso',
    'direccion seccional de impuestos y aduanas de san andres',
    'direccion seccional de impuestos y aduanas de florencia',
    'direccion seccional de impuestos y aduanas de barrancabermeja',
    'direccion seccional de impuestos de grandes contribuyentes',
    'direccion seccional de impuestos de bogota',
    'direccion seccional de impuestos y aduanas de arauca',
    'direccion seccional de impuestos y aduanas de buenaventura',
    'direccion seccional delegada de impuestos y aduanas de cartago',
    'direccion seccional de impuestos y aduanas de ipiales',
    'direccion seccional de impuestos y aduanas de leticia',
    'direccion seccional de impuestos y aduanas de maicao',
    'direccion seccional delegada de impuestos y aduanas de tumaco',
    'direccion seccional de impuestos y aduanas de uraba',
    'direccion seccional delegada de impuestos y aduanas de puerto carreno',
    'direccion seccional delegada de impuestos y aduanas de inirida',
    'direccion seccional de impuestos y aduanas de yopal',
    'direccion seccional delegada de impuestos y aduanas mitu',
    'direccion seccional delegada de impuestos y aduanas de puerto asis',
    'direccion seccional de aduanas de cartagena',
    'direccion seccional delegada de impuestos y aduanas de san jose de guaviare',
    'direccion seccional delegada de impuestos y aduanas de pamplona',
    'direccion seccional de aduanas de barranquilla',
    'direccion seccional de aduanas de cali',
    'direccion seccional de aduanas de cucuta',
    'direccion seccional de aduanas de medellin',
    'dirección seccional de aduanas de bogota',
    # Nuevas direcciones seccionales agregadas
    'oficina juridica',
    'gerencia seguimiento contractual',
    'gerencia seguimiento contractual, oti, gerencia financiera, gerencia servicio al cliente y gerencia administrativa y oficina juridica',
    'vicepresidencia de operaciones- gerencia de seguimiento contractual',
    'gerencia de control a las operaciones ilegales',
    'gerencia financiera',
    'vicepresidencia de operaciones',
    'vicepresidencia de desarrollo organizacional',
    'vicepresidencia desarrollo comercial',
    'gerencia fiscalizacion',
    'oficina de planeacion'

]
, 
                                                          replacement_map={
    'direccion seccional de impuestos barranquilla': 'direccion seccional de impuestos de barranquilla',
    'direccion seccional de impuestos cali': 'direccion seccional de impuestos de cali',
    'direccion seccional de impuestos cartagena': 'direccion seccional de impuestos de cartagena',
    'direccion seccional de impuestos cucuta': 'direccion seccional de impuestos de cucuta',
    'direccion seccional de impuestos medellin': 'direccion seccional de impuestos de medellin',
    'direccion seccional de impuestos grandes contribuyentes': 'direccion seccional de impuestos de grandes contribuyentes',
    'direccion seccional de impuestos bogota': 'direccion seccional de impuestos de bogota',
    'direccion seccional de impuestos y aduanas armenia': 'direccion seccional de impuestos y aduanas de armenia',
    'direccion seccional de impuestos y aduanas bucaramanga': 'direccion seccional de impuestos y aduanas de bucaramanga',
    'direccion seccional de impuestos y aduanas girardot': 'direccion seccional de impuestos y aduanas de girardot',
    'direccion seccional de impuestos y aduanas ibague': 'direccion seccional de impuestos y aduanas de ibague',
    'direccion seccional de impuestos y aduanas manizales': 'direccion seccional de impuestos y aduanas de manizales',
    'direccion seccional de impuestos y aduanas monteria': 'direccion seccional de impuestos y aduanas de monteria',
    'direccion seccional de impuestos y aduanas neiva': 'direccion seccional de impuestos y aduanas de neiva',
    'direccion seccional de impuestos y aduanas pasto': 'direccion seccional de impuestos y aduanas de pasto',
    'direccion seccional de impuestos y aduanas palmira': 'direccion seccional de impuestos y aduanas de palmira',
    'direccion seccional de impuestos y aduanas pereira': 'direccion seccional de impuestos y aduanas de pereira',
    'direccion seccional de impuestos y aduanas popayan': 'direccion seccional de impuestos y aduanas de popayan',
    'direccion seccional de impuestos y aduanas quibdo': 'direccion seccional de impuestos y aduanas de quibdo',
    'direccion seccional de impuestos y aduanas santa marta': 'direccion seccional de impuestos y aduanas de santa marta',
    'direccion seccional de impuestos y aduanas tunja': 'direccion seccional de impuestos y aduanas de tunja',
    'direccion seccional de impuestos y aduanas tulua': 'direccion seccional de impuestos y aduanas de tulua',
    'direccion seccional de impuestos y aduanas villavicencio': 'direccion seccional de impuestos y aduanas de villavicencio',
    'direccion seccional de impuestos y aduanas sincelejo': 'direccion seccional de impuestos y aduanas de sincelejo',
    'direccion seccional de impuestos y aduanas valledupar': 'direccion seccional de impuestos y aduanas de valledupar',
    'direccion seccional de impuestos y aduanas riohacha': 'direccion seccional de impuestos y aduanas de riohacha',
    'direccion seccional de impuestos y aduanas sogamoso': 'direccion seccional de impuestos y aduanas de sogamoso',
    'direccion seccional de impuestos y aduanas san andres': 'direccion seccional de impuestos y aduanas de san andres',
    'direccion seccional de impuestos y aduanas florencia': 'direccion seccional de impuestos y aduanas de florencia',
    'direccion seccional de impuestos y aduanas barrancabermeja': 'direccion seccional de impuestos y aduanas de barrancabermeja',
    'direccion seccional de impuestos y aduanas arauca': 'direccion seccional de impuestos y aduanas de arauca',
    'direccion seccional de impuestos y aduanas buenaventura': 'direccion seccional de impuestos y aduanas de buenaventura',
    'direccion seccional delegada de impuestos y aduanas cartago': 'direccion seccional delegada de impuestos y aduanas de cartago',
    'direccion seccional de impuestos y aduanas ipiales': 'direccion seccional de impuestos y aduanas de ipiales',
    'direccion seccional de impuestos y aduanas leticia': 'direccion seccional de impuestos y aduanas de leticia',
    'direccion seccional de impuestos y aduanas maicao': 'direccion seccional de impuestos y aduanas de maicao',
    'direccion seccional delegada de impuestos y aduanas tumaco': 'direccion seccional delegada de impuestos y aduanas de tumaco',
    'direccion seccional de impuestos y aduanas uraba': 'direccion seccional de impuestos y aduanas de uraba',
    'direccion seccional delegada de impuestos y aduanas puerto carreno': 'direccion seccional delegada de impuestos y aduanas de puerto carreno',
    'direccion seccional delegada de impuestos y aduanas inirida': 'direccion seccional delegada de impuestos y aduanas de inirida',
    'direccion seccional de impuestos y aduanas yopal': 'direccion seccional de impuestos y aduanas de yopal',
    'direccion seccional delegada de impuestos y aduanas puerto asis': 'direccion seccional delegada de impuestos y aduanas de puerto asis',
    'direccion seccional delegada de impuestos y aduanas san jose de guaviare': 'direccion seccional delegada de impuestos y aduanas de san jose de guaviare',
    'direccion seccional delegada de impuestos y aduanas pamplona': 'direccion seccional delegada de impuestos y aduanas de pamplona',
    'direccion seccional de aduanas bogota':'direccion seccional de aduanas de bogota',
    'direccion seccional de aduanas cartagena':'direccion seccional de aduanas de cartagena',
    'direccion seccional de aduanas barranquilla':'direccion seccional de aduanas de barranquilla',
    'direccion seccional de aduanas cali':'direccion seccional de aduanas de cali',
    'direccion seccional de aduanas cucuta':'direccion seccional de aduanas de cucuta',
    'direccion seccional de aduanas medellin':'direccion seccional de aduanas de medellin',
    'dreccion seccional de impuestos de cali': 'direccion seccional de aduanas de cali',
    'direccion seccional de impuestos de neiva': 'direccion seccional de impuestos y aduanas de neiva',
    'direccion seccional de impuestos y  aduanas de maicao': 'direccion seccional de impuestos y aduanas de maicao',
    'direccion seccional de impuestos y aduanas de sicelejo': 'direccion seccional de impuestos y aduanas de sincelejo',
    'direccion seccional de impuestos y aduanas de bucaramnaga': 'direccion seccional de impuestos y aduanas de bucaramanga',
    'direccion seccional de impuestos de barrabquilla':'direccion seccional de impuestos de barranquilla',
    'direccion seccional de impuestos grandes cuntribuyentes':'direccion seccional de impuestos de grandes contribuyentes',
    'direccion seccional de impuestos de arauca':'direccion seccional de impuestos y aduanas de arauca',
    'direccion seccional de impuestos y aduanas de bucamaranga': 'direccion seccional de impuestos y aduanas de bucaramanga',
    'direccion seccional de aduanas de maicao':'direccion seccional de impuestos y aduanas de maicao',
    'direccion seccional de grandes contribuyentes': 'direccion seccional de impuestos de grandes contribuyentes',
    'gerencia de control, a las operaciones ilegales': 'gerencia de control a las operaciones ilegales',
    'gerencia control a las operaciones ilegales': 'gerencia de control a las operaciones ilegales',
    'gerencia de cobro/gerencia de control las operaciones ilegales': 'gerencia de control a las operaciones ilegales',
    'gerencia de operaciones ilegales': 'gerencia de control a las operaciones ilegales',
    'oficina asesora de planeacion': 'oficina de planeacion',
}   ),
            'expediente': factory.create_validator('string', min_length=1, max_length=50),
            "cadena_sin_caracteres_especiales": factory.create_validator('string', min_length=1, max_length=50)
        }
    
    def _get_departamento_validator(self):
        """Obtiene el validador para departamentos."""
        try:
            departamentos = self.values_manager.get_all_values('departamento')
            logger.info(f"Valores cargados de BD para departamento: {len(departamentos)}")
        except Exception as e:
            logger.warning(f"No se pudieron cargar valores de departamento: {e}")
            # Valores por defecto
            default_departamentos = [
                "ANTIOQUIA", "ATLANTICO", "BOGOTA", "BOLIVAR", "BOYACA", "CALDAS", 
                "CAQUETA", "CAUCA", "CESAR", "CORDOBA", "CUNDINAMARCA", "CHOCO", # Corrected Cundinamarca
                "HUILA", "LA GUAJIRA", "MAGDALENA", "META", "NARIÑO", "NORTE DE SANTANDER", 
                "QUINDIO", "RISARALDA", "SANTANDER", "SUCRE", "TOLIMA", "VALLE DEL CAUCA", 
                "VAUPES", "VICHADA", "AMAZONAS", "GUAINIA", "GUAVIARE", "PUTUMAYO", 
                "SAN ANDRES Y PROVIDENCIA", "ARAUCA", "CASANARE"
            ]
            departamentos = default_departamentos
        
        # Importar el diccionario de reemplazos
        try:
            from repository.proyectos.DIAN.disciplinarios.valores_choice.departamento import VALORES_REEMPLAZO_DEPARTAMENTO
            replacement_map = VALORES_REEMPLAZO_DEPARTAMENTO
            logger.info(f"Diccionario de reemplazos de departamento cargado: {len(replacement_map)} entradas")
        except ImportError:
            logger.warning("No se pudo cargar el diccionario de reemplazos de departamento")
            replacement_map = {}
        
        from repository.proyectos.base.validators import create_location_validator_with_replacements
        return create_location_validator_with_replacements(departamentos, "DepartamentoValidator", replacement_map)

    def _get_ciudad_validator(self):
        """Obtiene el validador para ciudades."""
        # Valores por defecto que incluyen BOGOTA
        default_ciudades = [
            "MEDELLIN", "BARRANQUILLA", "BOGOTA", "CARTAGENA", "TUNJA", "MANIZALES",
            "FLORENCIA", "POPAYAN", "VALLEDUPAR", "MONTERIA", "BUCARAMANGA", "QUIBDO",
            "NEIVA", "RIOHACHA", "SANTA MARTA", "VILLAVICENCIO", "PASTO", "CUCUTA",
            "ARMENIA", "PEREIRA", "IBAGUE", "CALI", "MITU", "PUERTO CARREÑO", "LETICIA",
            "INIRIDA", "SAN JOSE DEL GUAVIARE", "MOCOA", "SAN ANDRES", "ARAUCA", "YOPAL"
        ]
        
        try:
            ciudades_db = self.values_manager.get_all_values('ciudad')
            logger.info(f"Valores cargados de BD para ciudad: {len(ciudades_db)}")
            # Combinar valores de BD con valores por defecto
            all_ciudades = list(set(ciudades_db + default_ciudades))
        except Exception as e:
            logger.warning(f"No se pudieron cargar valores de ciudad: {e}")
            all_ciudades = default_ciudades
        
        # Importar el diccionario de reemplazos
        try:
            from repository.proyectos.DIAN.disciplinarios.valores_choice.ciudad import VALORES_REEMPLAZO_CIUDAD
            replacement_map = VALORES_REEMPLAZO_CIUDAD
            logger.info(f"Diccionario de reemplazos de ciudad cargado: {len(replacement_map)} entradas")
        except ImportError:
            logger.warning("No se pudo cargar el diccionario de reemplazos de ciudad")
            replacement_map = {}
        
        from repository.proyectos.base.validators import create_location_validator_with_replacements
        return create_location_validator_with_replacements(all_ciudades, "CiudadValidator", replacement_map)
    
    def _get_direccion_seccional_validator(self):
        """Obtiene el validador para direcciones seccionales."""
        try:
            direcciones_db = self.values_manager.get_all_values('direccion_seccional')
            logger.info(f"Valores cargados de BD para direccion_seccional: {len(direcciones_db)}")
        except Exception as e:
            logger.warning(f"No se pudieron cargar valores de direccion_seccional de BD: {e}")
            direcciones_db = []
        
        # Valores por defecto que incluyen las nuevas direcciones seccionales
        default_direcciones = [
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
            'direccion seccional de impuestos de bogota',
            # Nuevas direcciones seccionales agregadas
            'oficina juridica',
            'gerencia seguimiento contractual',
            'gerencia seguimiento contractual, oti, gerencia financiera, gerencia servicio al cliente y gerencia administrativa y oficina juridica',
            'vicepresidencia de operaciones- gerencia de seguimiento contractual',
            'gerencia de control, a las operaciones ilegales',
            'gerencia de control a las operaciones ilegales',
            'gerencia financiera',
            'gerencia de cobro/gerencia de control las operaciones ilegales',
            'vicepresidencia de operaciones',
            'gerencia de operaciones ilegales',
            'vicepresidencia de desarrollo organizacional',
            'vicepresidencia desarrollo comercial',
            'por establecer',
            'gerencia fiscalizacion',
            'oficina asesora de planeacion',
            'gerencia control a las operaciones ilegales',
            'oficina de planeacion'
        ]
        
        # Combinar valores de BD con valores por defecto
        all_direcciones = list(set(direcciones_db + default_direcciones))
        logger.info(f"Total de direcciones seccionales disponibles: {len(all_direcciones)}")
        
        # Importar el diccionario de reemplazos
        try:
            from repository.proyectos.DIAN.disciplinarios.valores_choice.direccion_seccional import VALORES_REEMPLAZO_DIRECCION_SECCIONAL
            replacement_map = VALORES_REEMPLAZO_DIRECCION_SECCIONAL
            logger.info(f"Diccionario de reemplazos cargado: {len(replacement_map)} entradas")
        except ImportError:
            logger.warning("No se pudo cargar el diccionario de reemplazos de dirección seccional")
            replacement_map = {}
        
        from repository.proyectos.base.validators import create_location_validator_with_replacements
        return create_location_validator_with_replacements(all_direcciones, "DireccionSeccionalValidator", replacement_map)
    
    def normalize_column_name(self, column_name: str) -> str:
        """Normaliza nombres de columnas reemplazando espacios y caracteres especiales."""
        column_name = column_name.strip().upper()
        replacements = [
            (' ', '_'), ('-', '_'), ('Á', 'A'), ('É', 'E'), ('Í', 'I'),
            ('Ó', 'O'), ('Ú', 'U'), ('Ñ', 'N'), ('.', '')
        ]
        for old, new in replacements:
            column_name = column_name.replace(old, new)
        return column_name
    
    def organize_headers(self, actual_headers: List[str]) -> List[str]:
        """Organiza headers según REFERENCE_HEADERS y aplica reemplazos."""
        normalized = [self.normalize_column_name(h) for h in actual_headers]
        
        # Aplicar reemplazos
        for i, header in enumerate(normalized):
            normalized[i] = REPLACEMENT_MAP.get(header, header)
        
        # Eliminar duplicados manteniendo orden
        seen = set()
        unique_headers = []
        for h in normalized:
            if h not in seen:
                seen.add(h)
                unique_headers.append(h)

        # Ordenar según REFERENCE_HEADERS
        ref_headers_normalized = [self.normalize_column_name(h) for h in REFERENCE_HEADERS]
        ordered = []
        remaining = []
        
        for ref_h in ref_headers_normalized:
            if ref_h in unique_headers:
                ordered.append(ref_h)
        remaining = [h for h in unique_headers if h not in ordered]
        return ordered + remaining
    
    def clean_value(self, value: str) -> str:
        """Limpia valores nulos y espacios."""
        if value is None:
            return ""
        value = str(value).strip()
        return "" if value.upper() in NULL_VALUES else value
    
    def preprocess_line(self, line: str) -> str:
        """Preprocesa línea para manejar comas y saltos internos."""
        if not line.strip():
            return line
            
        line = line.replace('\\n', TEMP_NEWLINE)
        in_quotes = False
        processed = []
        
        for char in line:
            if char == '"':
                in_quotes = not in_quotes
                processed.append(char)
            elif char == ',' and not in_quotes:
                processed.append(TEMP_COMMA)
            else:
                processed.append(char)
        
        return ''.join(processed)
    
    def postprocess_field(self, field: str) -> str:
        """Restaura caracteres especiales a su forma original."""
        return field.replace(TEMP_COMMA, ',').replace(TEMP_NEWLINE, '\n')
    
    def read_csv(self, input_file: str) -> Tuple[List[str], List[List[str]]]:
        """Lee CSV con manejo de comas y saltos internos."""
        with open(input_file, 'r', encoding=ENCODING) as f:
            processed_content = [self.preprocess_line(line) for line in f.read().splitlines()]
            reader = csv.reader(
                processed_content,
                delimiter=DELIMITER,
                quotechar='"',
                escapechar='\\'
            )
            
            data = [row for row in reader]
            return data[0], data[1:] if len(data) > 1 else []
    
    def process_csv(self, input_file: str, output_file: str, error_file: str = None, 
                   type_mapping: Dict[str, List[int]] = None) -> None:
        """
        Procesa CSV completo con:
        - Normalización de headers
        - Validación de datos usando el sistema modular
        - Manejo de errores
        """
        try:
            logger.info(f"Iniciando procesamiento de {input_file}")
            
            header, rows = self.read_csv(input_file)
            normalized_header = self.organize_headers(header)
            
            errors = []
            processed_rows = []
            
            for row_num, row in enumerate(rows, start=1):
                try:
                    if len(row) != len(header):
                        raise ValueError(f"Columnas esperadas: {len(header)}, obtenidas: {len(row)}")
                    
                    processed_row = []
                    for col_num, (raw_val, col_name) in enumerate(zip(row, header), start=1):
                        value = self.postprocess_field(raw_val)
                        clean_val = self.clean_value(value)
                        
                        # Validación usando el sistema modular
                        if type_mapping:
                            clean_val, error = self._validate_value_modular(
                                clean_val, col_name, col_num, row_num, type_mapping
                            )
                            if error:
                                errors.append(error)
                        
                        processed_row.append(clean_val)
                    
                    # Reorganizar según headers normalizados
                    final_row = self._reorganize_row(processed_row, header, normalized_header)
                    processed_rows.append(final_row)
                
                except Exception as e:
                    errors.append(ErrorInfo(
                        columna="", numero_columna=0, tipo="processing",
                        valor=str(row), fila=row_num, error=str(e)
                    ))
            
            self._save_output(output_file, normalized_header, processed_rows)
            if errors and error_file:
                self._save_errors(error_file, errors)
            
            logger.info(f"Procesamiento completado. Filas procesadas: {len(processed_rows)}, Errores: {len(errors)}")
            
        except Exception as e:
            logger.error(f"Error procesando archivo: {str(e)}")
            raise Exception(f"Error procesando archivo: {str(e)}")
    
    def _validate_value_modular(self, value: str, col_name: str, col_num: int, 
                               row_num: int, type_mapping: Dict[str, List[int]]) -> Tuple[str, Optional[ErrorInfo]]:
        """Valida un valor usando el sistema modular de validadores."""
        if not value:
            return value, None
        
        # Determinar el tipo esperado
        expected_type = self._get_expected_type(col_name, type_mapping)
        try:
            if expected_type in self.validators:
                validator = self.validators[expected_type]
                if not validator.is_valid(value):
                    error_msg = self.error_messages.get(f'invalid_{expected_type}', f"Valor inválido para tipo {expected_type}")
                    error = ErrorInfo(
                        columna=col_name, numero_columna=col_num,
                        tipo=expected_type, valor=value, fila=row_num,
                        error=error_msg
                    )
                    return value, error
            
            return value, None
            
        except Exception as e:
            error = ErrorInfo(
                columna=col_name, numero_columna=col_num,
                tipo=expected_type, valor=value, fila=row_num,
                error=str(e)
            )
            return value, error
    
    def _get_expected_type(self, col_name: str, type_mapping: Dict[str, List[int]]) -> str:
        """Obtiene el tipo esperado para una columna."""
        for type_name, columns in type_mapping.items():
            if col_name in columns:
                return type_name
        return "string"
    
    def _reorganize_row(self, row: List[str], original_headers: List[str], 
                       final_headers: List[str]) -> List[str]:
        """Reorganiza una fila según los headers finales."""
        header_map = {self.normalize_column_name(h): i for i, h in enumerate(original_headers)}
        final_row = []
        for header in final_headers:
            norm_header = self.normalize_column_name(header)
            if norm_header in header_map:
                final_row.append(row[header_map[norm_header]])
            else:
                # Buscar posibles mapeos alternativos
                for orig, replacement in REPLACEMENT_MAP.items():
                    if replacement == header and orig in header_map:
                        final_row.append(row[header_map[orig]])
                        break
                    else:
                        final_row.append("")

        return final_row
    
    def _save_output(self, file_path: str, header: List[str], data: List[List[str]]) -> None:
        """Guarda datos procesados en CSV."""
        with open(file_path, 'w', newline='', encoding=ENCODING) as f:
            writer = csv.writer(f, delimiter=DELIMITER)
            writer.writerow(header)
            writer.writerows(data)
    
    def _save_errors(self, file_path: str, errors: List[ErrorInfo]) -> None:
        """Guarda errores en CSV."""
        if errors:
            with open(file_path, 'w', newline='', encoding=ENCODING) as f:
                writer = csv.DictWriter(f, fieldnames=errors[0].__dict__.keys())
                writer.writeheader()
                writer.writerows([e.__dict__ for e in errors])


# Clase de compatibilidad para mantener la interfaz existente
class CSVProcessor(DIANDisciplinariosProcessor):
    """
    Clase de compatibilidad que mantiene la interfaz original.
    Hereda de DIANDisciplinariosProcessor para usar el nuevo sistema modular.
    """
    
    def __init__(self, validator=None):
        """
        Inicializa el procesador manteniendo compatibilidad con el código existente.
        
        Args:
            validator: Validador legacy (ignorado, usa el sistema modular)
        """
        super().__init__()
        logger.info("Usando CSVProcessor con sistema modular integrado")


# Ejemplo de uso
if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    
    # Crear procesador
    processor = DIANDisciplinariosProcessor()
    
    # Mapeo de tipos para DIAN disciplinarios
    type_mapping = {
        "int": [],
        "float": [],
        "date": [4, 5, 7],
        "datetime": [],
        "str": [
            1, 2, 8, 6, 13, 14, 16, 17, 18, 19, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 33, 32, 34, 35, 36, 37, 38, 39, 40, 41, 42,
        ],
        "str-sin-caracteres-especiales": [15],
        "nit": [9],
        "choice_departamento": [10],
        "choice_ciudad": [11],
        "choice_direccion_seccional": [12],
        "expediente": [3],
    }
    
    # Rutas de archivos
    base_path = os.path.expanduser("~/Documentos/ITRC/DOCUMENTOS_LIMPIAR/DIAN_DISCIPLINARIOS/2024/CSV/")
    input_file = os.path.join(base_path, "consolidado_dian_disciplinarios_2024.csv")
    output_file = os.path.join(base_path, "consolidado_dian_disciplinarios_2024_procesado.csv")
    error_file = os.path.join(base_path, "consolidado_dian_disciplinarios_2024_errores_procesamiento.csv")
    
    # Procesar archivo
    processor.process_csv(input_file, output_file, error_file, type_mapping)