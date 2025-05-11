import pandas as pd
import json
from pathlib import Path
import os
import unicodedata
import chardet

# Rutas base
BASE_PATH = Path(__file__).resolve().parent.parent
RUTA_AREAS = BASE_PATH / 'datos' / 'csv' / 'areas'
RUTA_CATALOGOS = BASE_PATH / 'datos' / 'csv' / 'catalogos'
SALIDA_JSON = BASE_PATH / 'datos' / 'json' / 'revistas.json'

def normalizar_texto(texto):
    texto = str(texto).lower().strip()
    return unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode('ascii')

def quitar_sufijo(nombre):
    return nombre.replace(' RadGridExport', '').replace('_RadGridExport', '')

def detectar_codificacion(archivo):
    with open(archivo, 'rb') as f:
        resultado = chardet.detect(f.read())
        return resultado['encoding']

def cargar_csvs(ruta, tipo):
    lista_df = []
    posibles = ['utf-8', 'latin1', 'cp1252', 'iso-8859-1']

    for archivo in ruta.glob('*.csv'):
        etiqueta = quitar_sufijo(archivo.stem)
        leido = False

        # Intento con codificación automática
        codif = detectar_codificacion(archivo)
        try:
            df = pd.read_csv(archivo, encoding=codif, names=['nombre_revista'])
            df = df[df['nombre_revista'] != 'TITULO:']
            df[tipo] = etiqueta
            lista_df.append(df)
            leido = True
        except:
            pass

        # Codificaciones de respaldo
        if not leido:
            for cod in posibles:
                try:
                    df = pd.read_csv(archivo, encoding=cod, names=['nombre_revista'])
                    df = df[df['nombre_revista'] != 'TITULO:']
                    df[tipo] = etiqueta
                    lista_df.append(df)
                    break
                except:
                    continue

    return pd.concat(lista_df, ignore_index=True) if lista_df else pd.DataFrame()

def generar_json():
    print('Cargando áreas...')
    df_areas = cargar_csvs(RUTA_AREAS, 'area')

    print('Cargando catálogos...')
    df_catalogos = cargar_csvs(RUTA_CATALOGOS, 'catalogo')

    revistas = {}

    for _, fila in df_areas.iterrows():
        titulo = normalizar_texto(fila['nombre_revista'])
        area = fila['area']
        if titulo not in revistas:
            revistas[titulo] = {'areas': [], 'catalogos': []}
        if area not in revistas[titulo]['areas']:
            revistas[titulo]['areas'].append(area)

    for _, fila in df_catalogos.iterrows():
        titulo = normalizar_texto(fila['nombre_revista'])
        catalogo = fila['catalogo']
        if titulo not in revistas:
            revistas[titulo] = {'areas': [], 'catalogos': []}
        if catalogo not in revistas[titulo]['catalogos']:
            revistas[titulo]['catalogos'].append(catalogo)

    os.makedirs(SALIDA_JSON.parent, exist_ok=True)
    with open(SALIDA_JSON, 'w', encoding='utf-8') as f:
        json.dump(revistas, f, ensure_ascii=False, indent=2)

    print(f'Total de revistas procesadas: {len(revistas)}')

if __name__ == '__main__':
    generar_json()