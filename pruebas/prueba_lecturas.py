import csv

with open('session_info_transposed.csv', newline='') as archivo:
    lector = csv.reader(archivo)
    for fila in lector:
        # Saltar filas vacías o incompletas
        if len(fila) < 23:
            continue

        # Extraer columnas necesarias (0, 14, 15, 19, 21)
        col0 = fila[0] # Nombre de la columna con fecha y hora
        col15 = fila[14] # Número de puntos normales (NPs)
        col16 = fila[15] # Observaciones por NP
        col20 = fila[19] # RMS
        col22 = fila[21] #Standar deviation

        # Procesar columna 0
        partes = col0.split('_')
        if len(partes) >= 3:
            fecha_hora = partes[0]
            hora = partes[1]  # hhmm (últimos 4 dígitos)
            nombre = partes[2]
        else:
            hora = None
            nombre = None

        print(f'Hora: {hora}, Nombre: {nombre}, NPs: {col15}, obs/NP: {col16}, RMS: {col20}, NP_mm: {col22}')
