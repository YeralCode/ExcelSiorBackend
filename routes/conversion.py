from fastapi import APIRouter, File, UploadFile, Body, Form
from fastapi.responses import FileResponse, JSONResponse
import os
import pandas as pd
import tempfile
import zipfile
import csv
import shutil
import re

router = APIRouter(prefix="/api/v1", tags=["Conversión de archivos"])


@router.post("/csv-a-otro-separador/")
def csv_a_otro_separador(body: dict = Body(...)):
    """Convierte archivos CSV de un separador a otro"""
    import io

    lista_archivos_csv_at = body.get("lista_archivos_csv_at", [])
    antiguo_separador = body.get("antiguo_separador", "|@")
    nuevo_separador = body.get("nuevo_separador", "|")

    archivos_convertidos = []
    temp_dir = tempfile.mkdtemp()
    for nombre_archivo_csv_at in lista_archivos_csv_at:
        if not os.path.exists(nombre_archivo_csv_at):
            continue
        try:
            nombre_archivo_base, _ = os.path.splitext(
                os.path.basename(nombre_archivo_csv_at)
            )
            nombre_archivo_csv_pipe = nombre_archivo_base + ".csv"
            archivo_salida = os.path.join(temp_dir, nombre_archivo_csv_pipe)
            with open(
                nombre_archivo_csv_at, "r", newline="", encoding="utf-8"
            ) as infile, open(
                archivo_salida, "w", newline="", encoding="utf-8"
            ) as outfile:
                coincidencia_fecha = re.search(r"I(\d{8})", nombre_archivo_csv_at)
                mes_reporte = "Desconocido"
                if coincidencia_fecha:
                    fecha_str = coincidencia_fecha.group(1)
                    anio = fecha_str[:4]
                    mes = fecha_str[4:6]
                    mes_reporte = f"{mes}_{anio}"
                primera_linea = infile.readline().strip()
                cabecera = primera_linea.split(antiguo_separador)
                nueva_cabecera = ["nombre_archivo", "mes_reporte"] + cabecera
                outfile.write(nuevo_separador.join(nueva_cabecera) + "\n")
                for line in infile:
                    campos = line.strip().split(antiguo_separador)
                    nueva_linea = [
                        os.path.basename(nombre_archivo_csv_at),
                        mes_reporte,
                    ] + campos
                    outfile.write(nuevo_separador.join(nueva_linea) + "\n")
            archivos_convertidos.append(archivo_salida)
        except UnicodeDecodeError:
            try:
                with open(
                    nombre_archivo_csv_at, "r", newline="", encoding="latin-1"
                ) as infile_latin, open(
                    archivo_salida, "w", newline="", encoding="utf-8"
                ) as outfile:
                    coincidencia_fecha = re.search(r"I(\d{8})", nombre_archivo_csv_at)
                    mes_reporte = "Desconocido"
                    if coincidencia_fecha:
                        fecha_str = coincidencia_fecha.group(1)
                        anio = fecha_str[:4]
                        mes = fecha_str[4:6]
                        mes_reporte = f"{mes}_{anio}"
                    primera_linea = infile_latin.readline().strip()
                    cabecera = primera_linea.split(antiguo_separador)
                    nueva_cabecera = ["nombre_archivo", "mes_reporte"] + cabecera
                    outfile.write(nuevo_separador.join(nueva_cabecera) + "\n")
                    for line in infile_latin:
                        campos = line.strip().split(antiguo_separador)
                        nueva_linea = [
                            os.path.basename(nombre_archivo_csv_at),
                            mes_reporte,
                        ] + campos
                        outfile.write(nuevo_separador.join(nueva_linea) + "\n")
                archivos_convertidos.append(archivo_salida)
            except Exception as e_latin:
                continue
        except Exception as e:
            continue
    if not archivos_convertidos:
        return JSONResponse(
            status_code=400, content={"error": "No se pudo convertir ningún archivo."}
        )
    # Crear ZIP
    zip_path = os.path.join(temp_dir, "csv_convertidos.zip")
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for file in archivos_convertidos:
            zipf.write(file, os.path.basename(file))
    return FileResponse(
        zip_path, filename="csv_convertidos.zip", media_type="application/zip"
    )


@router.post("/csv-a-otro-separador-upload-simple/")
def csv_a_otro_separador_upload_simple(
    files: list[UploadFile] = File(...),
    antiguo_separador: str = Form("|@"),
    nuevo_separador: str = Form("|"),
):
    """Convierte archivos CSV subidos de un separador a otro (sin columnas adicionales)"""
    temp_dir = tempfile.mkdtemp()
    archivos_convertidos = []
    
    for file in files:
        try:
            # Leer el contenido del archivo directamente desde el UploadFile
            contenido = file.file.read()
            
            # Crear archivo temporal de entrada
            temp_input_path = os.path.join(temp_dir, file.filename)
            with open(temp_input_path, "wb") as f:
                f.write(contenido)
            
            # Crear nombre del archivo de salida
            nombre_archivo_base, _ = os.path.splitext(os.path.basename(file.filename))
            nombre_archivo_csv = nombre_archivo_base + ".csv"
            archivo_salida = os.path.join(temp_dir, nombre_archivo_csv)
            
            # Procesar el archivo con manejo de codificación
            try:
                # Intentar con UTF-8 primero
                with open(temp_input_path, "r", newline="", encoding="utf-8") as infile:
                    contenido_archivo = infile.read()
            except UnicodeDecodeError:
                try:
                    # Intentar con latin-1
                    with open(temp_input_path, "r", newline="", encoding="latin-1") as infile:
                        contenido_archivo = infile.read()
                except UnicodeDecodeError:
                    # Intentar con cp1252
                    with open(temp_input_path, "r", newline="", encoding="cp1252") as infile:
                        contenido_archivo = infile.read()
            
            # Procesar línea por línea
            with open(archivo_salida, "w", newline="", encoding="utf-8") as outfile:
                lineas = contenido_archivo.split('\n')
                for linea in lineas:
                    if linea.strip():  # Solo procesar líneas no vacías
                        campos = linea.strip().split(antiguo_separador)
                        nueva_linea = nuevo_separador.join(campos)
                        outfile.write(nueva_linea + "\n")
            
            archivos_convertidos.append(archivo_salida)
            
        except Exception as e:
            print(f"Error procesando {file.filename}: {str(e)}")
            continue
    
    if not archivos_convertidos:
        return JSONResponse(
            status_code=400, 
            content={"error": "No se pudo convertir ningún archivo. Verifique que los archivos no estén vacíos y tengan el formato correcto."}
        )
    
    # Crear ZIP
    zip_path = os.path.join(temp_dir, "csv_convertidos.zip")
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for archivo in archivos_convertidos:
            zipf.write(archivo, os.path.basename(archivo))
    
    return FileResponse(
        zip_path, 
        filename="csv_convertidos.zip", 
        media_type="application/zip"
    )


@router.post("/csv-a-otro-separador-upload/")
def csv_a_otro_separador_upload(
    files: list[UploadFile] = File(...),
    antiguo_separador: str = Form("|@"),
    nuevo_separador: str = Form("|"),
):
    """Convierte archivos CSV subidos de un separador a otro"""
    temp_dir = tempfile.mkdtemp()
    archivos_convertidos = []
    
    for file in files:
        try:
            # Leer el contenido del archivo directamente desde el UploadFile
            contenido = file.file.read()
            
            # Crear archivo temporal de entrada
            temp_input_path = os.path.join(temp_dir, file.filename)
            with open(temp_input_path, "wb") as f:
                f.write(contenido)
            
            # Crear nombre del archivo de salida
            nombre_archivo_base, _ = os.path.splitext(os.path.basename(file.filename))
            nombre_archivo_csv = nombre_archivo_base + ".csv"
            archivo_salida = os.path.join(temp_dir, nombre_archivo_csv)
            
            # Procesar el archivo con manejo de codificación
            try:
                # Intentar con UTF-8 primero
                with open(temp_input_path, "r", newline="", encoding="utf-8") as infile:
                    contenido_archivo = infile.read()
            except UnicodeDecodeError:
                try:
                    # Intentar con latin-1
                    with open(temp_input_path, "r", newline="", encoding="latin-1") as infile:
                        contenido_archivo = infile.read()
                except UnicodeDecodeError:
                    # Intentar con cp1252
                    with open(temp_input_path, "r", newline="", encoding="cp1252") as infile:
                        contenido_archivo = infile.read()
            
            # Extraer información del nombre del archivo
            coincidencia_fecha = re.search(r"I(\d{8})", file.filename)
            mes_reporte = "Desconocido"
            if coincidencia_fecha:
                fecha_str = coincidencia_fecha.group(1)
                anio = fecha_str[:4]
                mes = fecha_str[4:6]
                mes_reporte = f"{mes}_{anio}"
            
            # Procesar línea por línea
            with open(archivo_salida, "w", newline="", encoding="utf-8") as outfile:
                lineas = contenido_archivo.split('\n')
                primera_linea = True
                
                for linea in lineas:
                    if linea.strip():  # Solo procesar líneas no vacías
                        if primera_linea:
                            # Procesar cabecera
                            cabecera = linea.strip().split(antiguo_separador)
                            nueva_cabecera = ["NOMBRE_ARCHIVO", "MES_REPORTE"] + cabecera
                            outfile.write(nuevo_separador.join(nueva_cabecera) + "\n")
                            primera_linea = False
                        else:
                            # Procesar datos
                            campos = linea.strip().split(antiguo_separador)
                            nueva_linea = [file.filename, mes_reporte] + campos
                            outfile.write(nuevo_separador.join(nueva_linea) + "\n")
            
            archivos_convertidos.append(archivo_salida)
            
        except Exception as e:
            print(f"Error procesando {file.filename}: {str(e)}")
            continue
    
    if not archivos_convertidos:
        return JSONResponse(
            status_code=400, 
            content={"error": "No se pudo convertir ningún archivo. Verifique que los archivos no estén vacíos y tengan el formato correcto."}
        )
    
    # Crear ZIP
    zip_path = os.path.join(temp_dir, "csv_otro_separador.zip")
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for archivo in archivos_convertidos:
            zipf.write(archivo, os.path.basename(archivo))
    
    return FileResponse(
        zip_path, 
        filename="csv_otro_separador.zip", 
        media_type="application/zip"
    )


@router.post("/sav-a-csv-upload/")
def sav_a_csv_upload(files: list[UploadFile] = File(...)):
    """Convierte archivos .sav a CSV"""
    temp_dir = tempfile.mkdtemp()
    archivos_convertidos = []
    for file in files:
        # Guardar archivo temporalmente
        temp_input_path = os.path.join(temp_dir, file.filename)
        with open(temp_input_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        try:
            nombre_archivo_base, _ = os.path.splitext(os.path.basename(file.filename))
            nombre_archivo_csv = nombre_archivo_base + ".csv"
            archivo_salida = os.path.join(temp_dir, nombre_archivo_csv)
            df = pd.read_spss(temp_input_path)
            df.to_csv(archivo_salida, index=False, sep="|")
            archivos_convertidos.append(archivo_salida)
        except Exception as e:
            continue
    if not archivos_convertidos:
        return JSONResponse(
            status_code=400,
            content={"error": "No se pudo convertir ningún archivo .sav."},
        )
    # Crear ZIP
    zip_path = os.path.join(temp_dir, "csv_convertidos.zip")
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for file in archivos_convertidos:
            zipf.write(file, os.path.basename(file))
    return FileResponse(
        zip_path, filename="csv_convertidos.zip", media_type="application/zip"
    )


@router.post("/txt-a-csv-upload/")
def txt_a_csv_upload(
    files: list[UploadFile] = File(...),
):
    """Convierte archivos .txt a CSV (solo cambia la extensión)"""
    temp_dir = tempfile.mkdtemp()
    archivos_convertidos = []
    for file in files:
        # Guardar archivo temporalmente
        temp_input_path = os.path.join(temp_dir, file.filename)
        with open(temp_input_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        try:
            # Limpiar el nombre del archivo de extensiones extrañas
            nombre_archivo = os.path.basename(file.filename)
            
            # Remover todas las extensiones .txt, .TXT, .txt.txt, etc.
            nombre_limpio = nombre_archivo
            while True:
                nombre_anterior = nombre_limpio
                # Remover extensiones .txt y .TXT (case insensitive)
                nombre_limpio = re.sub(r'\.(txt|TXT)(\.txt|\.TXT)*$', '', nombre_limpio)
                # Remover puntos dobles al final
                nombre_limpio = re.sub(r'\.+$', '', nombre_limpio)
                # Si no cambió nada, salir del bucle
                if nombre_limpio == nombre_anterior:
                    break
            
            # Agregar extensión .csv
            nombre_archivo_csv = nombre_limpio + ".csv"
            archivo_salida = os.path.join(temp_dir, nombre_archivo_csv)
            
            # Copiar el archivo sin modificar, solo cambiar nombre
            shutil.copy2(temp_input_path, archivo_salida)
            archivos_convertidos.append(archivo_salida)
        except Exception as e:
            continue
    if not archivos_convertidos:
        return JSONResponse(
            status_code=400,
            content={"error": "No se pudo convertir ningún archivo .txt."},
        )
    # Crear ZIP
    zip_path = os.path.join(temp_dir, "csv_convertidos.zip")
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for file in archivos_convertidos:
            zipf.write(file, os.path.basename(file))
    return FileResponse(
        zip_path, filename="csv_convertidos.zip", media_type="application/zip"
    )


@router.post("/xlsx-a-csv-con-columna-mes-de-reporte-upload/")
def xlsx_a_csv_upload(
    files: list[UploadFile] = File(...), separador_salida: str = Form("|")
):
    """Convierte archivos .xlsx a CSV con columna de mes de reporte"""
    temp_dir = tempfile.mkdtemp()
    archivos_convertidos = []
    MESES = {
        "Enero": "01",
        "Febrero": "02",
        "Marzo": "03",
        "Abril": "04",
        "Mayo": "05",
        "Junio": "06",
        "Julio": "07",
        "Agosto": "08",
        "Septiembre": "09",
        "Octubre": "10",
        "Noviembre": "11",
        "Diciembre": "12",
    }
    MESES_LOWER = {
        "enero": "1",
        "febrero": "2",
        "marzo": "3",
        "abril": "4",
        "mayo": "5",
        "junio": "6",
        "julio": "7",
        "agosto": "8",
        "septiembre": "9",
        "octubre": "10",
        "noviembre": "11",
        "diciembre": "12",
    }
    for file in files:
        temp_input_path = os.path.join(temp_dir, file.filename)
        with open(temp_input_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        try:
            nombre_archivo_base, _ = os.path.splitext(os.path.basename(file.filename))
            nombre_archivo_csv = (
                nombre_archivo_base.replace(" ", "_")
                .replace("de_", "")
                .replace("de", "")
                .replace(".", "_")
                + ".csv"
            )
            archivo_salida = os.path.join(temp_dir, nombre_archivo_csv)
            coincidencia = re.search(r"Mes_([A-Za-z]+)_(\d{4})", nombre_archivo_csv)
            coincidencia_2 = re.search(
                r"Mes_de_([A-Za-z]+)_de_(\d{4})", nombre_archivo_csv
            )
            coincidencia_fecha = re.search(r"I(\d{8})", nombre_archivo_csv)
            coincidencia_pqr = re.search(r"(\d{4})-(\d{2})", nombre_archivo_csv)
            coincidencia_dynamics = re.search(r"_(\w+)_(\d{4})_", nombre_archivo_csv)
            mes_reporte = "Desconocido"
            if coincidencia:
                mes_nombre = coincidencia.group(1).capitalize()
                anio = coincidencia.group(2)
                mes_numero = MESES.get(mes_nombre)
                if mes_numero:
                    mes_reporte = f"{mes_numero}_{anio}"
            elif coincidencia_2:
                mes_nombre = coincidencia_2.group(1).capitalize()
                anio = coincidencia_2.group(2)
                mes_numero = MESES.get(mes_nombre)
                if mes_numero:
                    mes_reporte = f"{mes_numero}_{anio}"
            if coincidencia_fecha:
                fecha_str = coincidencia_fecha.group(1)
                anio = fecha_str[:4]
                mes = fecha_str[4:6]
                mes_reporte = f"{mes}_{anio}"
            if coincidencia_dynamics:
                mes_nombre = coincidencia_dynamics.group(1).lower()
                anio = coincidencia_dynamics.group(2)
                mes_numero = MESES_LOWER.get(mes_nombre)
                if mes_numero:
                    mes_reporte = f"{mes_numero}_{anio}"
            if coincidencia_pqr:
                anio = coincidencia_pqr.group(1)
                mes_numero = coincidencia_pqr.group(2)
                mes_numero_sin_cero = str(int(mes_numero))
                mes_reporte = f"{mes_numero_sin_cero}_{anio}"
            df = pd.read_excel(temp_input_path)
            if not df.empty and len(df) > 0:
                df = df.iloc[1:]
            df.insert(0, "nombre_archivo", nombre_archivo_base)
            df.insert(1, "mes_reporte", mes_reporte)
            df.to_csv(
                archivo_salida, index=False, sep=separador_salida, encoding="utf-8"
            )
            archivos_convertidos.append(archivo_salida)
        except Exception as e:
            continue
    if not archivos_convertidos:
        return JSONResponse(
            status_code=400,
            content={"error": "No se pudo convertir ningún archivo .xlsx."},
        )
    # Crear ZIP
    zip_path = os.path.join(temp_dir, "csv_convertidos.zip")
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for file in archivos_convertidos:
            zipf.write(file, os.path.basename(file))
    return FileResponse(
        zip_path, filename="csv_convertidos.zip", media_type="application/zip"
    )


@router.post("/xlsx-a-csv-upload/")
def xlsx_a_csv_con_columna_mes_de_reporte_upload(
    files: list[UploadFile] = File(...), separador_salida: str = Form("|")
):
    """Convierte archivos .xlsx a CSV simple"""
    temp_dir = tempfile.mkdtemp()
    archivos_convertidos = []
    for file in files:
        temp_input_path = os.path.join(temp_dir, file.filename)
        with open(temp_input_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        try:
            nombre_archivo_base, _ = os.path.splitext(os.path.basename(file.filename))
            nombre_archivo_csv = (
                nombre_archivo_base.replace(" ", "_")
                .replace("de_", "")
                .replace("de", "")
                .replace(".", "_")
                + ".csv"
            )
            archivo_salida = os.path.join(temp_dir, nombre_archivo_csv)
            df = pd.read_excel(temp_input_path)
            df.to_csv(
                archivo_salida, index=False, sep=separador_salida, encoding="utf-8"
            )
            archivos_convertidos.append(archivo_salida)
        except Exception as e:
            continue
    if not archivos_convertidos:
        return JSONResponse(
            status_code=400,
            content={"error": "No se pudo convertir ningún archivo .xlsx."},
        )
    # Crear ZIP
    zip_path = os.path.join(temp_dir, "csv_convertidos.zip")
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for file in archivos_convertidos:
            zipf.write(file, os.path.basename(file))
    return FileResponse(
        zip_path, filename="csv_convertidos.zip", media_type="application/zip"
    )


@router.post("/unir-archivos-csv-en-xlsx-upload/")
def unir_archivos_csv_en_xlsx_upload(
    files: list[UploadFile] = File(...), separador_salida: str = Form("|")
):
    """Une archivos CSV en un archivo Excel"""
    temp_dir = tempfile.mkdtemp()
    rutas_csv = []
    for file in files:
        temp_input_path = os.path.join(temp_dir, file.filename)
        with open(temp_input_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        rutas_csv.append(temp_input_path)
    archivo_excel_salida = os.path.join(temp_dir, "Consolidado_Final.xlsx")
    try:
        max_filas = 1048576  # Límite de filas en Excel
        excel_data = {}
        for ruta in rutas_csv:
            try:
                nombre_base = os.path.basename(ruta).replace(".csv", "")[:25]
                data = []
                with open(ruta, "r", encoding="utf-8") as archivo_csv:
                    lector_csv = csv.reader(archivo_csv, delimiter=separador_salida)
                    for fila in lector_csv:
                        data.append(fila)
                df = pd.DataFrame(data)
                num_partes = (len(df) // max_filas) + 1
                for i in range(num_partes):
                    inicio = i * max_filas
                    fin = (i + 1) * max_filas
                    nombre_hoja = f"{nombre_base}_part{i+1}"[:31]
                    excel_data[nombre_hoja] = df.iloc[inicio:fin]
            except Exception as e:
                continue
        with pd.ExcelWriter(archivo_excel_salida) as writer:
            for sheet_name, df in excel_data.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False, header=False)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Error general: {e}"})
    # Crear ZIP
    zip_path = os.path.join(temp_dir, "consolidado_xlsx.zip")
    with zipfile.ZipFile(zip_path, "w") as zipf:
        zipf.write(archivo_excel_salida, os.path.basename(archivo_excel_salida))
    return FileResponse(
        zip_path, filename="consolidado_xlsx.zip", media_type="application/zip"
    ) 