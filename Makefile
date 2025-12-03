# Makefile para ExcelSior API
# Automatiza tareas comunes de desarrollo, testing y despliegue

.PHONY: help install install-dev test test-cov lint format type-check clean run run-dev docker-build docker-run

# Variables
PYTHON = python3
PIP = pip3
PYTEST = pytest
BLACK = black
FLAKE8 = flake8
MYPY = mypy
ISORT = isort

# Colores para output
GREEN = \033[0;32m
YELLOW = \033[1;33m
RED = \033[0;31m
NC = \033[0m # No Color

help: ## Mostrar esta ayuda
	@echo "$(GREEN)ExcelSior API - Comandos disponibles:$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-15s$(NC) %s\n", $$1, $$2}'

install: ## Instalar dependencias de producción
	@echo "$(GREEN)Instalando dependencias de producción...$(NC)"
	$(PIP) install -r requirements.txt

install-dev: ## Instalar dependencias de desarrollo
	@echo "$(GREEN)Instalando dependencias de desarrollo...$(NC)"
	$(PIP) install -r requirements.txt
	$(PIP) install -e ".[dev]"

test: ## Ejecutar tests unitarios
	@echo "$(GREEN)Ejecutando tests unitarios...$(NC)"
	$(PYTEST) tests/ -v

test-cov: ## Ejecutar tests con cobertura
	@echo "$(GREEN)Ejecutando tests con cobertura...$(NC)"
	$(PYTEST) tests/ --cov=. --cov-report=html --cov-report=term-missing

test-watch: ## Ejecutar tests en modo watch
	@echo "$(GREEN)Ejecutando tests en modo watch...$(NC)"
	$(PYTEST) tests/ -f -v

lint: ## Ejecutar linting con flake8
	@echo "$(GREEN)Ejecutando linting...$(NC)"
	$(FLAKE8) . --count --select=E9,F63,F7,F82 --show-source --statistics
	$(FLAKE8) . --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics

format: ## Formatear código con black e isort
	@echo "$(GREEN)Formateando código...$(NC)"
	$(ISORT) .
	$(BLACK) .

format-check: ## Verificar formato del código
	@echo "$(GREEN)Verificando formato del código...$(NC)"
	$(ISORT) . --check-only
	$(BLACK) . --check

type-check: ## Verificar tipos con mypy
	@echo "$(GREEN)Verificando tipos...$(NC)"
	$(MYPY) .

quality: format-check lint type-check ## Ejecutar todas las verificaciones de calidad
	@echo "$(GREEN)✓ Todas las verificaciones de calidad pasaron$(NC)"

clean: ## Limpiar archivos temporales y cache
	@echo "$(GREEN)Limpiando archivos temporales...$(NC)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf .coverage

run: ## Ejecutar aplicación en modo producción
	@echo "$(GREEN)Iniciando aplicación en modo producción...$(NC)"
	uvicorn main:app --host 0.0.0.0 --port 8000

run-dev: ## Ejecutar aplicación en modo desarrollo
	@echo "$(GREEN)Iniciando aplicación en modo desarrollo...$(NC)"
	uvicorn main:app --host 0.0.0.0 --port 8000 --reload --log-level debug

docker-build: ## Construir imagen Docker
	@echo "$(GREEN)Construyendo imagen Docker...$(NC)"
	docker build -t excelsior-api .

docker-run: ## Ejecutar aplicación en Docker
	@echo "$(GREEN)Ejecutando aplicación en Docker...$(NC)"
	docker run -p 9000:8000 excelsior-api

docker-stop: ## Detener contenedores Docker
	@echo "$(GREEN)Deteniendo contenedores Docker...$(NC)"
	docker stop $$(docker ps -q --filter ancestor=excelsior-api) 2>/dev/null || true

logs: ## Mostrar logs de la aplicación
	@echo "$(GREEN)Mostrando logs...$(NC)"
	tail -f /tmp/excelsior.log 2>/dev/null || echo "$(YELLOW)No se encontraron logs$(NC)"

setup-dev: install-dev ## Configurar entorno de desarrollo completo
	@echo "$(GREEN)Configurando entorno de desarrollo...$(NC)"
	$(PYTHON) -c "import config.settings; print('✓ Configuración cargada correctamente')"
	@echo "$(GREEN)✓ Entorno de desarrollo configurado$(NC)"

pre-commit: format lint type-check test ## Ejecutar verificaciones pre-commit
	@echo "$(GREEN)✓ Todas las verificaciones pre-commit pasaron$(NC)"

ci: install-dev quality test-cov ## Pipeline de CI/CD
	@echo "$(GREEN)✓ Pipeline de CI completado exitosamente$(NC)"

# Comandos específicos para el proyecto
validate-config: ## Validar configuración del proyecto
	@echo "$(GREEN)Validando configuración...$(NC)"
	$(PYTHON) -c "from config.settings import *; print('✓ Configuración válida')"

create-temp-dir: ## Crear directorio temporal
	@echo "$(GREEN)Creando directorio temporal...$(NC)"
	mkdir -p /tmp/excelsior

health-check: ## Verificar salud de la aplicación
	@echo "$(GREEN)Verificando salud de la aplicación...$(NC)"
	curl -f http://localhost:8000/health || echo "$(RED)La aplicación no está respondiendo$(NC)"

# Comandos de base de datos (si se agrega en el futuro)
# db-migrate: ## Ejecutar migraciones de base de datos
# 	@echo "$(GREEN)Ejecutando migraciones...$(NC)"
# 	alembic upgrade head

# db-rollback: ## Revertir migración de base de datos
# 	@echo "$(GREEN)Revirtiendo migración...$(NC)"
# 	alembic downgrade -1

# Comandos de seguridad
security-check: ## Ejecutar verificación de seguridad
	@echo "$(GREEN)Ejecutando verificación de seguridad...$(NC)"
	bandit -r . -f json -o bandit-report.json || true
	@echo "$(YELLOW)Reporte de seguridad generado en bandit-report.json$(NC)"

# Comandos de documentación
docs: ## Generar documentación
	@echo "$(GREEN)Generando documentación...$(NC)"
	pdoc --html --output-dir docs/ .

docs-serve: ## Servir documentación localmente
	@echo "$(GREEN)Sirviendo documentación en http://localhost:8080$(NC)"
	python -m http.server 8080 -d docs/

# Comandos de monitoreo
monitor: ## Iniciar monitoreo de la aplicación
	@echo "$(GREEN)Iniciando monitoreo...$(NC)"
	watch -n 5 'curl -s http://localhost:8000/health | jq .' 2>/dev/null || \
	watch -n 5 'curl -s http://localhost:8000/health'

# Comandos de backup (si se agrega en el futuro)
# backup: ## Crear backup de datos
# 	@echo "$(GREEN)Creando backup...$(NC)"
# 	tar -czf backup-$$(date +%Y%m%d-%H%M%S).tar.gz data/

# restore: ## Restaurar backup de datos
# 	@echo "$(GREEN)Restaurando backup...$(NC)"
# 	tar -xzf backup-*.tar.gz

# Comandos de despliegue
deploy-staging: ## Desplegar en staging
	@echo "$(GREEN)Desplegando en staging...$(NC)"
	# Agregar comandos específicos de despliegue

deploy-production: ## Desplegar en producción
	@echo "$(GREEN)Desplegando en producción...$(NC)"
	# Agregar comandos específicos de despliegue

# Comandos de utilidad
version: ## Mostrar versión actual
	@echo "$(GREEN)Versión actual:$(NC)"
	@$(PYTHON) -c "import config.settings; print(config.settings.APP_VERSION)"

deps-tree: ## Mostrar árbol de dependencias
	@echo "$(GREEN)Árbol de dependencias:$(NC)"
	pipdeptree

update-deps: ## Actualizar dependencias
	@echo "$(GREEN)Actualizando dependencias...$(NC)"
	pip install --upgrade -r requirements.txt

# Comandos de desarrollo específicos
dev-setup: setup-dev create-temp-dir ## Configuración completa para desarrollo
	@echo "$(GREEN)✓ Entorno de desarrollo listo$(NC)"

dev-start: dev-setup run-dev ## Iniciar desarrollo completo
	@echo "$(GREEN)✓ Desarrollo iniciado$(NC)"

# Comandos de testing específicos
test-fast: ## Ejecutar tests rápidos (sin cobertura)
	@echo "$(GREEN)Ejecutando tests rápidos...$(NC)"
	$(PYTEST) tests/ -x -v --tb=short

test-slow: ## Ejecutar tests lentos
	@echo "$(GREEN)Ejecutando tests lentos...$(NC)"
	$(PYTEST) tests/ -m slow -v

test-integration: ## Ejecutar tests de integración
	@echo "$(GREEN)Ejecutando tests de integración...$(NC)"
	$(PYTEST) tests/ -m integration -v

# Comandos de debugging
debug: ## Ejecutar en modo debug
	@echo "$(GREEN)Ejecutando en modo debug...$(NC)"
	uvicorn main:app --host 0.0.0.0 --port 8000 --reload --log-level debug --access-log

profile: ## Ejecutar con profiling
	@echo "$(GREEN)Ejecutando con profiling...$(NC)"
	python -m cProfile -o profile.stats -m uvicorn main:app --host 0.0.0.0 --port 8000

# Comandos de limpieza específicos
clean-logs: ## Limpiar logs
	@echo "$(GREEN)Limpiando logs...$(NC)"
	rm -f /tmp/excelsior.log
	rm -f *.log

clean-docker: ## Limpiar recursos Docker
	@echo "$(GREEN)Limpiando recursos Docker...$(NC)"
	docker system prune -f
	docker image prune -f

clean-all: clean clean-logs clean-docker ## Limpieza completa
	@echo "$(GREEN)✓ Limpieza completa realizada$(NC)" 