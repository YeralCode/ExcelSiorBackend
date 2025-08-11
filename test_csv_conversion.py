#!/usr/bin/env python3
"""
Script de prueba para verificar la conversión de CSV.
"""

import tempfile
import os

def crear_archivo_prueba():
    """Crea un archivo CSV de prueba con separador |@"""
    contenido_prueba = """campo1|@campo2|@campo3
valor1|@valor2|@valor3
dato1|@dato2|@dato3"""
    
    # Crear archivo temporal
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
        f.write(contenido_prueba)
        return f.name

def simular_conversion(archivo_entrada, antiguo_separador="|@", nuevo_separador="|"):
    """Simula la conversión de separadores"""
    
    # Leer archivo de entrada
    with open(archivo_entrada, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Crear archivo de salida
    nombre_base = os.path.splitext(os.path.basename(archivo_entrada))[0]
    archivo_salida = f"{nombre_base}_convertido.csv"
    
    # Procesar línea por línea
    with open(archivo_salida, 'w', encoding='utf-8') as f:
        lineas = contenido.split('\n')
        for linea in lineas:
            if linea.strip():  # Solo procesar líneas no vacías
                campos = linea.strip().split(antiguo_separador)
                nueva_linea = nuevo_separador.join(campos)
                f.write(nueva_linea + "\n")
    
    return archivo_salida

def test_conversion():
    """Prueba la conversión de CSV"""
    
    print("🧪 PRUEBA DE CONVERSIÓN CSV")
    print("=" * 40)
    
    # Crear archivo de prueba
    archivo_prueba = crear_archivo_prueba()
    print(f"📁 Archivo de prueba creado: {archivo_prueba}")
    
    # Mostrar contenido original
    print("\n📄 CONTENIDO ORIGINAL:")
    print("-" * 20)
    with open(archivo_prueba, 'r', encoding='utf-8') as f:
        contenido_original = f.read()
        print(contenido_original)
    
    # Simular conversión
    archivo_convertido = simular_conversion(archivo_prueba, "|@", "|")
    print(f"\n🔄 Archivo convertido: {archivo_convertido}")
    
    # Mostrar contenido convertido
    print("\n📄 CONTENIDO CONVERTIDO:")
    print("-" * 20)
    with open(archivo_convertido, 'r', encoding='utf-8') as f:
        contenido_convertido = f.read()
        print(contenido_convertido)
    
    # Verificar que no esté vacío
    if contenido_convertido.strip():
        print("\n✅ CONVERSIÓN EXITOSA")
        print("El archivo convertido no está vacío y contiene datos.")
    else:
        print("\n❌ ERROR: El archivo convertido está vacío")
    
    # Limpiar archivos temporales
    os.unlink(archivo_prueba)
    os.unlink(archivo_convertido)
    
    print("\n🏁 PRUEBA COMPLETADA")

if __name__ == "__main__":
    test_conversion() 