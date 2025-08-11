#!/bin/bash

# Script de setup para ExcelSior API
# Este script configura el entorno de desarrollo completo

set -e  # Salir si hay algún error

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Función para imprimir mensajes
print_message() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Función para verificar si un comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Función para verificar versión de Python
check_python_version() {
    if command_exists python3; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        REQUIRED_VERSION="3.8"
        
        if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" = "$REQUIRED_VERSION" ]; then
            print_message "Python $PYTHON_VERSION encontrado ✓"
        else
            print_error "Se requiere Python 3.8 o superior. Versión actual: $PYTHON_VERSION"
            exit 1
        fi
    else
        print_error "Python 3 no está instalado"
        exit 1
    fi
}

# Función para crear entorno virtual
create_virtual_environment() {
    if [ ! -d "venv" ]; then
        print_message "Creando entorno virtual..."
        python3 -m venv venv
        print_message "Entorno virtual creado ✓"
    else
        print_message "Entorno virtual ya existe ✓"
    fi
}

# Función para activar entorno virtual
activate_virtual_environment() {
    print_message "Activando entorno virtual..."
    source venv/bin/activate
    print_message "Entorno virtual activado ✓"
}

# Función para instalar dependencias
install_dependencies() {
    print_message "Instalando dependencias..."
    
    # Actualizar pip
    pip install --upgrade pip
    
    # Instalar dependencias de producción
    pip install -r requirements.txt
    
    # Instalar dependencias de desarrollo si se especifica
    if [ "$1" = "--dev" ]; then
        print_message "Instalando dependencias de desarrollo..."
        pip install pytest pytest-cov black flake8 mypy isort
    fi
    
    print_message "Dependencias instaladas ✓"
}

# Función para crear directorios necesarios
create_directories() {
    print_message "Creando directorios necesarios..."
    
    mkdir -p /tmp/excelsior
    mkdir -p logs
    mkdir -p temp
    mkdir -p tests
    mkdir -p docs
    
    print_message "Directorios creados ✓"
}

# Función para configurar variables de entorno
setup_environment() {
    print_message "Configurando variables de entorno..."
    
    if [ ! -f ".env" ]; then
        cp env.example .env
        print_message "Archivo .env creado desde env.example ✓"
    else
        print_warning "Archivo .env ya existe, no se sobrescribirá"
    fi
}

# Función para verificar configuración
verify_configuration() {
    print_message "Verificando configuración..."
    
    # Verificar que se puede importar la configuración
    python3 -c "from config.settings import *; print('✓ Configuración válida')" 2>/dev/null || {
        print_error "Error al cargar la configuración"
        exit 1
    }
    
    print_message "Configuración verificada ✓"
}

# Función para ejecutar tests iniciales
run_initial_tests() {
    if [ "$1" = "--dev" ]; then
        print_message "Ejecutando tests iniciales..."
        
        if command_exists pytest; then
            pytest tests/ -v || {
                print_warning "Algunos tests fallaron, pero el setup continúa"
            }
        else
            print_warning "pytest no está disponible, omitiendo tests"
        fi
    fi
}

# Función para mostrar información final
show_final_info() {
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  ExcelSior API - Setup Completado ✓${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo -e "${YELLOW}Próximos pasos:${NC}"
    echo "1. Activar el entorno virtual: source venv/bin/activate"
    echo "2. Configurar variables de entorno: nano .env"
    echo "3. Ejecutar la aplicación: make run-dev"
    echo "4. Verificar la API: curl http://localhost:8000/health"
    echo ""
    echo -e "${YELLOW}Comandos útiles:${NC}"
    echo "- make help          # Ver todos los comandos disponibles"
    echo "- make test          # Ejecutar tests"
    echo "- make format        # Formatear código"
    echo "- make lint          # Verificar calidad del código"
    echo "- make run-dev       # Ejecutar en modo desarrollo"
    echo "- make run           # Ejecutar en modo producción"
    echo ""
    echo -e "${YELLOW}Documentación:${NC}"
    echo "- README_MEJORAS.md  # Documentación de mejoras implementadas"
    echo "- /docs              # Documentación de la API (cuando esté disponible)"
    echo ""
}

# Función principal
main() {
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  ExcelSior API - Setup Script${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    
    # Verificar argumentos
    DEV_MODE=false
    if [ "$1" = "--dev" ]; then
        DEV_MODE=true
        print_message "Modo desarrollo habilitado"
    fi
    
    # Ejecutar pasos de setup
    check_python_version
    create_virtual_environment
    activate_virtual_environment
    install_dependencies "$1"
    create_directories
    setup_environment
    verify_configuration
    
    if [ "$DEV_MODE" = true ]; then
        run_initial_tests "$1"
    fi
    
    show_final_info
}

# Función de ayuda
show_help() {
    echo "Uso: $0 [OPCIONES]"
    echo ""
    echo "Opciones:"
    echo "  --dev     Instalar dependencias de desarrollo y ejecutar tests"
    echo "  --help    Mostrar esta ayuda"
    echo ""
    echo "Ejemplos:"
    echo "  $0          # Setup básico"
    echo "  $0 --dev    # Setup completo con dependencias de desarrollo"
}

# Manejar argumentos
case "$1" in
    --help|-h)
        show_help
        exit 0
        ;;
    --dev|"")
        main "$1"
        ;;
    *)
        print_error "Opción desconocida: $1"
        show_help
        exit 1
        ;;
esac 