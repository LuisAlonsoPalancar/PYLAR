import json
from pprint import pprint
import os

carpeta_superior = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
carpetas = [nombre for nombre in os.listdir(carpeta_superior) if os.path.isdir(os.path.join(carpeta_superior, nombre))]
print("Carpetas en la carpeta superior:")
for carpeta in carpetas:
    print(carpeta)
archivo_json = "../Sesiones/Sessions_20250520/Session01/session_info.json.json"    
print(os.path.exists(archivo_json))
with open("../Sesiones/Sessions_20250520/Session01/session_info.json", "r", encoding="utf-8") as f:
    datos = json.load(f)

pprint(datos)
