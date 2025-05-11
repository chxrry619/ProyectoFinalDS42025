import os
import json
import time
import threading
import requests
import argparse
from flask import Flask, render_template, request, jsonify
from bs4 import BeautifulSoup
from pathlib import Path

app = Flask(__name__)

@app.route('/login')
def login():
    return render_template('login.html')

# Obtener la ruta base del proyecto
BASE_DIR = Path(__file__).parent
REVISTAS_JSON = BASE_DIR / 'datos' / 'json' / 'revistas.json'
SCIMAGOJR_JSON = BASE_DIR / 'datos' / 'json' / 'revistas_scimagojr.json'
BACKUP_JSON = BASE_DIR / 'datos' / 'json' / 'revistas_scimagojr_backup.json'

# Configurar argumentos de línea de comandos
parser = argparse.ArgumentParser(description='Scraper de ScimagoJR con punto de inicio configurable')
parser.add_argument('--inicio', type=int, default=0, help='Índice desde donde empezar a procesar (default: 0)')
parser.add_argument('--fin', type=int, help='Índice donde terminar de procesar (opcional)')
parser.add_argument('--reverso', action='store_true', help='Procesar las revistas en orden inverso')
args = parser.parse_args()

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, Gecko) Chrome/123.0.0.0 Safari/537.36'
}

SCIMAGO_BASE_URL = 'https://www.scimagojr.com'
SEARCH_URL = SCIMAGO_BASE_URL + '/journalsearch.php?q='

# Cargar datos de revistas
def cargar_datos():
    if os.path.exists(REVISTAS_JSON):
        with open(REVISTAS_JSON, 'r', encoding='utf-8') as f:
            revistas = json.load(f)
    else:
        revistas = {}

    if os.path.exists(SCIMAGOJR_JSON):
        with open(SCIMAGOJR_JSON, 'r', encoding='utf-8') as f:
            scimagojr = json.load(f)
    else:
        scimagojr = {}

    return revistas, scimagojr

# Función de scraping
def scrap(url):
    response = requests.get(url, headers=HEADERS, timeout=15)
    if response.status_code != 200:
        raise Exception(f"Error {response.status_code} en {url}")
    return response

def find_journal_url(journal_title):
    search = SEARCH_URL + journal_title.replace(" ", "+")
    soup = BeautifulSoup(scrap(search).text, 'html.parser')
    result = soup.select_one('span.jrnlname')
    if result:
        return SCIMAGO_BASE_URL + '/' + result.find_parent('a')['href']
    return None

def obtenerimagen(soup):
    try:
        img = soup.find('img', class_='imgwidget')
        if img and 'src' in img.attrs:
            return 'https://www.scimagojr.com/' + img['src']
    except Exception as e:
        print(f"Error al extraer imagen: {e}")
    return None

def extract_subject_area(soup):
    section = soup.find("h2", string="Subject Area and Category")
    if not section:
        return None
    table = section.find_next("table")
    if not table:
        return None
    items = table.find_all("td")
    categories = [td.get_text(strip=True) for td in items if td]
    return ', '.join(categories)

def scrape_journal_data(url):
    soup = BeautifulSoup(scrap(url).text, 'html.parser')

    # Obtener H-Index
    try:
        h_index_section = soup.find('h2', string=lambda s: s and 'H-Index' in s)
        h_index = h_index_section.find_next_sibling('p').text.strip() if h_index_section else None
    except Exception as e:
        print(f"Error al extraer H-Index: {e}")
        h_index = None

    # Obtener Homepage
    try:
        homepage_section = soup.find('a', string='Homepage')
        homepage_link = homepage_section['href'] if homepage_section else None
    except Exception as e:
        print(f"Error al extraer Homepage: {e}")
        homepage_link = None

    # Obtener Publisher
    try:
        publisher_section = soup.find('h2', string=lambda s: s and 'Publisher' in s)
        publisher = publisher_section.find_next_sibling('p').text.strip() if publisher_section else None
    except Exception as e:
        print(f"Error al extraer Publisher: {e}")
        publisher = None

    # Obtener ISSN
    try:
        issn_section = soup.find('h2', string=lambda s: s and 'ISSN' in s)
        issn = issn_section.find_next_sibling('p').text.strip() if issn_section else None
    except Exception as e:
        print(f"Error al extraer ISSN: {e}")
        issn = None

    # Obtener imagen del widget
    widget_url = obtenerimagen(soup)

    # Obtener Publication Type
    try:
        publication_type_section = soup.find('h2', string=lambda s: s and 'Publication type' in s)
        publication_type = publication_type_section.find_next_sibling('p').text.strip() if publication_type_section else None
    except Exception as e:
        print(f"Error al extraer Publication type: {e}")
        publication_type = None

    return {
        "site": homepage_link,
        "h_index": h_index,
        "subject_area_category": extract_subject_area(soup),
        "publisher": publisher,
        "issn": issn,
        "widget": widget_url,
        "publication_type": publication_type,
        "url": url
    }

# Guardar datos en un archivo JSON
def save_data_safely(data, titulo=""):
    try:
        with open(OUTPUT_JSON, 'w', encoding='utf-8') as archivo_salida:
            json.dump(data, archivo_salida, indent=4, ensure_ascii=False)
        
        if titulo:
            print(f"✅ Información guardada exitosamente: {titulo}")
        return True
    except Exception as save_error:
        print(f"❌ Error al guardar los datos: {str(save_error)}")
        return False

# Rutas principales en Flask
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/revistas')
def mostrar_revistas():
    revistas, _ = cargar_datos()
    return render_template('revistas.html', revistas=revistas)

@app.route('/revista/<titulo>')
def revista_detalle(titulo):
    revistas, scimagojr = cargar_datos()
    revista_info = revistas.get(titulo, {})
    scimagojr_info = scimagojr.get(titulo, {})
    return render_template('revista_detalle.html', titulo=titulo, revista=revista_info, scimagojr=scimagojr_info)

if __name__ == '__main__':
    app.run(debug=True)