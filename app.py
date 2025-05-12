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
    # Lógica para la vista de Catálogos
    return render_template('catalogos.html')

@app.route('/explorar')
def explorar():
    # Intentar cargar las revistas desde el archivo JSON
    scimagojr = sistema.cargar_json(r'C:\Users\YUGEN\Documents\ProyectoFinalDS42025\datos\json\revistas_scimagojr.json')
    
    if scimagojr is None:
        # Manejar el caso en que el archivo no se carga correctamente
        return "Error al cargar los datos de las revistas."

    # Asignar las revistas al valor cargado
    revistas = scimagojr
    
    if not revistas:
        # Si no hay revistas en el archivo JSON
        return "No se encontraron revistas en el archivo JSON."

    # Paginación de las revistas
    page = request.args.get('page', 1, type=int)
    items_per_page = 10  # Número de revistas por página
    total_pages = len(revistas) // items_per_page + (1 if len(revistas) % items_per_page > 0 else 0)
    
    # Obtener las revistas correspondientes a la página actual
    revistas_paginadas = revistas[(page - 1) * items_per_page : page * items_per_page]

    # Pasar los datos a la plantilla
    return render_template('explorar.html', revistas=revistas_paginadas, page=page, total_pages=total_pages, scimagojr=scimagojr)

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
