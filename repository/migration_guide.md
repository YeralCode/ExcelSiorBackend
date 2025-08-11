# Guía de Migración - Repository Reorganizado

## Resumen de Cambios

El directorio `/repository` ha sido completamente reorganizado siguiendo las mejores prácticas de programación. Esta guía te ayudará a migrar tu código existente a la nueva estructura.

## Nueva Estructura

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
└── legacy/                        # Código legacy (temporal)
    ├── unir_csv_en_excel.py
    ├── unit_todos_csv.py
    └── transformar/
```

## Migración por Funcionalidad

### 1. Procesamiento de CSV

**Código Antiguo:**
```python
# Código manual de procesamiento CSV
with open(file_path, 'r', encoding='utf-8') as f:
    reader = csv.reader(f, delimiter='|')
    # ... procesamiento manual
```

**Código Nuevo:**
```python
from repository.processors.csv_processor import CSVProcessor

processor = CSVProcessor()
headers, data = processor.read_csv_file(file_path)
cleaned_data = processor.clean_data(data)
processor.write_csv_file(output_path, headers, cleaned_data)
```

### 2. Procesamiento de Excel

**Código Antiguo:**
```python
# Código manual de procesamiento Excel
df = pd.read_excel(file_path)
# ... procesamiento manual
```

**Código Nuevo:**
```python
from repository.processors.excel_processor import ExcelProcessor

processor = ExcelProcessor()
headers, data = processor.read_excel_file(file_path)
sheets = processor.split_large_dataframe(headers, data, "mi_hoja")
processor.write_excel_file(output_path, sheets)
```

### 3. Consolidación de Archivos

**Código Antiguo:**
```python
# Código manual de consolidación
dataframes = []
for file in files:
    df = pd.read_csv(file)
    dataframes.append(df)
combined_df = pd.concat(dataframes)
```

**Código Nuevo:**
```python
from repository.processors.consolidation_processor import ConsolidationProcessor

processor = ConsolidationProcessor()
result = processor.consolidate_csv_files(csv_files, output_file)
print(f"Archivos procesados: {result['processed_files']}")
```

### 4. Conversiones de Formato

**Código Antiguo:**
```python
# Código manual de conversión
with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
    # ... conversión manual
```

**Código Nuevo:**
```python
from repository.transformers.format_transformer import FormatTransformer

transformer = FormatTransformer()
result = transformer.csv_to_csv_with_delimiter_change(
    input_file, output_file, '|@', '|', add_metadata=True
)
```

### 5. Conversiones de Codificación

**Código Antiguo:**
```python
# Código manual de detección de codificación
try:
    with open(file, 'r', encoding='utf-8') as f:
        # ...
except UnicodeDecodeError:
    with open(file, 'r', encoding='latin-1') as f:
        # ...
```

**Código Nuevo:**
```python
from repository.transformers.encoding_transformer import EncodingTransformer

transformer = EncodingTransformer()
encoding_info = transformer.detect_encoding(file_path)
result = transformer.convert_encoding(input_file, output_file, 'utf-8')
```

## Ejemplos de Migración

### Ejemplo 1: Migrar `unir_csv_en_excel.py`

**Código Original:**
```python
def unir_csv_en_excel(lista_archivos_csv, archivo_salida):
    # ... código manual
```

**Código Migrado:**
```python
from repository.processors.excel_processor import ExcelProcessor

def unir_csv_en_excel(lista_archivos_csv, archivo_salida):
    processor = ExcelProcessor()
    result = processor.merge_csv_files_to_excel(
        csv_files=lista_archivos_csv,
        output_file=archivo_salida
    )
    return result
```

### Ejemplo 2: Migrar `unit_todos_csv.py`

**Código Original:**
```python
# Procesamiento manual de consolidación
dataframes = []
for filename in filenames:
    df = pd.read_csv(file_path, delimiter='|', dtype=str)
    # ... limpieza manual
```

**Código Migrado:**
```python
from repository.processors.consolidation_processor import ConsolidationProcessor

def consolidar_csv_files(filenames, base_path, output_file):
    processor = ConsolidationProcessor()
    csv_files = [Path(base_path) / filename for filename in filenames]
    result = processor.consolidate_csv_files(csv_files, output_file)
    return result
```

### Ejemplo 3: Migrar `csv_a_otro_separador.py`

**Código Original:**
```python
# Conversión manual de delimitadores
with open(archivo_entrada, 'r') as infile, open(archivo_salida, 'w') as outfile:
    # ... conversión manual
```

**Código Migrado:**
```python
from repository.transformers.format_transformer import FormatTransformer

def convertir_delimitador(archivo_entrada, archivo_salida, old_delimiter, new_delimiter):
    transformer = FormatTransformer()
    result = transformer.csv_to_csv_with_delimiter_change(
        input_file=archivo_entrada,
        output_file=archivo_salida,
        old_delimiter=old_delimiter,
        new_delimiter=new_delimiter,
        add_metadata=True
    )
    return result
```

## Beneficios de la Nueva Estructura

### 1. **Manejo de Errores Robusto**
```python
# Antes: Manejo manual de errores
try:
    # código
except Exception as e:
    print(f"Error: {e}")

# Ahora: Manejo automático con logging
from utils.exceptions import handle_exception

@handle_exception
def mi_funcion():
    # código - errores manejados automáticamente
```

### 2. **Logging Estructurado**
```python
# Antes: Prints manuales
print(f"Procesando archivo: {filename}")

# Ahora: Logging estructurado
self.log_operation("processing_file", f"Procesando archivo: {filename}")
```

### 3. **Validación Automática**
```python
# Antes: Validación manual
if not os.path.exists(file_path):
    raise Exception("Archivo no encontrado")

# Ahora: Validación automática
processor.validate_file(file_path)  # Lanza excepciones específicas
```

### 4. **Configuración Centralizada**
```python
# Antes: Constantes hardcodeadas
DELIMITER = '|'
ENCODING = 'utf-8'

# Ahora: Configuración centralizada
from config.settings import DEFAULT_DELIMITER, DEFAULT_ENCODING
```

## Pasos para Migrar

### Paso 1: Identificar Funcionalidad
Determina qué tipo de operación realiza tu código:
- Procesamiento de CSV → `CSVProcessor`
- Procesamiento de Excel → `ExcelProcessor`
- Consolidación → `ConsolidationProcessor`
- Conversiones de formato → `FormatTransformer`
- Conversiones de codificación → `EncodingTransformer`

### Paso 2: Reemplazar Imports
```python
# Antes
import pandas as pd
import csv
import os

# Ahora
from repository.processors.csv_processor import CSVProcessor
from repository.processors.excel_processor import ExcelProcessor
from utils.logger import get_logger
from utils.exceptions import handle_exception
```

### Paso 3: Refactorizar Funciones
```python
# Antes
def procesar_archivo(file_path):
    # código manual largo
    pass

# Ahora
@handle_exception
def procesar_archivo(file_path):
    processor = CSVProcessor()
    return processor.read_csv_file(file_path)
```

### Paso 4: Actualizar Manejo de Errores
```python
# Antes
try:
    # código
except Exception as e:
    print(f"Error: {e}")

# Ahora
# Los errores se manejan automáticamente con logging estructurado
```

### Paso 5: Agregar Logging
```python
# Antes
print("Procesando archivo...")

# Ahora
logger = get_logger(__name__)
logger.info("Procesando archivo", extra={"file_path": str(file_path)})
```

## Comandos de Migración

### 1. Ejecutar Tests de Migración
```bash
cd backend
python -m pytest tests/test_migration.py -v
```

### 2. Validar Configuración
```bash
make validate-config
```

### 3. Ejecutar Análisis de Código
```bash
make quality
```

### 4. Ejecutar Tests Completos
```bash
make test
```

## Archivos Legacy

Los archivos originales se han movido a `repository/legacy/` para referencia:

- `legacy/unir_csv_en_excel.py`
- `legacy/unit_todos_csv.py`
- `legacy/transformar/`

**⚠️ Importante:** Los archivos legacy se eliminarán en la próxima versión. Migra tu código lo antes posible.

## Soporte

Si encuentras problemas durante la migración:

1. Revisa los logs detallados
2. Consulta la documentación de cada clase
3. Ejecuta los tests para validar la funcionalidad
4. Usa el comando `make help` para ver todas las opciones disponibles

## Próximos Pasos

1. **Migrar código existente** siguiendo esta guía
2. **Ejecutar tests** para validar la funcionalidad
3. **Actualizar documentación** de tu proyecto
4. **Eliminar archivos legacy** una vez completada la migración 