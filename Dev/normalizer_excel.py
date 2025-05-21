import logging
import pandas as pd
import os
from openpyxl import load_workbook
from dotenv import load_dotenv

def ajustar_ancho_columnas(writer, df, sheet_name):
    """Ajusta el ancho de las columnas en función del contenido."""
    workbook = writer.book
    worksheet = workbook[sheet_name]
    
    for i, col in enumerate(df.columns, 1):  # Enumerar desde 1 para ajustar a las columnas de Excel
        max_length = max(df[col].astype(str).map(len).max(), len(col))  # Longitud máxima del contenido y encabezado
        worksheet.column_dimensions[worksheet.cell(row=1, column=i).column_letter].width = max_length + 2  # Ajustar ancho con un margen

def execute(logging: logging):
    load_dotenv()
    local_file_name = os.getenv('local_file_name')
    sheets_name = ['Servidores Windows', 'Cajas POS', 'Servidores Linux GeoPos', 'Servidores Linux']
    local_path = os.path.join(os.path.dirname(__file__), local_file_name)
    
    for sheet_name in sheets_name:
        logging.info(f"Normalizando la hoja {sheet_name} ...")
        
        # Leer el archivo y la hoja especificada
        df = pd.read_excel(local_path, sheet_name=sheet_name)

        # Eliminar espacios en blanco al inicio y final de todas las columnas de tipo texto
        df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

        # Guardar los cambios en el mismo archivo con ajuste de ancho de columnas
        with pd.ExcelWriter(local_path, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            ajustar_ancho_columnas(writer, df, sheet_name)

        logging.info(f"Valores con espacios en blanco eliminados y ancho de columnas ajustado en la hoja {sheet_name}.")