"""
Tests para el analizador de CSV.

Pruebas unitarias y de integración para el sistema
de análisis automático de archivos CSV.
"""

import pytest
import pandas as pd
import tempfile
import os
from pathlib import Path
from io import BytesIO
from unittest.mock import Mock, patch

from routes.csv_analyzer import DataTypeDetector, router
from fastapi.testclient import TestClient
from fastapi import FastAPI

# Crear aplicación de prueba
app = FastAPI()
app.include_router(router)
client = TestClient(app)

class TestDataTypeDetector:
    """Tests para el detector de tipos de datos."""
    
    def setup_method(self):
        """Configuración inicial para cada test."""
        self.detector = DataTypeDetector()
    
    def test_detect_integer_type(self):
        """Test detección de tipo integer."""
        # Crear datos de prueba
        data = pd.Series(['123', '456', '789', '0', '1000'])
        
        result = self.detector.detect_column_type(data, 'test_column')
        
        assert result['type'] == 'integer'
        assert result['confidence'] > 0.8
        assert 'enteros' in result['reason']
    
    def test_detect_float_type(self):
        """Test detección de tipo float."""
        # Crear datos de prueba
        data = pd.Series(['123.45', '67.89', '0.0', '100.5', '999.99'])
        
        result = self.detector.detect_column_type(data, 'test_column')
        
        assert result['type'] == 'float'
        assert result['confidence'] > 0.7
        assert 'decimales' in result['reason']
    
    def test_detect_date_type(self):
        """Test detección de tipo date."""
        # Crear datos de prueba
        data = pd.Series(['2024-01-01', '2024-02-15', '2024-03-30'])
        
        result = self.detector.detect_column_type(data, 'test_column')
        
        assert result['type'] == 'date'
        assert result['confidence'] > 0.7
        assert 'fecha' in result['reason']
    
    def test_detect_nit_type(self):
        """Test detección de tipo NIT."""
        # Crear datos de prueba
        data = pd.Series(['123456789', '987654321', '111222333'])
        
        result = self.detector.detect_column_type(data, 'NIT')
        
        assert result['type'] == 'nit'
        assert result['confidence'] > 0.8
        assert 'NIT' in result['reason']
    
    def test_detect_boolean_type(self):
        """Test detección de tipo boolean."""
        # Crear datos de prueba
        data = pd.Series(['true', 'false', '1', '0', 'yes', 'no'])
        
        result = self.detector.detect_column_type(data, 'test_column')
        
        assert result['type'] == 'boolean'
        assert result['confidence'] > 0.8
        assert 'booleanos' in result['reason']
    
    def test_detect_percentage_type(self):
        """Test detección de tipo percentage."""
        # Crear datos de prueba
        data = pd.Series(['50%', '25.5%', '100%', '0%'])
        
        result = self.detector.detect_column_type(data, 'test_column')
        
        assert result['type'] == 'percentage'
        assert result['confidence'] > 0.7
        assert 'porcentaje' in result['reason']
    
    def test_detect_string_type(self):
        """Test detección de tipo string por defecto."""
        # Crear datos de prueba
        data = pd.Series(['texto', 'otro texto', 'más texto'])
        
        result = self.detector.detect_column_type(data, 'test_column')
        
        assert result['type'] == 'string'
        assert result['confidence'] == 0.5
        assert 'por defecto' in result['reason']
    
    def test_handle_empty_data(self):
        """Test manejo de datos vacíos."""
        # Crear datos vacíos
        data = pd.Series([])
        
        result = self.detector.detect_column_type(data, 'test_column')
        
        assert result['type'] == 'string'
        assert result['confidence'] == 0.5
    
    def test_handle_null_values(self):
        """Test manejo de valores nulos."""
        # Crear datos con valores nulos
        data = pd.Series(['123', None, '456', '', '789'])
        
        result = self.detector.detect_column_type(data, 'test_column')
        
        assert result['type'] == 'integer'
        assert result['confidence'] > 0.5

class TestCSVAnalyzerAPI:
    """Tests para la API del analizador de CSV."""
    
    def test_analyze_csv_endpoint(self):
        """Test endpoint de análisis de CSV."""
        # Crear archivo CSV de prueba
        csv_content = """columna1,columna2,columna3
123,texto,2024-01-01
456,otro texto,2024-02-15
789,más texto,2024-03-30"""
        
        files = {'file': ('test.csv', csv_content, 'text/csv')}
        data = {
            'project_name': 'DIAN',
            'auto_detect_types': 'true',
            'sample_size': '100'
        }
        
        response = client.post('/csv-analyzer/analyze', files=files, data=data)
        
        assert response.status_code == 200
        result = response.json()
        
        assert result['success'] is True
        assert 'file_info' in result
        assert 'column_analysis' in result
        assert 'data_types' in result
        assert 'recommendations' in result
    
    def test_generate_type_dictionary_endpoint(self):
        """Test endpoint de generación de diccionario de tipos."""
        # Crear archivo CSV de prueba
        csv_content = """PLAN_IDENTIF_ACTO,CODIGO_ADMINISTRACION,NIT
123,456,123456789
789,012,987654321"""
        
        files = {'file': ('test_dian.csv', csv_content, 'text/csv')}
        data = {'project_name': 'DIAN'}
        
        response = client.post('/csv-analyzer/generate-type-dictionary', 
                             files=files, data=data)
        
        assert response.status_code == 200
        result = response.json()
        
        assert 'project_name' in result
        assert 'data_types' in result
        assert 'column_details' in result
        assert result['project_name'] == 'DIAN'
    
    def test_supported_types_endpoint(self):
        """Test endpoint de tipos soportados."""
        response = client.get('/csv-analyzer/supported-types')
        
        assert response.status_code == 200
        result = response.json()
        
        assert 'supported_types' in result
        assert 'type_descriptions' in result
        assert 'integer' in result['supported_types']
        assert 'float' in result['supported_types']
        assert 'date' in result['supported_types']
    
    def test_analyze_csv_without_file(self):
        """Test análisis sin archivo."""
        response = client.post('/csv-analyzer/analyze')
        
        assert response.status_code == 422  # Validation error
    
    def test_analyze_csv_invalid_file(self):
        """Test análisis con archivo inválido."""
        files = {'file': ('test.txt', 'invalid content', 'text/plain')}
        
        response = client.post('/csv-analyzer/analyze', files=files)
        
        # Debería manejar el error graciosamente
        assert response.status_code in [200, 400, 422]
    
    def test_analyze_csv_large_file(self):
        """Test análisis de archivo grande."""
        # Crear archivo CSV grande
        rows = []
        for i in range(1000):
            rows.append(f"{i},texto{i},2024-01-01")
        
        csv_content = "columna1,columna2,columna3\n" + "\n".join(rows)
        
        files = {'file': ('large_test.csv', csv_content, 'text/csv')}
        data = {'sample_size': '100'}
        
        response = client.post('/csv-analyzer/analyze', files=files, data=data)
        
        assert response.status_code == 200
        result = response.json()
        
        assert result['success'] is True
        assert result['file_info']['total_rows'] == 1000

class TestCSVAnalyzerIntegration:
    """Tests de integración para el analizador de CSV."""
    
    def test_full_analysis_workflow(self):
        """Test flujo completo de análisis."""
        # Crear archivo CSV complejo
        csv_content = """PLAN_IDENTIF_ACTO,CODIGO_ADMINISTRACION,NIT,FECHA_ACTO,CUANTIA_ACTO,ESTADO
123,456,123456789,2024-01-01,1000000.50,ACTIVO
789,012,987654321,2024-02-15,2500000.75,INACTIVO
456,789,111222333,2024-03-30,500000.25,ACTIVO"""
        
        files = {'file': ('complex_test.csv', csv_content, 'text/csv')}
        data = {
            'project_name': 'DIAN',
            'auto_detect_types': 'true',
            'sample_size': '100'
        }
        
        # Análisis
        response = client.post('/csv-analyzer/analyze', files=files, data=data)
        assert response.status_code == 200
        
        analysis_result = response.json()
        
        # Verificar tipos detectados
        assert 'integer' in analysis_result['data_types']
        assert 'nit' in analysis_result['data_types']
        assert 'date' in analysis_result['data_types']
        assert 'float' in analysis_result['data_types']
        assert 'string' in analysis_result['data_types']
        
        # Generar diccionario
        dict_response = client.post('/csv-analyzer/generate-type-dictionary', 
                                  files=files, data={'project_name': 'DIAN'})
        assert dict_response.status_code == 200
        
        dict_result = dict_response.json()
        
        # Verificar diccionario
        assert dict_result['project_name'] == 'DIAN'
        assert 'data_types' in dict_result
        assert 'column_details' in dict_result
    
    def test_project_specific_analysis(self):
        """Test análisis específico por proyecto."""
        # Crear archivo CSV con estructura DIAN
        csv_content = """PLAN_IDENTIF_ACTO,CODIGO_ADMINISTRACION,CODIGO_DEPENDENCIA,ANO_CALENDARIO,NIT
123,456,789,2024,123456789
789,012,345,2024,987654321"""
        
        files = {'file': ('dian_test.csv', csv_content, 'text/csv')}
        data = {'project_name': 'DIAN'}
        
        response = client.post('/csv-analyzer/analyze', files=files, data=data)
        assert response.status_code == 200
        
        result = response.json()
        
        # Verificar que se detectaron las columnas específicas de DIAN
        assert 'PLAN_IDENTIF_ACTO' in result['column_analysis']
        assert 'CODIGO_ADMINISTRACION' in result['column_analysis']
        assert 'NIT' in result['column_analysis']
    
    def test_error_handling(self):
        """Test manejo de errores."""
        # Test con archivo corrupto
        files = {'file': ('corrupt.csv', 'invalid,csv,content\nwith,broken,format', 'text/csv')}
        
        response = client.post('/csv-analyzer/analyze', files=files)
        
        # Debería manejar el error sin fallar
        assert response.status_code in [200, 400, 422]
    
    def test_performance_with_large_files(self):
        """Test rendimiento con archivos grandes."""
        # Crear archivo CSV grande
        rows = []
        for i in range(5000):
            rows.append(f"{i},texto{i},2024-01-01,{i*1000.50}")
        
        csv_content = "id,texto,fecha,valor\n" + "\n".join(rows)
        
        files = {'file': ('performance_test.csv', csv_content, 'text/csv')}
        data = {'sample_size': '500'}
        
        import time
        start_time = time.time()
        
        response = client.post('/csv-analyzer/analyze', files=files, data=data)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        assert response.status_code == 200
        assert processing_time < 30  # No debería tomar más de 30 segundos

class TestCSVAnalyzerUI:
    """Tests para la interfaz de usuario del analizador."""
    
    def test_ui_home_page(self):
        """Test página principal de la UI."""
        response = client.get('/csv-analyzer-ui/')
        assert response.status_code == 200
        assert 'text/html' in response.headers['content-type']
    
    def test_ui_modal_page(self):
        """Test página del modal."""
        response = client.get('/csv-analyzer-ui/modal')
        assert response.status_code == 200
        assert 'text/html' in response.headers['content-type']
    
    def test_ui_widget_page(self):
        """Test página del widget."""
        response = client.get('/csv-analyzer-ui/widget')
        assert response.status_code == 200
        assert 'text/html' in response.headers['content-type']

# Fixtures para tests
@pytest.fixture
def sample_csv_file():
    """Fixture para crear archivo CSV de prueba."""
    csv_content = """columna1,columna2,columna3
123,texto,2024-01-01
456,otro texto,2024-02-15"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(csv_content)
        temp_file = f.name
    
    yield temp_file
    
    # Limpiar
    os.unlink(temp_file)

@pytest.fixture
def dian_csv_file():
    """Fixture para crear archivo CSV con estructura DIAN."""
    csv_content = """PLAN_IDENTIF_ACTO,CODIGO_ADMINISTRACION,NIT,FECHA_ACTO
123,456,123456789,2024-01-01
789,012,987654321,2024-02-15"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(csv_content)
        temp_file = f.name
    
    yield temp_file
    
    # Limpiar
    os.unlink(temp_file)

# Tests adicionales
def test_detector_with_real_data():
    """Test con datos reales simulados."""
    detector = DataTypeDetector()
    
    # Simular datos reales de DIAN
    real_data = pd.Series([
        '123456789',
        '987654321',
        '111222333',
        '444555666'
    ])
    
    result = detector.detect_column_type(real_data, 'NIT')
    
    assert result['type'] == 'nit'
    assert result['confidence'] > 0.8

def test_detector_edge_cases():
    """Test casos extremos del detector."""
    detector = DataTypeDetector()
    
    # Caso: mezcla de tipos
    mixed_data = pd.Series(['123', 'texto', '2024-01-01', '456'])
    result = detector.detect_column_type(mixed_data, 'mixed_column')
    
    # Debería detectar el tipo más común o string por defecto
    assert result['type'] in ['string', 'integer']
    
    # Caso: solo valores nulos
    null_data = pd.Series([None, '', 'null', 'nan'])
    result = detector.detect_column_type(null_data, 'null_column')
    
    assert result['type'] == 'string'
    assert result['confidence'] == 0.5

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 