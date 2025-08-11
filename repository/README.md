# Repository - ExcelSior API

## Descripción

El módulo `repository` contiene todos los procesadores y transformadores especializados para el manejo de archivos en ExcelSior API. Esta estructura ha sido completamente reorganizada siguiendo las mejores prácticas de programación.

## Estructura

```
repository/
├── __init__.py                    # Paquete principal
├── processors/                    # Procesadores de archivos
│   ├── __init__.py
│   ├── csv_processor.py          # Procesamiento de CSV
│   ├── excel_processor.py        # Procesamiento de Excel
│   └── consolidation_processor.py # Consolidación de archivos
├── transformers/                  # Transformadores
│   ├── __init__.py
│   ├── format_transformer.py     # Conversiones de formato
│   └── encoding_transformer.py   # Conversiones de codificación
├── projects/                      # Código específico por proyecto
│   ├── dian/
│   ├── coljuegos/
│   └── ugpp/
├── legacy/                        # Código legacy (temporal)
│   ├── unir_csv_en_excel.py
│   ├── unit_todos_csv.py
│   └── transformar/
├── example_usage.py              # Ejemplos de uso
├── migration_guide.md            # Guía de migración
└── README.md                     # Esta documentación
```

## Procesadores (Processors)

### CSVProcessor

Procesador especializado para archivos CSV con funcionalidades avanzadas.

**Características:**
- Detección automática de codificación
- Detección automática de delimitadores
- Extracción de metadatos de nombres de archivo
- Limpieza automática de datos
- Validación de estructura
- Estadísticas detalladas

**Ejemplo de uso:**
```python
from repository.processors.csv_processor import CSVProcessor

processor = CSVProcessor()
headers, data = processor.read_csv_file(file_path)
cleaned_data = processor.clean_data(data)
processor.write_csv_file(output_path, headers, cleaned_data)
```

### ExcelProcessor

Procesador especializado para archivos Excel con manejo de límites.

**Características:**
- Lectura de múltiples hojas
- División automática de archivos grandes
- Validación de estructura
- Información detallada de archivos
- Manejo de límites de Excel

**Ejemplo de uso:**
```python
from repository.processors.excel_processor import ExcelProcessor

processor = ExcelProcessor()
headers, data = processor.read_excel_file(file_path)
sheets = processor.split_large_dataframe(headers, data, "mi_hoja")
processor.write_excel_file(output_path, sheets)
```

### ConsolidationProcessor

Procesador para consolidación de múltiples archivos.

**Características:**
- Consolidación de archivos CSV
- Consolidación de archivos mixtos
- Validación previa a consolidación
- Estadísticas de consolidación
- Manejo de metadatos

**Ejemplo de uso:**
```python
from repository.processors.consolidation_processor import ConsolidationProcessor

processor = ConsolidationProcessor()
result = processor.consolidate_csv_files(csv_files, output_file)
print(f"Archivos procesados: {result['processed_files']}")
```

## Transformadores (Transformers)

### FormatTransformer

Transformador para conversiones entre diferentes formatos de archivo.

**Características:**
- Conversión CSV a CSV con cambio de delimitador
- Conversión SAV a CSV
- Conversión TXT a CSV
- Conversión Excel a CSV
- Procesamiento en lote
- Validación de conversiones

**Ejemplo de uso:**
```python
from repository.transformers.format_transformer import FormatTransformer

transformer = FormatTransformer()
result = transformer.csv_to_csv_with_delimiter_change(
    input_file, output_file, '|@', '|', add_metadata=True
)
```

### EncodingTransformer

Transformador para manejo de codificaciones de archivos.

**Características:**
- Detección automática de codificación
- Conversión entre codificaciones
- Arreglo automático de problemas de codificación
- Estadísticas de codificación
- Procesamiento en lote

**Ejemplo de uso:**
```python
from repository.transformers.encoding_transformer import EncodingTransformer

transformer = EncodingTransformer()
encoding_info = transformer.detect_encoding(file_path)
result = transformer.convert_encoding(input_file, output_file, 'utf-8')
```

## Características Principales

### 1. Manejo Robusto de Errores

Todos los procesadores y transformadores incluyen:
- Excepciones específicas y descriptivas
- Logging estructurado de errores
- Recuperación automática cuando es posible
- Información detallada de errores

```python
from utils.exceptions import handle_exception

@handle_exception
def mi_funcion():
    # Los errores se manejan automáticamente
    pass
```

### 2. Logging Estructurado

Cada operación se registra con información contextual:
- Operación realizada
- Archivos involucrados
- Métricas de rendimiento
- Información de contexto

```python
self.log_operation("processing_file", f"Procesando archivo: {filename}")
```

### 3. Validación Automática

Validación en múltiples niveles:
- Validación de archivos antes del procesamiento
- Validación de estructura de datos
- Validación de formatos
- Validación de codificaciones

### 4. Configuración Centralizada

Todas las configuraciones se manejan desde `config/settings.py`:
- Delimitadores por defecto
- Codificaciones soportadas
- Límites de archivos
- Configuraciones por proyecto

## Casos de Uso Comunes

### 1. Procesamiento de Archivo CSV

```python
from repository.processors.csv_processor import CSVProcessor

def procesar_csv(file_path: Path):
    processor = CSVProcessor()
    
    # Leer y procesar
    headers, data = processor.read_csv_file(file_path)
    cleaned_data = processor.clean_data(data)
    
    # Extraer metadatos
    date_info = processor.extract_date_from_filename(file_path.name)
    
    # Agregar metadatos
    new_headers, new_data = processor.add_metadata_columns(
        headers, cleaned_data, file_path.name, date_info
    )
    
    # Guardar resultado
    output_path = file_path.parent / f"procesado_{file_path.name}"
    processor.write_csv_file(output_path, new_headers, new_data)
    
    return output_path
```

### 2. Consolidación de Múltiples Archivos

```python
from repository.processors.consolidation_processor import ConsolidationProcessor

def consolidar_archivos(archivos: List[Path], output_file: Path):
    processor = ConsolidationProcessor()
    
    # Validar archivos
    validation = processor.validate_consolidation(archivos)
    if validation['invalid_files'] > 0:
        print(f"Advertencia: {validation['invalid_files']} archivos inválidos")
    
    # Consolidar
    result = processor.consolidate_csv_files(archivos, output_file)
    
    return result
```

### 3. Conversión de Formatos

```python
from repository.transformers.format_transformer import FormatTransformer

def convertir_formato(input_file: Path, output_format: str):
    transformer = FormatTransformer()
    
    if output_format == 'csv':
        output_file = input_file.with_suffix('.csv')
        return transformer.xlsx_to_csv(input_file, output_file)
    elif output_format == 'excel':
        output_file = input_file.with_suffix('.xlsx')
        return transformer.csv_to_excel(input_file, output_file)
```

### 4. Arreglo de Problemas de Codificación

```python
from repository.transformers.encoding_transformer import EncodingTransformer

def arreglar_codificacion(file_path: Path):
    transformer = EncodingTransformer()
    
    # Intentar arreglar automáticamente
    result = transformer.fix_encoding_issues(file_path)
    
    if result['success']:
        print(f"Archivo arreglado: {result['fixed_encoding']}")
        return result['output_file']
    else:
        print("No se pudo arreglar automáticamente")
        return None
```

## Migración desde Código Legacy

### Archivos Legacy

Los archivos originales se han movido a `repository/legacy/`:
- `legacy/unir_csv_en_excel.py`
- `legacy/unit_todos_csv.py`
- `legacy/transformar/`

### Guía de Migración

Consulta `migration_guide.md` para una guía detallada de migración.

### Ejemplos de Migración

**Antes:**
```python
import pandas as pd
import csv

def procesar_archivo(file_path):
    df = pd.read_csv(file_path)
    # procesamiento manual
    return df
```

**Después:**
```python
from repository.processors.csv_processor import CSVProcessor

def procesar_archivo(file_path):
    processor = CSVProcessor()
    headers, data = processor.read_csv_file(file_path)
    return processor.clean_data(data)
```

## Testing

### Ejecutar Tests

```bash
# Tests unitarios
pytest tests/test_repository.py -v

# Tests con cobertura
pytest tests/test_repository.py --cov=repository --cov-report=html

# Tests específicos
pytest tests/test_repository.py::TestCSVProcessor -v
```

### Ejemplos de Tests

```python
def test_csv_processor():
    processor = CSVProcessor()
    
    # Test lectura de archivo
    headers, data = processor.read_csv_file(test_file)
    assert len(headers) > 0
    assert len(data) > 0
    
    # Test limpieza de datos
    cleaned_data = processor.clean_data(data)
    assert len(cleaned_data) == len(data)
```

## Configuración

### Variables de Entorno

```bash
# Configuración de archivos
DEFAULT_ENCODING=utf-8
DEFAULT_DELIMITER=|
MAX_FILE_SIZE=104857600

# Configuración de logging
LOG_LEVEL=INFO
```

### Configuración por Proyecto

```python
from config.settings import get_project_config

# Configuración específica para DIAN
dian_config = get_project_config("DIAN")

# Configuración específica para COLJUEGOS
coljuegos_config = get_project_config("COLJUEGOS")
```

## Monitoreo y Logging

### Logs Estructurados

Todos los procesadores generan logs estructurados:
- Operación realizada
- Archivos involucrados
- Métricas de rendimiento
- Errores y advertencias

### Métricas Disponibles

- Tiempo de procesamiento
- Tamaño de archivos
- Número de filas/columnas
- Errores de validación
- Estadísticas de codificación

## Próximos Pasos

1. **Migrar código existente** siguiendo la guía de migración
2. **Ejecutar tests** para validar funcionalidad
3. **Actualizar documentación** de proyectos específicos
4. **Eliminar archivos legacy** una vez completada la migración

## Soporte

Para soporte técnico:
1. Revisar logs detallados
2. Consultar documentación de cada clase
3. Ejecutar tests para validar funcionalidad
4. Usar `make help` para comandos disponibles 