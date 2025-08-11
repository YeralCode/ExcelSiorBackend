#!/usr/bin/env python3
"""
Script para probar el endpoint con datos problemáticos específicos.
"""

import requests
import os
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_endpoint_with_problematic_data():
    """Prueba el endpoint con datos problemáticos específicos."""
    
    logger.info("=== PRUEBA DEL ENDPOINT CON DATOS PROBLEMÁTICOS ===")
    
    # URL del endpoint
    url = "http://localhost:8000/api/v1/normalizar-columnas/Dian/disciplinarios/upload/"
    
    # Ruta del archivo CSV con datos problemáticos
    file_path = "test_data_with_problems.csv"
    
    # Verificar que el archivo existe
    if not os.path.exists(file_path):
        logger.error(f"❌ El archivo no existe: {file_path}")
        return
    
    # Obtener el nombre del archivo
    filename = os.path.basename(file_path)
    logger.info(f"Archivo a procesar: {filename}")
    logger.info(f"Ruta completa: {os.path.abspath(file_path)}")
    
    # Verificar el tamaño del archivo
    file_size = os.path.getsize(file_path)
    logger.info(f"Tamaño del archivo: {file_size} bytes")
    
    # Preparar los datos del formulario
    data = {
        'nombre_archivo_salida': f'procesado_{filename}',
        'nombre_archivo_errores': f'errores_{filename}.txt'
    }
    
    logger.info(f"Datos del formulario: {data}")
    logger.info(f"URL del endpoint: {url}")
    
    try:
        # Abrir y enviar el archivo
        with open(file_path, 'rb') as f:
            files = {'file': (filename, f, 'text/csv')}
            
            logger.info("Enviando archivo al endpoint...")
            response = requests.post(url, data=data, files=files)
            
            logger.info(f"Código de respuesta: {response.status_code}")
            
            if response.status_code == 200:
                logger.info("✅ Archivo procesado exitosamente")
                
                # Guardar el archivo ZIP de respuesta
                output_path = f"archivos_procesados_{filename}.zip"
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                logger.info(f"Archivo ZIP guardado como: {output_path}")
                
                # Verificar el contenido del ZIP
                import zipfile
                with zipfile.ZipFile(output_path, 'r') as zipf:
                    file_list = zipf.namelist()
                    logger.info(f"Archivos en el ZIP: {file_list}")
                    
                    # Extraer y revisar el archivo procesado
                    for file_name in file_list:
                        if 'procesado' in file_name.lower():
                            logger.info(f"Extrayendo archivo procesado: {file_name}")
                            zipf.extract(file_name, "temp_extract")
                            
                            with open(f"temp_extract/{file_name}", 'r', encoding='utf-8') as f:
                                processed_content = f.read()
                            
                            logger.info(f"Archivo procesado tiene {len(processed_content)} caracteres")
                            logger.info("Primeras 1000 caracteres del archivo procesado:")
                            logger.info(processed_content[:1000])
                            
                            os.remove(f"temp_extract/{file_name}")
                            break
                    
                    # Extraer y revisar el archivo de errores
                    for file_name in file_list:
                        if 'errores' in file_name.lower():
                            logger.info(f"Extrayendo archivo de errores: {file_name}")
                            zipf.extract(file_name, "temp_extract")
                            
                            with open(f"temp_extract/{file_name}", 'r', encoding='utf-8') as f:
                                error_content = f.read()
                            
                            if error_content.strip():
                                logger.warning(f"⚠️ Archivo de errores contiene: {len(error_content)} caracteres")
                                
                                # Contar líneas de error
                                error_lines = error_content.strip().split('\n')
                                logger.warning(f"Total de líneas de error: {len(error_lines)}")
                                
                                # Analizar tipos de errores
                                error_types = {}
                                for line in error_lines[1:]:  # Saltar header
                                    if '|' in line:
                                        parts = line.split('|')
                                        if len(parts) >= 3:
                                            error_type = parts[2]  # Tipo de error
                                            error_types[error_type] = error_types.get(error_type, 0) + 1
                                
                                logger.warning("Distribución de errores por tipo:")
                                for error_type, count in error_types.items():
                                    logger.warning(f"  {error_type}: {count} errores")
                                
                                # Mostrar algunos ejemplos de errores
                                logger.warning("Ejemplos de errores encontrados:")
                                for i, line in enumerate(error_lines[1:11]):  # Primeros 10 errores
                                    logger.warning(f"  {i+1}. {line}")
                                
                                if len(error_lines) > 11:
                                    logger.warning(f"  ... y {len(error_lines) - 11} errores más")
                                
                                # Verificar casos específicos problemáticos
                                logger.info("\n=== ANÁLISIS DE CASOS PROBLEMÁTICOS ===")
                                
                                # Buscar errores específicos
                                bogota_errors = [line for line in error_lines if 'bogotá' in line.lower() or 'bogota' in line.lower()]
                                cundinamarca_errors = [line for line in error_lines if 'cundinamarca' in line.lower() or 'cundinamrca' in line.lower()]
                                oficina_errors = [line for line in error_lines if 'oficina jurídica' in line.lower()]
                                gerencia_errors = [line for line in error_lines if 'gerencia seguimiento' in line.lower()]
                                por_establecer_errors = [line for line in error_lines if 'por establecer' in line.lower()]
                                no_aplica_errors = [line for line in error_lines if 'no aplica' in line.lower()]
                                
                                logger.info(f"Errores con 'Bogotá': {len(bogota_errors)}")
                                logger.info(f"Errores con 'Cundinamarca': {len(cundinamarca_errors)}")
                                logger.info(f"Errores con 'Oficina Jurídica': {len(oficina_errors)}")
                                logger.info(f"Errores con 'Gerencia Seguimiento': {len(gerencia_errors)}")
                                logger.info(f"Errores con 'Por Establecer': {len(por_establecer_errors)}")
                                logger.info(f"Errores con 'No Aplica': {len(no_aplica_errors)}")
                                
                                if bogota_errors:
                                    logger.error("❌ AÚN HAY ERRORES CON 'Bogotá'")
                                else:
                                    logger.info("✅ NO hay errores con 'Bogotá'")
                                
                                if cundinamarca_errors:
                                    logger.error("❌ AÚN HAY ERRORES CON 'Cundinamarca'")
                                else:
                                    logger.info("✅ NO hay errores con 'Cundinamarca'")
                                
                                if oficina_errors:
                                    logger.error("❌ AÚN HAY ERRORES CON 'Oficina Jurídica'")
                                else:
                                    logger.info("✅ NO hay errores con 'Oficina Jurídica'")
                                
                                if gerencia_errors:
                                    logger.error("❌ AÚN HAY ERRORES CON 'Gerencia Seguimiento'")
                                else:
                                    logger.info("✅ NO hay errores con 'Gerencia Seguimiento'")
                                
                                if por_establecer_errors:
                                    logger.error("❌ AÚN HAY ERRORES CON 'Por Establecer'")
                                else:
                                    logger.info("✅ NO hay errores con 'Por Establecer'")
                                
                                if no_aplica_errors:
                                    logger.error("❌ AÚN HAY ERRORES CON 'No Aplica'")
                                else:
                                    logger.info("✅ NO hay errores con 'No Aplica'")
                                
                            else:
                                logger.info("✅ Archivo de errores está vacío (sin errores)")
                            
                            os.remove(f"temp_extract/{file_name}")
                            break
                
                # Limpiar directorio temporal
                if os.path.exists("temp_extract"):
                    os.rmdir("temp_extract")
                
            else:
                logger.error(f"❌ Error en la respuesta: {response.status_code}")
                logger.error(f"Contenido de la respuesta: {response.text}")
                
    except Exception as e:
        logger.error(f"❌ Error durante la prueba: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    logger.info("Iniciando prueba con datos problemáticos...")
    test_endpoint_with_problematic_data()
    logger.info("✅ Prueba completada") 