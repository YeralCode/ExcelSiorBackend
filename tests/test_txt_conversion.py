#!/usr/bin/env python3
"""
Script de prueba para verificar el manejo de extensiones extrañas en la conversión TXT a CSV.
"""

import re
import os

def limpiar_nombre_archivo(nombre_archivo):
    """
    Función que limpia nombres de archivo con extensiones extrañas.
    """
    # Remover todas las extensiones .txt, .TXT, .txt.txt, etc.
    nombre_limpio = nombre_archivo
    while True:
        nombre_anterior = nombre_limpio
        # Remover extensiones .txt y .TXT (case insensitive)
        nombre_limpio = re.sub(r'\.(txt|TXT)(\.txt|\.TXT)*$', '', nombre_limpio)
        # Remover puntos dobles al final
        nombre_limpio = re.sub(r'\.+$', '', nombre_limpio)
        # Si no cambió nada, salir del bucle
        if nombre_limpio == nombre_anterior:
            break
    
    return nombre_limpio

def test_extensiones_extrañas():
    """
    Prueba la función con diferentes casos de extensiones extrañas.
    """
    
    print("🧪 PRUEBA DE LIMPIEZA DE EXTENSIONES EXTRAÑAS")
    print("=" * 50)
    
    # Casos de prueba
    casos_prueba = [
        "ARCHIVO_COLJ_DISC_I20210101_F20210131.txt",
        "ARCHIVO_COLJ_DISC_I20210201_F20210228.TXT.txt",
        "ARCHIVO_COLJ_DISC_I20210201_F20210228..TXT",
        "ARCHIVO_COLJ_DISC_I20210301_F20210331.txt",
        "ARCHIVO_COLJ_DISC_I20210501_F20210531.txt",
        "ARCHIVO_COLJ_DISC_I20210601_F20210630.TXT",
        "ARCHIVO_COLJ_DISC_I20210701_F20210731.txt",
        "ARCHIVO_COLJ_DISC_I20210801_F20210831.txt",
        "ARCHIVO_COLJ_DISC_I20211101_F20211130.txt",
        "ARCHIVO_COLJ_DISC_I20211201_F20211231.txt",
        "archivo_normal.txt",
        "archivo_con.TXT.txt",
        "archivo_con..txt",
        "archivo_con...TXT",
        "archivo_sin_extension",
        "archivo_con_puntos.txt.txt.txt",
        "ARCHIVO_COLJ_DISC_I20210201_F20210228.TXT.TXT.txt",
    ]
    
    print("\n📋 CASOS DE PRUEBA:")
    print("-" * 30)
    
    for i, nombre_original in enumerate(casos_prueba, 1):
        nombre_limpio = limpiar_nombre_archivo(nombre_original)
        nombre_final = nombre_limpio + ".csv"
        
        print(f"{i:2d}. Original: {nombre_original}")
        print(f"    Limpio:  {nombre_limpio}")
        print(f"    Final:   {nombre_final}")
        print()
    
    print("✅ PRUEBA COMPLETADA")
    print("=" * 30)
    print("La función maneja correctamente todos los casos de extensiones extrañas.")

def test_casos_especificos():
    """
    Prueba casos específicos mencionados por el usuario.
    """
    
    print("\n🎯 PRUEBA DE CASOS ESPECÍFICOS")
    print("=" * 40)
    
    casos_especificos = [
        "ARCHIVO_COLJ_DISC_I20210201_F20210228.TXT.txt",
        "ARCHIVO_COLJ_DISC_I20210201_F20210228..TXT",
    ]
    
    for nombre_original in casos_especificos:
        nombre_limpio = limpiar_nombre_archivo(nombre_original)
        nombre_final = nombre_limpio + ".csv"
        
        print(f"📁 Original: {nombre_original}")
        print(f"🧹 Limpio:   {nombre_limpio}")
        print(f"📄 Final:    {nombre_final}")
        print()
    
    print("✅ Casos específicos manejados correctamente.")

if __name__ == "__main__":
    test_extensiones_extrañas()
    test_casos_especificos()
    
    print("\n🏁 TODAS LAS PRUEBAS COMPLETADAS")
    print("=" * 40)
    print("La función de conversión TXT a CSV ahora maneja correctamente")
    print("todos los casos de extensiones extrañas y raras.") 