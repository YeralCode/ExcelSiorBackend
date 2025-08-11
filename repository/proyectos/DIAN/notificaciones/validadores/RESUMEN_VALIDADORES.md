# Validadores Numéricos Mejorados para DIAN Notificaciones

## Resumen de Mejoras

Se han mejorado los validadores numéricos para manejar casos problemáticos como "N/A" y otros valores no numéricos que estaban pasando incorrectamente.

## Funcionalidades Implementadas

### 1. Validación Estricta de Tipos
- **Rechaza valores como "N/A"**: Ahora detecta y rechaza valores como "N/A", "n/a", "NA", "na"
- **Rechaza texto mixto**: Valores como "abc123", "123abc" son rechazados
- **Rechaza texto puro**: "ABC", "test", "prueba" son rechazados

### 2. Validación de Enteros (`validar_entero`)
```python
# Casos válidos
"123" -> "123" (True)
"0" -> "0" (True)
"-50" -> "-50" (True)
"1000.00" -> "1000" (True)

# Casos inválidos
"N/A" -> "" (False)
"abc123" -> "" (False)
"123.45" -> "123.45" (False)  # No es entero
```

### 3. Validación de Flotantes (`validar_flotante`)
```python
# Casos válidos
"123.45" -> "123.45" (True)
"0.5" -> "0.5" (True)
"1000" -> "1000.0" (True)
"1,234.56" -> "1234.56" (True)
"$1,234.56" -> "1234.56" (True)
"50%" -> "50.0" (True)

# Casos inválidos
"N/A" -> "" (False)
"abc123" -> "" (False)
"12.34.56" -> "12.34.56" (False)  # Formato inválido
```

## Características de Seguridad

### 1. Validación de Caracteres Permitidos
- Solo permite: números, espacios, signos (-), puntos (.), comas (,), símbolos de moneda ($), porcentajes (%)
- Rechaza cualquier otro carácter

### 2. Manejo de Valores Nulos
- Rechaza: `"nan"`, `"null"`, `"none"`, `""`, `"sin registro"`, `"desconocido"`, `"no aplica"`, `"n/a"`, `"na"`

### 3. Validación de Conversión
- Verifica que el valor se pueda convertir a float/int
- Valida el formato final del número

## Casos de Uso Comunes

### Para Montos Monetarios
```python
resultado, es_valido = validador.validar_flotante("$1,234.56")
# resultado = "1234.56", es_valido = True
```

### Para Porcentajes
```python
resultado, es_valido = validador.validar_flotante("50%")
# resultado = "50.0", es_valido = True
```

### Para Códigos Numéricos
```python
resultado, es_valido = validador.validar_entero("123")
# resultado = "123", es_valido = True
```

## Archivos Modificados

1. **`validadores_dian_notificaciones.py`**: Validadores principales mejorados
2. **`test_validacion_mejorada.py`**: Script de pruebas
3. **`ejemplo_uso_validadores_numericos.py`**: Ejemplos de uso

## Resultados de Pruebas

✅ **Casos problemáticos rechazados correctamente:**
- "N/A", "n/a", "NA", "na"
- "abc123", "123abc"
- "ABC", "test", "prueba"
- "sin datos", "no disponible"

✅ **Casos válidos que siguen funcionando:**
- Números enteros y flotantes
- Valores con formato monetario
- Porcentajes
- Números con separadores de miles 