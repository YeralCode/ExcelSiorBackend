"""
Configuración del procesador para BPM
Basado en la estructura de datos proporcionada
"""

from ..base.config_base import ProjectConfigBase
from typing import Dict, Any, List

class BPMConfig(ProjectConfigBase):
    """Configuración específica para BPM"""
    
    def __init__(self, module_path: str = ""):
        """Inicializar configuración de BPM"""
        super().__init__("BPM", module_path)
        
        # Configuración de tipos de datos para BPM
        self.type_mapping = {
            "string": [
                "NOMBRE_ARCHIVO",
                "TIPO_EXPEDIENTE",
                "EXPEDIENTE_(ANTIGUO)",
                "ID_EXPEDIENTE_ECM",
                "TIPO_DOC_IDENTIFICACION_APORTANTE",
                "NOMBRES_Y_O_RAZON_SOCIAL_APORTANTE",
                "TIPO_APORTANTE",
                "DIRECCION_RUT",
                "TELEFONO",
                "EMAIL",
                "NOMBRES_Y_APELLIDOS_REP_LEGAL",
                "TELEFONO_REP_LEGAL",
                "#_RADICADO_UGPP",
                "NOMBRE_REMITENTE",
                "#_RAD_REMITENTE",
                "HALLAZGO___DENUNCIA",
                "ANO_PROGRAMA",
                "INDICIO_NOV_2015",
                "NO_RQI",
                "OBSERVACIONES_AL_RDOC",
                "#_AMPLIACION_RDOC",
                "FORMA_DE_NOTIFICACION_AMPLIACION_RDOC_(FINAL_EXTREMA)",
                "OBSERVACIONES_A_LA_AMPLIACION",
                "ETAPA",
                "#_AUTO_DE_ARCHIVO",
                "FECHA_ENTREGA_AA",
                "OBSERVACIONES_AL_AA",
                "#_LO",
                "OBSERVACION_A_LA_NOTIFICACION",
                "CAMBIOS_DESPUES_DEL_CIERRE",
                "TIPO_DE_PROCESO_CONCURSAL",
                "NO_MEMORANDO_ASIGNACION_CARTERA_CONTINGENTE",
                "#_DE_MEMORANDO_ENVIO",
                "#_MEMORANDO_DEVOLUCION",
                "TIENE_RECURSO?",
                "RADICADO_RECURSO",
                "#_RDC_FALLO_RECURSO_RECONSIDERACION",
                "DECISION_DEL_RECURSO",
                "#_RESOLUCION_REVOCATORIA_DIRECTA",
                "MIGRADO_SI_NO",
                "OBSERVACIONES_A_LA_MIGRACION_BPM",
                "OBS_A_LA_NOTIFICACION"
            ],
            "date": [
                "MES_REPORTE",
                "FECHA_REPARTO",
                "FECHA_NACIMIENTO___CONSTITUCION_EMPRESA",
                "FECHA_RAD_UGPP",
                "FECHA_RAD_REMITENTE",
                "FECHA_INICIO_FISCALIZACION",
                "FECHA_FIN_FISCALIZACION",
                "FECHA_REVIVIDO",
                "FECHA_TERMINADO_BD",
                "F_TERMINADO",
                "FECHA_DE_EXPEDICION_RQI",
                "FECHA_NOTIFICACION_RQI",
                "FECHA_RDOC",
                "FECHA_FINAL_EXTREMA_NOTIFICACION_RDOC",
                "FECHA_EJECUTORIA_RDOC\n(CALCULADA_CON_FECHA_FINAL_EXTREMA_DE_NOT)",
                "FECHA_CM",
                "FECHA_AMPLIACION_RDOC",
                "FECHA_FINAL_EXTREMA_NOTIFICACION_AMPLIACION_RDOC",
                "FECHA_EJECUTORIA_AMPLIACION_RDOC_(CALCULADA_CON_FECHA_FINAL_EXTREMA_DE_NOT)",
                "FECHA_AUTO_DE_ARCHIVO",
                "FECHA_LO",
                "FECHA_FINAL_EXTREMA_NOT_LO",
                "FECHA_EJECUTORIA_LO_(CALCULADA_CON_FECHA_FINAL_EXTREMA_DE_NOT)",
                "FECHA_DE_NOT_DE_INSP_TRIBUTARIA_EN_ETAPA_LIQUIDACION",
                "FECHA_CONCURSAL",
                "FECHA_MEMORANDO_ASIGNACION_CARTERA_CONTINGENTE",
                "FECHA_ENVIO_A_COBRO_LO",
                "FECHA_RECIBO_COBRO_LO",
                "FECHA_DEVOLUCION_COBRO",
                "FECHA_REENVIO_A_COBRO",
                "FECHA_DE_RADICADO_RECURSO",
                "FECHA_FALLO_RECURSO",
                "FECHA_NOT_FALLO_RECURSO",
                "FECHA_RESOLUCION_REVOCATORIA",
                "FECHA_NOT_REVOCATORIA_DIRECTA",
                "OBSERVACIONES_DEL_EXPEDIENTE",
                "FECHA_SUSPENDIDO_BPM",
                "FECHA_INFORME",
                "FECHA_ENTREGA"
            ],
            "integer": [
                "ORDEN",
                "ANO_REPARTO",
                "ANO_GESTION",
                "#_EMPLEADOS",
                "VALIDA_FECHA_REVIVIDO",
                "VALIDA_FECHA_TERMINADO_BD",
                "VALIDA_FECHA_REPARTO",
                "RADICADO_RQI",
                "#_RDOC",
                "ANO_RDOC",
                "VALOR_RDOC",
                "SANCIONES_POR_OMISION_RDOC",
                "SANCIONES_POR_INEXACTITUD_RDOC",
                "SANCIONES_POR_MORA_RDOC",
                "MONTOS_CALCULADOS_PARTIDAS_GLOBALES_RDOC",
                "ANO_NOTIFICACION_RDOC",
                "VALIDA_FECHA_RDOC",
                "VALOR_CM",
                "SANCIONES_CM",
                "VALOR_CM_\"2DO_PERSUASIVO\"",
                "VALIDA_FECHA_CM",
                "ANO_AMPLIACION_RDOC",
                "VALOR_AMPLIACION_RDOC",
                "SANCIONES_POR_OMISION_AMPLIACION_RDOC",
                "SANCIONES_POR_INEXACTITUD__AMPLIACION_RDOC",
                "SANCIONES_POR_MORA__AMPLIACION_RDOC",
                "MONTOS_CALCULADOS_PARTIDAS_GLOBALES__AMPLIACION_RDOC",
                "ANO_NOTIFICACION_AMPLIACION_RDOC",
                "VALIDA_FECHA_AMPLIACION",
                "NO_DE_RADICADO_AA",
                "VALIDA_FECHA_AA",
                "ANO_LO",
                "VALOR_LO",
                "SANCIONES_POR_OMISION_LIQUIDACION_OFICIAL",
                "SANCIONES_POR_INEXACTITUD__LIQUIDACION_OFICIAL",
                "SANCIONES_POR_MORA__LIQUIDACION_OFICIAL",
                "MONTOS_CALCULADOS_PARTIDAS_GLOBALES_LIQUIDACION_OFICIAL",
                "ANO_NOT_LO",
                "VALIDA_FECHA_LO",
                "#_MEMORANDO_REENVIO",
                "ANO_FALLO_RECURSO",
                "$_VALOR_FINAL_LO_O_RS_EN_FIRME",
                "$VALOR_FINAL_SANCION_POR_OMISION_FALLO",
                "$VALOR_FINAL_SANCION_POR_INEXACTITUD_FALLO",
                "$VALOR_FINAL_SANCION_POR_MORA_FALLO",
                "ANO_NOT_FALLO_RECURSO",
                "ANO_RESOLUCION_REVOCATORIA",
                "$_VALOR_FINAL_LO_O_RS_DE_LA_REVOCATORIA",
                "VALOR_FINAL_SANCION_POR_OMISION_REVOCATORIA",
                "$VALOR_FINAL_SANCION_POR_INEXACTITUD_REVOCATORIA",
                "$VALOR_FINAL_SANCION_POR_MORA_REVOCATORIA",
                "ANO_NOT_REVOCATORIA_DIRECTA",
                "SANCIONES_POR_OMISION",
                "SANCIONES_POR_INEXACTITUD",
                "SANCIONES_POR_MORA",
                "MONTOS_CALCULADOS_PARTIDAS_GLOBALES",
                "SANCIONES_POR_OMISION1",
                "SANCIONES_POR_INEXACTITUD1",
                "SANCIONES_POR_MORA1",
                "MONTOS_CALCULADOS_PARTIDAS_GLOBALES1",
                "SANCIONES_POR_OMISION2",
                "SANCIONES_POR_INEXACTITUD2",
                "SANCIONES_POR_MORA2",
                "MONTOS_CALCULADOS_PARTIDAS_GLOBALES2",
                "$VALOR_FINAL_SANCION_POR_OMISION",
                "$VALOR_FINAL_SANCION_POR_INEXACTITUD",
                "$VALOR_FINAL_SANCION_POR_MORA",
                "VALOR_FINAL_SANCION_POR_OMISION",
                "$VALOR_FINAL_SANCION_POR_INEXACTITUD1",
                "$VALOR_FINAL_SANCION_POR_MORA1"
            ],
            "nit": [
                "NO_CC_O_NIT_APORTANTE",
                "CC_O_NIT_REP_LEGAL",
                "CC_O_NIT_DENUNCIANTE"
            ],
            "TAMANO": [
                "TAMANO"
            ],
            "MUNICIPIO_RUT": [
                "MUNICIPIO_RUT"
            ],
            "DPTO_RUT": [
                "DPTO_RUT"
            ],
            "FORMA_DE_NOTIFICACION_RDOC_(FINAL_EXTREMA)": [
                "FORMA_DE_NOTIFICACION_RDOC_(FINAL_EXTREMA)"
            ],
            "DECISION_DE_LA_REVOCATORIA_DIRECTA(FINAL_EXTREMA)": [
                "DECISION_DE_LA_REVOCATORIA_DIRECTA"
            ],
            "FORMA_DE_NOTIFICACION_REVOCATORIA_DIRECTA": [
                "FORMA_DE_NOTIFICACION_REVOCATORIA_DIRECTA"
            ],
            "TAREA_\nESPERA_BPM": [
                "TAREA_\nESPERA_BPM"
            ],
            "Denunciante_nombres_y_apellidos_y_o_razon_social": [
                "DENUNCIANTE___NOMBRES_Y_APELLIDOS_Y_O_RAZON_SOCIAL"
            ],
            "Programa": [
                "PROGRAMA"
            ],
            "Nombre_actividad_CIIU": [
                "NOMBRE_ACTIVIDAD_CIIU"
            ],
            "Nombre_sección_CIIU": [
                "NOMBRE_SECCION_CIIU"
            ],
            "Causa_terminado": [
                "CAUSA_TERMINADO"
            ],
            "Estado": [
                "ESTADO"
            ],
            "Obs_a_la_Notificacion_RDOC": [
                "FORMA_DE_NOTIFICACION_RQI",
                "OBS_A_LA_NOTIFICACION_RDOC"
            ],
            "Estado_CM": [
                "ESTADO_CM"
            ],
            "Causa_terminado_auto_de_archivo": [
                "CAUSA_TERMINADO_AUTO_DE_ARCHIVO"
            ],
            "Forma_de_comunicacion_AA": [
                "FORMA_DE_COMUNICACION_AA"
            ],
            "Forma_de_notificacion_LO_Final_extrema": [
                "FORMA_DE_NOTIFICACION_LO_(FINAL_EXTREMA)"
            ],
            "area_que_informa_proceso": [
                "AREA_QUE_INFORMA_PROCESO"
            ],
            "Causal_devolucion": [
                "CAUSAL_DEVOLUCION"
            ],
            "Recuso_admitido": [
                "RECUSO_ADMITIDO?"
            ],
            "Forma_de_notificacion_fallo_recurso": [
                "FORMA_DE_NOTIFICACION_FALLO_RECURSO"
            ],
            "Etapa_con_la_que_migro_BPM": [
                "ETAPA_CON_LA_QUE_MIGRO_BPM"
            ],
            "Motivo_suspension": [
                "MOTIVO_SUSPENSION"
            ],
            "Etapa_suspension": [
                "ETAPA_SUSPENSION"
            ]
        }
        
        # Configuración de validadores para BPM
        self.validators = {
            "date": {
                "description": "Validación de fechas en formato DD/MM/YYYY",
                "pattern": r"^\d{2}/\d{2}/\d{4}$",
                "example": "25/12/2023"
            },
            "string": {
                "description": "Validación de texto libre",
                "pattern": r".*",
                "example": "Texto de ejemplo"
            },
            "integer": {
                "description": "Validación de números enteros",
                "pattern": r"^\d+$",
                "example": "12345"
            },
            "telefono": {
                "description": "Validación de números telefónicos y NIT",
                "pattern": r"^[\d\-\(\)\s]+$",
                "example": "3001234567"
            },
            "email": {
                "description": "Validación de correos electrónicos",
                "pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
                "example": "usuario@empresa.com"
            },
            "boolean": {
                "description": "Validación de valores booleanos",
                "pattern": r"^(SI|NO|VERDADERO|FALSO|TRUE|FALSE|1|0)$",
                "example": "SI"
            }
        }
        
        # Configuración de transformaciones específicas para BPM
        self.transformations = {
            "date": {
                "description": "Convertir fechas a formato DD/MM/YYYY",
                "function": "convert_to_date"
            },
            "string": {
                "description": "Limpiar y normalizar texto",
                "function": "clean_string"
            },
            "integer": {
                "description": "Convertir a números enteros",
                "function": "convert_to_integer"
            },
            "telefono": {
                "description": "Formatear números telefónicos y NIT",
                "function": "format_phone_nit"
            },
            "email": {
                "description": "Validar y limpiar correos electrónicos",
                "function": "clean_email"
            },
            "boolean": {
                "description": "Convertir a valores booleanos estándar",
                "function": "convert_to_boolean"
            }
        }
        
        # Configuración de columnas de referencia para BPM
        self.reference_headers = [
            "ORDEN",
            "EXPEDIENTE_(ANTIGUO)",
            "TIPO_EXPEDIENTE",
            "ID_EXPEDIENTE_ECM",
            "NOMBRE_ARCHIVO",
            "MES_REPORTE",
            "FECHA_REPARTO",
            "ANO_REPARTO",
            "ANO_GESTION",
            "TIPO_DOC_IDENTIFICACION_APORTANTE",
            "NO_CC_O_NIT_APORTANTE",
            "NOMBRES_Y_O_RAZON_SOCIAL_APORTANTE",
            "TIPO_APORTANTE",
            "TAMANO",
            "#_EMPLEADOS",
            "DIRECCION_RUT",
            "MUNICIPIO_RUT",
            "DPTO_RUT",
            "TELEFONO",
            "EMAIL",
            "NOMBRES_Y_APELLIDOS_REP_LEGAL",
            "CC_O_NIT_REP_LEGAL",
            "TELEFONO_REP_LEGAL",
            "NOMBRE_REMITENTE",
            "DENUNCIANTE___NOMBRES_Y_APELLIDOS_Y_O_RAZON_SOCIAL",
            "CC_O_NIT_DENUNCIANTE",
            "HALLAZGO___DENUNCIA",
            "PROGRAMA",
            "ANO_PROGRAMA",
            "NOMBRE_ACTIVIDAD_CIIU",
            "NOMBRE_SECCION_CIIU",
            "ESTADO"
        ]
        
        # Configuración de mapeo de tipos de datos
        self.type_mapping_config = {
            "default_type": "string",
            "auto_detect": True,
            "strict_validation": False,
            "allow_unknown_columns": True
        }
        
        # Configuración de logging para BPM
        self.logging_config = {
            "level": "INFO",
            "format": "%(asctime)s - BPM_PROCESSOR - %(levelname)s - %(message)s",
            "file": "bpm_processor.log"
        }
        
        # Configuración de procesamiento para BPM
        self.processing_config = {
            "batch_size": 1000,
            "max_workers": 4,
            "timeout": 300,
            "retry_attempts": 3,
            "cleanup_temp_files": True
        }
    
    def get_type_mapping(self) -> Dict[str, List[str]]:
        """Obtiene el mapeo de tipos de datos"""
        return self.type_mapping
    
    def get_validators(self) -> Dict[str, Dict[str, Any]]:
        """Obtiene la configuración de validadores"""
        return self.validators
    
    def get_transformations(self) -> Dict[str, Dict[str, Any]]:
        """Obtiene la configuración de transformaciones"""
        return self.transformations
    
    def get_reference_headers(self) -> List[str]:
        """Obtiene las columnas de referencia"""
        return self.reference_headers
    
    def get_type_mapping_config(self) -> Dict[str, Any]:
        """Obtiene la configuración del mapeo de tipos"""
        return self.type_mapping_config
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Obtiene la configuración de logging"""
        return self.logging_config
    
    def get_processing_config(self) -> Dict[str, Any]:
        """Obtiene la configuración de procesamiento"""
        return self.processing_config
    
    def validate_column_type(self, column_name: str, data_type: str) -> bool:
        """
        Valida si una columna puede tener un tipo de dato específico
        
        Args:
            column_name: Nombre de la columna
            data_type: Tipo de dato a validar
            
        Returns:
            bool: True si es válido, False en caso contrario
        """
        if data_type not in self.type_mapping:
            return False
        
        return column_name in self.type_mapping[data_type]
    
    def get_column_type(self, column_name: str) -> str:
        """
        Obtiene el tipo de dato asignado a una columna
        
        Args:
            column_name: Nombre de la columna
            
        Returns:
            str: Tipo de dato de la columna o 'string' por defecto
        """
        for data_type, columns in self.type_mapping.items():
            if column_name in columns:
                return data_type
        
        return "string"  # Tipo por defecto
    
    def get_processor_info(self) -> Dict[str, Any]:
        """
        Obtiene información del procesador
        
        Returns:
            Dict: Información del procesador
        """
        return {
            "name": "BPM Processor",
            "version": "1.0.0",
            "description": "Procesador especializado para archivos BPM",
            "supported_types": list(self.type_mapping.keys()),
            "total_columns": sum(len(cols) for cols in self.type_mapping.values()),
            "reference_headers": len(self.reference_headers),
            "config": self.processing_config
        } 