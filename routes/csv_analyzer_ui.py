"""
Ruta para la interfaz de usuario del analizador de CSV.

Proporciona endpoints para servir la interfaz web del analizador
y manejar las interacciones del usuario.
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

from utils.logger import get_logger
from utils.exceptions import handle_exception

logger = get_logger(__name__)
router = APIRouter(prefix="/csv-analyzer-ui", tags=["CSV Analyzer UI"])

# Configurar templates
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def csv_analyzer_home(request: Request):
    """
    Página principal del analizador de CSV.
    
    Args:
        request: Request de FastAPI
        
    Returns:
        Página HTML del analizador
    """
    logger.info("Sirviendo página principal del analizador CSV")
    
    return templates.TemplateResponse(
        "csv_analyzer_modal.html",
        {
            "request": request,
            "title": "Analizador de CSV - ExcelSior",
            "description": "Herramienta interactiva para analizar archivos CSV"
        }
    )

@router.get("/modal", response_class=HTMLResponse)
async def csv_analyzer_modal(request: Request):
    """
    Modal del analizador de CSV.
    
    Args:
        request: Request de FastAPI
        
    Returns:
        Modal HTML del analizador
    """
    logger.info("Sirviendo modal del analizador CSV")
    
    return templates.TemplateResponse(
        "csv_analyzer_modal.html",
        {
            "request": request,
            "title": "Analizador de CSV",
            "is_modal": True
        }
    )

@router.get("/widget", response_class=HTMLResponse)
async def csv_analyzer_widget(request: Request):
    """
    Widget del analizador de CSV para integrar en otras páginas.
    
    Args:
        request: Request de FastAPI
        
    Returns:
        Widget HTML del analizador
    """
    logger.info("Sirviendo widget del analizador CSV")
    
    return templates.TemplateResponse(
        "csv_analyzer_widget.html",
        {
            "request": request,
            "title": "Widget Analizador CSV"
        }
    ) 