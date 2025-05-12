import os
import json
import time
import threading
import requests
import argparse
from bs4 import BeautifulSoup


ROOT_DIR = r'/home/chrry/Documentos/desarrollo4/ProyectoFinalDS42025/ProyectoFinalDS42025'
INPUT_PATH = os.path.join(ROOT_DIR, 'datos', 'json', 'revistas.json')
OUTPUT_PATH = os.path.join(ROOT_DIR, 'datos', 'json', 'revistas_scimagojr.json')
BACKUP_PATH = os.path.join(ROOT_DIR, 'datos', 'json', 'revistas_scimagojr_backup.json')

# Parámetros CLI
cli = argparse.ArgumentParser(description='Extractor de datos desde ScimagoJR.')
cli.add_argument('--inicio', type=int, default=0, help='Índice inicial del procesamiento')
cli.add_argument('--fin', type=int, help='Índice final del procesamiento')
cli.add_argument('--invertir', action='store_true', help='Procesar en orden inverso')
args = cli.parse_args()

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (compatible; ScraperBot/1.0; +https://example.com/bot)'
}

BASE_URL = 'https://www.scimagojr.com'
BUSQUEDA_URL = BASE_URL + '/journalsearch.php?q='

# Logging symbols
OK = "-- OK --"
ERR = "-- ERROR --"
WAIT = "..."
WARN = "Advertencia!"
INFO = "!!!"

# Pausa dinámica
pausado = False

def alternar_pausa():
    global pausado
    pausado = not pausado
    estado = "Pausado" if pausado else "Reanudado"
    print(f"{INFO} {estado} el proceso.")

def hilo_entrada():
    while True:
        comando = input("Escribe 'pausar' para pausar/reanudar: ").strip().lower()
        if comando == 'pausar':
            alternar_pausa()

threading.Thread(target=hilo_entrada, daemon=True).start()

def leer_json(path):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def guardar_json(data, mensaje=""):
    try:
        with open(BACKUP_PATH, 'w', encoding='utf-8') as bkp:
            json.dump(data, bkp, indent=4, ensure_ascii=False)
        with open(OUTPUT_PATH, 'w', encoding='utf-8') as out:
            json.dump(data, out, indent=4, ensure_ascii=False)
        if mensaje:
            print(f"{OK} Se ha guardado: {mensaje}")
        return True
    except Exception as ex:
        print(f"{ERR} Fallo al guardar: {str(ex)}")
        return False

def buscar_url_revista(nombre):
    consulta = BUSQUEDA_URL + nombre.replace(" ", "+")
    html = requests.get(consulta, headers=HEADERS, timeout=15).text
    dom = BeautifulSoup(html, 'html.parser')
    elemento = dom.select_one('span.jrnlname')
    if elemento:
        return BASE_URL + '/' + elemento.find_parent('a')['href']
    return None

def extraer_categoria(dom):
    bloque = dom.find("h2", string="Subject Area and Category")
    if not bloque:
        return None
    tabla = bloque.find_next("table")
    if not tabla:
        return None
    celdas = [td.get_text(strip=True) for td in tabla.find_all("td")]
    return ', '.join(celdas)

def obtener_widget(dom):
    try:
        img = dom.find('img', class_='imgwidget')
        if img and img.get('src'):
            return BASE_URL + '/' + img['src']
    except:
        pass
    return None

def recolectar_datos(url):
    html = requests.get(url, headers=HEADERS, timeout=15).text
    dom = BeautifulSoup(html, 'html.parser')

    def extraer_texto(seccion):
        encabezado = dom.find('h2', string=lambda s: s and seccion in s)
        return encabezado.find_next_sibling('p').text.strip() if encabezado else None

    sitio = dom.find('a', string='Homepage')
    return {
        'site': sitio['href'] if sitio else None,
        'h_index': extraer_texto('H-Index'),
        'subject_area_category': extraer_categoria(dom),
        'publisher': extraer_texto('Publisher'),
        'issn': extraer_texto('ISSN'),
        'widget': obtener_widget(dom),
        'publication_type': extraer_texto('Publication type'),
        'url': url
    }

# Preparar datos
titulos = leer_json(INPUT_PATH)
procesados = leer_json(OUTPUT_PATH) or leer_json(BACKUP_PATH) or {}
lista_revistas = list(titulos.items())

# Invertir si es necesario
if args.invertir:
    lista_revistas = lista_revistas[::-1]
    if args.fin is not None:
        args.inicio, args.fin = len(lista_revistas) - args.fin, len(lista_revistas) - args.inicio

sublista = lista_revistas[args.inicio:args.fin if args.fin else len(lista_revistas)]

print(f"{INFO} Procesando revistas del índice {args.inicio} al {args.fin or len(lista_revistas)}")
print(f"{INFO} Total a procesar: {len(sublista)}")

nuevos = 0
for i, (nombre, _) in enumerate(sublista):
    while pausado:
        print(f"{INFO} Pausado. Progreso: {len(procesados)} revistas.")
        time.sleep(5)

    if nombre in procesados:
        print(f"{WARN} Ya procesada: {nombre}")
        continue

    print(f"{WAIT} Procesando: {nombre} (n.{args.inicio + i})")
    try:
        url = buscar_url_revista(nombre)
        if not url:
            print(f"{ERR} No se ha encontrado: {nombre}")
            continue

        datos = recolectar_datos(url)
        procesados[nombre] = datos
        guardar_json(procesados, nombre)
        nuevos += 1
        time.sleep(2)

    except Exception as err:
        print(f"{ERR} Fallo con {nombre}: {str(err)}")

guardar_json(procesados)
print(f"{OK} Proceso completo. Revistas nuevas procesadas: {nuevos}")
