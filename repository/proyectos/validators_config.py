"""
Configuración de validadores para diferentes proyectos y módulos.
Centraliza la configuración de validadores para facilitar el mantenimiento.
"""

from typing import Dict, List, Any
from .simple_csv_processor import (
    DataValidator, DateValidator, NITValidator, 
    ChoiceValidator, StringValidator
)

# Configuración de validadores por proyecto y módulo
VALIDATORS_CONFIG = {
    'DIAN': {
        'disciplinarios': {
            'departamento': ChoiceValidator([
                'AMAZONAS', 'ANTIOQUIA', 'ARAUCA', 'ATLANTICO', 'BOGOTA', 'BOLIVAR',
                'BOYACA', 'CALDAS', 'CAQUETA', 'CASANARE', 'CAUCA', 'CESAR', 'CHOCO',
                'CORDOBA', 'CUNDINAMARCA', 'GUAINIA', 'GUAVIARE', 'HUILA', 'LA GUAJIRA',
                'MAGDALENA', 'META', 'NARINO', 'NORTE DE SANTANDER', 'PUTUMAYO',
                'QUINDIO', 'RISARALDA', 'SAN ANDRES Y PROVIDENCIA', 'SANTANDER',
                'SUCRE', 'TOLIMA', 'VALLE DEL CAUCA', 'VICHADA'
            ], {
                'GUAJIRA': 'LA GUAJIRA',
                'N.SANTANDER': 'NORTE DE SANTANDER',
                'NORTE SANTANDER': 'NORTE DE SANTANDER',
                'VALLE': 'VALLE DEL CAUCA',
                'SAN_ANDRES_Y_PROVIDENCIA': 'SAN ANDRES Y PROVIDENCIA',
                'BOGOTA DC': 'BOGOTA',
                'BOGOTA D.C.': 'BOGOTA',
                'DISTRITO CAPITAL': 'BOGOTA'
            }),
            'ciudad': ChoiceValidator([
                'LETICIA', 'MEDELLIN', 'TURBO', 'ARAUCA', 'BARRANQUILLA', 'BOGOTA',
                'CARTAGENA', 'TUNJA', 'MANIZALES', 'FLORENCIA', 'POPAYAN', 'VALLEDUPAR',
                'QUIBDO', 'MONTERIA', 'NEIVA', 'RIOHACHA', 'SANTA MARTA', 'VILLAVICENCIO',
                'PASTO', 'CUCUTA', 'ARMENIA', 'PEREIRA', 'BUCARAMANGA', 'IBAGUE',
                'CALI', 'PALMIRA', 'SINCELEJO'
            ], {
                'MANIZALEZ': 'MANIZALES',
                'BARRAQUILLA': 'BARRANQUILLA',
                'SANTAMARTA': 'SANTA MARTA',
                'PUERTO_ASÍS': 'PUERTO ASIS'
            }),
            'direccion_seccional': ChoiceValidator([
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
                'oficina juridica',
                'gerencia seguimiento contractual',
                'gerencia de control a las operaciones ilegales',
                'gerencia financiera',
                'vicepresidencia de operaciones',
                'gerencia fiscalizacion',
                'oficina de planeacion'
            ], {
                'direccion seccional de impuestos barranquilla': 'direccion seccional de impuestos de barranquilla',
                'direccion seccional de impuestos cali': 'direccion seccional de impuestos de cali',
                'direccion seccional de impuestos cartagena': 'direccion seccional de impuestos de cartagena',
                'direccion seccional de impuestos cucuta': 'direccion seccional de impuestos de cucuta',
                'direccion seccional de impuestos medellin': 'direccion seccional de impuestos de medellin',
                'direccion seccional de impuestos grandes contribuyentes': 'direccion seccional de impuestos de grandes contribuyentes',
                'direccion seccional de impuestos bogota': 'direccion seccional de impuestos de bogota'
            }),
            'proceso': ChoiceValidator([
                'proceso 1', 'proceso 2', 'proceso 3', 'proceso 4'
            ])
        },
        'notificaciones': {
            'estado_notificacion': ChoiceValidator([
                'estado 1', 'estado 2', 'estado 3'
            ]),
            'proceso': ChoiceValidator([
                'proceso notificaciones 1', 'proceso notificaciones 2'
            ]),
            'dependencia': ChoiceValidator([
                'dependencia 1', 'dependencia 2', 'dependencia 3'
            ])
        },
        'PQR': {
            'muisca': {
                'clasificacion': ChoiceValidator([
                    'clasificacion 1', 'clasificacion 2', 'clasificacion 3'
                ]),
                'calidad_quien_solicito': ChoiceValidator([
                    'calidad 1', 'calidad 2', 'calidad 3'
                ]),
                'estado_solicitud': ChoiceValidator([
                    'estado 1', 'estado 2', 'estado 3'
                ]),
                'direccion_seccional': ChoiceValidator([
                    'direccion 1', 'direccion 2', 'direccion 3'
                ])
            },
            'dynamics': {
                'direccion_seccional': ChoiceValidator([
                    'direccion dynamics 1', 'direccion dynamics 2'
                ])
            }
        }
    },
    'COLJUEGOS': {
        'disciplinarios': {
            'direccion_seccional': ChoiceValidator([
                'direccion coljuegos 1', 'direccion coljuegos 2'
            ]),
            'proceso': ChoiceValidator([
                'proceso coljuegos 1', 'proceso coljuegos 2'
            ])
        },
        'PQR': {
            'direccion_seccional': ChoiceValidator([
                'direccion coljuegos pqr 1', 'direccion coljuegos pqr 2'
            ])
        }
    },
    'UGPP': {
        'disciplinarios': {
            'direccion_seccional': ChoiceValidator([
                'direccion ugpp 1', 'direccion ugpp 2'
            ])
        },
        'PQR': {
            'direccion_seccional': ChoiceValidator([
                'direccion ugpp pqr 1', 'direccion ugpp pqr 2'
            ])
        }
    }
}


def get_validators_for_project(project_code: str, module_name: str) -> Dict[str, DataValidator]:
    """
    Obtiene los validadores específicos para un proyecto y módulo.
    
    Args:
        project_code: Código del proyecto (DIAN, COLJUEGOS, UGPP)
        module_name: Nombre del módulo (disciplinarios, pqr, notificaciones)
    
    Returns:
        Diccionario de validadores por tipo
    """
    # Validadores base que se aplican a todos los proyectos
    base_validators = {
        'datetime': DateValidator(),
        'date': DateValidator(),
        'nit': NITValidator(),
        'string': StringValidator(),
        'str': StringValidator(),
    }
    
    # Obtener validadores específicos del proyecto
    project_validators = VALIDATORS_CONFIG.get(project_code.upper(), {})
    module_validators = project_validators.get(module_name.lower(), {})
    
    # Combinar validadores base con los específicos
    all_validators = base_validators.copy()
    all_validators.update(module_validators)
    
    return all_validators


def get_type_mapping_for_project(project_code: str, module_name: str) -> Dict[str, List[str]]:
    """
    Obtiene el mapeo de tipos para un proyecto y módulo específico.
    
    Args:
        project_code: Código del proyecto
        module_name: Nombre del módulo
    
    Returns:
        Mapeo de tipos por columna
    """
    # Mapeos específicos por proyecto y módulo
    type_mappings = {
        'DIAN': {
            'disciplinarios': {
                "datetime": ["FECHA_DE_RADICACION", "FECHA_DE_LOS_HECHOS", "FECHA_DE_INDAGACION_PRELIMINAR", 
                            "FECHA_DE_INVESTIGACION_DISCIPLINARIA", "FECHA_DE_FALLO", "FECHA_CITACION", 
                            "FECHA_DE_PLIEGO_DE__CARGOS", "FECHA_DE_CIERRE_INVESTIGACION"],
                "str": ["NOMBRE_ARCHIVO", "MES_REPORTE", "EXPEDIENTE", "IMPLICADO", "DEPENDENCIA", "SUBPROCESO", 
                       "PROCEDIMIENTO", "CARGO", "ORIGEN", "CONDUCTA", "ETAPA_PROCESAL", "SANCION_IMPUESTA", 
                       "HECHOS", "DECISION_DE_LA_INVESTIGACION", "TIPO_DE_PROCESO_AFECTADO", 
                       "SENALADOS_O_VINCULADOS_CON_LA_INVESTIGACION", "ADECUACION_TIPICA", "ABOGADO", 
                       "SENTIDO_DEL_FALLO", "QUEJOSO", "TIPO_DE_PROCESO"],
                "nit": ["DOCUMENTO_DEL_IMPLICADO", "DOC_QUEJOSO"],
                "departamento": ["DEPARTAMENTO_DE_LOS_HECHOS"],
                "ciudad": ["CIUDAD_DE_LOS_HECHOS"],
                "direccion_seccional": ["DIRECCION_SECCIONAL"],
                "proceso": ["PROCESO"]
            },
            'notificaciones': {
                "datetime": ["FECHA_RADICADO_EN_DEFENSORIA", "FECHA_ASIGNACION"],
                "str": ["ARCHIVO_FUENTE", "MES_REPORTE", "ID_CASO", "TIPO_SOLICITUD", "NOMBRE_O_RAZON_SOCIAL"],
                "nit": ["NIT/CC"],
                "estado_notificacion": ["ESTADO_NOTIFICACION"],
                "proceso": ["PROCESO"],
                "dependencia": ["DEPENDENCIA_DIAN"]
            },
            'PQR': {
                'muisca': {
                    "date": ["FEC_CREACION"],
                    "str": ["IDE_EXPEDIENTE", "NUM_IDENT", "PRI_APELL", "SEG_APELL", "RAZ_SOCIAL"],
                    "nit": ["NUM_IDENT"],
                    "clasificacion": ["CLASIFICACION"],
                    "calidad_quien_solicito": ["CALIDAD_QUIEN_IN_SOLICI"],
                    "estado_solicitud": ["ESTADO_SOLICITUD"],
                    "direccion_seccional": ["DIR_SECCIONAL_INGRESO", "DIR_SECCIONAL_ASIGNADO"]
                },
                'dynamics': {
                    "date": ["FECHA_DE_CREACION_(SOLICITUD)_(REGISTRO_DE_SOLICITUD)", "FECHA_DE_RADICACION_(SOLICITUD)_(REGISTRO_DE_SOLICITUD)"],
                    "str": ["SOLICITUD", "CLIENTE_(SOLICITUD)_(REGISTRO_DE_SOLICITUD)", "TIPO_DE_SOLICITUD_(SOLICITUD)_(REGISTRO_DE_SOLICITUD)"],
                    "nit": ["NUMERO_DE_IDENTIFICACION_(CLIENTE)_(PERSONA_NATURAL)_(SOLICITUD)_(REGISTRO_DE_SOLICITUD)"],
                    "direccion_seccional": ["AREA_DESDE_DONDE_SE_EJECUTO_LA_ACCION"]
                }
            }
        },
        'COLJUEGOS': {
            'disciplinarios': {
                "str": ["NOMBRE_ARCHIVO", "MES_REPORTE", "EXPEDIENTE"],
                "direccion_seccional": ["DIRECCION_SECCIONAL"],
                "proceso": ["PROCESO"]
            },
            'PQR': {
                "str": ["NOMBRE_ARCHIVO", "MES_REPORTE", "EXPEDIENTE"],
                "direccion_seccional": ["DIRECCION_SECCIONAL"]
            }
        },
        'UGPP': {
            'disciplinarios': {
                "str": ["NOMBRE_ARCHIVO", "MES_REPORTE", "EXPEDIENTE"],
                "direccion_seccional": ["DIRECCION_SECCIONAL"]
            },
            'PQR': {
                "str": ["NOMBRE_ARCHIVO", "MES_REPORTE", "EXPEDIENTE"],
                "direccion_seccional": ["DIRECCION_SECCIONAL"]
            }
        }
    }
    
    return type_mappings.get(project_code.upper(), {}).get(module_name.lower(), {})


def get_reference_headers_for_project(project_code: str, module_name: str) -> List[str]:
    """
    Obtiene los headers de referencia para un proyecto y módulo específico.
    
    Args:
        project_code: Código del proyecto
        module_name: Nombre del módulo
    
    Returns:
        Lista de headers de referencia
    """
    # Headers de referencia por proyecto y módulo
    reference_headers = {
        'DIAN': {
            'disciplinarios': [
                'NOMBRE_ARCHIVO', 'MES_REPORTE', 'EXPEDIENTE', 'FECHA_RADICACION',
                'FECHA_HECHOS', 'INDAGACION_PRELIMINAR', 'INVESTIGACION_DISCIPLINARIA',
                'IMPLICADO', 'IDENTIFICACION', 'DEPARTAMENTO', 'CIUDAD',
                'DIRECCION_SECCIONAL', 'DEPENDENCIA', 'PROCESO', 'SUBPROCESO',
                'PROCEDIMIENTO', 'CARGO', 'ORIGEN', 'CONDUCTA', 'ETAPA_PROCESAL',
                'FECHA_FALLO', 'SANCION_IMPUESTA', 'HECHO', 'DECISION',
                'PROCESO_AFECTADO', 'SENALADOS_O_VINCULADOS', 'ADECUACION_TIPICA',
                'ABOGADO', 'SENTIDO_DEL_FALLO', 'QUEJOSO', 'IDENTIFICACION_QUEJOSO',
                'TIPO_DE_PROCESO', 'FECHA_PLIEGO_DE_CARGOS', 'FECHA_CITACION',
                'FECHA_CIERRE_DE_INVESTIGACION'
            ],
            'notificaciones': [
                'ARCHIVO_FUENTE', 'MES_REPORTE', 'ID_CASO', 'TIPO_SOLICITUD',
                'FECHA_RADICADO_EN_DEFENSORIA', 'NOMBRE_O_RAZON_SOCIAL',
                'REPRESENTANTE_O_APODERADO', 'NIT/CC', 'DIRECCION', 'TELEFONO',
                'E_MAIL', 'DEPENDENCIA_DIAN', 'MACROPROCESO', 'PROCESO',
                'SUBPROCESO', 'PROCEDIMIENTO', 'RIESGO', 'MOTIVO_RIESGO',
                'DESCRIPCION_DE_LA_SOLICITUD', 'ASIGNACION', 'CARGO',
                'FECHA_ASIGNACION', 'ACTUACIONES', 'SOLUCIONADO_A_FAVOR'
            ],
            'PQR': {
                'muisca': [
                    'NOMBRE_ARCHIVO', 'MES_REPORTE', 'IDE_EXPEDIENTE', 'NUM_IDENT',
                    'PRI_APELL', 'SEG_APELL', 'RAZ_SOCIAL', 'MUNICIPIO',
                    'FEC_CREACION', 'MEDIO_INGRESO', 'CLASIFICACION', 'TEMA',
                    'SUBTEMA', 'OTRA', 'TIPO', 'CALIDAD_QUIEN_IN_SOLICI',
                    'ESTADO_SOLICITUD', 'DIR_SECCIONAL_INGRESO', 'EVENTO_ACTUAL',
                    'FUNCI_QUE_LA_TIENE_ASIG', 'ROL_DEL_FUNCIONARIO',
                    'FEC_ASIGNACION_COMP', 'DIR_SECCIONAL_ASIGNADO',
                    'UNIDAD_ADM_QUE_GES', 'DIAS_HABILES_EVENTO', 'ESTADO_EVENTO',
                    'FEC_TERMINACION', 'FEC_MAX_TERMINACION', 'DIR_SECC_CERR_ASUNT',
                    'DIAS_HABILES_SOLICITUD', 'DESCRIPCION_LOS_HECHOS'
                ],
                'dynamics': [
                    'NOMBRE_ARCHIVO', 'MES_REPORTE', 'SOLICITUD',
                    'NUMERO_DE_IDENTIFICACION_(CLIENTE)_(PERSONA_NATURAL)',
                    'CLIENTE_(SOLICITUD)_(REGISTRO_DE_SOLICITUD)',
                    'PERSONA_JURIDICA_(SOLICITUD)_(REGISTRO_DE_SOLICITUD)',
                    'CIUDAD_MUNICIPIO_(SOLICITUD)_(REGISTRO_DE_SOLICITUD)',
                    'FECHA_DE_CREACION_(SOLICITUD)_(REGISTRO_DE_SOLICITUD)',
                    'FECHA_DE_RADICACION_(SOLICITUD)_(REGISTRO_DE_SOLICITUD)',
                    'TIPO_DE_SOLICITUD_(SOLICITUD)_(REGISTRO_DE_SOLICITUD)',
                    'TEMA_(SOLICITUD)_(REGISTRO_DE_SOLICITUD)',
                    'ESTADO_(SOLICITUD)_(REGISTRO_DE_SOLICITUD)',
                    'AREA_DESDE_DONDE_SE_EJECUTO_LA_ACCION'
                ]
            }
        },
        'COLJUEGOS': {
            'disciplinarios': [
                'NOMBRE_ARCHIVO', 'MES_REPORTE', 'EXPEDIENTE', 'DIRECCION_SECCIONAL',
                'PROCESO', 'CARGO', 'ORIGEN', 'CONDUCTA', 'SANCION_IMPUESTA'
            ],
            'PQR': [
                'NOMBRE_ARCHIVO', 'MES_REPORTE', 'EXPEDIENTE', 'DIRECCION_SECCIONAL',
                'TIPO_SOLICITUD', 'ESTADO_SOLICITUD'
            ]
        },
        'UGPP': {
            'disciplinarios': [
                'NOMBRE_ARCHIVO', 'MES_REPORTE', 'EXPEDIENTE', 'DIRECCION_SECCIONAL',
                'PROCESO', 'CARGO', 'ORIGEN', 'CONDUCTA', 'SANCION_IMPUESTA'
            ],
            'PQR': [
                'NOMBRE_ARCHIVO', 'MES_REPORTE', 'EXPEDIENTE', 'DIRECCION_SECCIONAL',
                'TIPO_SOLICITUD', 'ESTADO_SOLICITUD'
            ]
        }
    }
    
    project_headers = reference_headers.get(project_code.upper(), {})
    
    if module_name.lower() in project_headers:
        return project_headers[module_name.lower()]
    elif isinstance(project_headers, dict) and 'PQR' in project_headers:
        # Para módulos PQR con subcategorías
        return project_headers['PQR'].get(module_name.lower(), [])
    else:
        return []


def create_processor_for_project(project_code: str, module_name: str, 
                                custom_validators: Dict[str, DataValidator] = None,
                                delimiter: str = None) -> 'CSVProcessor':
    """
    Crea un procesador CSV configurado para un proyecto y módulo específico.
    
    Args:
        project_code: Código del proyecto
        module_name: Nombre del módulo
        custom_validators: Validadores personalizados adicionales
        delimiter: Delimitador específico
    
    Returns:
        Instancia de CSVProcessor configurada
    """
    from .simple_csv_processor import CSVProcessor
    
    # Obtener configuración del proyecto
    reference_headers = get_reference_headers_for_project(project_code, module_name)
    type_mapping = get_type_mapping_for_project(project_code, module_name)
    validators = get_validators_for_project(project_code, module_name)
    
    # Agregar validadores personalizados si los hay
    if custom_validators:
        validators.update(custom_validators)
    
    return CSVProcessor(
        reference_headers=reference_headers,
        type_mapping=type_mapping,
        validators=validators,
        delimiter=delimiter
    ) 