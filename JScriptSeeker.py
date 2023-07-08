import urllib.request
import jsbeautifier
import ssl
import find_secrets as fs
import find_urls as fu
import find_vulns as fv
import json
import argparse
import sys
import time
import threading
import signal
import os
from urllib.parse import urlparse

## Spinner sin bibliotecas externas
spinner_chars = '|/-\\'  # Secuencia de caracteres para el spinner
mensaje_actual = ""

def mostrar_spinner():
    i = 0
    while not detener_spinner_event.is_set():
        sys.stdout.write('\r{} {}'.format(spinner_chars[i], mensaje_actual))
        sys.stdout.flush()
        time.sleep(0.1)
        i = (i + 1) % len(spinner_chars)

def print_especial(mensaje):
    global mensaje_actual
    sys.stdout.write('\033[2K\r')  # Borrar la línea completa
    sys.stdout.flush()
    mensaje_actual = mensaje

def detener_spinner():
    detener_spinner_event.set()
    sys.stdout.write('\r\033[K')  # Borrar la línea actual
    sys.stdout.flush()

# Crear un evento para indicar que se debe detener el spinner
detener_spinner_event = threading.Event()

def manejar_interrupcion(signal, frame):
    print("Programa interrumpido por el usuario.")
    detener_spinner()
    sys.exit(0)

# Registrar el manejador de señal para la interrupción (Ctrl + C)
signal.signal(signal.SIGINT, manejar_interrupcion)

## Descargar el archivo javascript y formatearlo
def analisis_completo(js_url, ruta_json):
    # Desactivar la verificación del certificado SSL
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    print_especial("Descargando...")
    try:
        with urllib.request.urlopen(js_url, context=ssl_context) as f:
            js_code = f.read().decode('utf-8')
            js_code = jsbeautifier.beautify(js_code)
            if args.storage_js:
                output_dir = os.path.join(args.storage_js, urlparse(js_url).netloc)  # Directorio proporcionado por el usuario
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                file_name = os.path.join(output_dir, os.path.relpath(urlparse(js_url).path, '/'))
                with open(file_name, 'w') as js_file:
                    js_file.write(js_code)

            print_especial(fv.buscar_vulns(ruta_json,js_url,js_code))
            print_especial(fu.buscar_urls(ruta_json,js_url,js_code))
            print_especial(fs.buscar_tokens(ruta_json,js_url,js_code))
            print_especial(fs.buscar_entropia(ruta_json,js_url, js_code))
    except Exception as e:
        print("Ocurrió un error al obtener el código JS:", str(e))

def resultados_finales(ruta_json):
    with open(ruta_json, encoding="utf-8") as archivo:
            data = json.load(archivo)
            
    for i in data:
        url_tmp = i["URL"]
        print(f"\n*************\nLos resultados del endpoint {url_tmp} son los siguientes:\n")

        num_patterns = len(i["JS_Analisis"]["JS_Possible_endpoints"])
        print(f"{num_patterns} patrones coincidentes, en la búsqueda de endpoints")
        for j in i["JS_Analisis"]["JS_Possible_endpoints"]:
            num_patterns = len(i["JS_Analisis"]["JS_Possible_endpoints"][j]["results"])
            print(f"    Un total de {num_patterns} posibles {j}")
        
        num_patterns = len(i["JS_Analisis"]["JS_Possible_Vulns"])
        print(f"{num_patterns} patrones coincidentes, en el análisis de vulnerabilidades")
        for j in i["JS_Analisis"]["JS_Possible_Vulns"]:
            num_patterns = len(i["JS_Analisis"]["JS_Possible_Vulns"][j]["results"])
            print(f"    Un total de {num_patterns} de tipo {j}")
        
        num_patterns = len(i["JS_Analisis"]["JS_Possible_tokens"])
        print(f"{num_patterns} patrones coincidentes, en la búsqueda de tokens")
        
        num_patterns = len(i["JS_Analisis"]["JS_Entropy_Tokens"]["results"])
        print(f"{num_patterns} patrones coincidentes, en el análisis de entropía")
        for j in i["JS_Analisis"]["JS_Entropy_Tokens"]["results"]:
            match_tmp = j["match"]
            print(f"    Posible token {match_tmp}")
    
    print("\n*************\n")

def crear_json_vacio(ruta_json):
    # Crear el json
    data = []
    with open(ruta_json, "w", encoding="utf-8") as archivo:
        json.dump(data, archivo, indent=4, ensure_ascii=False)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--urls-file', help='Archivo de URLs')
    parser.add_argument('-U', '--url', help='URL Única')
    parser.add_argument('-o', '--output', help='Archivo de salida')
    parser.add_argument('-s', '--storage-js', help='Indicar el directorio en el que almacenar el código JS')

    args = parser.parse_args()

    if args.output:
        ruta_json = args.output + ".json"
    else:
        # Valor por defecto si no se proporciona el argumento
        ruta_json = "js_analysis.json"
    
    # Crear y ejecutar el hilo para mostrar el spinner
    spinner_thread = threading.Thread(target=mostrar_spinner)
    spinner_thread.start()

    if args.urls_file:
        fichero = args.urls_file 
        ## Main ##
        print_especial("Comenzamos a descargar y analizar los archivos, este proceso puede tardar un rato")
        # Lista para almacenar las URLs
        urls = []
        # Leer las URLs del archivo de texto
        with open(fichero, 'r') as f:
            urls = f.read().splitlines()
        # Crear un json vacío que se irá rellenando
        crear_json_vacio(ruta_json)
        # Llama a la función principal del programa
        for js_url in urls:
            analisis_completo(js_url,ruta_json)

    elif args.url:
        ## Main ##
        print_especial("Comenzamos a descargar y analizar los archivos, este proceso puede tardar un rato")
        # Crear un json vacío que se irá rellenando
        crear_json_vacio(ruta_json)
        # Llama a la función principal del programa
        analisis_completo(args.url,ruta_json)

    else:
        # Detener el spinner
        detener_spinner()
        spinner_thread.join()  # Esperar a que el hilo del spinner termine

        parser.error("Es necesario introducir un Input")

    # Detener el spinner
    detener_spinner()
    spinner_thread.join()  # Esperar a que el hilo del spinner termine

    print(f"\nLos resultados se encuentran en {ruta_json}")
    resultados_finales(ruta_json)
