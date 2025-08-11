from fastapi import APIRouter, File, UploadFile, Form
from fastapi.responses import FileResponse, JSONResponse
import os
import tempfile
import zipfile
import shutil
import logging

# Importar el sistema unificado
from repository.proyectos.unified_csv_processor import UnifiedCSVProcessor, process_csv_file
from repository.proyectos.factory import get_project_config

# Configurar logger simple para debugging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/normalizar-columnas", tags=["Normalización de columnas"])


@router.post("/coljuegos/disciplinarios/upload/")
def normalizar_columnas_coljuegos_disciplinarios_upload(
    file: UploadFile = File(...),
    nombre_archivo_salida: str = Form(...),
    nombre_archivo_errores: str = Form(...),
):
    """Normaliza columnas para archivos disciplinarios de COLJUEGOS usando el sistema unificado"""
    temp_dir = None
    zip_dir = None
    
    try:
        # Configurar directorio temporal para procesamiento
        temp_dir = tempfile.mkdtemp()
        temp_input_path = os.path.join(temp_dir, file.filename)
        
        # Guardar archivo subido
        with open(temp_input_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        output_file = os.path.join(temp_dir, nombre_archivo_salida)
        error_file = os.path.join(temp_dir, nombre_archivo_errores)
        
        # type_mapping para COLJUEGOS disciplinarios usando nombres de columnas
        type_mapping = {
            "datetime": ["FECHA_DE_RADICACION", "FECHA_DE_LOS_HECHOS", "FECHA_DE_INDAGACION_PRELIMINAR", 
                        "FECHA_DE_INVESTIGACION_DISCIPLINARIA", "FECHA_DE_FALLO", "FECHA_CITACION", 
                        "FECHA_DE_PLIEGO_DE__CARGOS", "FECHA_DE_CIERRE_INVESTIGACION"],
            "str": ["NOMBRE_ARCHIVO", "MES_REPORTE", "EXPEDIENTE", "IMPLICADO", "DEPARTAMENTO_DE_LOS_HECHOS",
                   "CIUDAD_DE_LOS_HECHOS", "DEPENDENCIA", "SUBPROCESO", "PROCEDIMIENTO", "CARGO", "ORIGEN",
                   "CONDUCTA", "ETAPA_PROCESAL", "SANCION_IMPUESTA", "HECHOS", "DECISION_DE_LA_INVESTIGACION",
                   "TIPO_DE_PROCESO_AFECTADO", "SENALADOS_O_VINCULADOS_CON_LA_INVESTIGACION", "ADECUACION_TIPICA",
                   "ABOGADO", "SENTIDO_DEL_FALLO", "QUEJOSO", "TIPO_DE_PROCESO"],
            "nit": ["DOCUMENTO_DEL_IMPLICADO", "DOC_QUEJOSO"],
            "choice_direccion_seccional": ["DIRECCION_SECCIONAL"],
            "choice_proceso": ["PROCESO"],
        }
        
        # Usar el sistema unificado
        process_csv_file('COLJUEGOS', 'disciplinarios', temp_input_path, output_file, error_file, type_mapping)
        
        # Crear directorio temporal separado para el ZIP
        zip_dir = tempfile.mkdtemp()
        zip_path = os.path.join(zip_dir, "archivos_procesados.zip")
        
        # Crear ZIP con ambos archivos
        with zipfile.ZipFile(zip_path, "w") as zipf:
            zipf.write(output_file, nombre_archivo_salida)
            if os.path.exists(error_file) and os.path.getsize(error_file) > 0:
                zipf.write(error_file, nombre_archivo_errores)
        
        logger.info(f"Archivo procesado exitosamente: {file.filename}")
        return FileResponse(
            zip_path, filename="archivos_procesados.zip", media_type="application/zip"
        )
        
    except Exception as e:
        logger.error(f"Error procesando archivo COLJUEGOS disciplinarios: {str(e)}")
        return JSONResponse(
            status_code=500, content={"error": f"Error procesando archivo: {e}"}
        )
    finally:
        # Limpiar archivos temporales de procesamiento
        try:
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
                logger.info(f"Archivos temporales de procesamiento limpiados: {temp_dir}")
        except Exception as cleanup_error:
            logger.warning(f"Error limpiando archivos temporales de procesamiento: {cleanup_error}")
        
        # Limpiar archivos temporales del ZIP después de un delay
        try:
            if zip_dir and os.path.exists(zip_dir):
                # Programar limpieza después de 30 segundos para permitir descarga
                import threading
                import time
                
                def delayed_cleanup():
                    time.sleep(30)
                    try:
                        if os.path.exists(zip_dir):
                            shutil.rmtree(zip_dir)
                            logger.info(f"Archivos temporales del ZIP limpiados: {zip_dir}")
                    except Exception as e:
                        logger.warning(f"Error en limpieza retrasada: {e}")
                
                cleanup_thread = threading.Thread(target=delayed_cleanup)
                cleanup_thread.daemon = True
                cleanup_thread.start()
                
        except Exception as cleanup_error:
            logger.warning(f"Error programando limpieza del ZIP: {cleanup_error}")


@router.post("/coljuegos/pqr/upload/")
def normalizar_columnas_coljuegos_pqr_upload(
    file: UploadFile = File(...),
    nombre_archivo_salida: str = Form(...),
    nombre_archivo_errores: str = Form(...),
):
    """Normaliza columnas para archivos PQR de COLJUEGOS usando el sistema unificado"""
    temp_dir = None
    zip_dir = None
    
    try:
        # Configurar directorio temporal para procesamiento
        temp_dir = tempfile.mkdtemp()
        temp_input_path = os.path.join(temp_dir, file.filename)
        
        # Guardar archivo subido
        with open(temp_input_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        output_file = os.path.join(temp_dir, nombre_archivo_salida)
        error_file = os.path.join(temp_dir, nombre_archivo_errores)
        
        # type_mapping para COLJUEGOS PQR usando nombres de columnas
        type_mapping = {
            "datetime": ["FECHA_RADICACION", "FECHA_RESPUESTA"],
            "str": ["NOMBRE_ARCHIVO", "MES_REPORTE", "NUMERO_PQR", "TIPO_PQR", "DESCRIPCION", 
                   "ESTADO", "RESPUESTA", "FUNCIONARIO_RESPONSABLE"],
            "nit": ["DOCUMENTO_SOLICITANTE"],
        }
        
        # Usar el sistema unificado
        process_csv_file('COLJUEGOS', 'pqr', temp_input_path, output_file, error_file, type_mapping)
        
        # Crear directorio temporal separado para el ZIP
        zip_dir = tempfile.mkdtemp()
        zip_path = os.path.join(zip_dir, "archivos_procesados.zip")
        
        # Crear ZIP con ambos archivos
        with zipfile.ZipFile(zip_path, "w") as zipf:
            zipf.write(output_file, nombre_archivo_salida)
            if os.path.exists(error_file) and os.path.getsize(error_file) > 0:
                zipf.write(error_file, nombre_archivo_errores)
        
        logger.info(f"Archivo procesado exitosamente: {file.filename}")
        return FileResponse(
            zip_path, filename="archivos_procesados.zip", media_type="application/zip"
        )
        
    except Exception as e:
        logger.error(f"Error procesando archivo COLJUEGOS PQR: {str(e)}")
        return JSONResponse(
            status_code=500, content={"error": f"Error procesando archivo: {e}"}
        )
    finally:
        # Limpiar archivos temporales de procesamiento
        try:
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
                logger.info(f"Archivos temporales de procesamiento limpiados: {temp_dir}")
        except Exception as cleanup_error:
            logger.warning(f"Error limpiando archivos temporales de procesamiento: {cleanup_error}")
        
        # Limpiar archivos temporales del ZIP después de un delay
        try:
            if zip_dir and os.path.exists(zip_dir):
                # Programar limpieza después de 30 segundos para permitir descarga
                import threading
                import time
                
                def delayed_cleanup():
                    time.sleep(30)
                    try:
                        if os.path.exists(zip_dir):
                            shutil.rmtree(zip_dir)
                            logger.info(f"Archivos temporales del ZIP limpiados: {zip_dir}")
                    except Exception as e:
                        logger.warning(f"Error en limpieza retrasada: {e}")
                
                cleanup_thread = threading.Thread(target=delayed_cleanup)
                cleanup_thread.daemon = True
                cleanup_thread.start()
                
        except Exception as cleanup_error:
            logger.warning(f"Error programando limpieza del ZIP: {cleanup_error}")


@router.post("/Dian/disciplinarios/upload/")
def normalizar_columnas_dian_disciplinarios_upload(
    file: UploadFile = File(...),
    nombre_archivo_salida: str = Form(...),
    nombre_archivo_errores: str = Form(...),
):
    """Normaliza columnas para archivos disciplinarios de DIAN usando el sistema unificado"""
    logger.info(f"=== INICIO: normalizar_columnas_dian_disciplinarios_upload ===")
    logger.info(f"Archivo recibido: {file.filename}")
    logger.info(f"Archivo de salida: {nombre_archivo_salida}")
    logger.info(f"Archivo de errores: {nombre_archivo_errores}")
    
    temp_dir = None
    zip_dir = None
    
    try:
        # Configurar directorio temporal para procesamiento
        temp_dir = tempfile.mkdtemp()
        temp_input_path = os.path.join(temp_dir, file.filename)
        logger.info(f"Directorio temporal creado: {temp_dir}")
        logger.info(f"Ruta del archivo de entrada: {temp_input_path}")
        
        # Verificar estado del archivo UploadFile
        logger.info(f"Estado del archivo UploadFile:")
        logger.info(f"  - filename: {file.filename}")
        logger.info(f"  - content_type: {file.content_type}")
        logger.info(f"  - size: {file.size if hasattr(file, 'size') else 'N/A'}")
        # Guardar archivo subido
        with open(temp_input_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        logger.info(f"Archivo guardado exitosamente: {temp_input_path}")
        
        # Verificar que el archivo existe y tiene contenido
        if os.path.exists(temp_input_path):
            file_size = os.path.getsize(temp_input_path)
            logger.info(f"Archivo existe y tiene tamaño: {file_size} bytes")
            
            # Leer las primeras líneas para verificar contenido
            try:
                with open(temp_input_path, 'r', encoding='utf-8') as f:
                    first_lines = [f.readline().strip() for _ in range(3)]
                logger.info(f"Primeras líneas del archivo: {first_lines}")
            except Exception as read_error:
                logger.warning(f"Error leyendo archivo: {read_error}")
        else:
            logger.error(f"❌ El archivo no existe después de guardarlo: {temp_input_path}")
            raise Exception("El archivo no se guardó correctamente")
        
        output_file = os.path.join(temp_dir, nombre_archivo_salida)
        error_file = os.path.join(temp_dir, nombre_archivo_errores)
        logger.info(f"Archivo de salida: {output_file}")
        logger.info(f"Archivo de errores: {error_file}")
        
        # type_mapping para DIAN disciplinarios usando nombres de columnas
        type_mapping = {
            "datetime": ["FECHA_DE_RADICACION", "FECHA_DE_LOS_HECHOS", "FECHA_DE_INDAGACION_PRELIMINAR", 
                        "FECHA_DE_INVESTIGACION_DISCIPLINARIA", "FECHA_DE_FALLO", "FECHA_CITACION", 
                        "FECHA_DE_PLIEGO_DE__CARGOS", "FECHA_DE_CIERRE_INVESTIGACION"],
            "str": ["NOMBRE_ARCHIVO", "MES_REPORTE", "EXPEDIENTE", "IMPLICADO", "DEPENDENCIA", "SUBPROCESO", "PROCEDIMIENTO", "CARGO", "ORIGEN",
                   "CONDUCTA", "ETAPA_PROCESAL", "SANCION_IMPUESTA", "HECHOS", "DECISION_DE_LA_INVESTIGACION",
                   "TIPO_DE_PROCESO_AFECTADO", "SENALADOS_O_VINCULADOS_CON_LA_INVESTIGACION", "ADECUACION_TIPICA",
                   "ABOGADO", "SENTIDO_DEL_FALLO", "QUEJOSO", "TIPO_DE_PROCESO"],
            "nit": ["DOCUMENTO_DEL_IMPLICADO", "DOC_QUEJOSO"],
            "departamento": ["DEPARTAMENTO_DE_LOS_HECHOS"],
            "ciudad": ["CIUDAD_DE_LOS_HECHOS"],
            "direccion_seccional": ["DIRECCION_SECCIONAL"],
            "proceso": ["PROCESO"],
        }
        logger.info(f"Type mapping configurado: {type_mapping}")
        
        # Usar el sistema unificado
        logger.info("=== LLAMANDO A process_csv_file ===")
        process_csv_file('DIAN', 'disciplinarios', temp_input_path, output_file, error_file, type_mapping)
        logger.info("=== process_csv_file COMPLETADO ===")
        
        # Crear directorio temporal separado para el ZIP
        zip_dir = tempfile.mkdtemp()
        zip_path = os.path.join(zip_dir, "archivos_procesados.zip")
        logger.info(f"Directorio ZIP creado: {zip_dir}")
        logger.info(f"Ruta del ZIP: {zip_path}")
        
        # Crear ZIP con ambos archivos
        with zipfile.ZipFile(zip_path, "w") as zipf:
            zipf.write(output_file, nombre_archivo_salida)
            if os.path.exists(error_file) and os.path.getsize(error_file) > 0:
                zipf.write(error_file, nombre_archivo_errores)
        logger.info("ZIP creado exitosamente")
        
        logger.info(f"Archivo procesado exitosamente: {file.filename}")
        return FileResponse(
            zip_path, filename="archivos_procesados.zip", media_type="application/zip"
        )
        
    except Exception as e:
        logger.error(f"Error procesando archivo DIAN disciplinarios: {str(e)}")
        logger.error(f"Traceback completo:", exc_info=True)
        return JSONResponse(
            status_code=500, content={"error": f"Error procesando archivo: {e}"}
        )
    finally:
        logger.info("=== INICIANDO LIMPIEZA DE ARCHIVOS ===")
        # Limpiar archivos temporales de procesamiento
        try:
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
                logger.info(f"Archivos temporales de procesamiento limpiados: {temp_dir}")
        except Exception as cleanup_error:
            logger.warning(f"Error limpiando archivos temporales de procesamiento: {cleanup_error}")
        
        # Limpiar archivos temporales del ZIP después de un delay
        try:
            if zip_dir and os.path.exists(zip_dir):
                # Programar limpieza después de 30 segundos para permitir descarga
                import threading
                import time
                
                def delayed_cleanup():
                    time.sleep(30)
                    try:
                        if os.path.exists(zip_dir):
                            shutil.rmtree(zip_dir)
                            logger.info(f"Archivos temporales del ZIP limpiados: {zip_dir}")
                    except Exception as e:
                        logger.warning(f"Error en limpieza retrasada: {e}")
                
                cleanup_thread = threading.Thread(target=delayed_cleanup)
                cleanup_thread.daemon = True
                cleanup_thread.start()
                logger.info("Limpieza retrasada programada")
                
        except Exception as cleanup_error:
            logger.warning(f"Error programando limpieza del ZIP: {cleanup_error}")
        
        logger.info("=== FIN: normalizar_columnas_dian_disciplinarios_upload ===")


@router.post("/Dian/pqr/upload/")
def normalizar_columnas_dian_pqr_upload(
    file: UploadFile = File(...),
    nombre_archivo_salida: str = Form(...),
    nombre_archivo_errores: str = Form(...),
):
    """Normaliza columnas para archivos PQR de DIAN usando el sistema unificado"""
    temp_dir = None
    zip_dir = None
    
    try:
        # Configurar directorio temporal para procesamiento
        temp_dir = tempfile.mkdtemp()
        temp_input_path = os.path.join(temp_dir, file.filename)
        
        # Guardar archivo subido
        with open(temp_input_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        output_file = os.path.join(temp_dir, nombre_archivo_salida)
        error_file = os.path.join(temp_dir, nombre_archivo_errores)
        
        # type_mapping para DIAN PQR usando nombres de columnas
        type_mapping = {
            "datetime": ["FECHA_RADICACION", "FECHA_RESPUESTA"],
            "str": ["NOMBRE_ARCHIVO", "MES_REPORTE", "NUMERO_PQR", "TIPO_PQR", "DESCRIPCION", 
                   "ESTADO", "RESPUESTA", "FUNCIONARIO_RESPONSABLE"],
            "nit": ["DOCUMENTO_SOLICITANTE"],
        }
        
        # Usar el sistema unificado
        process_csv_file('DIAN', 'pqr', temp_input_path, output_file, error_file, type_mapping)
        
        # Crear directorio temporal separado para el ZIP
        zip_dir = tempfile.mkdtemp()
        zip_path = os.path.join(zip_dir, "archivos_procesados.zip")
        
        # Crear ZIP con ambos archivos
        with zipfile.ZipFile(zip_path, "w") as zipf:
            zipf.write(output_file, nombre_archivo_salida)
            if os.path.exists(error_file) and os.path.getsize(error_file) > 0:
                zipf.write(error_file, nombre_archivo_errores)
        
        logger.info(f"Archivo procesado exitosamente: {file.filename}")
        return FileResponse(
            zip_path, filename="archivos_procesados.zip", media_type="application/zip"
        )
        
    except Exception as e:
        logger.error(f"Error procesando archivo DIAN PQR: {str(e)}")
        return JSONResponse(
            status_code=500, content={"error": f"Error procesando archivo: {e}"}
        )
    finally:
        # Limpiar archivos temporales de procesamiento
        try:
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
                logger.info(f"Archivos temporales de procesamiento limpiados: {temp_dir}")
        except Exception as cleanup_error:
            logger.warning(f"Error limpiando archivos temporales de procesamiento: {cleanup_error}")
        
        # Limpiar archivos temporales del ZIP después de un delay
        try:
            if zip_dir and os.path.exists(zip_dir):
                # Programar limpieza después de 30 segundos para permitir descarga
                import threading
                import time
                
                def delayed_cleanup():
                    time.sleep(30)
                    try:
                        if os.path.exists(zip_dir):
                            shutil.rmtree(zip_dir)
                            logger.info(f"Archivos temporales del ZIP limpiados: {zip_dir}")
                    except Exception as e:
                        logger.warning(f"Error en limpieza retrasada: {e}")
                
                cleanup_thread = threading.Thread(target=delayed_cleanup)
                cleanup_thread.daemon = True
                cleanup_thread.start()
                
        except Exception as cleanup_error:
            logger.warning(f"Error programando limpieza del ZIP: {cleanup_error}")


@router.post("/Dian/notificaciones/upload/")
def normalizar_columnas_dian_notificaciones_upload(
    file: UploadFile = File(...),
    nombre_archivo_salida: str = Form(...),
    nombre_archivo_errores: str = Form(...),
):
    """Normaliza columnas para archivos de notificaciones de DIAN usando el sistema unificado"""
    temp_dir = None
    zip_dir = None
    
    try:
        # Configurar directorio temporal para procesamiento
        temp_dir = tempfile.mkdtemp()
        temp_input_path = os.path.join(temp_dir, file.filename)
        
        # Guardar archivo subido
        with open(temp_input_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        output_file = os.path.join(temp_dir, nombre_archivo_salida)
        error_file = os.path.join(temp_dir, nombre_archivo_errores)
        
        # type_mapping para DIAN notificaciones usando nombres de columnas
        type_mapping = {
            "datetime": ["FECHA_ACTO", "FECHA_PLANILLA_REMISION", "FECHA_CITACION", 
                        "FECHA_PLANILLA_CORR", "FECHA_NOTIFICACION", "FECHA_EJECUTORIA"],
            "str": ["PLAN_IDENTIF_ACTO", "CODIGO_ADMINISTRACION", "SECCIONAL", "CODIGO_DEPENDENCIA",
                   "DEPENDENCIA", "ANO_CALENDARIO", "CODIGO_ACTO", "DESCRIPCION_ACTO", "ANO_ACTO",
                   "CONSECUTIVO_ACTO", "RAZON_SOCIAL", "DIRECCION", "PLANILLA_REMISION", "FUNCIONARIO_ENVIA",
                   "PLANILLA_CORR", "GUIA", "COD_ESTADO", "COD_NOTIFICACION"],
            "nit": ["NIT"],
            "float": ["CUANTIA_ACTO"],
            "choice_estado_notificacion": ["ESTADO_NOTIFICACION"],
            "choice_proceso": ["PROCESO"],
            "choice_dependencia": ["DEPENDENCIA"],
        }
        
        # Usar el sistema unificado
        process_csv_file('DIAN', 'notificaciones', temp_input_path, output_file, error_file, type_mapping)
        
        # Crear directorio temporal separado para el ZIP
        zip_dir = tempfile.mkdtemp()
        zip_path = os.path.join(zip_dir, "archivos_procesados.zip")
        
        # Crear ZIP con ambos archivos
        with zipfile.ZipFile(zip_path, "w") as zipf:
            zipf.write(output_file, nombre_archivo_salida)
            if os.path.exists(error_file) and os.path.getsize(error_file) > 0:
                zipf.write(error_file, nombre_archivo_errores)
        
        logger.info(f"Archivo procesado exitosamente: {file.filename}")
        return FileResponse(
            zip_path, filename="archivos_procesados.zip", media_type="application/zip"
        )
        
    except Exception as e:
        logger.error(f"Error procesando archivo DIAN notificaciones: {str(e)}")
        return JSONResponse(
            status_code=500, content={"error": f"Error procesando archivo: {e}"}
        )
    finally:
        # Limpiar archivos temporales de procesamiento
        try:
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
                logger.info(f"Archivos temporales de procesamiento limpiados: {temp_dir}")
        except Exception as cleanup_error:
            logger.warning(f"Error limpiando archivos temporales de procesamiento: {cleanup_error}")
        
        # Limpiar archivos temporales del ZIP después de un delay
        try:
            if zip_dir and os.path.exists(zip_dir):
                # Programar limpieza después de 30 segundos para permitir descarga
                import threading
                import time
                
                def delayed_cleanup():
                    time.sleep(30)
                    try:
                        if os.path.exists(zip_dir):
                            shutil.rmtree(zip_dir)
                            logger.info(f"Archivos temporales del ZIP limpiados: {zip_dir}")
                    except Exception as e:
                        logger.warning(f"Error en limpieza retrasada: {e}")
                
                cleanup_thread = threading.Thread(target=delayed_cleanup)
                cleanup_thread.daemon = True
                cleanup_thread.start()
                
        except Exception as cleanup_error:
            logger.warning(f"Error programando limpieza del ZIP: {cleanup_error}")


# Endpoint adicional para obtener información de procesadores disponibles
@router.get("/processors/info")
def get_processors_info():
    """Obtiene información de todos los procesadores disponibles."""
    try:
        from repository.proyectos.unified_csv_processor import get_processor_info
        
        processors_info = {}
        
        # Información de procesadores disponibles
        available_processors = [
            ('DIAN', 'notificaciones'),
            ('DIAN', 'disciplinarios'),
            ('DIAN', 'pqr'),
            ('COLJUEGOS', 'disciplinarios'),
            ('COLJUEGOS', 'pqr'),
        ]
        
        for project_code, module_name in available_processors:
            try:
                info = get_processor_info(project_code, module_name)
                processors_info[f"{project_code}:{module_name}"] = info
            except Exception as e:
                logger.warning(f"No se pudo obtener información para {project_code}:{module_name}: {e}")
                processors_info[f"{project_code}:{module_name}"] = {"error": str(e)}
        
        return JSONResponse(content={
            "processors": processors_info,
            "total_available": len(processors_info)
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo información de procesadores: {str(e)}")
        return JSONResponse(
            status_code=500, content={"error": f"Error obteniendo información: {e}"}
        ) 


