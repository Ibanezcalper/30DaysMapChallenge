#Debido al tamaño del archivo (255MB+), los datos crudos no se incluyen en este repositorio. 
#Para replicar el análisis, por favor descarga el dataset oficial del INEGI: (Tambien dejo una script para automatizar la descarga si lo prefieres)

#Fuente: Directorio Estadístico Nacional de Unidades Económicas (DENUE) - CDMX 2025.
#Enlace de descarga directa:[Descargar .zip del INEGI](https://www.inegi.org.mx/contenidos/masiva/denue/denue_09_csv.zip)
#Instrucciones:
#    1.  Descarga el archivo.
#    2.  Descomprímelo.
 #   3.  Coloca el archivo `.csv` dentro de la carpeta `00_Datos/`.


import os
import requests
import zipfile
import io

# Configuración
URL_INEGI = "https://www.inegi.org.mx/contenidos/masiva/denue/denue_09_csv.zip"
CARPETA_DESTINO = "00_Datos/"

def descargar_denue():
    print(f"Iniciando descarga desde INEGI: {URL_INEGI}")
    print("Esto puede tardar unos minutos dependiendo de tu conexión...")
    
    try:
        # 1. Hacemos la petición al servidor (Stream para no saturar RAM)
        response = requests.get(URL_INEGI)
        response.raise_for_status() # Lanza error si el link está roto
        
        # 2. Descomprimimos en memoria sin guardar el zip
        print("Descarga completada. Descomprimiendo...")
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            # Crear carpeta si no existe
            if not os.path.exists(CARPETA_DESTINO):
                os.makedirs(CARPETA_DESTINO)
            
            z.extractall(CARPETA_DESTINO)
            
        print(f"Datos guardados en: {CARPETA_DESTINO}")
        print(" Ahora puedes correr el notebook del análisis.")
        
    except Exception as e:
        print(f"Error durante la descarga: {e}")

if __name__ == "__main__":
    descargar_denue()
