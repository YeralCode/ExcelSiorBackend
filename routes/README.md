# Estructura Modular de Rutas

Este directorio contiene las rutas de la API organizadas de manera modular para mejorar la mantenibilidad y legibilidad del código.

## Archivos de Rutas

### `conversion.py`
Contiene todas las rutas relacionadas con la conversión de archivos:
- **CSV a otro separador**: Convierte archivos CSV de un separador a otro
- **SAV a CSV**: Convierte archivos SPSS (.sav) a CSV
- **TXT a CSV**: Convierte archivos de texto a CSV
- **XLSX a CSV**: Convierte archivos Excel a CSV (con y sin columna de mes de reporte)
- **Unir archivos CSV en XLSX**: Consolida múltiples archivos CSV en un archivo Excel

### `consolidacion.py`
Contiene las rutas para la consolidación de archivos:
- **Unir CSV**: Combina múltiples archivos CSV en uno solo

### `normalizacion.py`
Contiene las rutas para la normalización de columnas por entidad:
- **COLJUEGOS Disciplinarios**: Normalización de archivos disciplinarios de COLJUEGOS
- **COLJUEGOS PQR**: Normalización de archivos PQR de COLJUEGOS
- **DIAN Disciplinarios**: Normalización de archivos disciplinarios de DIAN
- **DIAN PQR**: Normalización de archivos PQR de DIAN

## Beneficios de la Estructura Modular

1. **Separación de responsabilidades**: Cada archivo maneja una funcionalidad específica
2. **Mantenibilidad**: Es más fácil encontrar y modificar rutas específicas
3. **Escalabilidad**: Facilita agregar nuevas funcionalidades sin afectar el código existente
4. **Legibilidad**: El código es más fácil de leer y entender
5. **Reutilización**: Los módulos pueden ser reutilizados en otros proyectos

## Uso

Las rutas se importan automáticamente en `main.py` usando:

```python
from routes import conversion, consolidacion, normalizacion

app.include_router(conversion.router)
app.include_router(consolidacion.router)
app.include_router(normalizacion.router)
```

Cada router tiene su propio prefijo y tags para una mejor organización en la documentación de la API. 