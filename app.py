from flask import Flask, render_template, request, redirect, url_for, session, flash
from funciones import SistemaRevistas
import os
import csv
import json

app = Flask(__name__)
app.secret_key = 'clave_secreta_super_segura'

# Inicializar sistema
sistema = SistemaRevistas()
sistema.cargar_usuarios_desde_csv(r'C:\Users\YUGEN\Documents\ProyectoFinalDS42025\datos\csv\users\users.csv')
sistema.cargar_areas_desde_csv(r'C:\Users\YUGEN\Documents\ProyectoFinalDS42025\datos\csv\areas')
sistema.cargar_catalogos_desde_csv(r'C:\Users\YUGEN\Documents\ProyectoFinalDS42025\datos\csv\catalogos')
sistema.cargar_json(r'C:\Users\YUGEN\Documents\ProyectoFinalDS42025\datos\json\revistas_scimagojr.json')


@app.route('/')
def index():
    if 'usuario' not in session:
        return redirect(url_for('login'))  

    usuario = session['usuario']
    return render_template('index.html', usuario=usuario)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if sistema.login(username, password):
            session['usuario'] = username
            flash('Inicio de sesión exitoso.', 'success')
            return redirect(url_for('index'))
        else:
            flash('Credenciales incorrectas.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('usuario', None)  
    return redirect(url_for('index')) 

@app.route('/buscar', methods=['GET', 'POST'])
def buscar():
    resultados = []
    if request.method == 'POST':
        termino = request.form['termino']
        resultados = sistema.buscar_revistas_por_nombre(termino)
    return render_template('buscar.html', resultados=resultados)

@app.route('/top')
def top():
    revistas_top = sistema.top_revistas_por_indice(10)
    return render_template('top.html', revistas=revistas_top)

@app.route('/area', methods=['GET', 'POST'])
def area():
    revistas_area = []
    if request.method == 'POST':
        area = request.form['area']
        revistas_area = sistema.revistas_por_area(area)
    return render_template('area.html', revistas=revistas_area)

@app.route('/areas')
def listar_areas():
    areas = sistema.areas_disponibles()
    return render_template('areas.html', areas=areas)


@app.route('/area/<area>')
def area_detalle(area):
    revistas = sistema.revistas_por_area(area)
    return render_template('area_detalle.html', area=area, revistas=revistas)
    

@app.route('/catalogos')
def catalogos():
    catalogos = sistema.catalogos_disponibles()
    return render_template('catalogos.html', catalogos=catalogos)

@app.route('/catalogo/<catalogo>')
def catalogo_detalle(catalogo):
    revistas = sistema.revistas_por_catalogo(catalogo)  # Ahora debería funcionar
    return render_template('catalogo_detalle.html', catalogo=catalogo, revistas=revistas)


@app.route('/explorar')
def explorar():
    letra = request.args.get('letra', '').upper()
    area_filtro = request.args.get('area', '')
    page = int(request.args.get('page', 1))
    por_pagina = 50

    # Obtener todas las revistas
    todas_revistas = list(sistema.revistas.values())

    # Filtrar por letra inicial del nombre
    if letra:
        todas_revistas = [r for r in todas_revistas if r.nombre.upper().startswith(letra)]

    # Filtrar por área
    if area_filtro:
        todas_revistas = [r for r in todas_revistas if r.subject_area_category == area_filtro]

    # Total de páginas
    total_paginas = (len(todas_revistas) - 1) // por_pagina + 1
    inicio = (page - 1) * por_pagina
    fin = inicio + por_pagina
    revistas_pagina = todas_revistas[inicio:fin]

    # Crear diccionario enriquecido
    revistas_dict = {}
    for r in revistas_pagina:
        catalogos = [
            nombre_cat for nombre_cat, revistas in sistema.catalogos_data.items()
            if any(r.nombre.lower() == rev['nombre'].strip().lower() for rev in revistas)
        ]
        areas = [r.subject_area_category] if r.subject_area_category else []

        revistas_dict[r.nombre] = {
            'h_index': r.h_index,
            'catalogos': catalogos,
            'areas': areas
        }

    # Para el filtro
    letras = sorted(set(r.nombre[0].upper() for r in sistema.revistas.values() if r.nombre))
    areas_disponibles = sorted(set(r.subject_area_category for r in sistema.revistas.values() if r.subject_area_category))

    return render_template(
        'explorar.html',
        revistas=revistas_dict.items(),
        scimagojr=sistema.scimagojr,
        page=page,
        total_pages=total_paginas,
        letras=letras,
        letra_actual=letra,
        areas=areas_disponibles,
        area_actual=area_filtro
    )
    
@app.route('/creditos')
def creditos():
    return render_template('creditos.html')

@app.route('/revista/<titulo>')
def revista_detalle(titulo):
    revista = sistema.revistas.get(titulo.lower())
    return render_template('revista_detalle.html', revista=revista)

@app.route('/resumen')
def resumen():
    total = len(sistema.revistas)
    promedio = sum(r.h_index for r in sistema.revistas.values()) / total if total > 0 else 0
    return render_template('resumen.html', total=total, promedio=promedio)

if __name__ == '__main__':
    app.run(debug=True)
