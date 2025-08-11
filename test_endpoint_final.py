#!/usr/bin/env python3
"""
Script final para probar el endpoint de DIAN disciplinarios con el archivo real del usuario.
"""

import requests
import os
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_dian_disciplinarios_endpoint():
    """Prueba el endpoint de DIAN disciplinarios con el archivo real del usuario."""
    
    logger.info("=== PRUEBA FINAL DEL ENDPOINT DIAN DISCIPLINARIOS ===")
    
    # URL correcta del endpoint
    url = "http://localhost:8000/api/v1/normalizar-columnas/Dian/disciplinarios/upload/"
    
    # Ruta correcta del archivo del usuario
    file_path = "/home/yeralcode/Descargas/consolidado_2021_disciplinarios.csv"
    
    # Verificar que el archivo existe
    if not os.path.exists(file_path):
        logger.error(f"❌ El archivo no existe: {file_path}")
        return
    
    # Obtener el nombre del archivo
    filename = os.path.basename(file_path)
    logger.info(f"Archivo a procesar: {filename}")
    logger.info(f"Ruta completa: {file_path}")
    
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
            logger.info(f"Headers de respuesta: {dict(response.headers)}")
            
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
                            logger.info("Primeras 500 caracteres del archivo procesado:")
                            logger.info(processed_content[:500])
                            
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
                                logger.warning("Primeras 1000 caracteres del archivo de errores:")
                                logger.warning(error_content[:1000])
                                
                                # Contar líneas de error
                                error_lines = error_content.strip().split('\n')
                                logger.warning(f"Total de líneas de error: {len(error_lines)}")
                                
                                # Mostrar algunos ejemplos de errores
                                logger.warning("Ejemplos de errores encontrados:")
                                for i, line in enumerate(error_lines[:10]):
                                    logger.warning(f"  {i+1}. {line}")
                                
                                if len(error_lines) > 10:
                                    logger.warning(f"  ... y {len(error_lines) - 10} errores más")
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

def test_with_sample_data():
    """Prueba con datos de muestra para verificar el comportamiento."""
    
    logger.info("\n=== PRUEBA CON DATOS DE MUESTRA ===")
    
    # Crear un archivo CSV de prueba con los casos problemáticos
    test_data = """FECHA_DE_RADICACION,FECHA_DE_LOS_HECHOS,EXPEDIENTE,IMPLICADO,DEPENDENCIA,SUBPROCESO,PROCEDIMIENTO,CARGO,ORIGEN,CONDUCTA,ETAPA_PROCESAL,SANCION_IMPUESTA,HECHOS,DECISION_DE_LA_INVESTIGACION,TIPO_DE_PROCESO_AFECTADO,SENALADOS_O_VINCULADOS_CON_LA_INVESTIGACION,ADECUACION_TIPICA,ABOGADO,SENTIDO_DEL_FALLO,QUEJOSO,TIPO_DE_PROCESO,DOCUMENTO_DEL_IMPLICADO,DOC_QUEJOSO,DEPARTAMENTO_DE_LOS_HECHOS,CIUDAD_DE_LOS_HECHOS,DIRECCION_SECCIONAL,PROCESO
2021-01-15,2021-01-10,EXP001,Juan Pérez,DIAN,Disciplinario,Investigación,Cargo1,Origen1,Conducta1,Etapa1,Sanción1,Hechos1,Decisión1,Tipo1,Señalados1,Adecuación1,Abogado1,Sentido1,Quejoso1,Tipo2,12345678,87654321,Cundinamrca,Bogotá D.C.,Oficina Jurídica,Proceso1
2021-01-16,2021-01-11,EXP002,María López,DIAN,Disciplinario,Investigación,Cargo2,Origen2,Conducta2,Etapa2,Sanción2,Hechos2,Decisión2,Tipo2,Señalados2,Adecuación2,Abogado2,Sentido2,Quejoso2,Tipo3,No Aplica,Por Establecer,Cundinamrca,Bogotá D.C.,Gerencia Seguimiento Contractual,Proceso2"""
    
    # Guardar archivo de prueba
    test_file_path = "test_sample_data.csv"
    with open(test_file_path, 'w', encoding='utf-8') as f:
        f.write(test_data)
    
    logger.info(f"Archivo de prueba creado: {test_file_path}")
    
    # URL correcta del endpoint
    url = "http://localhost:8000/api/v1/normalizar-columnas/Dian/disciplinarios/upload/"
    
    # Preparar los datos del formulario
    data = {
        'nombre_archivo_salida': 'procesado_test_sample.csv',
        'nombre_archivo_errores': 'errores_test_sample.txt'
    }
    
    try:
        # Enviar archivo de prueba
        with open(test_file_path, 'rb') as f:
            files = {'file': ('test_sample_data.csv', f, 'text/csv')}
            
            logger.info("Enviando archivo de prueba al endpoint...")
            response = requests.post(url, data=data, files=files)
            
            logger.info(f"Código de respuesta: {response.status_code}")
            
            if response.status_code == 200:
                logger.info("✅ Archivo de prueba procesado exitosamente")
                
                # Guardar el archivo ZIP de respuesta
                output_path = "archivos_procesados_test_sample.zip"
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                logger.info(f"Archivo ZIP guardado como: {output_path}")
                
                # Extraer y revisar archivos
                import zipfile
                with zipfile.ZipFile(output_path, 'r') as zipf:
                    file_list = zipf.namelist()
                    logger.info(f"Archivos en el ZIP: {file_list}")
                    
                    # Revisar archivo procesado
                    for file_name in file_list:
                        if 'procesado' in file_name.lower():
                            logger.info(f"Extrayendo archivo procesado: {file_name}")
                            zipf.extract(file_name, "temp_extract")
                            
                            with open(f"temp_extract/{file_name}", 'r', encoding='utf-8') as f:
                                processed_content = f.read()
                            
                            logger.info("Contenido del archivo procesado:")
                            logger.info(processed_content)
                            
                            os.remove(f"temp_extract/{file_name}")
                            break
                    
                    # Revisar archivo de errores
                    for file_name in file_list:
                        if 'errores' in file_name.lower():
                            logger.info(f"Extrayendo archivo de errores: {file_name}")
                            zipf.extract(file_name, "temp_extract")
                            
                            with open(f"temp_extract/{file_name}", 'r', encoding='utf-8') as f:
                                error_content = f.read()
                            
                            if error_content.strip():
                                logger.warning(f"⚠️ Archivo de errores contiene: {len(error_content)} caracteres")
                                logger.warning("Contenido del archivo de errores:")
                                logger.warning(error_content)
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
    
    finally:
        # Limpiar archivo de prueba
        if os.path.exists(test_file_path):
            os.remove(test_file_path)
            logger.info(f"Archivo de prueba eliminado: {test_file_path}")

if __name__ == "__main__":
    logger.info("Iniciando pruebas finales del endpoint...")
    
    # Primero probar con datos de muestra
    test_with_sample_data()
    
    # Luego probar con el archivo real del usuario
    test_dian_disciplinarios_endpoint()
    
    logger.info("✅ Pruebas finales completadas") 