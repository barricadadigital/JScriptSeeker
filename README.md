# JScriptSeeker
Tool to extract information from Javascript files

Herramienta para extraer información de archivos Javascript

Por ahora la herramienta es totalmente funcional, aunque está en desarrollo y pueden aparecer errores, además de que hay opciones que todavía no contempla cómo poder introducir directamente un archivo javascript en vez de descargarlo desde internet.

## Instalación

hay que instalar la librería jsbeautifier, el resto son por defecto de la instalación de python.

```bash
pip install jsbeautifier
```
---

## Uso

Uso básico -> Le pasas un listado de URLs al script y se encarga de descargarlas e ir almacenando la información por defecto en "js_analysis.json"

```bash
python .\JScriptSeeker.py -u test
```
---

### Argumentos
- -u -> Un archivo con un listado de urls
- -U -> Una URL única
- -o -> Dónde almacenar el output
- -s -> Directorio seleccionado si se quiere almacenar el código javascript limpio

---
### ¿Qué información extrae?

- Endpoints -> Mediante los regex que se encuentran en los diccionarios "url_regex.json"
- Funciones vulnerables -> Por ahora hay pocas añadidas, las encuentras en los diccionarios "funciones_vulns_dict.json"
- Secretos -> Se obtienen de dos formas, por un lado mediante regex, los encuentras en el diccionario "secret_regex.json"; Por otro lado también se obtienen mediante entropía, por defecto en 4.5 aunque puedes modificarlo directamente en el código en find_secrets.py

---
*****
EN CONSTRUCCIÓN
*****
