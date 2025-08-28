"""
Ejemplo de uso del nuevo sistema simple de procesamiento CSV.
Muestra cómo usar el procesador para diferentes proyectos y módulos.
"""

import os
from simple_csv_processor import CSVProcessor, process_csv_simple
from validators_config import create_processor_for_project

def ejemplo_dian_disciplinarios():
    """Ejemplo de procesamiento para DIAN disciplinarios."""
    print("=== Procesamiento DIAN Disciplinarios ===")
    
    # Opción 1: Usar la función de conveniencia
    try:
        stats = process_csv_simple(
            input_file="archivo_entrada_dian_disciplinarios.csv",
            output_file="archivo_salida_dian_disciplinarios.csv",
            reference_headers=[
                'NOMBRE_ARCHIVO', 'MES_REPORTE', 'EXPEDIENTE', 'FECHA_RADICACION',
                'FECHA_HECHOS', 'IMPLICADO', 'IDENTIFICACION', 'DEPARTAMENTO',
                'CIUDAD', 'DIRECCION_SECCIONAL', 'PROCESO', 'CARGO'
            ],
            type_mapping={
                "datetime": ["FECHA_RADICACION", "FECHA_HECHOS"],
                "str": ["NOMBRE_ARCHIVO", "MES_REPORTE", "EXPEDIENTE", "IMPLICADO", "CARGO"],
                "nit": ["IDENTIFICACION"],
                "departamento": ["DEPARTAMENTO"],
                "ciudad": ["CIUDAD"],
                "direccion_seccional": ["DIRECCION_SECCIONAL"],
                "proceso": ["PROCESO"]
            },
            error_file="errores_dian_disciplinarios.csv"
        )
        
        print(f"Procesamiento completado: {stats}")
        
    except Exception as e:
        print(f"Error: {e}")
    
    # Opción 2: Usar el procesador configurado automáticamente
    try:
        processor = create_processor_for_project('DIAN', 'disciplinarios')
        
        stats = processor.process_csv(
            input_file="archivo_entrada_dian_disciplinarios.csv",
            output_file="archivo_salida_dian_disciplinarios_v2.csv",
            error_file="errores_dian_disciplinarios_v2.csv"
        )
        
        print(f"Procesamiento con procesador configurado: {stats}")
        
    except Exception as e:
        print(f"Error: {e}")


def ejemplo_dian_notificaciones():
    """Ejemplo de procesamiento para DIAN notificaciones."""
    print("\n=== Procesamiento DIAN Notificaciones ===")
    
    try:
        processor = create_processor_for_project('DIAN', 'notificaciones')
        
        stats = processor.process_csv(
            input_file="archivo_entrada_dian_notificaciones.csv",
            output_file="archivo_salida_dian_notificaciones.csv",
            error_file="errores_dian_notificaciones.csv"
        )
        
        print(f"Procesamiento DIAN notificaciones: {stats}")
        
    except Exception as e:
        print(f"Error: {e}")


def ejemplo_coljuegos_disciplinarios():
    """Ejemplo de procesamiento para COLJUEGOS disciplinarios."""
    print("\n=== Procesamiento COLJUEGOS Disciplinarios ===")
    
    try:
        processor = create_processor_for_project('COLJUEGOS', 'disciplinarios')
        
        stats = processor.process_csv(
            input_file="archivo_entrada_coljuegos_disciplinarios.csv",
            output_file="archivo_salida_coljuegos_disciplinarios.csv",
            error_file="errores_coljuegos_disciplinarios.csv"
        )
        
        print(f"Procesamiento COLJUEGOS disciplinarios: {stats}")
        
    except Exception as e:
        print(f"Error: {e}")


def ejemplo_ugpp_pqr():
    """Ejemplo de procesamiento para UGPP PQR."""
    print("\n=== Procesamiento UGPP PQR ===")
    
    try:
        processor = create_processor_for_project('UGPP', 'PQR')
        
        stats = processor.process_csv(
            input_file="archivo_entrada_ugpp_pqr.csv",
            output_file="archivo_salida_ugpp_pqr.csv",
            error_file="errores_ugpp_pqr.csv"
        )
        
        print(f"Procesamiento UGPP PQR: {stats}")
        
    except Exception as e:
        print(f"Error: {e}")


def ejemplo_con_validadores_personalizados():
    """Ejemplo de uso con validadores personalizados."""
    print("\n=== Procesamiento con Validadores Personalizados ===")
    
    from simple_csv_processor import ChoiceValidator, DateValidator
    
    # Crear validadores personalizados
    custom_validators = {
        'departamento_personalizado': ChoiceValidator([
            'DEPARTAMENTO_A', 'DEPARTAMENTO_B', 'DEPARTAMENTO_C'
        ], {
            'DEPT_A': 'DEPARTAMENTO_A',
            'DEPT_B': 'DEPARTAMENTO_B'
        }),
        'fecha_personalizada': DateValidator()
    }
    
    try:
        processor = create_processor_for_project(
            'DIAN', 
            'disciplinarios',
            custom_validators=custom_validators
        )
        
        stats = processor.process_csv(
            input_file="archivo_entrada_personalizado.csv",
            output_file="archivo_salida_personalizado.csv",
            error_file="errores_personalizado.csv"
        )
        
        print(f"Procesamiento con validadores personalizados: {stats}")
        
    except Exception as e:
        print(f"Error: {e}")


def ejemplo_deteccion_automatica_delimitador():
    """Ejemplo de detección automática de delimitador."""
    print("\n=== Detección Automática de Delimitador ===")
    
    try:
        processor = create_processor_for_project('DIAN', 'disciplinarios')
        
        # El delimitador se detecta automáticamente
        stats = processor.process_csv(
            input_file="archivo_con_delimitador_coma.csv",  # Archivo con delimitador ','
            output_file="archivo_salida_delimitador_detectado.csv",
            error_file="errores_delimitador_detectado.csv"
        )
        
        print(f"Procesamiento con delimitador detectado: {stats}")
        
    except Exception as e:
        print(f"Error: {e}")


def ejemplo_procesamiento_lote():
    """Ejemplo de procesamiento en lote de múltiples archivos."""
    print("\n=== Procesamiento en Lote ===")
    
    # Lista de archivos a procesar
    archivos_entrada = [
        "archivo_1.csv",
        "archivo_2.csv",
        "archivo_3.csv"
    ]
    
    try:
        processor = create_processor_for_project('DIAN', 'disciplinarios')
        
        for i, archivo_entrada in enumerate(archivos_entrada, 1):
            if os.path.exists(archivo_entrada):
                archivo_salida = f"archivo_salida_{i}.csv"
                archivo_errores = f"errores_{i}.csv"
                
                print(f"Procesando {archivo_entrada}...")
                
                stats = processor.process_csv(
                    input_file=archivo_entrada,
                    output_file=archivo_salida,
                    error_file=archivo_errores
                )
                
                print(f"  - Filas procesadas: {stats['filas_procesadas']}")
                print(f"  - Errores: {stats['total_errores']}")
            else:
                print(f"Archivo {archivo_entrada} no encontrado")
                
    except Exception as e:
        print(f"Error en procesamiento en lote: {e}")


def mostrar_informacion_procesador():
    """Muestra información de los procesadores disponibles."""
    print("\n=== Información de Procesadores Disponibles ===")
    
    proyectos = ['DIAN', 'COLJUEGOS', 'UGPP']
    modulos = ['disciplinarios', 'PQR', 'notificaciones']
    
    for proyecto in proyectos:
        print(f"\n{proyecto}:")
        for modulo in modulos:
            try:
                processor = create_processor_for_project(proyecto, modulo)
                print(f"  - {modulo}: {len(processor.reference_headers)} headers, {len(processor.validators)} validadores")
            except:
                print(f"  - {modulo}: No disponible")


if __name__ == "__main__":
    # Mostrar información de procesadores disponibles
    mostrar_informacion_procesador()
    
    # Ejemplos de uso
    ejemplo_dian_disciplinarios()
    ejemplo_dian_notificaciones()
    ejemplo_coljuegos_disciplinarios()
    ejemplo_ugpp_pqr()
    ejemplo_con_validadores_personalizados()
    ejemplo_deteccion_automatica_delimitador()
    ejemplo_procesamiento_lote()
    
    print("\n=== Todos los ejemplos completados ===") 