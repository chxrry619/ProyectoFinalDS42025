import pandas as pd
import json
from pathlib import Path
import os
import unicodedata
import chardet

BASE = Path.cwd()
CARPETA_AREAS = BASE / 'datos' / 'csv' / 'areas'
CARPETA_CATALOGOS = BASE / 'datos' / 'csv' / 'catalogos'
SALIDA_JSON = BASE / 'datos' / 'json' / 'revistas.json'

def normalizar_texto(texto):
    texto = str(texto).strip().lower()
    texto = unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode('ascii')
    return texto

def nombre_limpio(nombre_archivo):

    return nombre_archivo.replace(' RadGridExport', '').replace('_RadGridExport', '')

def obtener_codificacion(ruta_archivo):
    with open(ruta_archivo, 'rb') as f:
        raw = f.read()
        resultado = chardet.detect(raw)
        return resultado['encoding']

def cargar_csv_desde_carpeta(carpeta, tipo_columna):
    lista_dataframes = []
    posibles_codificaciones = ['utf-8', 'latin1', 'cp1252', 'iso-8859-1']

    for archivo in carpeta.glob('*.csv'):
        etiqueta = nombre_limpio(archivo.stem)

        try:
            codificacion = obtener_codificacion(archivo)
            df = pd.read_csv(archivo, encoding=codificacion, names=['revista'])
            df = df[df['revista'] != 'TITULO:']
            df[tipo_columna] = etiqueta
            lista_dataframes.append(df)
            continue
        except Exception:
            pass


        for cod in posibles_codificaciones:
            try:
                df = pd.read_csv(archivo, encoding=cod, names=['revista'])
                df = df[df['revista'] != 'TITULO:']
                df[tipo_columna] = etiqueta
                lista_dataframes.append(df)
                break
            except:
                continue
        else:
            print(f'No se pudo leer el archivo: {archivo.name}')
    
    return pd.concat(lista_dataframes, ignore_index=True) if lista_dataframes else pd.DataFrame()

def crear_json_revistas():
    print('Se están cargando las areas, favor de esperar...')
    df_areas = cargar_csv_desde_carpeta(CARPETA_AREAS, 'area')

    print('Se están cargando los catalogos, favor de esperar...')
    df_catalogos = cargar_csv_desde_carpeta(CARPETA_CATALOGOS, 'catalogo')

    coleccion = {}

    for _, fila in df_areas.iterrows():
        titulo = normalizar_texto(fila['revista'])
        area = fila['area']
        if titulo not in coleccion:
            coleccion[titulo] = {'areas': [], 'catalogos': []}
        if area not in coleccion[titulo]['areas']:
            coleccion[titulo]['areas'].append(area)

    for _, fila in df_catalogos.iterrows():
        titulo = normalizar_texto(fila['revista'])
        catalogo = fila['catalogo']
        if titulo not in coleccion:
            coleccion[titulo] = {'areas': [], 'catalogos': []}
        if catalogo not in coleccion[titulo]['catalogos']:
            coleccion[titulo]['catalogos'].append(catalogo)

    os.makedirs(SALIDA_JSON.parent, exist_ok=True)
    with open(SALIDA_JSON, 'w', encoding='utf-8') as f:
        json.dump(coleccion, f, ensure_ascii=False, indent=2)

    print(f'Archivo generado: {SALIDA_JSON}')
    print(f'Revistas procesadas: {len(coleccion)} revistas')

if __name__ == '__main__':
    crear_json_revistas()
