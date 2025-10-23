#!/usr/bin/env python3
"""
Prueba Exhaustiva del Endpoint BPM
Este script realiza pruebas completas del endpoint /BPM/upload/ para verificar
que funcione correctamente con archivos CSV usando separador |
"""

import asyncio
import httpx
import pandas as pd
import zipfile
import tempfile
import os
import shutil
import time
from pathlib import Path
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BPMEndpointTester:
    """Clase para realizar pruebas exhaustivas del endpoint BPM"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_results = []
        self.test_data_path = "test_bpm_data.csv"
        
    def log_test_result(self, test_name: str, success: bool, details: str = ""):
        """Registra el resultado de una prueba"""
        status = "✅ PASÓ" if success else "❌ FALLÓ"
        logger.info(f"{status} - {test_name}: {details}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
    
    def analyze_csv_structure(self, csv_path: str) -> dict:
        """Analiza la estructura del CSV de prueba"""
        try:
            # Leer CSV con separador |
            df = pd.read_csv(csv_path, sep='|', encoding='utf-8')
            
            analysis = {
                "total_rows": len(df),
                "total_columns": len(df.columns),
                "columns": list(df.columns),
                "data_types": df.dtypes.to_dict(),
                "sample_data": df.head(2).to_dict('records'),
                "separator_detected": "|"
            }
            
            logger.info(f"📊 Análisis del CSV:")
            logger.info(f"   - Filas: {analysis['total_rows']}")
            logger.info(f"   - Columnas: {analysis['total_columns']}")
            logger.info(f"   - Separador: {analysis['separator_detected']}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analizando CSV: {e}")
            return {"error": str(e)}
    
    def validate_csv_content(self, csv_path: str) -> dict:
        """Valida el contenido del CSV contra los valores choices de BPM"""
        try:
            df = pd.read_csv(csv_path, sep='|', encoding='utf-8')
            
            # Campos que deben tener valores válidos según choices
            choice_fields = {
                "Programa": ["Selección 2014", "Denuncias"],
                "Estado": ["Terminado", "terminado"],
                "Tipo de proceso concursal": ["Liquidación"],
                "Área que informa proceso": ["Completitud"],
                "Etapa con la que migró BPM": ["COMPLETITUD", "OMISOS_Y_ATENCION_APORTANTES", "NOTIF_RDOC"]
            }
            
            validation_results = {}
            
            for field, expected_values in choice_fields.items():
                if field in df.columns:
                    unique_values = df[field].dropna().unique()
                    valid_values = [val for val in unique_values if val in expected_values]
                    invalid_values = [val for val in unique_values if val not in expected_values]
                    
                    validation_results[field] = {
                        "total_values": len(unique_values),
                        "valid_values": valid_values,
                        "invalid_values": invalid_values,
                        "valid_percentage": len(valid_values) / len(unique_values) * 100 if unique_values.size > 0 else 0
                    }
                    
                    logger.info(f"🔍 Validación {field}:")
                    logger.info(f"   - Valores válidos: {valid_values}")
                    logger.info(f"   - Valores inválidos: {invalid_values}")
                    logger.info(f"   - Porcentaje válido: {validation_results[field]['valid_percentage']:.1f}%")
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Error validando contenido CSV: {e}")
            return {"error": str(e)}
    
    async def test_endpoint_availability(self) -> bool:
        """Prueba si el endpoint está disponible"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/docs")
                success = response.status_code == 200
                self.log_test_result(
                    "Endpoint Disponibilidad", 
                    success, 
                    f"Status: {response.status_code}"
                )
                return success
        except Exception as e:
            self.log_test_result(
                "Endpoint Disponibilidad", 
                False, 
                f"Error: {str(e)}"
            )
            return False
    
    async def test_file_upload_success(self) -> bool:
        """Prueba la carga exitosa de un archivo"""
        try:
            # Verificar que el archivo de prueba existe
            if not os.path.exists(self.test_data_path):
                self.log_test_result(
                    "Archivo de Prueba Existe", 
                    False, 
                    f"Archivo no encontrado: {self.test_data_path}"
                )
                return False
            
            self.log_test_result(
                "Archivo de Prueba Existe", 
                True, 
                f"Archivo encontrado: {os.path.getsize(self.test_data_path)} bytes"
            )
            
            # Preparar datos para la carga
            files = {
                'file': ('test_bpm_data.csv', open(self.test_data_path, 'rb'), 'text/csv')
            }
            data = {
                'nombre_archivo_salida': 'bpm_procesado.csv',
                'nombre_archivo_errores': 'bpm_errores.csv'
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/BPM/upload/",
                    files=files,
                    data=data
                )
                
                success = response.status_code == 200
                self.log_test_result(
                    "Carga de Archivo", 
                    success, 
                    f"Status: {response.status_code}, Content-Type: {response.headers.get('content-type', 'N/A')}"
                )
                
                if success:
                    # Verificar que la respuesta es un ZIP
                    content_type = response.headers.get('content-type', '')
                    if 'zip' in content_type.lower() or 'application/octet-stream' in content_type:
                        self.log_test_result(
                            "Respuesta ZIP", 
                            True, 
                            f"Archivo ZIP recibido: {len(response.content)} bytes"
                        )
                    else:
                        self.log_test_result(
                            "Respuesta ZIP", 
                            False, 
                            f"Content-Type inesperado: {content_type}"
                        )
                
                return success
                
        except Exception as e:
            self.log_test_result(
                "Carga de Archivo", 
                False, 
                f"Error: {str(e)}"
            )
            return False
    
    async def test_file_upload_invalid_file(self) -> bool:
        """Prueba el manejo de archivos inválidos"""
        try:
            # Crear un archivo inválido
            invalid_content = "Este no es un CSV válido\nLínea 2\nLínea 3"
            
            files = {
                'file': ('invalid_file.txt', invalid_content.encode(), 'text/plain')
            }
            data = {
                'nombre_archivo_salida': 'output.csv',
                'nombre_archivo_errores': 'errors.csv'
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/BPM/upload/",
                    files=files,
                    data=data
                )
                
                # Debería devolver un error 500 o similar
                success = response.status_code >= 400
                self.log_test_result(
                    "Manejo de Archivo Inválido", 
                    success, 
                    f"Status: {response.status_code}, Respuesta: {response.text[:200]}"
                )
                
                return success
                
        except Exception as e:
            self.log_test_result(
                "Manejo de Archivo Inválido", 
                False, 
                f"Error: {str(e)}"
            )
            return False
    
    async def test_file_upload_missing_parameters(self) -> bool:
        """Prueba el manejo de parámetros faltantes"""
        try:
            # Solo enviar el archivo sin los parámetros requeridos
            files = {
                'file': ('test_bpm_data.csv', open(self.test_data_path, 'rb'), 'text/csv')
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/BPM/upload/",
                    files=files
                )
                
                # Debería devolver un error 422 (Unprocessable Entity)
                success = response.status_code == 422
                self.log_test_result(
                    "Manejo de Parámetros Faltantes", 
                    success, 
                    f"Status: {response.status_code}, Respuesta: {response.text[:200]}"
                )
                
                return success
                
        except Exception as e:
            self.log_test_result(
                "Manejo de Parámetros Faltantes", 
                False, 
                f"Error: {str(e)}"
            )
            return False
    
    def test_csv_processing_quality(self) -> bool:
        """Prueba la calidad del procesamiento del CSV"""
        try:
            # Crear un archivo de prueba pequeño para análisis
            test_csv = """nombre_archivo|mes_reporte|Programa|Estado
test1|01/2020|Selección 2014|Terminado
test2|02/2020|Denuncias|Activo"""
            
            temp_csv = "temp_test.csv"
            with open(temp_csv, 'w', encoding='utf-8') as f:
                f.write(test_csv)
            
            # Analizar el archivo temporal
            analysis = self.analyze_csv_structure(temp_csv)
            
            # Limpiar archivo temporal
            os.remove(temp_csv)
            
            success = analysis.get('total_columns', 0) == 4
            self.log_test_result(
                "Calidad de Procesamiento CSV", 
                success, 
                f"Columnas detectadas: {analysis.get('total_columns', 0)}"
            )
            
            return success
            
        except Exception as e:
            self.log_test_result(
                "Calidad de Procesamiento CSV", 
                False, 
                f"Error: {str(e)}"
            )
            return False
    
    async def run_all_tests(self) -> dict:
        """Ejecuta todas las pruebas"""
        logger.info("🚀 INICIANDO PRUEBAS EXHAUSTIVAS DEL ENDPOINT BPM")
        logger.info("=" * 60)
        
        start_time = time.time()
        
        # Pruebas básicas
        await self.test_endpoint_availability()
        
        # Análisis del CSV de prueba
        csv_analysis = self.analyze_csv_structure(self.test_data_path)
        if "error" not in csv_analysis:
            self.log_test_result(
                "Análisis de Estructura CSV", 
                True, 
                f"CSV analizado correctamente: {csv_analysis['total_rows']} filas, {csv_analysis['total_columns']} columnas"
            )
        
        # Validación de contenido
        validation_results = self.validate_csv_content(self.test_data_path)
        if "error" not in validation_results:
            self.log_test_result(
                "Validación de Contenido CSV", 
                True, 
                f"Contenido validado: {len(validation_results)} campos verificados"
            )
        
        # Pruebas de funcionalidad
        await self.test_file_upload_success()
        await self.test_file_upload_invalid_file()
        await self.test_file_upload_missing_parameters()
        
        # Pruebas de calidad
        self.test_csv_processing_quality()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Resumen de resultados
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        logger.info("=" * 60)
        logger.info("📊 RESUMEN DE PRUEBAS")
        logger.info(f"   - Total de pruebas: {total_tests}")
        logger.info(f"   - Pruebas exitosas: {passed_tests}")
        logger.info(f"   - Pruebas fallidas: {failed_tests}")
        logger.info(f"   - Tasa de éxito: {(passed_tests/total_tests)*100:.1f}%")
        logger.info(f"   - Tiempo total: {duration:.2f} segundos")
        
        if failed_tests == 0:
            logger.info("🎉 ¡TODAS LAS PRUEBAS PASARON EXITOSAMENTE!")
        else:
            logger.warning(f"⚠️  {failed_tests} prueba(s) fallaron. Revisar detalles arriba.")
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": (passed_tests/total_tests)*100,
            "duration": duration,
            "results": self.test_results
        }

async def main():
    """Función principal para ejecutar las pruebas"""
    tester = BPMEndpointTester()
    
    try:
        results = await tester.run_all_tests()
        
        # Guardar resultados en un archivo
        with open("test_results_bpm.json", "w") as f:
            import json
            json.dump(results, f, indent=2, default=str)
        
        logger.info("💾 Resultados guardados en test_results_bpm.json")
        
        return results
        
    except Exception as e:
        logger.error(f"Error ejecutando pruebas: {e}")
        return None

if __name__ == "__main__":
    # Ejecutar pruebas
    results = asyncio.run(main())
    
    if results:
        exit(0 if results['failed_tests'] == 0 else 1)
    else:
        exit(1) 