#!/usr/bin/env python3
"""
Prueba de Validación de Valores Choices en BPM
Este script verifica que todos los valores choices estén funcionando correctamente
"""

import sys
import os
import pandas as pd
from pathlib import Path

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_bpm_choices_import():
    """Prueba la importación de los valores choices de BPM"""
    try:
        from repository.proyectos.BPM.disciplinarios.valores_choice import (
            BPM_CHOICES,
            get_choices_for_field,
            validate_choice_value,
            CHOICE_FIELDS
        )
        
        print("✅ Importación de valores choices exitosa")
        return True
        
    except ImportError as e:
        print(f"❌ Error importando valores choices: {e}")
        return False

def test_choices_structure():
    """Prueba la estructura de los valores choices"""
    try:
        from repository.proyectos.BPM.disciplinarios.valores_choice import BPM_CHOICES, CHOICE_FIELDS
        
        print(f"📊 Estructura de valores choices:")
        print(f"   - Total de campos con choices: {len(CHOICE_FIELDS)}")
        print(f"   - Campos disponibles: {', '.join(CHOICE_FIELDS)}")
        
        # Verificar que cada campo tenga valores
        for field in CHOICE_FIELDS:
            choices = BPM_CHOICES.get(field, [])
            print(f"   - {field}: {len(choices)} valores")
            
            if len(choices) == 0:
                print(f"     ⚠️  Campo {field} no tiene valores")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verificando estructura: {e}")
        return False

def test_choice_validation():
    """Prueba la validación de valores choices"""
    try:
        from repository.proyectos.BPM.disciplinarios.valores_choice import validate_choice_value
        
        # Casos de prueba
        test_cases = [
            ("PROGRAMA", "Selección 2014", True),
            ("PROGRAMA", "Denuncias", True),
            ("PROGRAMA", "Programa Inexistente", False),
            ("ESTADO", "Terminado", True),
            ("ESTADO", "Activo", True),
            ("ESTADO", "Estado Invalido", False),
            ("TIPO_DE_PROCESO_CONCURSAL", "Liquidación", True),
            ("AREA_QUE_INFORMA_PROCESO", "Completitud", True),
            ("ETAPA_CON_LA_QUE_MIGRO_BPM", "COMPLETITUD", True),
        ]
        
        print("🔍 Probando validación de valores choices:")
        
        all_passed = True
        for field, value, expected in test_cases:
            result = validate_choice_value(field, value)
            status = "✅" if result == expected else "❌"
            print(f"   {status} {field}: '{value}' -> {result} (esperado: {expected})")
            
            if result != expected:
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Error en validación: {e}")
        return False

def test_csv_data_against_choices():
    """Prueba los datos del CSV contra los valores choices"""
    try:
        from repository.proyectos.BPM.disciplinarios.valores_choice import validate_choice_value
        
        csv_path = "test_bpm_data.csv"
        if not os.path.exists(csv_path):
            print(f"⚠️  Archivo CSV no encontrado: {csv_path}")
            return False
        
        # Leer CSV
        df = pd.read_csv(csv_path, sep='|', encoding='utf-8')
        print(f"📊 Analizando CSV: {len(df)} filas, {len(df.columns)} columnas")
        
        # Campos importantes para validar
        important_fields = [
            "Programa", "Estado", "Tipo de proceso concursal", 
            "Área que informa proceso", "Etapa con la que migró BPM"
        ]
        
        validation_results = {}
        
        for field in important_fields:
            if field in df.columns:
                unique_values = df[field].dropna().unique()
                valid_count = 0
                invalid_values = []
                
                for value in unique_values:
                    if validate_choice_value(field, str(value)):
                        valid_count += 1
                    else:
                        invalid_values.append(str(value))
                
                total_values = len(unique_values)
                valid_percentage = (valid_count / total_values * 100) if total_values > 0 else 0
                
                validation_results[field] = {
                    "total": total_values,
                    "valid": valid_count,
                    "invalid": len(invalid_values),
                    "percentage": valid_percentage,
                    "invalid_values": invalid_values
                }
                
                print(f"🔍 {field}:")
                print(f"   - Total valores únicos: {total_values}")
                print(f"   - Valores válidos: {valid_count}")
                print(f"   - Valores inválidos: {len(invalid_values)}")
                print(f"   - Porcentaje válido: {valid_percentage:.1f}%")
                
                if invalid_values:
                    print(f"   - Valores inválidos: {invalid_values[:5]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error analizando CSV: {e}")
        return False

def test_choices_completeness():
    """Prueba la completitud de los valores choices"""
    try:
        from repository.proyectos.BPM.disciplinarios.valores_choice import BPM_CHOICES
        
        # Verificar que todos los campos tengan valores
        empty_fields = []
        total_choices = 0
        
        for field, choices in BPM_CHOICES.items():
            if len(choices) == 0:
                empty_fields.append(field)
            total_choices += len(choices)
        
        print(f"📋 Completitud de valores choices:")
        print(f"   - Total de campos: {len(BPM_CHOICES)}")
        print(f"   - Total de valores: {total_choices}")
        print(f"   - Campos vacíos: {len(empty_fields)}")
        
        if empty_fields:
            print(f"   - Campos sin valores: {empty_fields}")
        
        # Verificar campos críticos
        critical_fields = ["PROGRAMA", "ESTADO", "TIPO_DE_PROCESO_CONCURSAL"]
        missing_critical = []
        
        for field in critical_fields:
            if field not in BPM_CHOICES or len(BPM_CHOICES[field]) == 0:
                missing_critical.append(field)
        
        if missing_critical:
            print(f"   ⚠️  Campos críticos faltantes: {missing_critical}")
            return False
        
        return len(empty_fields) == 0
        
    except Exception as e:
        print(f"❌ Error verificando completitud: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 PRUEBA DE VALIDACIÓN DE VALORES CHOICES EN BPM")
    print("=" * 60)
    
    tests = [
        ("Importación de Choices", test_bpm_choices_import),
        ("Estructura de Choices", test_choices_structure),
        ("Validación de Valores", test_choice_validation),
        ("Datos CSV vs Choices", test_csv_data_against_choices),
        ("Completitud de Choices", test_choices_completeness),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Ejecutando: {test_name}")
        print("-" * 40)
        
        try:
            result = test_func()
            results.append((test_name, result))
            print(f"   Resultado: {'✅ PASÓ' if result else '❌ FALLÓ'}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results.append((test_name, False))
    
    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS")
    
    total_tests = len(results)
    passed_tests = sum(1 for _, result in results if result)
    failed_tests = total_tests - passed_tests
    
    print(f"   - Total de pruebas: {total_tests}")
    print(f"   - Pruebas exitosas: {passed_tests}")
    print(f"   - Pruebas fallidas: {failed_tests}")
    print(f"   - Tasa de éxito: {(passed_tests/total_tests)*100:.1f}%")
    
    if failed_tests == 0:
        print("🎉 ¡TODAS LAS PRUEBAS PASARON EXITOSAMENTE!")
        return 0
    else:
        print(f"⚠️  {failed_tests} prueba(s) fallaron.")
        return 1

if __name__ == "__main__":
    exit(main()) 