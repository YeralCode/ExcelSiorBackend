# Sistema Modular de Proyectos - Ejemplos de Uso

## 🎯 **Descripción General**

Este sistema proporciona una arquitectura modular y reutilizable para manejar diferentes proyectos (DIAN, COLJUEGOS, UGPP) con configuraciones específicas pero manteniendo una estructura común.

## 🏗️ **Arquitectura del Sistema**

```
backend/repository/proyectos/
├── base/                          # Configuraciones base reutilizables
│   ├── __init__.py
│   ├── config_base.py            # Clase base abstracta
│   ├── values_manager.py         # Gestor de valores_choice
│   └── validators.py             # Sistema de validadores
├── DIAN/                         # Configuración específica DIAN
│   ├── config.py
│   └── [módulos específicos]/
├── COLJUEGOS/                    # Configuración específica COLJUEGOS
│   ├── config.py
│   └── [módulos específicos]/
├── UGPP/                         # Configuración específica UGPP
│   ├── config.py
│   └── [módulos específicos]/
└── factory.py                    # Factory para gestionar proyectos
```

## 🚀 **Ejemplos de Uso**

### **1. Obtener Configuración de un Proyecto**

```python
from repository.proyectos.factory import get_project_config

# Configuración básica de DIAN
dian_config = get_project_config('DIAN')

# Configuración específica de DIAN notificaciones
dian_notif_config = get_project_config('DIAN', 'notificaciones')

# Configuración específica de COLJUEGOS disciplinarios
coljuegos_disc_config = get_project_config('COLJUEGOS', 'disciplinarios')

print(dian_config.project_name)
print(dian_config.get_required_columns())
print(dian_config.get_validators())
```

### **2. Validar Datos de un Proyecto**

```python
from repository.proyectos.factory import validate_project_data

# Datos de ejemplo para DIAN notificaciones
dian_data = {
    'NIT': '900123456-7',
    'CUANTIA_ACTO': 1500000.50,
    'ANO_CALENDARIO': 2024,
    'FECHA_ACTO': '2024-01-15',
    'ESTADO_NOTIFICACION': 'notificado',
    'RAZON_SOCIAL': 'Empresa Ejemplo S.A.S.'
}

# Validar datos
result = validate_project_data('DIAN', dian_data, 'notificaciones')

if result['valid']:
    print("✅ Datos válidos")
else:
    print("❌ Errores encontrados:")
    for error in result['errors']:
        print(f"  - {error}")
```

### **3. Usar el Gestor de Valores**

```python
from repository.proyectos.base.values_manager import ValuesManager

# Crear gestor para DIAN defensoria
values_manager = ValuesManager('DIAN', 'defensoria')

# Cargar valores de proceso
proceso_config = values_manager.get_values('proceso')
print(f"Valores de proceso: {proceso_config.values}")

# Validar un valor específico
is_valid = values_manager.validate_value('proceso', 'asistencia al cliente')
print(f"¿Es válido 'asistencia al cliente'? {is_valid}")

# Obtener reemplazo de un valor
replacement = values_manager.get_replacement('dependencia', 'direccion seccional de impuestos barranquilla')
print(f"Reemplazo: {replacement}")
```

### **4. Usar Validadores Específicos**

```python
from repository.proyectos.base.validators import ValidatorFactory

# Crear validadores específicos
nit_validator = ValidatorFactory.create_validator('nit')
date_validator = ValidatorFactory.create_validator('date')
float_validator = ValidatorFactory.create_validator('float', min_value=0.0)

# Validar NIT
print(nit_validator.is_valid('900123456-7'))  # True
print(nit_validator.is_valid('123'))          # False

# Validar fecha
print(date_validator.is_valid('2024-01-15'))  # True
print(date_validator.is_valid('fecha inválida'))  # False

# Validar flotante
print(float_validator.is_valid(1500000.50))   # True
print(float_validator.is_valid(-100))         # False
```

### **5. Procesar Archivos con Configuración Específica**

```python
from repository.proyectos.factory import project_manager

# Procesar archivo de DIAN notificaciones
result = project_manager.process_file(
    project_code='DIAN',
    file_path='data/dian_notificaciones.csv',
    module_name='notificaciones'
)

print(f"Proyecto: {result['project_code']}")
print(f"Columnas requeridas: {result['required_columns']}")
print(f"Validadores disponibles: {result['validators']}")
```

### **6. Obtener Información de Proyectos**

```python
from repository.proyectos.factory import project_manager

# Listar todos los proyectos
projects = project_manager.list_projects()
for code, info in projects.items():
    print(f"Proyecto: {code}")
    print(f"  Nombre: {info['name']}")
    print(f"  Columnas requeridas: {info['required_columns_count']}")
    print(f"  Validadores: {info['validators_count']}")

# Obtener información detallada de un proyecto
dian_info = project_manager.get_project_info('DIAN', 'notificaciones')
print(f"Configuración DIAN notificaciones:")
print(f"  Formatos soportados: {dian_info['supported_formats']}")
print(f"  Encoding: {dian_info['encoding']}")
print(f"  Delimiter: {dian_info['delimiter']}")
```

## 🔧 **Configuración de Nuevos Proyectos**

### **1. Crear Configuración Base**

```python
from repository.proyectos.base.config_base import ProjectConfigBase

class NuevoProyectoConfig(ProjectConfigBase):
    def __init__(self, module_path: str = ""):
        super().__init__(
            project_name="Nuevo Proyecto",
            project_code="NUEVO",
            description="Descripción del nuevo proyecto"
        )
        self.module_path = module_path
    
    def get_required_columns(self) -> List[str]:
        return ["COLUMNA_1", "COLUMNA_2", "COLUMNA_3"]
    
    def get_optional_columns(self) -> List[str]:
        return ["COLUMNA_OPCIONAL_1", "COLUMNA_OPCIONAL_2"]
    
    def get_column_mappings(self) -> Dict[str, str]:
        return {
            "columna_1": "COLUMNA_1",
            "columna_2": "COLUMNA_2"
        }
    
    def get_validators(self) -> Dict[str, Any]:
        factory = ValidatorFactory()
        return {
            'COLUMNA_1': factory.create_validator('string', min_length=1),
            'COLUMNA_2': factory.create_validator('integer', min_value=1)
        }
```

### **2. Registrar el Nuevo Proyecto**

```python
from repository.proyectos.factory import ProjectConfigFactory

# Registrar la nueva configuración
ProjectConfigFactory.register_config('NUEVO', NuevoProyectoConfig)

# Usar la nueva configuración
nuevo_config = get_project_config('NUEVO')
```

## 📋 **Estructura de valores_choice**

### **Formato Estándar**

```python
# valores_choice/proceso.py
VALORES_PROCESO = [
    "proceso_1",
    "proceso_2",
    "proceso_3"
]

VALORES_REEMPLAZO_PROCESO = {
    "proceso_1_old": "proceso_1",
    "proceso_2_old": "proceso_2"
}
```

### **Carga Automática**

```python
# El sistema carga automáticamente los valores
values_manager = ValuesManager('DIAN', 'defensoria')
proceso_values = values_manager.get_all_values('proceso')
```

## 🎯 **Ventajas del Sistema**

### **1. Reutilización**
- ✅ Configuraciones base compartidas
- ✅ Validadores reutilizables
- ✅ Gestión unificada de valores

### **2. Flexibilidad**
- ✅ Configuraciones específicas por proyecto
- ✅ Módulos específicos por proyecto
- ✅ Validadores personalizables

### **3. Mantenibilidad**
- ✅ Estructura clara y organizada
- ✅ Fácil agregar nuevos proyectos
- ✅ Configuraciones centralizadas

### **4. Escalabilidad**
- ✅ Factory pattern para gestión
- ✅ Cache de configuraciones
- ✅ Sistema de validación extensible

## 🔍 **Casos de Uso Comunes**

### **1. Validación de Datos de Entrada**
```python
# Validar datos antes de procesar
data = {'NIT': '900123456-7', 'CUANTIA': 1500000.50}
result = validate_project_data('DIAN', data, 'notificaciones')
```

### **2. Mapeo de Columnas**
```python
# Mapear nombres de columnas
config = get_project_config('DIAN')
mappings = config.get_column_mappings()
```

### **3. Gestión de Valores**
```python
# Gestionar valores específicos del proyecto
values_manager = ValuesManager('COLJUEGOS', 'disciplinarios')
direcciones = values_manager.get_all_values('direccion_seccional')
```

### **4. Configuración de Procesamiento**
```python
# Obtener configuración de procesamiento
config = get_project_config('UGPP', 'pqr')
batch_size = config.batch_size
encoding = config.encoding
```

## 🚀 **Próximos Pasos**

1. **Implementar procesadores específicos** para cada proyecto
2. **Agregar más validadores** según necesidades
3. **Crear interfaces de usuario** para gestión de configuraciones
4. **Implementar tests unitarios** para cada componente
5. **Agregar logging y monitoreo** del sistema

¡El sistema está listo para ser usado y extendido según las necesidades específicas de cada proyecto! 🎉 