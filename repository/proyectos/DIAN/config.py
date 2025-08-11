"""
Configuración específica para el proyecto DIAN.
Extiende la configuración base con valores específicos de DIAN.
"""

from typing import Dict, List, Any
from pathlib import Path
from ..base.config_base import ProjectConfigBase
from ..base.values_manager import ValuesManager
from ..base.validators import ValidatorFactory


class DIANConfig(ProjectConfigBase):
    """
    Configuración específica para el proyecto DIAN.
    Define las configuraciones, columnas y validadores específicos de DIAN.
    """
    
    def __init__(self, module_path: str = ""):
        super().__init__(
            project_name="DIAN - Dirección de Impuestos y Aduanas Nacionales",
            project_code="DIAN",
            description="Procesamiento de datos de la DIAN para diferentes módulos"
        )
        self.module_path = module_path
        self.values_manager = ValuesManager("DIAN", module_path)
    
    def get_required_columns(self) -> List[str]:
        """Retorna las columnas requeridas para DIAN."""
        base_columns = [

        ]
        
        # Agregar columnas específicas según el módulo
        if "notificaciones" in self.module_path:
            base_columns.extend([
                "PLAN_IDENTIF_ACTO",
                "CODIGO_ADMINISTRACION", 
                "CODIGO_DEPENDENCIA",
                "ANO_CALENDARIO",
                "CODIGO_ACTO",
                "ANO_ACTO",
                "CONSECUTIVO_ACTO",
                "FECHA_ACTO",
                "CUANTIA_ACTO",
                "NIT",
                "RAZON_SOCIAL",
                "PLANILLA_REMISION",
                "FECHA_PLANILLA_REMISION",
                "FECHA_CITACION",
                "FECHA_NOTIFICACION",
                "ESTADO_NOTIFICACION"
            ])
        elif "disciplinarios" in self.module_path:
            base_columns.extend(['NOMBRE_ARCHIVO',
            'MES_REPORTE',
            'EXPEDIENTE',
            'FECHA_DE_RADICACION',
            'FECHA_DE_LOS_HECHOS',
            'FECHA_DE_INDAGACION_PRELIMINAR',
            'FECHA_DE_INVESTIGACION_DISCIPLINARIA',
            'IMPLICADO',
            'DOCUMENTO_DEL_IMPLICADO',
            'DEPARTAMENTO_DE_LOS_HECHOS',
            'CIUDAD_DE_LOS_HECHOS',
            'DIRECCION_SECCIONAL',
            'DEPENDENCIA',
            'PROCESO',
            'SUBPROCESO',
            'PROCEDIMIENTO',
            'CARGO',
            'ORIGEN',
            'CONDUCTA',
            'ETAPA_PROCESAL',
            'FECHA_DE_FALLO',
            'SANCION_IMPUESTA',
            'HECHOS',
            'DECISION_DE_LA_INVESTIGACION',
            'TIPO_DE_PROCESO_AFECTADO',
            'SENALADOS_O_VINCULADOS_CON_LA_INVESTIGACION',
            'ADECUACION_TIPICA',
            'ABOGADO',
            'SENTIDO_DEL_FALLO',
            'QUEJOSO',
            'DOC_QUEJOSO',
            'TIPO_DE_PROCESO',
            'FECHA_CITACION',
            'FECHA_DE_PLIEGO_DE__CARGOS',
            'FECHA_DE_CIERRE_INVESTIGACION'])
        elif "defensoria" in self.module_path:
            base_columns.extend([
                "PROCESO",
                "DEPENDENCIA",
                "FECHA_RADICACION"
            ])
        
        return base_columns
    
    def get_optional_columns(self) -> List[str]:
        """Retorna las columnas opcionales para DIAN."""
        optional_columns = [
            "SECCIONAL",
            "DEPENDENCIA",
            "DESCRIPCION_ACTO",
            "DIRECCION",
            "FUNCIONARIO_ENVIA",
            "PLANILLA_CORR",
            "FECHA_PLANILLA_CORR",
            "FECHA_EJECUTORIA",
            "GUIA",
            "COD_ESTADO",
            "COD_NOTIFICACION",
            "MEDIO_NOTIFICACION",
            "NUMERO_EXPEDIENTE",
            "TIPO_DOCUMENTO",
            "PERI_IMPUESTO",
            "PERI_PERIODO",
            "NOMBRE_APLICACION",
            "PAIS_COD_NUM_PAIS",
            "PAIS",
            "MUNI_CODIGO_DEPART",
            "DEPARTAMENTO",
            "MUNI_CODIGO_MUNICI",
            "MUNICIPIO",
            "REGIMEN",
            "FECHA_LEVANTE",
            "MOTIVO_LEVANTE",
            "NORMATIVIDAD",
            "FUNCIONARIO_RECIBE",
            "PLANILLA_REMI_ARCHIVO",
            "FECHA_PLANILLA_REMI_ARCHIVO"
        ]
        
        return optional_columns
    
    def get_column_mappings(self) -> Dict[str, str]:
        """Retorna los mapeos de columnas para DIAN."""
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
    
    def get_validators(self) -> Dict[str, Any]:
        """Retorna los validadores específicos para DIAN."""
        factory = ValidatorFactory()
        
        return {
            'NIT': factory.create_validator('nit'),
            'CUANTIA_ACTO': factory.create_validator('float', min_value=0.0),
            'ANO_CALENDARIO': factory.create_validator('integer', min_value=2000, max_value=2030),
            'ANO_ACTO': factory.create_validator('integer', min_value=2000, max_value=2030),
            'CONSECUTIVO_ACTO': factory.create_validator('integer', min_value=1),
            'FECHA_ACTO': factory.create_validator('date'),
            'FECHA_PLANILLA_REMISION': factory.create_validator('date'),
            'FECHA_CITACION': factory.create_validator('date'),
            'FECHA_PLANILLA_CORR': factory.create_validator('date'),
            'FECHA_NOTIFICACION': factory.create_validator('date'),
            'FECHA_EJECUTORIA': factory.create_validator('date'),
            'FECHA_LEVANTE': factory.create_validator('date'),
            'FECHA_PLANILLA_REMI_ARCHIVO': factory.create_validator('date'),
            'CODIGO_ADMINISTRACION': factory.create_validator('integer', min_value=1),
            'CODIGO_DEPENDENCIA': factory.create_validator('integer', min_value=1),
            'CODIGO_ACTO': factory.create_validator('integer', min_value=1),
            'PLAN_IDENTIF_ACTO': factory.create_validator('integer', min_value=1),
            'PLANILLA_REMISION': factory.create_validator('string', min_length=1),
            'PLANILLA_CORR': factory.create_validator('string', min_length=1),
            'NUMERO_EXPEDIENTE': factory.create_validator('string', min_length=1),
            'RAZON_SOCIAL': factory.create_validator('string', min_length=2, max_length=200),
            'ESTADO_NOTIFICACION': self._get_estado_validator(),
            'PROCESO': self._get_proceso_validator(),
            'DEPENDENCIA': self._get_dependencia_validator()
        }
    
    def _get_estado_validator(self):
        """Obtiene el validador para estados de notificación."""
        try:
            estados = self.values_manager.get_all_values('estado_notificacion')
            return ValidatorFactory.create_validator('choice', choices=estados)
        except:
            # Si no se puede cargar, usar valores por defecto
            return ValidatorFactory.create_validator('choice', choices=[
                'notificado', 'pendiente', 'devuelto', 'cancelado'
            ])
    
    def _get_proceso_validator(self):
        """Obtiene el validador para procesos."""
        try:
            procesos = self.values_manager.get_all_values('proceso')
            return ValidatorFactory.create_validator('choice', choices=procesos)
        except:
            # Si no se puede cargar, usar valores por defecto
            return ValidatorFactory.create_validator('choice', choices=[
                'asistencia al cliente', 'fiscalización y liquidación', 'operación aduanera'
            ])
    
    def _get_dependencia_validator(self):
        """Obtiene el validador para dependencias."""
        try:
            dependencias = self.values_manager.get_all_values('dependencia')
            return ValidatorFactory.create_validator('choice', choices=dependencias)
        except:
            # Si no se puede cargar, usar valores por defecto
            return ValidatorFactory.create_validator('choice', choices=[
                'nivel central', 'dirección seccional'
            ])
    
    def get_module_config(self, module_name: str) -> Dict[str, Any]:
        """
        Obtiene la configuración específica para un módulo.
        
        Args:
            module_name: Nombre del módulo (notificaciones, disciplinarios, defensoria, pqr)
            
        Returns:
            Configuración específica del módulo
        """
        module_configs = {
            'notificaciones': {
                'description': 'Procesamiento de notificaciones DIAN',
                'required_columns': [
                    'PLANILLA_REMISION', 'FECHA_PLANILLA_REMISION', 'ESTADO_NOTIFICACION'
                ],
                'validators': {
                    'ESTADO_NOTIFICACION': self._get_estado_validator()
                }
            },
            'disciplinarios': {
                'description': 'Procesamiento de casos disciplinarios DIAN',
                'required_columns': [
                    'FECHA_INICIO', 'ESTADO_PROCESO', 'TIPO_SANCION'
                ],
                'validators': {
                    'ESTADO_PROCESO': ValidatorFactory.create_validator('choice', choices=[
                        'en trámite', 'resuelto', 'archivado'
                    ])
                }
            },
            'defensoria': {
                'description': 'Procesamiento de casos de defensoría DIAN',
                'required_columns': [
                    'PROCESO', 'DEPENDENCIA', 'FECHA_RADICACION'
                ],
                'validators': {
                    'PROCESO': self._get_proceso_validator(),
                    'DEPENDENCIA': self._get_dependencia_validator()
                }
            },
            'pqr': {
                'description': 'Procesamiento de PQR DIAN',
                'required_columns': [
                    'TIPO_PQR', 'ESTADO_PQR', 'FECHA_RADICACION'
                ],
                'validators': {
                    'TIPO_PQR': ValidatorFactory.create_validator('choice', choices=[
                        'petición', 'queja', 'reclamo', 'sugerencia'
                    ])
                }
            }
        }
        
        return module_configs.get(module_name, {})
    
    def validate_module_data(self, data: Dict[str, Any], module_name: str) -> Dict[str, Any]:
        """
        Valida datos específicos de un módulo.
        
        Args:
            data: Datos a validar
            module_name: Nombre del módulo
            
        Returns:
            Resultado de la validación
        """
        module_config = self.get_module_config(module_name)
        validators = self.get_validators()
        
        # Agregar validadores específicos del módulo
        if 'validators' in module_config:
            validators.update(module_config['validators'])
        
        results = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        for column, value in data.items():
            if column in validators:
                validator = validators[column]
                if not validator.is_valid(value):
                    results['valid'] = False
                    results['errors'].extend(validator.get_errors())
        
        return results 