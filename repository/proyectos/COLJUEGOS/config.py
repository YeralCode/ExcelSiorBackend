"""
Configuración específica para el proyecto COLJUEGOS.
Extiende la configuración base con valores específicos de COLJUEGOS.
"""

from typing import Dict, List, Any
from pathlib import Path
from ..base.config_base import ProjectConfigBase
from ..base.values_manager import ValuesManager
from ..base.validators import ValidatorFactory


class COLJUEGOSConfig(ProjectConfigBase):
    """
    Configuración específica para el proyecto COLJUEGOS.
    Define las configuraciones, columnas y validadores específicos de COLJUEGOS.
    """
    
    def __init__(self, module_path: str = ""):
        super().__init__(
            project_name="COLJUEGOS - Coljuegos",
            project_code="COLJUEGOS",
            description="Procesamiento de datos de Coljuegos para diferentes módulos"
        )
        self.module_path = module_path
        self.values_manager = ValuesManager("COLJUEGOS", module_path)
    
    def get_required_columns(self) -> List[str]:
        """Retorna las columnas requeridas para COLJUEGOS."""
        base_columns = [
            "NUMERO_EXPEDIENTE",
            "FECHA_RADICACION",
            "TIPO_PROCESO",
            "ESTADO_PROCESO",
            "DIRECCION_SECCIONAL"
        ]
        
        # Agregar columnas específicas según el módulo
        if "disciplinarios" in self.module_path:
            base_columns.extend([
                "FECHA_INICIO",
                "FECHA_FIN",
                "TIPO_SANCION",
                "CUANTIA_SANCION"
            ])
        elif "pqr" in self.module_path:
            base_columns.extend([
                "TIPO_PQR",
                "ESTADO_PQR",
                "FECHA_RESPUESTA"
            ])
        
        return base_columns
    
    def get_optional_columns(self) -> List[str]:
        """Retorna las columnas opcionales para COLJUEGOS."""
        optional_columns = [
            "NOMBRE_OPERADOR",
            "NIT_OPERADOR",
            "DIRECCION_OPERADOR",
            "TELEFONO_OPERADOR",
            "EMAIL_OPERADOR",
            "REPRESENTANTE_LEGAL",
            "DOCUMENTO_REPRESENTANTE",
            "TIPO_DOCUMENTO",
            "DESCRIPCION_PROCESO",
            "MOTIVO_PROCESO",
            "FUNCIONARIO_ASIGNADO",
            "FECHA_ASIGNACION",
            "FECHA_VENCIMIENTO",
            "OBSERVACIONES",
            "ARCHIVOS_ADJUNTOS",
            "REFERENCIA_NORMATIVA",
            "DEPARTAMENTO",
            "MUNICIPIO",
            "ZONA_GEOGRAFICA",
            "CATEGORIA_OPERADOR",
            "TIPO_LICENCIA",
            "NUMERO_LICENCIA",
            "FECHA_VENCIMIENTO_LICENCIA",
            "ESTADO_LICENCIA"
        ]
        
        return optional_columns
    
    def get_column_mappings(self) -> Dict[str, str]:
        """Retorna los mapeos de columnas para COLJUEGOS."""
        return {
            "numero_expediente": "NUMERO_EXPEDIENTE",
            "fecha_radicacion": "FECHA_RADICACION",
            "tipo_proceso": "TIPO_PROCESO",
            "estado_proceso": "ESTADO_PROCESO",
            "direccion_seccional": "DIRECCION_SECCIONAL",
            "nombre_operador": "NOMBRE_OPERADOR",
            "nit_operador": "NIT_OPERADOR",
            "direccion_operador": "DIRECCION_OPERADOR",
            "telefono_operador": "TELEFONO_OPERADOR",
            "email_operador": "EMAIL_OPERADOR",
            "representante_legal": "REPRESENTANTE_LEGAL",
            "documento_representante": "DOCUMENTO_REPRESENTANTE",
            "tipo_documento": "TIPO_DOCUMENTO",
            "descripcion_proceso": "DESCRIPCION_PROCESO",
            "motivo_proceso": "MOTIVO_PROCESO",
            "funcionario_asignado": "FUNCIONARIO_ASIGNADO",
            "fecha_asignacion": "FECHA_ASIGNACION",
            "fecha_vencimiento": "FECHA_VENCIMIENTO",
            "observaciones": "OBSERVACIONES",
            "archivos_adjuntos": "ARCHIVOS_ADJUNTOS",
            "referencia_normativa": "REFERENCIA_NORMATIVA",
            "departamento": "DEPARTAMENTO",
            "municipio": "MUNICIPIO",
            "zona_geografica": "ZONA_GEOGRAFICA",
            "categoria_operador": "CATEGORIA_OPERADOR",
            "tipo_licencia": "TIPO_LICENCIA",
            "numero_licencia": "NUMERO_LICENCIA",
            "fecha_vencimiento_licencia": "FECHA_VENCIMIENTO_LICENCIA",
            "estado_licencia": "ESTADO_LICENCIA"
        }
    
    def get_validators(self) -> Dict[str, Any]:
        """Retorna los validadores específicos para COLJUEGOS."""
        factory = ValidatorFactory()
        
        return {
            'NUMERO_EXPEDIENTE': factory.create_validator('string', min_length=1, max_length=50),
            'FECHA_RADICACION': factory.create_validator('date'),
            'TIPO_PROCESO': self._get_tipo_proceso_validator(),
            'ESTADO_PROCESO': self._get_estado_proceso_validator(),
            'DIRECCION_SECCIONAL': self._get_direccion_seccional_validator(),
            'NIT_OPERADOR': factory.create_validator('nit'),
            'TELEFONO_OPERADOR': factory.create_validator('phone'),
            'EMAIL_OPERADOR': factory.create_validator('email'),
            'DOCUMENTO_REPRESENTANTE': factory.create_validator('string', min_length=5, max_length=20),
            'CUANTIA_SANCION': factory.create_validator('float', min_value=0.0),
            'FECHA_INICIO': factory.create_validator('date'),
            'FECHA_FIN': factory.create_validator('date'),
            'FECHA_ASIGNACION': factory.create_validator('date'),
            'FECHA_VENCIMIENTO': factory.create_validator('date'),
            'FECHA_RESPUESTA': factory.create_validator('date'),
            'FECHA_VENCIMIENTO_LICENCIA': factory.create_validator('date'),
            'NOMBRE_OPERADOR': factory.create_validator('string', min_length=2, max_length=200),
            'DIRECCION_OPERADOR': factory.create_validator('string', min_length=5, max_length=300),
            'REPRESENTANTE_LEGAL': factory.create_validator('string', min_length=2, max_length=200),
            'DESCRIPCION_PROCESO': factory.create_validator('string', min_length=5, max_length=500),
            'MOTIVO_PROCESO': factory.create_validator('string', min_length=5, max_length=300),
            'FUNCIONARIO_ASIGNADO': factory.create_validator('string', min_length=2, max_length=100),
            'OBSERVACIONES': factory.create_validator('string', min_length=0, max_length=1000),
            'REFERENCIA_NORMATIVA': factory.create_validator('string', min_length=5, max_length=200),
            'DEPARTAMENTO': factory.create_validator('string', min_length=2, max_length=100),
            'MUNICIPIO': factory.create_validator('string', min_length=2, max_length=100),
            'ZONA_GEOGRAFICA': factory.create_validator('string', min_length=2, max_length=50),
            'CATEGORIA_OPERADOR': factory.create_validator('string', min_length=2, max_length=100),
            'TIPO_LICENCIA': factory.create_validator('string', min_length=2, max_length=100),
            'NUMERO_LICENCIA': factory.create_validator('string', min_length=1, max_length=50),
            'ESTADO_LICENCIA': factory.create_validator('choice', choices=[
                'activa', 'suspendida', 'cancelada', 'vencida', 'en trámite'
            ])
        }
    
    def _get_tipo_proceso_validator(self):
        """Obtiene el validador para tipos de proceso."""
        try:
            tipos = self.values_manager.get_all_values('tipo_proceso')
            return ValidatorFactory.create_validator('choice', choices=tipos)
        except:
            # Si no se puede cargar, usar valores por defecto
            return ValidatorFactory.create_validator('choice', choices=[
                'disciplinario', 'administrativo', 'sancionatorio', 'preventivo'
            ])
    
    def _get_estado_proceso_validator(self):
        """Obtiene el validador para estados de proceso."""
        try:
            estados = self.values_manager.get_all_values('estado_proceso')
            return ValidatorFactory.create_validator('choice', choices=estados)
        except:
            # Si no se puede cargar, usar valores por defecto
            return ValidatorFactory.create_validator('choice', choices=[
                'en trámite', 'resuelto', 'archivado', 'suspendido', 'apelado'
            ])
    
    def _get_direccion_seccional_validator(self):
        """Obtiene el validador para direcciones seccionales."""
        try:
            direcciones = self.values_manager.get_all_values('direccion_seccional')
            return ValidatorFactory.create_validator('choice', choices=direcciones)
        except:
            # Si no se puede cargar, usar valores por defecto
            return ValidatorFactory.create_validator('choice', choices=[
                'gerencia control a las operaciones ilegales',
                'gerencia de cobro',
                'gerencia financiera',
                'gerencia seguimiento contractual',
                'vicepresidencia de desarrollo organizacional',
                'vicepresidencia de operaciones',
                'vicepresidencia desarrollo comercial'
            ])
    
    def get_module_config(self, module_name: str) -> Dict[str, Any]:
        """
        Obtiene la configuración específica para un módulo.
        
        Args:
            module_name: Nombre del módulo (disciplinarios, pqr)
            
        Returns:
            Configuración específica del módulo
        """
        module_configs = {
            'disciplinarios': {
                'description': 'Procesamiento de casos disciplinarios Coljuegos',
                'required_columns': [
                    'FECHA_INICIO', 'TIPO_SANCION', 'CUANTIA_SANCION'
                ],
                'validators': {
                    'TIPO_SANCION': ValidatorFactory.create_validator('choice', choices=[
                        'amonestación', 'multa', 'suspensión', 'cancelación de licencia'
                    ])
                }
            },
            'pqr': {
                'description': 'Procesamiento de PQR Coljuegos',
                'required_columns': [
                    'TIPO_PQR', 'ESTADO_PQR', 'FECHA_RESPUESTA'
                ],
                'validators': {
                    'TIPO_PQR': ValidatorFactory.create_validator('choice', choices=[
                        'petición', 'queja', 'reclamo', 'sugerencia', 'denuncia'
                    ]),
                    'ESTADO_PQR': ValidatorFactory.create_validator('choice', choices=[
                        'radicado', 'en trámite', 'respondido', 'cerrado'
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