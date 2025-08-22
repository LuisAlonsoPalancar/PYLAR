import os
import paramiko
import configparser

config = configparser.ConfigParser(interpolation=None)
config.read('sftp_credenciales.ini')

host = config['SFTP']['host']
puerto = int(config['SFTP']['port'])
usuario = config['SFTP']['username']
contrasena = config['SFTP']['password']
ruta_remota = config['SFTP']['remote_path']
#https://docs.paramiko.org/en/stable/api/sftp.html

try:
    # Establecer conexión SFTP
    transport = paramiko.Transport((host, puerto))
    transport.connect(username=usuario, password=contrasena)
    sftp = paramiko.SFTPClient.from_transport(transport)
    lista_fotos = []
    '''for i in os.listdir("./PNG/pruebas_fotos"):
        if i.endswith(".png"):
            lista_fotos.append(f"./PNG/pruebas_fotos/{i}")
    # Subir archivos de ambas listas
    i = len(sftp.listdir(ruta_remota))
    for archivo_local in lista_fotos:
        if not os.path.exists(archivo_local):
            print("Archivo no encontrado", f"No existe: {archivo_local}")
            continue
        nombre = os.path.basename(archivo_local)
        ruta_destino = os.path.join(ruta_remota, nombre)
        print("Subiendo archivo:", archivo_local, "a", ruta_destino)
        sftp.put(archivo_local, ruta_destino)
    print(f"Subida completada. {len(lista_fotos)} archivos subidos.")'''
    print (len(sftp.listdir(ruta_remota)), "archivos en el servidor")
    print (sftp.listdir())
    lista_cosas=sftp.listdir('download')
    print(lista_cosas)
    sftp.get(f"download/{lista_cosas[4]}",lista_cosas[4])
    #print(sftp.listdir("/upload/"))
    #print(len(sftp.listdir("/upload/")))
    #print(sftp.listdir("/download/"), len(sftp.listdir("/download/")))
    '''archivo_local = "./PNG/pruebas_fotos/espadas.png"
    print(len(sftp.listdir(ruta_remota)), "archivos en el servidor")

    if not os.path.exists(archivo_local):
        print("Archivo no encontrado", f"No existe: {archivo_local}")
    else:
        print("Subiendo archivo:", archivo_local)
        # Subir archivo
    sftp.put(archivo_local,  f"{ruta_remota}espadas.png")
    archivos_subidos = sftp.listdir(ruta_remota)
    # Comprobar si 'espadas.png' está en la lista de archivos subidos
    print('espadas.png' in archivos_subidos)
    print(len(archivos_subidos), "archivos en el servidor")
    #sftp.get('readme.txt', 'readme.txt')'''
    sftp.close()
    transport.close()

    print("Éxito", "Todos los archivos fueron subidos correctamente")

except Exception as e:
    print("Error",{e})
