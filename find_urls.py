import re
import json

## Función para buscar urls ##
def buscar_urls(ruta_json, js_url, js_code):
    matches = {
        "URL": js_url,
        "JS_Analisis": {
        "JS_Possible_endpoints": {}
        }
    }

    # Leer el archivo JSON en un diccionario
    with open('dictionaries/url_regex.json', 'r', encoding="utf-8") as archivo:
        datos = json.load(archivo)

    for patron in datos['patrones']:
            name = patron['patron']['name']
            regex = patron['patron']['regex']
            info = patron['patron']['info']
            for num_linea, line in enumerate(js_code.split('\n'), start=1):
                if re.search(regex, line):
                    if name not in matches["JS_Analisis"]["JS_Possible_endpoints"]:
                        matches["JS_Analisis"]["JS_Possible_endpoints"][name] = {
                                'regex': regex,
                                'info': info,
                                'results': []
                            }
                    for match in re.finditer(regex, line):
                        matches["JS_Analisis"]["JS_Possible_endpoints"][name]["results"].append({
                            'match': match.group(0),
                            'line': num_linea,
                            'position': match.start(),
                        })

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
    num_patterns = len(matches["JS_Analisis"]["JS_Possible_endpoints"])
    return(f"Se han encontrado {num_patterns} patrones coincidentes, los resultados están en test_urls_js.json")