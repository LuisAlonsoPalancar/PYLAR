import os
import re

def encontrar_archivo(directorio, nombre, fecha, hora):
    patron = re.compile(rf"\d{{4}}_{re.escape(nombre)}_[A-Z]{{3}}_{fecha}_{hora}_\d{{2}}\.fr2$", re.IGNORECASE)
    ruta_fr2 = None
    ruta_np2 = None
    directorio_frd = f'{directorio}/FRD'
    print(f"Directorio FRD: {directorio_frd}")
    print(f"Nombre: {nombre}, Fecha: {fecha}, Hora: {hora}")
    print(f"Patrón: {patron.pattern}")
    for archivo in os.listdir(directorio_frd):
        
        if patron.match(archivo):
            ruta_fr2 = os.path.join(directorio_frd, archivo)
    if ruta_fr2:
        directorio_npt = f'{directorio}/NPT'

        patron = re.compile(rf"\d{{4}}_{re.escape(nombre)}_[A-Z]{{3}}_{fecha}_{hora}_\d{{2}}\.np2$", re.IGNORECASE)
        for archivo in os.listdir(directorio_npt):
            if patron.match(archivo):
                ruta_np2 = os.path.join(directorio_npt,archivo)
    return ruta_fr2, ruta_np2

# Ejemplo de uso
directorio = "../Sesiones/Sessions_20250520/Session01"
nombre = "ajisai"
fecha = "20250519"
hora = "0727"

try:
    fr2,np2 = encontrar_archivo(directorio, nombre, fecha, hora)
except FileNotFoundError as e:
    print(f"Error: {e}")
    fr2 = None
    np2 = None
print (f"Ruta FR2: {fr2}")
print (f"Ruta NP2: {np2}") 
try:    
    print( os.path.exists(fr2))
except TypeError:
    print("Ruta FR2 no encontrada")


