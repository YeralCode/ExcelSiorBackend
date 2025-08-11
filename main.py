"""
Aplicación principal de ExcelSior API.

Configuración centralizada de FastAPI con middleware,
manejo de errores y logging estructurado.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import logging

# Importar configuraciones
from config.settings import (
    APP_NAME, APP_VERSION, APP_DESCRIPTION, 
    CORS_ORIGINS, LOG_LEVEL
)

# Importar utilidades
from utils.logger import get_logger, setup_logger
from utils.exceptions import ExcelSiorException, handle_exception

# Importar las rutas modulares
from routes import conversion, consolidacion, csv_analyzer, csv_analyzer_ui, normalizacion, dynamic_types

# Configurar logging
logger = setup_logger("excelsior.main")

# Crear aplicación FastAPI
app = FastAPI(
    title=APP_NAME,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware para logging de requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware para logging de requests HTTP."""
    start_time = time.time()
    
    # Log del request
    logger.info(
        f"Request iniciado: {request.method} {request.url}",
        extra={
            "component": "middleware",
            "operation": "request_start",
            "method": request.method,
            "url": str(request.url),
            "client_ip": request.client.host if request.client else "unknown"
        }
    )
    
    # Procesar request
    response = await call_next(request)
    
    # Calcular tiempo de procesamiento
    process_time = time.time() - start_time
    
    # Log del response
    logger.info(
        f"Request completado: {request.method} {request.url} - Status: {response.status_code} - Tiempo: {process_time:.3f}s",
        extra={
            "component": "middleware",
            "operation": "request_end",
            "method": request.method,
            "url": str(request.url),
            "status_code": response.status_code,
            "process_time": process_time
        }
    )
    
    # Agregar header con tiempo de procesamiento
    response.headers["X-Process-Time"] = str(process_time)
    
    return response

# Manejador de excepciones personalizadas
@app.exception_handler(ExcelSiorException)
async def excelsior_exception_handler(request: Request, exc: ExcelSiorException):
    """Manejador para excepciones personalizadas de ExcelSior."""
    logger.error(
        f"Excepción ExcelSior capturada: {exc.message}",
        extra={
            "component": "exception_handler",
            "operation": "excelsior_exception",
            "error_code": exc.error_code,
            "details": exc.details,
            "url": str(request.url),
            "method": request.method
        }
    )
    
    return JSONResponse(
        status_code=400,
        content=exc.to_dict()
    )

# Manejador de excepciones genéricas
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Manejador para excepciones genéricas."""
    logger.error(
        f"Excepción genérica capturada: {str(exc)}",
        extra={
            "component": "exception_handler",
            "operation": "generic_exception",
            "error_type": type(exc).__name__,
            "url": str(request.url),
            "method": request.method
        }
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Error interno del servidor",
            "error_code": "INTERNAL_SERVER_ERROR",
            "details": {
                "error_type": type(exc).__name__,
                "message": str(exc)
            }
        }
    )

# Incluir las rutas modulares
app.include_router(conversion.router)
app.include_router(consolidacion.router)
app.include_router(normalizacion.router)
app.include_router(csv_analyzer.router)
app.include_router(csv_analyzer_ui.router)
app.include_router(dynamic_types.router)

@app.get("/")
def read_root():
    """Endpoint raíz de la API."""
    logger.info("Acceso al endpoint raíz")
    
    return {
        "message": f"Bienvenido a {APP_NAME}",
        "version": APP_VERSION,
        "description": APP_DESCRIPTION,
        "endpoints": {
            "documentation": "/docs",
            "redoc": "/redoc",
            "conversion": "/api/v1/",
            "consolidacion": "/api/v1/",
            "normalizacion": "/api/v1/normalizar-columnas/"
        },
        "status": "operational"
    }

@app.get("/health")
def health_check():
    """Endpoint para verificar el estado de la API."""
    logger.info("Verificación de salud de la API")
    
    return {
        "status": "healthy",
        "service": APP_NAME,
        "version": APP_VERSION,
        "timestamp": time.time()
    }

@app.get("/info")
def get_api_info():
    """Endpoint para obtener información detallada de la API."""
    logger.info("Solicitud de información de la API")
    
    return {
        "name": APP_NAME,
        "version": APP_VERSION,
        "description": APP_DESCRIPTION,
        "environment": {
            "log_level": LOG_LEVEL,
            "cors_origins": CORS_ORIGINS
        },
        "features": {
            "file_processing": True,
            "validation": True,
            "logging": True,
            "error_handling": True
        }
    }

# Eventos de inicio y cierre
@app.on_event("startup")
async def startup_event():
    """Evento ejecutado al iniciar la aplicación."""
    logger.info(
        f"Iniciando {APP_NAME} v{APP_VERSION}",
        extra={
            "component": "startup",
            "operation": "app_startup",
            "version": APP_VERSION
        }
    )

@app.on_event("shutdown")
async def shutdown_event():
    """Evento ejecutado al cerrar la aplicación."""
    logger.info(
        f"Cerrando {APP_NAME}",
        extra={
            "component": "shutdown",
            "operation": "app_shutdown"
        }
    )
