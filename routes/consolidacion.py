from fastapi import APIRouter, File, UploadFile, Form
from fastapi.responses import FileResponse, JSONResponse
import os
import pandas as pd
import tempfile
from typing import List

router = APIRouter(prefix="/api/v1", tags=["Consolidación de archivos"])


@router.post("/unir-csv")
def unir_csv(files: List[UploadFile] = File(...), 
    separador_salida: str = Form("|"),
    nombre_archivo_salida: str = Form("consolidado.csv")):
    """Une múltiples archivos CSV en uno solo"""
    dataframes = []
    for file in files:
        try:
            # Guardar archivo temporalmente
            with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
                tmp.write(file.file.read())
                tmp_path = tmp.name
            # Intentar leer con UTF-8 primero, si falla usar latin-1
            try:
                df = pd.read_csv(tmp_path, delimiter=separador_salida, dtype=str, encoding='utf-8')
            except UnicodeDecodeError:
                try:
                    df = pd.read_csv(tmp_path, delimiter=separador_salida, dtype=str, encoding='latin-1')
                except UnicodeDecodeError:
                    df = pd.read_csv(tmp_path, delimiter=separador_salida, dtype=str, encoding='cp1252')
            dataframes.append(df)
            os.unlink(tmp_path)
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"error": f"Error al leer {file.filename}: {str(e)}"},
            )

    if not dataframes:
        return JSONResponse(
            status_code=400, content={"error": "No se cargó ningún archivo válido."}
        )
    else:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as out_tmp:
            combined_df = pd.concat(dataframes, ignore_index=True)
            combined_df.to_csv(out_tmp.name, sep=separador_salida, index=False)
            out_path = out_tmp.name
        return FileResponse(
            out_path,
            filename=nombre_archivo_salida,
            media_type="text/csv",
        ) 