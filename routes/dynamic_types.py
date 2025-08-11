"""
Endpoints para gestionar tipos de datos dinámicos.

Permite agregar, modificar y eliminar tipos de datos personalizados
antes del análisis de CSV.
"""

from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from utils.dynamic_data_types import data_type_manager, CustomDataType
from utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/dynamic-types", tags=["Dynamic Data Types"])

class CustomDataTypeRequest(BaseModel):
    """Modelo para solicitudes de tipos de datos personalizados."""
    name: str
    description: str
    pattern: Optional[str] = None  # Regex opcional
    validation_function: Optional[str] = None
    confidence_threshold: float = 0.7
    priority: int = 1
    examples: List[str] = []

class CustomDataTypeResponse(BaseModel):
    """Modelo para respuestas de tipos de datos personalizados."""
    success: bool
    message: str
    data_type: Optional[Dict[str, Any]] = None

@router.get("/types", response_model=List[Dict[str, Any]])
async def get_all_types():
    """Obtiene todos los tipos de datos disponibles."""
    try:
        types = data_type_manager.get_all_types()
        logger.info(f"Obtenidos {len(types)} tipos de datos")
        return types
    except Exception as e:
        logger.error(f"Error obteniendo tipos de datos: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/types/single/{type_name}", response_model=Dict[str, Any])
async def get_type(type_name: str):
    """Obtiene un tipo de datos específico."""
    try:
        data_type = data_type_manager.get_custom_type(type_name)
        if not data_type:
            raise HTTPException(status_code=404, detail=f"Tipo de datos '{type_name}' no encontrado")
        
        type_dict = data_type.__dict__.copy()
        type_dict['name'] = type_name
        return type_dict
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo tipo de datos: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.post("/types", response_model=CustomDataTypeResponse)
async def add_custom_type(request: CustomDataTypeRequest):
    """Agrega un nuevo tipo de datos personalizado."""
    try:
        # Verificar que el nombre no exista
        if data_type_manager.get_custom_type(request.name):
            raise HTTPException(status_code=400, detail=f"El tipo de datos '{request.name}' ya existe")
        
        # Crear el tipo de datos
        data_type = CustomDataType(
            name=request.name,
            description=request.description,
            pattern=request.pattern,
            validation_function=request.validation_function,
            confidence_threshold=request.confidence_threshold,
            priority=request.priority,
            examples=request.examples
        )
        
        # Agregar el tipo
        success = data_type_manager.add_custom_type(data_type)
        if not success:
            raise HTTPException(status_code=400, detail="Error al agregar el tipo de datos")
        
        logger.info(f"Tipo de datos agregado: {request.name}")
        return CustomDataTypeResponse(
            success=True,
            message=f"Tipo de datos '{request.name}' agregado correctamente",
            data_type=data_type.__dict__
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error agregando tipo de datos: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.put("/types/{type_name}", response_model=CustomDataTypeResponse)
async def update_custom_type(type_name: str, request: CustomDataTypeRequest):
    """Actualiza un tipo de datos existente."""
    try:
        # Verificar que el tipo existe
        if not data_type_manager.get_custom_type(type_name):
            raise HTTPException(status_code=404, detail=f"Tipo de datos '{type_name}' no encontrado")
        
        # Eliminar el tipo existente
        data_type_manager.remove_custom_type(type_name)
        
        # Crear el nuevo tipo
        data_type = CustomDataType(
            name=request.name,
            description=request.description,
            pattern=request.pattern,
            validation_function=request.validation_function,
            confidence_threshold=request.confidence_threshold,
            priority=request.priority,
            examples=request.examples
        )
        
        # Agregar el tipo actualizado
        success = data_type_manager.add_custom_type(data_type)
        if not success:
            raise HTTPException(status_code=400, detail="Error al actualizar el tipo de datos")
        
        logger.info(f"Tipo de datos actualizado: {type_name}")
        return CustomDataTypeResponse(
            success=True,
            message=f"Tipo de datos '{type_name}' actualizado correctamente",
            data_type=data_type.__dict__
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error actualizando tipo de datos: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.delete("/types/{type_name}", response_model=CustomDataTypeResponse)
async def delete_custom_type(type_name: str):
    """Elimina un tipo de datos personalizado."""
    try:
        success = data_type_manager.remove_custom_type(type_name)
        if not success:
            raise HTTPException(status_code=404, detail=f"Tipo de datos '{type_name}' no encontrado")
        
        logger.info(f"Tipo de datos eliminado: {type_name}")
        return CustomDataTypeResponse(
            success=True,
            message=f"Tipo de datos '{type_name}' eliminado correctamente"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error eliminando tipo de datos: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.post("/types/validate", response_model=Dict[str, Any])
async def validate_value(value: str = Body(...), type_name: str = Body(...)):
    """Valida un valor contra un tipo de datos específico."""
    try:
        is_valid = data_type_manager.validate_value(value, type_name)
        return {
            "success": True,
            "value": value,
            "type": type_name,
            "is_valid": is_valid
        }
    except Exception as e:
        logger.error(f"Error validando valor: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.post("/types/batch", response_model=CustomDataTypeResponse)
async def add_multiple_types(types: List[CustomDataTypeRequest]):
    """Agrega múltiples tipos de datos de una vez."""
    try:
        added_count = 0
        errors = []
        
        for request in types:
            try:
                # Verificar que el nombre no exista
                if data_type_manager.get_custom_type(request.name):
                    errors.append(f"El tipo '{request.name}' ya existe")
                    continue
                
                # Crear y agregar el tipo
                data_type = CustomDataType(
                    name=request.name,
                    description=request.description,
                    pattern=request.pattern,
                    validation_function=request.validation_function,
                    confidence_threshold=request.confidence_threshold,
                    priority=request.priority,
                    examples=request.examples
                )
                
                if data_type_manager.add_custom_type(data_type):
                    added_count += 1
                else:
                    errors.append(f"Error agregando '{request.name}'")
                    
            except Exception as e:
                errors.append(f"Error con '{request.name}': {str(e)}")
        
        message = f"Agregados {added_count} tipos de datos"
        if errors:
            message += f". Errores: {', '.join(errors)}"
        
        logger.info(f"Agregados {added_count} tipos de datos en lote")
        return CustomDataTypeResponse(
            success=added_count > 0,
            message=message
        )
    except Exception as e:
        logger.error(f"Error agregando tipos en lote: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor") 