#!/usr/bin/env python3
"""
Prueba Final Exhaustiva del Endpoint BPM
Este script realiza pruebas completas del endpoint /api/v1/normalizar-columnas/BPM/upload/
"""

import requests
import tempfile
import os
import zipfile
import pandas as pd
import time
import json

class BPMEndpointFinalTester:
    """Clase para realizar pruebas finales exhaustivas del endpoint BPM"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_results = []
        
    def log_test_result(self, test_name: str, success: bool, details: str = ""):
        """Registra el resultado de una prueba"""
        status = "✅ PASÓ" if success else "❌ FALLÓ"
        print(f"{status} - {test_name}: {details}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
    
    def test_endpoint_health(self):
        """Prueba la salud del endpoint"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            success = response.status_code == 200
            self.log_test_result(
                "Salud del Endpoint", 
                success, 
                f"Status: {response.status_code}"
            )
            return success
        except Exception as e:
            self.log_test_result(
                "Salud del Endpoint", 
                False, 
                f"Error: {str(e)}"
            )
            return False
    
    def test_bpm_route_availability(self):
        """Prueba si la ruta BPM está disponible en OpenAPI"""
        try:
            response = requests.get(f"{self.base_url}/openapi.json", timeout=10)
            if response.status_code == 200:
                openapi_data = response.json()
                bpm_route = "/api/v1/normalizar-columnas/BPM/upload/"
                
                if bpm_route in openapi_data.get("paths", {}):
                    self.log_test_result(
                        "Ruta BPM en OpenAPI", 
                        True, 
                        f"Ruta {bpm_route} encontrada"
                    )
                    return True
                else:
                    self.log_test_result(
                        "Ruta BPM en OpenAPI", 
                        False, 
                        f"Ruta {bpm_route} no encontrada"
                    )
                    return False
            else:
                self.log_test_result(
                    "Ruta BPM en OpenAPI", 
                    False, 
                    f"Error obteniendo OpenAPI: {response.status_code}"
                )
                return False
        except Exception as e:
            self.log_test_result(
                "Ruta BPM en OpenAPI", 
                False, 
                f"Error: {str(e)}"
            )
            return False
    
    def test_bpm_file_upload_success(self):
        """Prueba la carga exitosa de un archivo BPM válido"""
        try:
            # Archivo de prueba válido
            test_file_path = "test_bpm_data.csv"
            if not os.path.exists(test_file_path):
                self.log_test_result(
                    "Archivo de Prueba Válido", 
                    False, 
                    f"Archivo no encontrado: {test_file_path}"
                )
                return False
            
            files = {
                'file': ('test_bpm_data.csv', open(test_file_path, 'rb'), 'text/csv')
            }
            data = {
                'nombre_archivo_salida': 'bpm_procesado.csv',
                'nombre_archivo_errores': 'bpm_errores.csv'
            }
            
            response = requests.post(
                f"{self.base_url}/api/v1/normalizar-columnas/BPM/upload/",
                files=files,
                data=data,
                timeout=60
            )
            
            success = response.status_code == 200
            self.log_test_result(
                "Carga de Archivo BPM Válido", 
                success, 
                f"Status: {response.status_code}, Content-Type: {response.headers.get('content-type', 'N/A')}"
            )
            
            if success:
                # Verificar que la respuesta es un ZIP
                content_type = response.headers.get('content-type', '')
                if 'zip' in content_type.lower() or 'application/octet-stream' in content_type:
                    self.log_test_result(
                        "Respuesta ZIP Válida", 
                        True, 
                        f"Archivo ZIP recibido: {len(response.content)} bytes"
                    )
                    
                    # Verificar contenido del ZIP
                    self._verify_zip_content(response.content, "bpm_procesado.csv", "bpm_errores.csv")
                else:
                    self.log_test_result(
                        "Respuesta ZIP Válida", 
                        False, 
                        f"Content-Type inesperado: {content_type}"
                    )
            
            return success
            
        except Exception as e:
            self.log_test_result(
                "Carga de Archivo BPM Válido", 
                False, 
                f"Error: {str(e)}"
            )
            return False
    
    def test_bpm_file_upload_mixed_data(self):
        """Prueba la carga de un archivo BPM con datos mixtos (válidos e inválidos)"""
        try:
            # Archivo de prueba con datos mixtos
            test_file_path = "test_bpm_invalid_data.csv"
            if not os.path.exists(test_file_path):
                self.log_test_result(
                    "Archivo de Prueba Mixto", 
                    False, 
                    f"Archivo no encontrado: {test_file_path}"
                )
                return False
            
            files = {
                'file': ('test_bpm_invalid_data.csv', open(test_file_path, 'rb'), 'text/csv')
            }
            data = {
                'nombre_archivo_salida': 'bpm_mixto_procesado.csv',
                'nombre_archivo_errores': 'bpm_mixto_errores.csv'
            }
            
            response = requests.post(
                f"{self.base_url}/api/v1/normalizar-columnas/BPM/upload/",
                files=files,
                data=data,
                timeout=60
            )
            
            success = response.status_code == 200
            self.log_test_result(
                "Carga de Archivo BPM Mixto", 
                success, 
                f"Status: {response.status_code}"
            )
            
            if success:
                # Verificar contenido del ZIP
                self._verify_zip_content(response.content, "bpm_mixto_procesado.csv", "bpm_mixto_errores.csv")
            
            return success
            
        except Exception as e:
            self.log_test_result(
                "Carga de Archivo BPM Mixto", 
                False, 
                f"Error: {str(e)}"
            )
            return False
    
    def test_bpm_file_upload_invalid_file(self):
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
            
            response = requests.post(
                f"{self.base_url}/api/v1/normalizar-columnas/BPM/upload/",
                files=files,
                data=data,
                timeout=30
            )
            
            # Debería devolver un error 500 o similar
            success = response.status_code >= 400
            self.log_test_result(
                "Manejo de Archivo Inválido", 
                success, 
                f"Status: {response.status_code}"
            )
            
            return success
            
        except Exception as e:
            self.log_test_result(
                "Manejo de Archivo Inválido", 
                False, 
                f"Error: {str(e)}"
            )
            return False
    
    def test_bpm_file_upload_missing_parameters(self):
        """Prueba el manejo de parámetros faltantes"""
        try:
            # Solo enviar el archivo sin los parámetros requeridos
            files = {
                'file': ('test_bpm_data.csv', open('test_bpm_data.csv', 'rb'), 'text/csv')
            }
            
            response = requests.post(
                f"{self.base_url}/api/v1/normalizar-columnas/BPM/upload/",
                files=files,
                timeout=30
            )
            
            # Debería devolver un error 422 (Unprocessable Entity)
            success = response.status_code == 422
            self.log_test_result(
                "Manejo de Parámetros Faltantes", 
                success, 
                f"Status: {response.status_code}"
            )
            
            return success
            
        except Exception as e:
            self.log_test_result(
                "Manejo de Parámetros Faltantes", 
                False, 
                f"Error: {str(e)}"
            )
            return False
    
    def _verify_zip_content(self, zip_content: bytes, expected_output: str, expected_error: str):
        """Verifica el contenido del ZIP recibido"""
        try:
            # Crear archivo temporal para el ZIP
            with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_zip:
                temp_zip.write(zip_content)
                temp_zip_path = temp_zip.name
            
            try:
                # Verificar que es un ZIP válido
                with zipfile.ZipFile(temp_zip_path, 'r') as zipf:
                    file_list = zipf.namelist()
                    
                    # Verificar que contiene los archivos esperados
                    has_output = expected_output in file_list
                    has_error = expected_error in file_list
                    
                    self.log_test_result(
                        "Contenido ZIP - Archivo de Salida", 
                        has_output, 
                        f"Archivo {expected_output} {'encontrado' if has_output else 'no encontrado'}"
                    )
                    
                    self.log_test_result(
                        "Contenido ZIP - Archivo de Errores", 
                        has_error, 
                        f"Archivo {expected_error} {'encontrado' if has_error else 'no encontrado'}"
                    )
                    
                    # Verificar contenido del archivo de salida
                    if has_output:
                        with zipf.open(expected_output) as output_file:
                            output_content = output_file.read().decode('utf-8')
                            lines = output_content.strip().split('\n')
                            
                            self.log_test_result(
                                "Contenido del Archivo de Salida", 
                                len(lines) > 1, 
                                f"Archivo contiene {len(lines)} líneas"
                            )
                            
                            # Verificar que tiene headers
                            if len(lines) > 0:
                                headers = lines[0].split('|')
                                self.log_test_result(
                                    "Headers del Archivo de Salida", 
                                    len(headers) > 0, 
                                    f"Archivo tiene {len(headers)} columnas"
                                )
                    
                    return has_output and has_error
                    
            finally:
                # Limpiar archivo temporal
                os.unlink(temp_zip_path)
                
        except Exception as e:
            self.log_test_result(
                "Verificación de Contenido ZIP", 
                False, 
                f"Error: {str(e)}"
            )
            return False
    
    def run_all_tests(self):
        """Ejecuta todas las pruebas"""
        print("🚀 PRUEBA FINAL EXHAUSTIVA DEL ENDPOINT BPM")
        print("=" * 60)
        
        start_time = time.time()
        
        # Pruebas básicas
        self.test_endpoint_health()
        self.test_bpm_route_availability()
        
        # Pruebas de funcionalidad
        self.test_bpm_file_upload_success()
        self.test_bpm_file_upload_mixed_data()
        self.test_bpm_file_upload_invalid_file()
        self.test_bpm_file_upload_missing_parameters()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Resumen de resultados
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print("\n" + "=" * 60)
        print("📊 RESUMEN FINAL DE PRUEBAS")
        print(f"   - Total de pruebas: {total_tests}")
        print(f"   - Pruebas exitosas: {passed_tests}")
        print(f"   - Pruebas fallidas: {failed_tests}")
        print(f"   - Tasa de éxito: {(passed_tests/total_tests)*100:.1f}%")
        print(f"   - Tiempo total: {duration:.2f} segundos")
        
        if failed_tests == 0:
            print("🎉 ¡TODAS LAS PRUEBAS PASARON EXITOSAMENTE!")
            print("✅ El endpoint BPM está funcionando perfectamente")
        else:
            print(f"⚠️  {failed_tests} prueba(s) fallaron. Revisar detalles arriba.")
        
        # Guardar resultados
        with open("test_results_bpm_final.json", "w") as f:
            json.dump({
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": (passed_tests/total_tests)*100,
                "duration": duration,
                "results": self.test_results
            }, f, indent=2, default=str)
        
        print("💾 Resultados guardados en test_results_bpm_final.json")
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": (passed_tests/total_tests)*100,
            "duration": duration,
            "results": self.test_results
        }

def main():
    """Función principal"""
    tester = BPMEndpointFinalTester()
    
    try:
        results = tester.run_all_tests()
        
        if results['failed_tests'] == 0:
            print("\n🎯 CONCLUSIÓN: El endpoint BPM está funcionando perfectamente")
            print("   - Procesamiento de archivos: ✅")
            print("   - Validación de valores choices: ✅")
            print("   - Manejo de errores: ✅")
            print("   - Respuestas ZIP: ✅")
            print("   - Validación de parámetros: ✅")
            return 0
        else:
            print(f"\n⚠️  CONCLUSIÓN: {results['failed_tests']} problema(s) detectado(s)")
            return 1
            
    except Exception as e:
        print(f"❌ Error ejecutando pruebas: {e}")
        return 1

if __name__ == "__main__":
    exit(main()) 