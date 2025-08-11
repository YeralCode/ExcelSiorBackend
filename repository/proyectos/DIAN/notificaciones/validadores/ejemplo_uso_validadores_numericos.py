"""
Ejemplo de uso de los validadores numéricos para DIAN Notificaciones.

Este archivo muestra cómo utilizar los diferentes validadores numéricos
creados para validar valores de entrada.
"""

from validadores_dian_notificaciones import ValidadoresDianNotificaciones

def ejemplo_uso_validadores():
    """Ejemplo completo de uso de todos los validadores numéricos."""
    
    # Crear instancia del validador
    validador = ValidadoresDianNotificaciones()
    
    print("=== EJEMPLOS DE VALIDACIÓN NUMÉRICA ===\n")
    
    # Ejemplos de valores para probar
    valores_prueba = [
        "123.45",
        "1000",
        "0.5",
        "-50.25",
        "abc",
        "12.345",
        "0",
        "100.00",
        "nan",
        "null",
        "",
        "sin registro",
        "50%",
        "$1,234.56",
        "1,000,000"
    ]
    
    print("1. VALIDACIÓN BÁSICA DE NÚMEROS:")
    print("-" * 40)
    for valor in valores_prueba:
        resultado, es_valido = validador.validador_numerico(valor, tipo_numerico="auto")
        print(f"'{valor}' -> '{resultado}' (válido: {es_valido})")
    
    print("\n2. VALIDACIÓN DE ENTEROS:")
    print("-" * 40)
    for valor in valores_prueba:
        resultado, es_valido = validador.validar_entero(valor)
        print(f"'{valor}' -> '{resultado}' (entero válido: {es_valido})")
    
    print("\n3. VALIDACIÓN DE FLOTANTES:")
    print("-" * 40)
    for valor in valores_prueba:
        resultado, es_valido = validador.validar_flotante(valor)
        print(f"'{valor}' -> '{resultado}' (float válido: {es_valido})")
    
    print("\n4. VALIDACIÓN DE PORCENTAJES (0-100):")
    print("-" * 40)
    porcentajes_prueba = ["0", "50", "100", "150", "-10", "25.5", "99.99"]
    for valor in porcentajes_prueba:
        resultado, es_valido = validador.validar_porcentaje(valor)
        print(f"'{valor}' -> '{resultado}' (porcentaje válido: {es_valido})")
    
    print("\n5. VALIDACIÓN DE MONEDA (máximo 2 decimales):")
    print("-" * 40)
    monedas_prueba = ["1000.50", "1234.567", "0.99", "1000000.00", "50.1"]
    for valor in monedas_prueba:
        resultado, es_valido = validador.validar_moneda(valor)
        print(f"'{valor}' -> '{resultado}' (moneda válida: {es_valido})")
    
    print("\n6. VALIDACIÓN CON RANGOS PERSONALIZADOS:")
    print("-" * 40)
    # Validar números entre 0 y 1000 con máximo 3 decimales
    valores_rango = ["500", "1500", "0.123", "999.999", "-50"]
    for valor in valores_rango:
        resultado, es_valido = validador.validador_numerico(
            valor, 
            tipo_numerico="float",
            valor_minimo=0.0,
            valor_maximo=1000.0,
            decimales_maximos=3
        )
        print(f"'{valor}' -> '{resultado}' (rango 0-1000, 3 decimales: {es_valido})")

def ejemplo_validacion_especifica():
    """Ejemplo de validación para casos específicos de DIAN."""
    
    validador = ValidadoresDianNotificaciones()
    
    print("\n=== CASOS ESPECÍFICOS DIAN ===")
    
    # Ejemplo: Validar montos de declaraciones
    montos_declaracion = [
        "1,234,567.89",
        "50000",
        "0.00",
        "1000000.50",
        "abc123"
    ]
    
    print("\nValidación de montos de declaración (0 - 1,000,000,000):")
    for monto in montos_declaracion:
        resultado, es_valido = validador.validador_numerico(
            monto,
            tipo_numerico="float",
            valor_minimo=0.0,
            valor_maximo=1_000_000_000.0,
            decimales_maximos=2
        )
        print(f"'{monto}' -> '{resultado}' (válido: {es_valido})")
    
    # Ejemplo: Validar códigos numéricos (enteros positivos)
    codigos = ["123", "0", "-5", "abc", "12.5"]
    
    print("\nValidación de códigos (enteros positivos):")
    for codigo in codigos:
        resultado, es_valido = validador.validador_numerico(
            codigo,
            tipo_numerico="int",
            valor_minimo=0
        )
        print(f"'{codigo}' -> '{resultado}' (código válido: {es_valido})")

if __name__ == "__main__":
    ejemplo_uso_validadores()
    ejemplo_validacion_especifica() 