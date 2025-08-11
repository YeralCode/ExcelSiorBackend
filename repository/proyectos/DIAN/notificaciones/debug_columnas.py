"""
Script para debuggear las columnas del archivo y ver el mapeo correcto.
"""

from transformar_columnas_dian_notifiaciones_mejorado import CSVProcessor
import sys

def debug_columnas(archivo_csv):
    """Debuggea las columnas del archivo CSV."""
    
    processor = CSVProcessor()
    
    try:
        # Leer el archivo para obtener las columnas
        header, rows = processor.read_csv(archivo_csv)
        
        print("=== COLUMNAS ENCONTRADAS ===")
        print(f"Total de columnas: {len(header)}")
        print()
        
        for i, columna in enumerate(header, 1):
            print(f"Columna {i}: {columna}")
        
        print()
        print("=== PRIMERAS FILAS DE DATOS ===")
        for i, row in enumerate(rows[:3], 1):
            print(f"Fila {i}: {row}")
        
        print()
        print("=== SUGERENCIA DE TYPE_MAPPING ===")
        print("Basado en los nombres de las columnas, aquí tienes una sugerencia:")
        print()
        
        # Sugerir mapeo basado en nombres de columnas
        sugerencia = {
            "integer": [],
            "float": [],
            "date": [],
            "nit": [],
            "string": []
        }
        
        for i, columna in enumerate(header, 1):
            col_lower = columna.lower()
            
            if any(palabra in col_lower for palabra in ['fecha', 'date']):
                sugerencia["date"].append(i)
            elif any(palabra in col_lower for palabra in ['nit', 'identificacion']):
                sugerencia["nit"].append(i)
            elif any(palabra in col_lower for palabra in ['cantidad', 'valor', 'monto', 'cuantia', 'precio']):
                sugerencia["float"].append(i)
            elif any(palabra in col_lower for palabra in ['codigo', 'id', 'numero', 'consecutivo']):
                sugerencia["integer"].append(i)
            else:
                sugerencia["string"].append(i)
        
        print("type_mapping = {")
        for tipo, columnas in sugerencia.items():
            if columnas:
                print(f'    "{tipo}": {columnas},')
        print("}")
        
    except Exception as e:
        print(f"Error al leer el archivo: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python3 debug_columnas.py <archivo_csv>")
        sys.exit(1)
    
    archivo_csv = sys.argv[1]
    debug_columnas(archivo_csv) 