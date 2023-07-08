import re
import json
import math

## Función para buscar tokens ##
def buscar_tokens(ruta_json, js_url, js_code):
    matches = {
        "URL": js_url,
        "JS_Analisis": {
        "JS_Possible_tokens": {}
        }
    }

    # Leer el archivo JSON en un diccionario
    with open('dictionaries/secret_regex.json', 'r', encoding="utf-8") as archivo:
        datos = json.load(archivo)

    for patron in datos['patterns']:
        name = patron['pattern']['name']
        regex = patron['pattern']['regex']
        confidence = patron['pattern']['confidence']
        for num_linea, line in enumerate(js_code.split('\n'), start=1):
            if re.search(regex, line):
                if name not in matches["JS_Analisis"]["JS_Possible_tokens"]:
                    matches["JS_Analisis"]["JS_Possible_tokens"][name] = {
                            'regex': regex,
                            'confidence': confidence,
                            'results': []
                        }
                for match in re.finditer(regex, line):
                    matches["JS_Analisis"]["JS_Possible_tokens"][name]["results"].append({
                        'match': match.group(0)[:min(100, len(match.group(0)))],
                        'line': num_linea,
                        'position': match.start(),
                    })

    with open(ruta_json, encoding="utf-8") as archivo:
        data = json.load(archivo)

    encontrado = False
    for elemento in data:
        if elemento["URL"] == matches["URL"]:
            elemento["JS_Analisis"].update(matches["JS_Analisis"])
            encontrado = True
            break
    
    if not encontrado:
        # La URL no existe en el JSON, agregar una nueva entrada
        data.append(matches)
    
    # Guardar el JSON actualizado en el archivo
    with open(ruta_json, "w", encoding="utf-8") as archivo:
        json.dump(data, archivo, indent=4, ensure_ascii=False)

    # imprimir un resumen por consola
    num_patterns = len(matches["JS_Analisis"]["JS_Possible_tokens"])
    return(f"Se han encontrado {num_patterns} patrones coincidentes, los resultados están en test_secret_js.json")

##  Función para calcular la entropía  ##
def calculate_entropy(password):
    entropy = 0
    for char in set(password):
        p = password.count(char) / len(password)
        entropy += - p * math.log2(p)
    return entropy

##  Función para buscar tokens por entropía  ##
def buscar_entropia(ruta_json, js_url, js_code, caracteres=8, entropia=4.5):
    # Expresión regular para buscar cadenas de texto de al menos 8 caracteres
    regex = fr"\b\w{{{caracteres},}}\b"

    # Buscar todas las coincidencias en el código JavaScript
    coincidencias = re.findall(regex, js_code)

    matches = {
        "URL": js_url,
        "JS_Analisis": {}
    }
    
    # Iterar sobre todas las coincidencias y calcular su entropía
    for num_linea, match in enumerate(coincidencias, start=1):
        entropy = calculate_entropy(match)
        # Si la entropía es inferior al umbral, imprimir un mensaje de advertencia
        if entropy > entropia:
            if "JS_Entropy_Tokens" not in matches["JS_Analisis"]:
                matches["JS_Analisis"]["JS_Entropy_Tokens"] = {
                        'nivel_entropia': entropia,
                        'info': "Se determina un nivel de entropia para intentar buscar posibles tokens en el codigo",
                        'results': []
                    }
            position = js_code.find(match)
            matches["JS_Analisis"]["JS_Entropy_Tokens"]["results"].append({
                'match': match,
                'line': num_linea,
                'position': position,
            })
            #print(f"La cadena '{match}' tiene una entropía de {entropy} bits y podría ser un token o contraseña")

    with open(ruta_json, encoding="utf-8") as archivo:
        data = json.load(archivo)
    
    # Buscar la URL en el JSON
    encontrado = False
    for elemento in data:
        if elemento["URL"] == matches["URL"]:
            elemento["JS_Analisis"].update(matches["JS_Analisis"])
            encontrado = True
            break
    
    if not encontrado:
        # La URL no existe en el JSON, agregar una nueva entrada
        data.append(matches)
    
    # Guardar el JSON actualizado en el archivo
    with open(ruta_json, "w", encoding="utf-8") as archivo:
        json.dump(data, archivo, indent=4, ensure_ascii=False)
    
    # imprimir un resumen por consola
    num_patterns = len(matches["JS_Analisis"]["JS_Entropy_Tokens"]["results"])
    return(f"Se han encontrado {num_patterns} patrones coincidentes, los resultados están en test_secret_js.json")



