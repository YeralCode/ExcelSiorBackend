#!/usr/bin/env python3
"""
Script de prueba para demostrar el funcionamiento del sistema modular de proyectos.
"""

import sys
import os
from pathlib import Path

# Agregar el directorio backend al path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from repository.proyectos.factory import (
    get_project_config, 
    validate_project_data, 
    project_manager,
    ProjectConfigFactory
)
from repository.proyectos.base.values_manager import ValuesManager
from repository.proyectos.base.validators import ValidatorFactory


def test_basic_configurations():
    """Prueba las configuraciones básicas de los proyectos."""
    print("🔧 Probando configuraciones básicas...")
    print("=" * 50)
    
    projects = ['DIAN', 'COLJUEGOS', 'UGPP']
    
    for project_code in projects:
        try:
            config = get_project_config(project_code)
            print(f"\n📋 Proyecto: {project_code}")
            print(f"   Nombre: {config.project_name}")
            print(f"   Descripción: {config.description}")
            print(f"   Columnas requeridas: {len(config.get_required_columns())}")
            print(f"   Columnas opcionales: {len(config.get_optional_columns())}")
            print(f"   Validadores: {len(config.get_validators())}")
            print(f"   Formatos soportados: {config.supported_formats}")
        except Exception as e:
            print(f"❌ Error con {project_code}: {str(e)}")


def test_module_specific_configurations():
    """Prueba configuraciones específicas de módulos."""
    print("\n\n🔧 Probando configuraciones específicas de módulos...")
    print("=" * 50)
    
    module_tests = [
        ('DIAN', 'notificaciones'),
        ('DIAN', 'disciplinarios'),
        ('DIAN', 'defensoria'),
        ('COLJUEGOS', 'disciplinarios'),
        ('COLJUEGOS', 'pqr'),
        ('UGPP', 'disciplinarios'),
        ('UGPP', 'pqr')
    ]
    
    for project_code, module_name in module_tests:
        try:
            config = get_project_config(project_code, module_name)
            print(f"\n📋 {project_code} - {module_name}")
            print(f"   Columnas requeridas: {len(config.get_required_columns())}")
            print(f"   Módulo path: {config.module_path}")
        except Exception as e:
            print(f"❌ Error con {project_code} - {module_name}: {str(e)}")


def test_data_validation():
    """Prueba la validación de datos."""
    print("\n\n🔍 Probando validación de datos...")
    print("=" * 50)
    
    # Datos de prueba para DIAN
    dian_test_data = {
        'NIT': '900123456-7',
        'CUANTIA_ACTO': 1500000.50,
        'ANO_CALENDARIO': 2024,
        'FECHA_ACTO': '2024-01-15',
        'ESTADO_NOTIFICACION': 'notificado',
        'RAZON_SOCIAL': 'Empresa Ejemplo S.A.S.',
        'CODIGO_ADMINISTRACION': 1,
        'CODIGO_DEPENDENCIA': 2,
        'CODIGO_ACTO': 3,
        'ANO_ACTO': 2024,
        'CONSECUTIVO_ACTO': 1,
        'PLAN_IDENTIF_ACTO': 1
    }
    
    print("📋 Validando datos DIAN notificaciones...")
    result = validate_project_data('DIAN', dian_test_data, 'notificaciones')
    
    if result['valid']:
        print("✅ Datos válidos")
    else:
        print("❌ Errores encontrados:")
        for error in result['errors']:
            print(f"   - {error}")
    
    # Datos de prueba para COLJUEGOS
    coljuegos_test_data = {
        'NUMERO_EXPEDIENTE': 'EXP-2024-001',
        'FECHA_RADICACION': '2024-01-15',
        'TIPO_PROCESO': 'disciplinario',
        'ESTADO_PROCESO': 'en trámite',
        'DIRECCION_SECCIONAL': 'gerencia control a las operaciones ilegales',
        'NIT_EMPRESA': '900123456-7'
    }
    
    print("\n📋 Validando datos COLJUEGOS disciplinarios...")
    result = validate_project_data('COLJUEGOS', coljuegos_test_data, 'disciplinarios')
    
    if result['valid']:
        print("✅ Datos válidos")
    else:
        print("❌ Errores encontrados:")
        for error in result['errors']:
            print(f"   - {error}")


def test_values_manager():
    """Prueba el gestor de valores."""
    print("\n\n📊 Probando gestor de valores...")
    print("=" * 50)
    
    try:
        # Probar con DIAN defensoria
        values_manager = ValuesManager('DIAN', 'defensoria')
        
        print("📋 Valores disponibles en DIAN defensoria:")
        available_modules = values_manager.get_available_modules()
        for module in available_modules:
            print(f"   - {module}")
        
        # Probar carga de valores de proceso
        if 'proceso' in available_modules:
            proceso_config = values_manager.get_values('proceso')
            print(f"\n📋 Valores de proceso DIAN:")
            print(f"   Cantidad: {len(values_manager.get_all_values('proceso'))}")
            print(f"   Primeros 3: {values_manager.get_all_values('proceso')[:3]}")
        
        # Probar validación de valores
        is_valid = values_manager.validate_value('proceso', 'asistencia al cliente')
        print(f"\n✅ ¿'asistencia al cliente' es válido? {is_valid}")
        
    except Exception as e:
        print(f"❌ Error con gestor de valores: {str(e)}")


def test_validators():
    """Prueba los validadores específicos."""
    print("\n\n🔍 Probando validadores específicos...")
    print("=" * 50)
    
    factory = ValidatorFactory()
    
    # Probar validadores básicos
    validators_to_test = [
        ('nit', 'NIT', '900123456-7', True),
        ('nit', 'NIT', '123', False),
        ('date', 'Fecha', '2024-01-15', True),
        ('date', 'Fecha', 'fecha inválida', False),
        ('float', 'Flotante', 1500000.50, True),
        ('float', 'Flotante', -100, False),
        ('integer', 'Entero', 2024, True),
        ('integer', 'Entero', 'no es número', False),
        ('email', 'Email', 'test@example.com', True),
        ('email', 'Email', 'email inválido', False),
        ('phone', 'Teléfono', '3001234567', True),
        ('phone', 'Teléfono', '123', False),
        ('percentage', 'Porcentaje', '50%', True),
        ('percentage', 'Porcentaje', '150%', False),
        ('boolean', 'Booleano', 'true', True),
        ('boolean', 'Booleano', 'invalid', False)
    ]
    
    for validator_type, name, value, expected in validators_to_test:
        try:
            validator = factory.create_validator(validator_type)
            result = validator.is_valid(value)
            status = "✅" if result == expected else "❌"
            print(f"{status} {name} ({validator_type}): {value} -> {result} (esperado: {expected})")
        except Exception as e:
            print(f"❌ Error con {name}: {str(e)}")


def test_project_manager():
    """Prueba el gestor de proyectos."""
    print("\n\n🏢 Probando gestor de proyectos...")
    print("=" * 50)
    
    # Listar proyectos
    print("📋 Proyectos disponibles:")
    projects = project_manager.list_projects()
    for code, info in projects.items():
        if 'error' not in info:
            print(f"   - {code}: {info['name']}")
            print(f"     Columnas requeridas: {info['required_columns_count']}")
            print(f"     Validadores: {info['validators_count']}")
        else:
            print(f"   - {code}: Error - {info['error']}")
    
    # Obtener información detallada
    print("\n📋 Información detallada DIAN notificaciones:")
    try:
        dian_info = project_manager.get_project_info('DIAN', 'notificaciones')
        print(f"   Formatos soportados: {dian_info['supported_formats']}")
        print(f"   Encoding: {dian_info['encoding']}")
        print(f"   Delimiter: {dian_info['delimiter']}")
        print(f"   Columnas requeridas: {len(dian_info['required_columns'])}")
    except Exception as e:
        print(f"❌ Error obteniendo información DIAN: {str(e)}")


def test_factory_functionality():
    """Prueba funcionalidades del factory."""
    print("\n\n🏭 Probando funcionalidades del factory...")
    print("=" * 50)
    
    # Obtener proyectos disponibles
    available_projects = ProjectConfigFactory.get_available_projects()
    print(f"📋 Proyectos registrados: {available_projects}")
    
    # Probar cache
    print("\n📋 Probando cache de configuraciones...")
    config1 = get_project_config('DIAN')
    config2 = get_project_config('DIAN')
    print(f"   ¿Misma instancia? {config1 is config2}")
    
    # Limpiar cache
    ProjectConfigFactory.clear_cache()
    config3 = get_project_config('DIAN')
    print(f"   ¿Nueva instancia después de limpiar cache? {config1 is not config3}")


def main():
    """Función principal de pruebas."""
    print("🚀 Iniciando pruebas del sistema modular de proyectos")
    print("=" * 60)
    
    try:
        # Ejecutar todas las pruebas
        test_basic_configurations()
        test_module_specific_configurations()
        test_data_validation()
        test_values_manager()
        test_validators()
        test_project_manager()
        test_factory_functionality()
        
        print("\n\n🎉 ¡Todas las pruebas completadas!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error general en las pruebas: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 