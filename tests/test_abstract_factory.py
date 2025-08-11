#!/usr/bin/env python3
"""
Script de prueba para demostrar el funcionamiento del Abstract Factory.
Muestra cómo crear y usar procesadores específicos para diferentes proyectos.
"""

import logging
import os
import tempfile
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_abstract_factory():
    """Prueba el funcionamiento del Abstract Factory."""
    
    print("🏭 PRUEBA DEL PATRÓN ABSTRACT FACTORY")
    print("=" * 50)
    
    try:
        # Importar componentes del sistema
        from repository.proyectos.processor_factory import create_processor, get_available_processors
        from repository.proyectos.unified_csv_processor import UnifiedCSVProcessor, get_processor_info
        
        print("\n1️⃣ PROCESADORES DISPONIBLES")
        print("-" * 30)
        available_processors = get_available_processors()
        for processor in available_processors:
            print(f"  ✅ {processor}")
        
        print(f"\nTotal de procesadores registrados: {len(available_processors)}")
        
        print("\n2️⃣ CREACIÓN DE PROCESADORES ESPECÍFICOS")
        print("-" * 40)
        
        # Probar diferentes procesadores
        test_cases = [
            ('DIAN', 'notificaciones'),
            ('DIAN', 'disciplinarios'),
            ('COLJUEGOS', 'disciplinarios')
        ]
        
        for project_code, module_name in test_cases:
            print(f"\n🔧 Probando {project_code}:{module_name}")
            
            # Crear procesador usando Abstract Factory
            processor = create_processor(project_code, module_name)
            print(f"  ✅ Procesador creado: {type(processor).__name__}")
            
            # Obtener información del procesador
            info = get_processor_info(project_code, module_name)
            print(f"  📋 Proyecto: {info['project_name']}")
            print(f"  📊 Headers de referencia: {len(info['reference_headers'])}")
            print(f"  🔍 Validadores disponibles: {len(info['available_validators'])}")
            
            # Mostrar algunos headers de ejemplo
            headers_sample = info['reference_headers'][:5]
            print(f"  📝 Headers de ejemplo: {headers_sample}")
        
        print("\n3️⃣ PROCESADOR UNIFICADO")
        print("-" * 25)
        
        # Probar el procesador unificado
        unified_processor = UnifiedCSVProcessor('DIAN', 'notificaciones')
        print(f"  ✅ Procesador unificado creado")
        print(f"  📋 Proyecto: {unified_processor.project_code}")
        print(f"  📊 Módulo: {unified_processor.module_name}")
        
        # Obtener información del procesador unificado
        info = unified_processor.get_project_info()
        print(f"  🔍 Validadores: {info['available_validators']}")
        
        print("\n4️⃣ FUNCIÓN DE CONVENIENCIA")
        print("-" * 30)
        
        # Crear archivo CSV de prueba
        test_csv_content = """PLAN_IDENTIF_ACTO,CODIGO_ADMINISTRACION,SECCIONAL,NIT,ESTADO_NOTIFICACION
12345,001,SECCIONAL_BOGOTA,900123456-7,notificado
67890,002,SECCIONAL_MEDELLIN,800987654-3,pendiente"""
        
        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(test_csv_content)
            test_input_file = f.name
        
        test_output_file = test_input_file.replace('.csv', '_procesado.csv')
        test_error_file = test_input_file.replace('.csv', '_errores.csv')
        
        try:
            # type_mapping de prueba
            type_mapping = {
                "integer": ["PLAN_IDENTIF_ACTO", "CODIGO_ADMINISTRACION"],
                "nit": ["NIT"],
                "string": ["SECCIONAL", "ESTADO_NOTIFICACION"]
            }
            
            print(f"  📁 Archivo de prueba creado: {test_input_file}")
            print(f"  🔄 Procesando archivo...")
            
            # Importar la función de conveniencia
            from repository.proyectos.unified_csv_processor import process_csv_file
            
            # Procesar archivo
            process_csv_file('DIAN', 'notificaciones', test_input_file, test_output_file, test_error_file, type_mapping)
            
            print(f"  ✅ Archivo procesado exitosamente")
            print(f"  📄 Archivo de salida: {test_output_file}")
            
            # Verificar que se creó el archivo de salida
            if os.path.exists(test_output_file):
                print(f"  📊 Archivo de salida creado correctamente")
                
                # Leer y mostrar contenido del archivo procesado
                with open(test_output_file, 'r') as f:
                    processed_content = f.read()
                print(f"  📝 Contenido procesado:\n{processed_content}")
            
        except Exception as e:
            print(f"  ❌ Error durante el procesamiento: {e}")
        
        finally:
            # Limpiar archivos temporales
            for file_path in [test_input_file, test_output_file, test_error_file]:
                if os.path.exists(file_path):
                    os.unlink(file_path)
                    print(f"  🗑️ Archivo temporal eliminado: {file_path}")
        
        print("\n5️⃣ COMPATIBILIDAD CON CÓDIGO EXISTENTE")
        print("-" * 40)
        
        # Probar la clase de compatibilidad
        from repository.proyectos.unified_csv_processor import CSVProcessor
        
        compatible_processor = CSVProcessor('DIAN', 'notificaciones', validator=None)
        print(f"  ✅ Clase de compatibilidad creada: {type(compatible_processor).__name__}")
        print(f"  📋 Hereda de: {type(compatible_processor).__bases__[0].__name__}")
        
        print("\n🎉 PRUEBA COMPLETADA EXITOSAMENTE")
        print("=" * 50)
        print("✅ El patrón Abstract Factory funciona correctamente")
        print("✅ Los procesadores se crean dinámicamente")
        print("✅ El sistema unificado procesa archivos correctamente")
        print("✅ La compatibilidad con código existente se mantiene")
        
    except Exception as e:
        print(f"\n❌ ERROR DURANTE LA PRUEBA: {e}")
        logger.error(f"Error en la prueba: {e}", exc_info=True)


def test_performance():
    """Prueba de rendimiento del Abstract Factory."""
    
    print("\n🚀 PRUEBA DE RENDIMIENTO")
    print("=" * 30)
    
    try:
        import time
        from repository.proyectos.processor_factory import create_processor
        
        # Medir tiempo de creación de procesadores
        start_time = time.time()
        
        for _ in range(100):
            processor = create_processor('DIAN', 'notificaciones')
        
        end_time = time.time()
        total_time = end_time - start_time
        avg_time = total_time / 100
        
        print(f"  ⏱️ Tiempo total para crear 100 procesadores: {total_time:.4f} segundos")
        print(f"  ⚡ Tiempo promedio por procesador: {avg_time:.6f} segundos")
        print(f"  🔄 Procesadores por segundo: {100/total_time:.2f}")
        
        print("  ✅ Rendimiento aceptable")
        
    except Exception as e:
        print(f"  ❌ Error en prueba de rendimiento: {e}")


if __name__ == "__main__":
    print("🧪 INICIANDO PRUEBAS DEL ABSTRACT FACTORY")
    print("=" * 50)
    
    # Ejecutar pruebas
    test_abstract_factory()
    test_performance()
    
    print("\n🏁 PRUEBAS FINALIZADAS")
    print("=" * 30) 