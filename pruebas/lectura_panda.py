import pandas as pd
import os

archivo_csv = 'session_info_transposed.csv'

if os.path.exists(archivo_csv):
    try:
        df = pd.read_csv(archivo_csv)

        # Columnas que queremos (0, 14, 15, 19, 21)
        columnas = [0, 14, 15, 19, 21]

        # Manejar caso en que no existan esas columnas
        max_col = df.shape[1]
        columnas_validas = [i for i in columnas if i < max_col]
        df = df.iloc[:, columnas_validas]

        # Rellenar NaNs con '-'
        df.fillna('-', inplace=True)

        # Procesar columna 0 (si existe)
        if 0 in columnas:
            def extraer_datos(cadena):
                try:
                    partes = cadena.split('_')
                    fecha_hora = partes[0] if len(partes) > 0 else "-"
                    hora = fecha_hora[8:] if len(fecha_hora) >= 12 else "-"
                    nombre = partes[1] if len(partes) > 1 else "-"
                    return pd.Series([hora, nombre])
                except:
                    return pd.Series(["-", "-"])

            df[['hora', 'nombre']] = df.iloc[:, 0].apply(lambda x: extraer_datos(str(x)))
        else:
            df['hora'] = '-'
            df['nombre'] = '-'

        print(df)

    except Exception as e:
        print("Error al leer el archivo:", e)
else:
    print("El archivo no existe.")
