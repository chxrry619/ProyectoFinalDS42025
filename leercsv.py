import os
import csv
import json

# Ruta base
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_DIR = os.path.join(BASE_DIR, 'datos', 'datos', 'csv')
AREAS_DIR = os.path.join(CSV_DIR, 'areas')
CATALOGOS_DIR = os.path.join(CSV_DIR, 'catalogos')
JSON_DIR = os.path.join(BASE_DIR, 'datos', 'json')

# Aseguramos que el directorio de JSON exista
os.makedirs(JSON_DIR, exist_ok=True)

def leer_csv(nombre_archivo):
    """Lee un archivo CSV y devuelve una lista de diccionarios."""
    with open(nombre_archivo, mode='r', encoding='utf-8') as file:
        lector = csv.DictReader(file)
        return [fila for fila in lector]

def procesar_archivos_csv():
    """Procesa los archivos CSV de áreas y catálogos y crea el diccionario de revistas."""
    revistas = {}

    # Leer los archivos de áreas
    areas_path = os.path.join(AREAS_DIR, 'areas.csv')
    areas_data = leer_csv(areas_path)

    # Leer los archivos de catálogos
    catalogos_path = os.path.join(CATALOGOS_DIR, 'catalogos.csv')
    catalogos_data = leer_csv(catalogos_path)

    # Procesar las áreas
    for area in areas_data:
        titulo_revista = area['revista']
        if titulo_revista not in revistas:
            revistas[titulo_revista] = {'areas': [], 'catalogos': []}
        revistas[titulo_revista]['areas'].append(area['area'])

    # Procesar los catálogos
    for catalogo in catalogos_data:
        titulo_revista = catalogo['revista']
        if titulo_revista not in revistas:
            revistas[titulo_revista] = {'areas': [], 'catalogos': []}
        revistas[titulo_revista]['catalogos'].append(catalogo['catalogo'])

    return revistas

def guardar_json(datos, nombre_archivo):
    """Guarda los datos en un archivo JSON."""
    ruta_json = os.path.join(JSON_DIR, nombre_archivo)
    with open(ruta_json, 'w', encoding='utf-8') as json_file:
        json.dump(datos, json_file, indent=4, ensure_ascii=False)
    print(f"Datos guardados en: {ruta_json}")

def verificar_json(nombre_archivo):
    """Verifica que el archivo JSON puede ser leído."""
    ruta_json = os.path.join(JSON_DIR, nombre_archivo)
    try:
        with open(ruta_json, 'r', encoding='utf-8') as file:
            data = json.load(file)
        print(f"Archivo JSON leído correctamente: {ruta_json}")
    except Exception as e:
        print(f"Error al leer el archivo JSON: {e}")

def main():
    # Procesamos los archivos CSV y obtenemos el diccionario de revistas
    revistas_data = procesar_archivos_csv()

    # Guardamos el diccionario en un archivo JSON
    guardar_json(revistas_data, 'revistas.json')

    # Verificamos que el JSON puede ser leído
    verificar_json('revistas.json')

if __name__ == '__main__':
    main()
