"""
Ejemplo de uso de la nueva estructura reorganizada del repository.

Este archivo muestra cómo usar los nuevos procesadores y transformadores
siguiendo las mejores prácticas implementadas.
"""

from pathlib import Path
from typing import List

# Importar los nuevos procesadores y transformadores
from repository.processors.csv_processor import CSVProcessor
from repository.processors.excel_processor import ExcelProcessor
from repository.processors.consolidation_processor import ConsolidationProcessor
from repository.transformers.format_transformer import FormatTransformer
from repository.transformers.encoding_transformer import EncodingTransformer

# Importar utilidades
from utils.logger import get_logger
from utils.exceptions import handle_exception

# Configurar logging
logger = get_logger(__name__)

@handle_exception
def ejemplo_procesamiento_csv():
    """Ejemplo de procesamiento de archivos CSV."""
    logger.info("Iniciando ejemplo de procesamiento CSV")
    
    # Crear instancia del procesador
    csv_processor = CSVProcessor()
    
    # Archivo de ejemplo
    input_file = Path("ejemplo.csv")
    output_file = Path("procesado.csv")
    
    try:
        # Leer archivo CSV
        headers, data = csv_processor.read_csv_file(input_file)
        logger.info(f"Archivo leído: {len(headers)} columnas, {len(data)} filas")
        
        # Limpiar datos
        cleaned_data = csv_processor.clean_data(data)
        logger.info("Datos limpiados")
        
        # Extraer información de fecha del nombre del archivo
        date_info = csv_processor.extract_date_from_filename(input_file.name)
        logger.info(f"Fecha extraída: {date_info['mes_reporte']}")
        
        # Agregar metadatos
        new_headers, new_data = csv_processor.add_metadata_columns(
            headers, cleaned_data, input_file.name, date_info
        )
        
        # Escribir archivo procesado
        csv_processor.write_csv_file(output_file, new_headers, new_data)
        logger.info(f"Archivo procesado guardado: {output_file}")
        
        # Obtener estadísticas
        stats = csv_processor.get_csv_statistics(new_headers, new_data)
        logger.info(f"Estadísticas: {stats}")
        
        return {
            "success": True,
            "input_file": str(input_file),
            "output_file": str(output_file),
            "stats": stats
        }
        
    except Exception as e:
        logger.error(f"Error en procesamiento CSV: {str(e)}")
        raise

@handle_exception
def ejemplo_procesamiento_excel():
    """Ejemplo de procesamiento de archivos Excel."""
    logger.info("Iniciando ejemplo de procesamiento Excel")
    
    # Crear instancia del procesador
    excel_processor = ExcelProcessor()
    
    # Archivo de ejemplo
    input_file = Path("datos.xlsx")
    output_file = Path("procesado.xlsx")
    
    try:
        # Leer archivo Excel
        headers, data = excel_processor.read_excel_file(input_file)
        logger.info(f"Archivo Excel leído: {len(headers)} columnas, {len(data)} filas")
        
        # Dividir en hojas si es necesario
        sheets = excel_processor.split_large_dataframe(headers, data, "datos")
        logger.info(f"Dividido en {len(sheets)} hojas")
        
        # Escribir archivo Excel
        excel_processor.write_excel_file(output_file, sheets)
        logger.info(f"Archivo Excel guardado: {output_file}")
        
        # Obtener información del archivo
        info = excel_processor.get_excel_info(output_file)
        logger.info(f"Información del archivo: {info}")
        
        return {
            "success": True,
            "input_file": str(input_file),
            "output_file": str(output_file),
            "sheets": len(sheets),
            "info": info
        }
        
    except Exception as e:
        logger.error(f"Error en procesamiento Excel: {str(e)}")
        raise

@handle_exception
def ejemplo_consolidacion():
    """Ejemplo de consolidación de archivos."""
    logger.info("Iniciando ejemplo de consolidación")
    
    # Crear instancia del procesador
    consolidation_processor = ConsolidationProcessor()
    
    # Lista de archivos CSV a consolidar
    csv_files = [
        Path("archivo1.csv"),
        Path("archivo2.csv"),
        Path("archivo3.csv")
    ]
    
    output_file = Path("consolidado.csv")
    
    try:
        # Validar archivos antes de consolidar
        validation = consolidation_processor.validate_consolidation(csv_files)
        logger.info(f"Validación: {validation['valid_files']} archivos válidos")
        
        # Consolidar archivos CSV
        result = consolidation_processor.consolidate_csv_files(
            csv_files, output_file, add_metadata=True
        )
        logger.info(f"Consolidación completada: {result['processed_files']} archivos")
        
        # Obtener resumen
        summary = consolidation_processor.get_consolidation_summary(csv_files)
        logger.info(f"Resumen: {summary}")
        
        return {
            "success": True,
            "result": result,
            "summary": summary
        }
        
    except Exception as e:
        logger.error(f"Error en consolidación: {str(e)}")
        raise

@handle_exception
def ejemplo_conversion_formato():
    """Ejemplo de conversión de formatos."""
    logger.info("Iniciando ejemplo de conversión de formato")
    
    # Crear instancia del transformador
    format_transformer = FormatTransformer()
    
    # Archivos de ejemplo
    input_file = Path("datos.csv")
    output_file = Path("convertido.csv")
    
    try:
        # Cambiar delimitador de CSV
        result = format_transformer.csv_to_csv_with_delimiter_change(
            input_file=input_file,
            output_file=output_file,
            old_delimiter='|@',
            new_delimiter='|',
            add_metadata=True
        )
        logger.info(f"Conversión completada: {result['rows_processed']} filas")
        
        # Convertir Excel a CSV
        excel_file = Path("datos.xlsx")
        csv_output = Path("excel_a_csv.csv")
        
        excel_result = format_transformer.xlsx_to_csv(
            input_file=excel_file,
            output_file=csv_output,
            add_month_column=True
        )
        logger.info(f"Excel a CSV completado: {excel_result['rows_processed']} filas")
        
        return {
            "success": True,
            "csv_conversion": result,
            "excel_conversion": excel_result
        }
        
    except Exception as e:
        logger.error(f"Error en conversión de formato: {str(e)}")
        raise

@handle_exception
def ejemplo_conversion_codificacion():
    """Ejemplo de conversión de codificación."""
    logger.info("Iniciando ejemplo de conversión de codificación")
    
    # Crear instancia del transformador
    encoding_transformer = EncodingTransformer()
    
    # Archivo de ejemplo
    input_file = Path("archivo_latin1.txt")
    output_file = Path("archivo_utf8.txt")
    
    try:
        # Detectar codificación
        encoding_info = encoding_transformer.detect_encoding(input_file)
        logger.info(f"Codificación detectada: {encoding_info['encoding']} (confianza: {encoding_info['confidence']:.2f})")
        
        # Convertir codificación
        result = encoding_transformer.convert_encoding(
            input_file=input_file,
            output_file=output_file,
            target_encoding='utf-8'
        )
        logger.info(f"Conversión completada: {result['source_encoding']} -> {result['target_encoding']}")
        
        # Arreglar problemas de codificación automáticamente
        problematic_file = Path("archivo_problematico.txt")
        fixed_result = encoding_transformer.fix_encoding_issues(problematic_file)
        logger.info(f"Problemas de codificación arreglados: {fixed_result['fixed_encoding']}")
        
        return {
            "success": True,
            "encoding_detection": encoding_info,
            "conversion": result,
            "fix": fixed_result
        }
        
    except Exception as e:
        logger.error(f"Error en conversión de codificación: {str(e)}")
        raise

@handle_exception
def ejemplo_procesamiento_lote():
    """Ejemplo de procesamiento en lote."""
    logger.info("Iniciando ejemplo de procesamiento en lote")
    
    # Crear instancias
    csv_processor = CSVProcessor()
    format_transformer = FormatTransformer()
    encoding_transformer = EncodingTransformer()
    
    # Lista de archivos a procesar
    input_files = [
        Path("archivo1.csv"),
        Path("archivo2.xlsx"),
        Path("archivo3.txt")
    ]
    
    output_dir = Path("procesados")
    output_dir.mkdir(exist_ok=True)
    
    try:
        results = []
        
        for input_file in input_files:
            logger.info(f"Procesando: {input_file}")
            
            # Detectar y convertir codificación si es necesario
            encoding_info = encoding_transformer.detect_encoding(input_file)
            if encoding_info['encoding'].lower() != 'utf-8':
                temp_file = output_dir / f"temp_{input_file.name}"
                encoding_transformer.convert_encoding(input_file, temp_file, 'utf-8')
                input_file = temp_file
            
            # Procesar según el tipo de archivo
            if input_file.suffix.lower() == '.csv':
                # Procesar CSV
                headers, data = csv_processor.read_csv_file(input_file)
                cleaned_data = csv_processor.clean_data(data)
                
                output_file = output_dir / f"procesado_{input_file.name}"
                csv_processor.write_csv_file(output_file, headers, cleaned_data)
                
                results.append({
                    "file": str(input_file),
                    "type": "csv",
                    "rows": len(cleaned_data),
                    "columns": len(headers)
                })
                
            elif input_file.suffix.lower() in ['.xlsx', '.xls']:
                # Procesar Excel
                headers, data = ExcelProcessor().read_excel_file(input_file)
                
                output_file = output_dir / f"procesado_{input_file.stem}.csv"
                format_transformer.xlsx_to_csv(input_file, output_file)
                
                results.append({
                    "file": str(input_file),
                    "type": "excel",
                    "rows": len(data),
                    "columns": len(headers)
                })
        
        logger.info(f"Procesamiento en lote completado: {len(results)} archivos")
        return {
            "success": True,
            "processed_files": len(results),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Error en procesamiento en lote: {str(e)}")
        raise

def main():
    """Función principal que ejecuta todos los ejemplos."""
    logger.info("Iniciando ejemplos de uso de la nueva estructura")
    
    examples = [
        ("Procesamiento CSV", ejemplo_procesamiento_csv),
        ("Procesamiento Excel", ejemplo_procesamiento_excel),
        ("Consolidación", ejemplo_consolidacion),
        ("Conversión de Formato", ejemplo_conversion_formato),
        ("Conversión de Codificación", ejemplo_conversion_codificacion),
        ("Procesamiento en Lote", ejemplo_procesamiento_lote)
    ]
    
    results = {}
    
    for name, example_func in examples:
        try:
            logger.info(f"Ejecutando ejemplo: {name}")
            result = example_func()
            results[name] = result
            logger.info(f"✓ Ejemplo {name} completado exitosamente")
        except Exception as e:
            logger.error(f"✗ Error en ejemplo {name}: {str(e)}")
            results[name] = {"error": str(e)}
    
    # Resumen final
    successful = sum(1 for r in results.values() if "error" not in r)
    total = len(results)
    
    logger.info(f"Resumen: {successful}/{total} ejemplos completados exitosamente")
    
    return results

if __name__ == "__main__":
    main() 