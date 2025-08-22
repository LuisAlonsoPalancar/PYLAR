import csv
import os
import re
archivo_csv = 'session_info_transposed.csv'

if os.path.exists(archivo_csv):
    with open(archivo_csv, newline='') as archivo:
        lector = csv.reader(archivo)
        for fila in lector:
            # Evitar errores con filas incompletas
            def obtener(col_idx):
                return fila[col_idx] if len(fila) > col_idx and fila[col_idx].strip() != '' else "-"

            col0 = obtener(0)
            col15 = obtener(14)
            col16 = obtener(15)
            col20 = obtener(19)
            col22 = obtener(21)

            # Procesar columna 0 (formato esperado: yyyymmdd_hhmm_nombre_codigo)
            partes = col0.split('_')
            if len(partes) >= 2:
                fecha_hora = partes[0]
                hora = partes[1]  # hhmm (últimos 4 dígitos)
                nombre = partes[2]
            else:
                hora = "-"
                nombre = "-"

            print(f'Hora: {hora[:2]}:{hora[2:]}, Nombre: {nombre}, Col15: {col15}, Col16: {col16}, Col20: {col20}, Col22: {col22}')
else:
    print("El archivo no existe.")
    hora = "-"
    nombre = "-" 
    col15 = "-"
    col16 = "-"
    col20 = "-"
    col22 = "-"
    #Obtengo nombre por lectura de archivo en subcarpeta RAW
    # Aquí podrías agregar lógica para manejar el caso de que el archivo no exista
    

    # Ruta a la subcarpeta
    ruta_subcarpeta = "./RAW"

    # Expresión regular para extraer hora y nombre
    patron = re.compile(r"\d{8}_(\d{4})_(.*?)_\w+\.frd")

    # Recorremos los archivos de la subcarpeta
    for nombre_archivo in os.listdir(ruta_subcarpeta):
        if nombre_archivo.endswith(".frd"):
            coincidencia = patron.match(nombre_archivo)
            if coincidencia:
                hora = coincidencia.group(1)
                nombre = coincidencia.group(2)
        print(f'Hora: {hora[:2]}:{hora[2:]}, Nombre: {nombre}, Col15: {col15}, Col16: {col16}, Col20: {col20}, Col22: {col22}')
