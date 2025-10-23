#!/usr/bin/env python3
"""
PRUEBA DEL PROCESADOR BPM
Verifica que el procesador BPM funcione correctamente
"""

import pandas as pd
import tempfile
import os
import sys

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_bpm_processor():
    """Prueba el procesador BPM completo"""
    
    print("🧪 PRUEBA DEL PROCESADOR BPM")
    print("=" * 70)
    
    try:
        # 1. Importar componentes de BPM
        print("1️⃣ Importando componentes de BPM...")
        from repository.proyectos.BPM import bpm_processor, bpm_transformer, bpm_validator
        print("   ✅ Componentes importados exitosamente")
        
        # 2. Crear datos de prueba
        print("\n2️⃣ Creando datos de prueba...")
        
        # Crear DataFrame con datos de prueba BPM
        test_data = {
            'ORDEN': [1, 2, 3, 4, 5],
            'EXPEDIENTE_(ANTIGUO)': ['EXP001', 'EXP002', 'EXP003', 'EXP004', 'EXP005'],
            'TIPO_EXPEDIENTE': ['FISCALIZACION', 'SANCION', 'COBRO_COACTIVO', 'RECURSO', 'REVOCATORIA'],
            'ID_EXPEDIENTE_ECM': ['ID001', 'ID002', 'ID003', 'ID004', 'ID005'],
            'NOMBRE_ARCHIVO': ['archivo1.csv', 'archivo2.csv', 'archivo3.csv', 'archivo4.csv', 'archivo5.csv'],
            'MES_REPORTE': ['01_2024', '02_2024', '03_2024', '04_2024', '05_2024'],
            'FECHA_REPARTO': ['15/01/2024', '20/02/2024', '25/03/2024', '30/04/2024', '05/05/2024'],
            'ANO_REPARTO': [2024, 2024, 2024, 2024, 2024],
            'ANO_GESTION': [2024, 2024, 2024, 2024, 2024],
            'TIPO_DOC_IDENTIFICACION_APORTANTE': ['CC', 'NIT', 'CE', 'TI', 'PP'],
            'NO_CC_O_NIT_APORTANTE': ['12345678', '900123456-7', '98765432', '123456789', '87654321'],
            'NOMBRES_Y_O_RAZON_SOCIAL_APORTANTE': ['Juan Pérez', 'Empresa ABC S.A.', 'María García', 'Carlos López', 'Ana Rodríguez'],
            'TIPO_APORTANTE': ['PERSONA_NATURAL', 'PERSONA_JURIDICA', 'PERSONA_NATURAL', 'PERSONA_NATURAL', 'PERSONA_NATURAL'],
            'TAMANO': ['PEQUEÑA', 'MEDIANA', 'PEQUEÑA', 'GRANDE', 'MICROEMPRESA'],
            '#_EMPLEADOS': [5, 50, 3, 200, 2],
            'DIRECCION_RUT': ['Calle 123 #45-67', 'Carrera 78 #90-12', 'Avenida 34 #56-78', 'Calle 90 #12-34', 'Carrera 56 #78-90'],
            'MUNICIPIO_RUT': ['BOGOTA', 'MEDELLIN', 'CALI', 'BARRANQUILLA', 'CARTAGENA'],
            'DPTO_RUT': ['CUNDINAMARCA', 'ANTIOQUIA', 'VALLE DEL CAUCA', 'ATLANTICO', 'BOLIVAR'],
            'TELEFONO': ['3001234567', '3002345678', '3003456789', '3004567890', '3005678901'],
            'EMAIL': ['juan@email.com', 'empresa@abc.com', 'maria@email.com', 'carlos@email.com', 'ana@email.com'],
            'ESTADO': ['ACTIVO', 'SUSPENDIDO', 'EN_PROCESO', 'TERMINADO', 'ARCHIVADO']
        }
        
        df = pd.DataFrame(test_data)
        print(f"   ✅ DataFrame de prueba creado: {len(df)} filas × {len(df.columns)} columnas")
        
        # 3. Probar transformador de columnas
        print("\n3️⃣ Probando transformador de columnas...")
        
        try:
            df_transformed = bpm_transformer.transform_dataframe(df)
            print(f"   ✅ Transformación completada: {len(df_transformed)} filas × {len(df_transformed.columns)} columnas")
            
            # Mostrar estadísticas de transformación
            stats = bpm_transformer.get_transformation_stats()
            print(f"   📊 Estadísticas de transformación:")
            print(f"      - Total de columnas: {stats['total_columns']}")
            print(f"      - Tipos soportados: {list(stats['column_types'].keys())}")
            print(f"      - Columnas de referencia: {stats['reference_headers']}")
            
        except Exception as e:
            print(f"   ❌ Error en transformación: {str(e)}")
            return False
        
        # 4. Probar validadores
        print("\n4️⃣ Probando validadores...")
        
        try:
            # Probar validación de fecha
            date_result = bpm_validator.validate_date('15/01/2024')
            print(f"   ✅ Validación de fecha: {date_result}")
            
            # Probar validación de email
            email_result = bpm_validator.validate_email('test@email.com')
            print(f"   ✅ Validación de email: {email_result}")
            
            # Probar validación de teléfono/NIT
            phone_result = bpm_validator.validate_telefono('3001234567')
            print(f"   ✅ Validación de teléfono: {phone_result}")
            
            # Probar validación de booleano
            bool_result = bpm_validator.validate_boolean('SI')
            print(f"   ✅ Validación de booleano: {bool_result}")
            
        except Exception as e:
            print(f"   ❌ Error en validadores: {str(e)}")
            return False
        
        # 5. Probar procesador completo
        print("\n5️⃣ Probando procesador completo...")
        
        try:
            # Crear archivos temporales
            with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as tmp_input:
                temp_input_path = tmp.name
            
            with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as tmp_output:
                temp_output_path = tmp.name
            
            with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as tmp_error:
                temp_error_path = tmp.name
            
            try:
                # Guardar datos de prueba
                df.to_csv(temp_input_path, index=False, sep=';', encoding='utf-8')
                
                # Procesar archivo
                stats = bpm_processor.process_csv(temp_input_path, temp_output_path, temp_error_path)
                
                print(f"   ✅ Procesamiento completado exitosamente")
                print(f"   📊 Estadísticas del procesamiento:")
                print(f"      - Filas procesadas: {stats['total_rows_processed']}")
                print(f"      - Columnas procesadas: {stats['total_columns_processed']}")
                print(f"      - Errores de validación: {stats['validation_errors']}")
                print(f"      - Tiempo de procesamiento: {stats['processing_time']:.2f} segundos")
                
                # Verificar archivos de salida
                if os.path.exists(temp_output_path):
                    output_size = os.path.getsize(temp_output_path)
                    print(f"      - Archivo de salida: {output_size:,} bytes")
                
                if os.path.exists(temp_error_path):
                    error_size = os.path.getsize(temp_error_path)
                    print(f"      - Archivo de errores: {error_size:,} bytes")
                
            finally:
                # Limpiar archivos temporales
                for temp_file in [temp_input_path, temp_output_path, temp_error_path]:
                    if os.path.exists(temp_file):
                        os.unlink(temp_file)
                
        except Exception as e:
            print(f"   ❌ Error en procesador: {str(e)}")
            return False
        
        # 6. Probar configuración
        print("\n6️⃣ Probando configuración...")
        
        try:
            from repository.proyectos.BPM.config import BPMConfig
            
            config = BPMConfig()
            print(f"   ✅ Configuración creada exitosamente")
            
            # Verificar tipos de datos
            type_mapping = config.get_type_mapping()
            print(f"   📊 Tipos de datos configurados:")
            for data_type, columns in type_mapping.items():
                print(f"      - {data_type}: {len(columns)} columnas")
            
            # Verificar columnas de referencia
            ref_headers = config.get_reference_headers()
            print(f"   📋 Columnas de referencia: {len(ref_headers)}")
            
            # Verificar información del procesador
            processor_info = config.get_processor_info()
            print(f"   🏭 Información del procesador:")
            print(f"      - Nombre: {processor_info['name']}")
            print(f"      - Versión: {processor_info['version']}")
            print(f"      - Descripción: {processor_info['description']}")
            
        except Exception as e:
            print(f"   ❌ Error en configuración: {str(e)}")
            return False
        
        print("\n" + "="*70)
        print("✅ PRUEBA DEL PROCESADOR BPM COMPLETADA EXITOSAMENTE!")
        print("🎯 El procesador BPM está funcionando correctamente")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR GENERAL EN LA PRUEBA: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_bpm_processor()
    if success:
        print("\n🎉 ¡BPM está listo para usar!")
    else:
        print("\n💥 BPM tiene problemas que necesitan ser resueltos")
        sys.exit(1) 