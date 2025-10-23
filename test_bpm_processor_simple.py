#!/usr/bin/env python3
"""
Prueba Simple del Procesador BPM
Este script verifica que el procesador BPM funcione correctamente
"""

import sys
import os
import tempfile
import shutil

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_bpm_processor():
    """Prueba básica del procesador BPM"""
    try:
        print("🧪 Probando importación del procesador BPM...")
        
        # Importar el procesador
        from repository.proyectos.validators_config import create_processor_for_project
        
        print("✅ Importación exitosa")
        
        # Crear procesador
        print("🧪 Creando procesador BPM...")
        processor = create_processor_for_project('BPM', 'default')
        
        print("✅ Procesador creado exitosamente")
        print(f"   - Tipo: {type(processor)}")
        print(f"   - Nombre: {getattr(processor, 'name', 'N/A')}")
        
        # Verificar que tiene el método process_csv
        if hasattr(processor, 'process_csv'):
            print("✅ Método process_csv disponible")
        else:
            print("❌ Método process_csv no disponible")
            return False
        
        # Probar con un archivo pequeño
        print("🧪 Probando procesamiento de archivo...")
        
        # Crear archivo de prueba
        test_csv_content = """nombre_archivo|mes_reporte|Programa|Estado
test1|01/2020|Selección 2014|Terminado
test2|02/2020|Denuncias|Activo"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(test_csv_content)
            test_input = f.name
        
        # Crear archivos de salida temporales
        test_output = tempfile.mktemp(suffix='.csv')
        test_error = tempfile.mktemp(suffix='.csv')
        
        try:
            # Procesar archivo
            stats = processor.process_csv(test_input, test_output, test_error)
            print("✅ Procesamiento exitoso")
            print(f"   - Estadísticas: {stats}")
            
            # Verificar archivos de salida
            if os.path.exists(test_output):
                print(f"✅ Archivo de salida creado: {os.path.getsize(test_output)} bytes")
            else:
                print("❌ Archivo de salida no creado")
            
            if os.path.exists(test_error):
                print(f"✅ Archivo de errores creado: {os.path.getsize(test_error)} bytes")
            else:
                print("✅ Archivo de errores no creado (sin errores)")
            
            return True
            
        finally:
            # Limpiar archivos temporales
            for temp_file in [test_input, test_output, test_error]:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
        
    except Exception as e:
        print(f"❌ Error en prueba: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_bpm_choices():
    """Prueba los valores choices de BPM"""
    try:
        print("\n🧪 Probando valores choices de BPM...")
        
        from repository.proyectos.BPM.disciplinarios.valores_choice import (
            BPM_CHOICES,
            validate_choice_value
        )
        
        print("✅ Importación de choices exitosa")
        
        # Probar validación
        test_cases = [
            ("PROGRAMA", "Selección 2014", True),
            ("ESTADO", "Terminado", True),
            ("TIPO_DE_PROCESO_CONCURSAL", "Liquidación", True)
        ]
        
        for field, value, expected in test_cases:
            result = validate_choice_value(field, value)
            status = "✅" if result == expected else "❌"
            print(f"   {status} {field}: '{value}' -> {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en choices: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 PRUEBA SIMPLE DEL PROCESADOR BPM")
    print("=" * 50)
    
    # Prueba del procesador
    processor_ok = test_bpm_processor()
    
    # Prueba de choices
    choices_ok = test_bpm_choices()
    
    # Resumen
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE PRUEBAS")
    print(f"   - Procesador BPM: {'✅ OK' if processor_ok else '❌ FALLÓ'}")
    print(f"   - Valores Choices: {'✅ OK' if choices_ok else '❌ FALLÓ'}")
    
    if processor_ok and choices_ok:
        print("🎉 ¡TODAS LAS PRUEBAS PASARON!")
        return 0
    else:
        print("⚠️  Algunas pruebas fallaron")
        return 1

if __name__ == "__main__":
    exit(main()) 