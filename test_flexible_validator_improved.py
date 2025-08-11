#!/usr/bin/env python3
"""
Script de prueba para verificar la nueva lógica del FlexibleChoiceValidator.
"""

import sys
import os
import logging

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from repository.proyectos.base.validators import FlexibleChoiceValidator, normalize_location_name

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_departamento_validator():
    """Prueba el validador de departamento con casos problemáticos."""
    
    logger.info("=== PRUEBA DE VALIDADOR DE DEPARTAMENTO MEJORADO ===")
    
    # Valores válidos de departamento
    choices = [
        "ANTIOQUIA", "ATLANTICO", "BOGOTA", "BOLIVAR", "BOYACA", "CALDAS", 
        "CAQUETA", "CAUCA", "CESAR", "CORDOBA", "CUNDINAMARCA", "CHOCO",
        "HUILA", "LA GUAJIRA", "MAGDALENA", "META", "NARIÑO", "NORTE DE SANTANDER", 
        "QUINDIO", "RISARALDA", "SANTANDER", "SUCRE", "TOLIMA", "VALLE DEL CAUCA", 
        "VAUPES", "VICHADA", "AMAZONAS", "GUAINIA", "GUAVIARE", "PUTUMAYO", 
        "SAN ANDRES Y PROVIDENCIA", "ARAUCA", "CASANARE"
    ]
    
    # Diccionario de reemplazos
    replacement_map = {
        "GUAJIRA": "LA GUAJIRA",
        "N.SANTANDER": "NORTE DE SANTANDER",
        "NORTE SANTANDER": "NORTE DE SANTANDER",
        "NSANTANDER": "NORTE DE SANTANDER",
        "VALLE": "VALLE DEL CAUCA",
        "SAN_ANDRES_Y_PROVIDENCIA": "SAN ANDRES Y PROVIDENCIA",
        "SAN ANDRES": "SAN ANDRES Y PROVIDENCIA",
        "BOGOTA DC": "BOGOTA",
        "BOGOTA D.C.": "BOGOTA",
        "BOGOTÁ D.C.": "BOGOTA",
        "BOGOTÁ DC": "BOGOTA",
        "BOGOTÁ D C": "BOGOTA",
        "BOGOTÁ DISTRITO CAPITAL": "BOGOTA",
        "DISTRITO CAPITAL": "BOGOTA",
        "D.C.": "BOGOTA",
        "DC": "BOGOTA",
        "BOGOTÁ": "BOGOTA",
        "CUNDINAMRCA": "CUNDINAMARCA",
        "CUNDINAMCA": "CUNDINAMARCA",
        "CUNDINAMRACA": "CUNDINAMARCA",
    }
    
    # Crear validador
    validator = FlexibleChoiceValidator(
        choices=choices,
        normalizer=normalize_location_name,
        replacement_map=replacement_map
    )
    
    # Casos de prueba
    test_cases = [
        # Casos que deben ser reemplazados
        ("Cundinamrca", "CUNDINAMARCA"),
        ("CUNDINAMRCA", "CUNDINAMARCA"),
        ("cundinamrca", "CUNDINAMARCA"),
        ("Bogotá D.C.", "BOGOTA"),
        ("BOGOTÁ D.C.", "BOGOTA"),
        ("bogotá d.c.", "BOGOTA"),
        ("Guajira", "LA GUAJIRA"),
        ("GUAJIRA", "LA GUAJIRA"),
        ("guajira", "LA GUAJIRA"),
        
        # Casos que ya están correctos
        ("Cundinamarca", "CUNDINAMARCA"),
        ("CUNDINAMARCA", "CUNDINAMARCA"),
        ("cundinamarca", "CUNDINAMARCA"),
        ("Bogota", "BOGOTA"),
        ("BOGOTA", "BOGOTA"),
        ("bogota", "BOGOTA"),
        
        # Casos que no están en la lista pero deben devolver el valor normalizado
        ("Valle del Cauca", "VALLE DEL CAUCA"),  # Ya está en la lista
        ("VALLE DEL CAUCA", "VALLE DEL CAUCA"),  # Ya está en la lista
        ("valle del cauca", "VALLE DEL CAUCA"),  # Ya está en la lista
        ("Departamento Inventado", "DEPARTAMENTO INVENTADO"),  # No está en la lista
        ("DEPARTAMENTO INVENTADO", "DEPARTAMENTO INVENTADO"),  # No está en la lista
    ]
    
    logger.info(f"Probando {len(test_cases)} casos de departamento...")
    
    for i, (input_value, expected_output) in enumerate(test_cases, 1):
        logger.info(f"\n--- Prueba {i}: '{input_value}' (esperado: '{expected_output}') ---")
        
        # Limpiar errores previos
        validator.clear_errors()
        
        # Validar
        result = validator.validate(input_value)
        errors = validator.get_errors()
        
        logger.info(f"  Resultado: '{result}'")
        if errors:
            logger.info(f"  Errores: {errors}")
        
        # Verificar resultado
        if result == expected_output:
            logger.info("  ✅ CORRECTO")
        else:
            logger.info(f"  ❌ INCORRECTO - Esperado: '{expected_output}'")

def test_ciudad_validator():
    """Prueba el validador de ciudad con casos problemáticos."""
    
    logger.info("\n=== PRUEBA DE VALIDADOR DE CIUDAD MEJORADO ===")
    
    # Valores válidos de ciudad
    choices = [
        'LETICIA', 'MEDELLIN', 'TURBO', 'URABA', 'ARAUCA', 'SARAVENA',
        'BARRANQUILLA', 'BOGOTA', 'CARTAGENA', 'SOGAMOSO', 'TUNJA', 'MANIZALES',
        'FLORENCIA', 'YOPAL', 'POPAYAN', 'VALLEDUPAR', 'QUIBDO', 'MONTERIA',
        'GIRARDOT', 'INIRIDA', 'SAN JOSE DEL GUAVIARE', 'NEIVA', 'MAICAO',
        'RIOHACHA', 'SANTA MARTA', 'VILLAVICENCIO', 'IPIALES', 'PASTO',
        'TUMACO', 'CUCUTA', 'PAMPLONA', 'POR DETERMINAR', 'PUERTO ASIS',
        'ARMENIA', 'LA TEBAIDA', 'PEREIRA', 'SAN ANDRES', 'BARRANCABERMEJA',
        'BUCARAMANGA', 'SINCELEJO', 'IBAGUE', 'BUENAVENTURA', 'CALI',
        'PALMIRA', 'TULUA', 'PUERTO CARREÑO'
    ]
    
    # Diccionario de reemplazos
    replacement_map = {
        "MANIZALEZ": "MANIZALES",
        "BARRAQUILLA": "BARRANQUILLA",
        "SAN_JOSE": "SAN JOSE DEL GUAVIARE",
        "SANTAMARTA": "SANTA MARTA",
        "SAN_ANDRES": "SAN ANDRES",
        "SANTA_MARTA": "SANTA MARTA",
        "PUERTO_ASÍS": "PUERTO ASIS",
        "BOGOTA D.C.": "BOGOTA",
        "BOGOTÁ D.C.": "BOGOTA",
        "BOGOTÁ DC": "BOGOTA",
        "BOGOTÁ D C": "BOGOTA",
        "BOGOTÁ DISTRITO CAPITAL": "BOGOTA",
        "DISTRITO CAPITAL": "BOGOTA",
        "D.C.": "BOGOTA",
        "DC": "BOGOTA",
        "BOGOTÁ": "BOGOTA",
    }
    
    # Crear validador
    validator = FlexibleChoiceValidator(
        choices=choices,
        normalizer=normalize_location_name,
        replacement_map=replacement_map
    )
    
    # Casos de prueba
    test_cases = [
        # Casos que deben ser reemplazados
        ("Bogotá D.C.", "BOGOTA"),
        ("BOGOTÁ D.C.", "BOGOTA"),
        ("bogotá d.c.", "BOGOTA"),
        ("Manizalez", "MANIZALES"),
        ("MANIZALEZ", "MANIZALES"),
        ("manizalez", "MANIZALES"),
        
        # Casos que ya están correctos
        ("Bogota", "BOGOTA"),
        ("BOGOTA", "BOGOTA"),
        ("bogota", "BOGOTA"),
        ("Medellin", "MEDELLIN"),
        ("MEDELLIN", "MEDELLIN"),
        ("medellin", "MEDELLIN"),
        
        # Casos que no están en la lista pero deben devolver el valor normalizado
        ("Ciudad Inventada", "CIUDAD INVENTADA"),
        ("CIUDAD INVENTADA", "CIUDAD INVENTADA"),
        ("ciudad inventada", "CIUDAD INVENTADA"),
    ]
    
    logger.info(f"Probando {len(test_cases)} casos de ciudad...")
    
    for i, (input_value, expected_output) in enumerate(test_cases, 1):
        logger.info(f"\n--- Prueba {i}: '{input_value}' (esperado: '{expected_output}') ---")
        
        # Limpiar errores previos
        validator.clear_errors()
        
        # Validar
        result = validator.validate(input_value)
        errors = validator.get_errors()
        
        logger.info(f"  Resultado: '{result}'")
        if errors:
            logger.info(f"  Errores: {errors}")
        
        # Verificar resultado
        if result == expected_output:
            logger.info("  ✅ CORRECTO")
        else:
            logger.info(f"  ❌ INCORRECTO - Esperado: '{expected_output}'")

def test_edge_cases():
    """Prueba casos extremos y valores especiales."""
    
    logger.info("\n=== PRUEBA DE CASOS EXTREMOS ===")
    
    # Valores válidos simples
    choices = ["BOGOTA", "MEDELLIN", "CALI"]
    
    # Diccionario de reemplazos simple
    replacement_map = {
        "BOGOTÁ": "BOGOTA",
        "BOGOTA D.C.": "BOGOTA",
    }
    
    # Crear validador
    validator = FlexibleChoiceValidator(
        choices=choices,
        normalizer=normalize_location_name,
        replacement_map=replacement_map
    )
    
    # Casos extremos
    test_cases = [
        # Valores None y vacíos
        (None, None),
        ("", ""),
        ("   ", "   "),
        
        # Valores con espacios extra
        ("  Bogotá D.C.  ", "BOGOTA"),
        ("  BOGOTÁ  ", "BOGOTA"),
        ("  bogota  ", "BOGOTA"),
        
        # Valores que no están en la lista
        ("Ciudad Nueva", "CIUDAD NUEVA"),
        ("CIUDAD NUEVA", "CIUDAD NUEVA"),
        ("ciudad nueva", "CIUDAD NUEVA"),
    ]
    
    logger.info(f"Probando {len(test_cases)} casos extremos...")
    
    for i, (input_value, expected_output) in enumerate(test_cases, 1):
        logger.info(f"\n--- Prueba {i}: '{input_value}' (esperado: '{expected_output}') ---")
        
        # Limpiar errores previos
        validator.clear_errors()
        
        # Validar
        result = validator.validate(input_value)
        errors = validator.get_errors()
        
        logger.info(f"  Resultado: '{result}'")
        if errors:
            logger.info(f"  Errores: {errors}")
        
        # Verificar resultado
        if result == expected_output:
            logger.info("  ✅ CORRECTO")
        else:
            logger.info(f"  ❌ INCORRECTO - Esperado: '{expected_output}'")

if __name__ == "__main__":
    logger.info("Iniciando prueba del FlexibleChoiceValidator mejorado...")
    test_departamento_validator()
    test_ciudad_validator()
    test_edge_cases()
    logger.info("✅ Prueba completada exitosamente") 