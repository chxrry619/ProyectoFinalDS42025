from flask import Flask, render_template, request, redirect, url_for, session, flash
from funciones import SistemaRevistas
import os
import csv
import json

app = Flask(__name__)
app.secret_key = 'clave_secreta_super_segura'

# Inicializar sistema
sistema = SistemaRevistas()
sistema.cargar_areas_desde_csv(r'C:\Users\YUGEN\Documents\ProyectoFinalDS42025\datos\csv\areas')
sistema.cargar_catalogos_desde_csv(r'C:\Users\YUGEN\Documents\ProyectoFinalDS42025\datos\csv\catalogos')
sistema.cargar_json(r'C:\Users\YUGEN\Documents\ProyectoFinalDS42025\datos\json\revistas_scimagojr.json')
sistema.cargar_usuarios_desde_csv(r'C:\Users\YUGEN\Documents\ProyectoFinalDS42025\datos\csv\users\users.csv')

@app.route('/')
def index():
    if 'usuario' not in session:
        return redirect(url_for('login'))  # Si no hay usuario en la sesión, redirige al login

    # Si hay usuario en la sesión, pasa el nombre de usuario a la plantilla
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
    session.pop('usuario', None)  # Elimina el 'usuario' de la sesión
    return redirect(url_for('index'))  # Redirige a la página principal

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
def detalle_area(area):
    revistas = sistema.revistas_por_area(area)
    revistas_dict = {
        r.nombre: {
            'h_index': r.h_index,
            'categorias': r.subject_area_category
        } for r in revistas
    }

    return render_template(
        'area_detalle.html',
        area=area,
        revistas=revistas_dict
    )

@app.route('/catalogos')
def catalogos():
    catalogos = sistema.catalogos_disponibles()
    return render_template('catalogos.html', catalogos=catalogos)

@app.route('/catalogo/<catalogo>')
def catalogo_detalle(catalogo):
    revistas = sistema.revistas_por_catalogo(catalogo)
    return render_template('detalle_catalogo.html', catalogo=catalogo, revistas=revistas)


@app.route('/explorar')
def explorar():
    letra = request.args.get('letra', '').upper()
    page = int(request.args.get('page', 1))
    por_pagina = 10  # Número de resultados por página

    # Crear una instancia del sistema
    sistema = SistemaRevistas()

    # Cargar los datos de SCImago en el sistema
    sistema.cargar_json(r'C:\Users\YUGEN\Documents\ProyectoFinalDS42025\datos\json\revistas_scimagojr.json')

    # Obtener todas las revistas (esto asume que 'revistas' ya está cargado)
    todas = list(sistema.revistas.items())  # Convierte dict_items a lista

    # Filtrar revistas por letra (si se pasa una letra en la URL)
    if letra:
        todas = [(k, v) for k, v in todas if k.upper().startswith(letra)]

    # Calcular paginación
    total_paginas = (len(todas) - 1) // por_pagina + 1
    inicio = (page - 1) * por_pagina
    fin = inicio + por_pagina
    revistas_pagina = todas[inicio:fin]

    # Generar lista de letras disponibles para la navegación
    letras = sorted(set(r.nombre[0].upper() for r in sistema.revistas.values() if r.nombre))

    return render_template(
        'explorar.html',
        revistas=revistas_pagina,
        scimagojr=sistema.scimagojr,  # Ahora pasamos el scimagojr correctamente
        page=page,
        total_pages=total_paginas,
        letras=letras,
        letra_actual=letra
    )


@app.route('/creditos')
def creditos():
    return render_template('creditos.html')

@app.route('/revista/<titulo>')
def revista_detalle(titulo):
    # Aquí puedes cargar los detalles de la revista usando el título
    # Por ejemplo, si tienes un diccionario de revistas, puedes buscarla por título
    revista = sistema.revistas.get(titulo)
    if revista:
        return render_template('revista_detalle.html', revista=revista)
    else:
        flash('Revista no encontrada.', 'danger')
        return redirect(url_for('explorar'))

@app.route('/resumen')
def resumen():
    total = len(sistema.revistas)
    promedio = sum(r.h_index for r in sistema.revistas.values()) / total if total > 0 else 0
    return render_template('resumen.html', total=total, promedio=promedio)

if __name__ == '__main__':
    app.run(debug=True)
