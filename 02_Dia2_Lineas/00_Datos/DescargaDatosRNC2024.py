# Debido al tamaño del archivo (Pesado), los datos crudos no se incluyen en este repositorio. 
# Para replicar el análisis, por favor descarga el dataset oficial del INEGI.
# (También dejo este script para automatizar la descarga si lo prefieres).

# Fuente: Red Nacional de Caminos (RNC) - INEGI 2024.
# Enlace de descarga directa: [Descargar .zip del INEGI](https://www.inegi.org.mx/contenidos/productos/prod_serv/contenidos/espanol/bvinegi/productos/geografia/caminos/2024/794551132166_s.zip)
# Instrucciones:
#     1.  Descarga el archivo.
#     2.  Descomprímelo.
#     3.  Coloca la carpeta descomprimida dentro de `00_Datos/`.

import os
import requests
import zipfile
import io

# Configuración
# URL oficial de la RNC 2024 (Formato SHP)
URL_INEGI = "https://www.inegi.org.mx/contenidos/productos/prod_serv/contenidos/espanol/bvinegi/productos/geografia/caminos/2024/794551132166_s.zip"
CARPETA_DESTINO = "00_Datos/"

def descargar_rnc():
    print("---------------------------------------------------------")
    print(f"Iniciando descarga de la Red Nacional de Caminos (RNC)")
    print(f"Fuente: {URL_INEGI}")
    print("Esto puede tardar varios minutos (el archivo es grande)...")
    print("---------------------------------------------------------")
    
    try:
        # 1. Hacemos la petición al servidor (Stream para no saturar RAM)
        # stream=True es vital aquí porque la RNC pesa cientos de MB
        response = requests.get(URL_INEGI, stream=True)
        response.raise_for_status() # Lanza error si el link está roto
        
        # 2. Descomprimimos en memoria
        # Nota: Si tu internet es lento o tienes poca RAM, podría convenir guardar el zip primero.
        # Pero para fines del script rápido, mantenemos el flujo en memoria.
        print("Descarga completada. Descomprimiendo archivos...")
        
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            # Crear carpeta si no existe
            if not os.path.exists(CARPETA_DESTINO):
                os.makedirs(CARPETA_DESTINO)
                print(f"📂 Carpeta creada: {CARPETA_DESTINO}")
            
            z.extractall(CARPETA_DESTINO)
            
        print("---------------------------------------------------------")
        print(f"¡Éxito! Datos guardados en: {CARPETA_DESTINO}")
        print("La estructura debería ser: 00_Datos/conjunto_de_datos/red_vial.shp")
        print("Ahora puedes correr el notebook del análisis.")
        print("---------------------------------------------------------")
        
    except Exception as e:
        print(f"Error durante la descarga o descompresión: {e}")
        print("Intenta descargarlo manualmente del link en el encabezado.")

if __name__ == "__main__":
    descargar_rnc()