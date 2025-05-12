from flask import Flask, render_template, request, redirect, url_for, session, flash
from funciones import SistemaRevistas
import os
import csv
import json
from functools import wraps


app = Flask(__name__)
app.secret_key = 'clave_secreta_super_segura'

# Inicializar sistema
sistema = SistemaRevistas()
sistema.cargar_usuarios_desde_csv(r'C:\Users\YUGEN\Documents\ProyectoFinalDS42025\datos\csv\users\users.csv')
sistema.cargar_areas_desde_csv(r'C:\Users\YUGEN\Documents\ProyectoFinalDS42025\datos\csv\areas')
sistema.cargar_catalogos_desde_csv(r'C:\Users\YUGEN\Documents\ProyectoFinalDS42025\datos\csv\catalogos')
sistema.cargar_json(r'C:\Users\YUGEN\Documents\ProyectoFinalDS42025\datos\json\revistas_scimagojr.json')



def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function





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

@app.route("/buscar", methods=["GET", "POST"])
@login_required
def buscar():
    resultados = []
    if request.method == "POST":
        termino = request.form.get("termino", "").lower()
        if termino:
            for nombre_revista, revista in sistema.revistas.items():
                if termino in nombre_revista:
                    # Buscar catálogos en los que está
                    catalogos = []
                    for nombre_catalogo, revistas in sistema.catalogos_data.items():
                        if any(r['nombre'].strip().lower() == nombre_revista for r in revistas):
                            catalogos.append(nombre_catalogo)

                    # Buscar áreas en las que está
                    areas = []
                    for nombre_area, revistas in sistema.areas_data.items():
                        if any(r['nombre'].strip().lower() == nombre_revista for r in revistas):
                            areas.append(nombre_area)

                    resultados.append({
                        "nombre": revista.nombre,
                        "h_index": revista.h_index,
                        "catalogos": catalogos,
                        "areas": areas
                    })
    return render_template("buscar.html", resultados=resultados)

@app.route('/top')
def top():
    revistas_top = sistema.top_revistas_por_indice(10)
    return render_template('top.html', revistas=revistas_top)

@app.route('/area', methods=['GET', 'POST'])
@login_required
def area():
    revistas_area = []
    if request.method == 'POST':
        area = request.form['area']
        revistas_area = sistema.revistas_por_area(area)
    return render_template('area.html', revistas=revistas_area)

@app.route('/areas')
@login_required
def listar_areas():
    areas = sistema.areas_disponibles()
    return render_template('areas.html', areas=areas)


@app.route('/area/<area>')
@login_required
def area_detalle(area):
    revistas = sistema.revistas_por_area(area)
    return render_template('area_detalle.html', area=area, revistas=revistas)
    

@app.route('/catalogos')
@login_required
def catalogos():
    catalogos = sistema.catalogos_disponibles()
    return render_template('catalogos.html', catalogos=catalogos)

@app.route('/catalogo/<catalogo>')
@login_required
def catalogo_detalle(catalogo):
    revistas = sistema.revistas_por_catalogo(catalogo)  # Ahora debería funcionar
    return render_template('catalogo_detalle.html', catalogo=catalogo, revistas=revistas)


@app.route('/explorar')
@login_required
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

    # Filtrar por área usando los nombres mapeados
    if area_filtro:
        nombres_area = {revista['nombre'].strip().lower() for revista in sistema.areas_data.get(area_filtro, [])}
        todas_revistas = [r for r in todas_revistas if r.nombre.strip().lower() in nombres_area]

    # Paginación (versión corregida)
    total_paginas = (len(todas_revistas) - 1) // por_pagina + 1
    inicio = (page - 1) * por_pagina
    fin = inicio + por_pagina
    revistas_pagina = todas_revistas[inicio:fin]

    # Crear diccionario con datos enriquecidos
    revistas_dict = {}
    for revista in revistas_pagina:
        # Buscar áreas mapeadas
        areas_revista = [
            nombre_area for nombre_area, revistas_area in sistema.areas_data.items()
            if any(revista.nombre.lower() == r['nombre'].strip().lower() for r in revistas_area)
        ]
        
        # Buscar catálogos
        catalogos_revista = [
            nombre_cat for nombre_cat, revistas_cat in sistema.catalogos_data.items()
            if any(revista.nombre.lower() == r['nombre'].strip().lower() for r in revistas_cat)
        ]

        # Obtener h_index (versión corregida con paréntesis)
        nombre_normalizado = revista.nombre.strip().lower()
        h_index = next(
            (info.get('h_index') for nombre, info in sistema.scimagojr.items()
            if nombre.strip().lower() == nombre_normalizado
        ), revista.h_index)

        revistas_dict[revista.nombre] = {
            'h_index': h_index,
            'catalogos': catalogos_revista,
            'areas': areas_revista
        }

    # Obtener letras y áreas disponibles
    letras = sorted({r.nombre[0].upper() for r in sistema.revistas.values() if r.nombre})
    areas_disponibles = sorted(sistema.areas_data.keys())

    return render_template(
        'explorar.html',
        revistas=revistas_dict.items(),
        scimagojr=sistema.scimagojr,
        letras=letras,
        letra_actual=letra,
        areas=areas_disponibles,
        area_actual=area_filtro,
        page=page,
        total_pages=total_paginas
    )
    
@app.route('/creditos')
def creditos():
    return render_template('creditos.html')

@app.route('/revista/<titulo>')
def revista_detalle(titulo):
    # Obtener la revista por su nombre (asegurándote de que el título está en el formato correcto)
    revista = sistema.revistas.get(titulo)
    
    # Si no se encuentra la revista, redirigir o mostrar un error
    if not revista:
        flash('Revista no encontrada', 'danger')
        return redirect(url_for('index'))
    
    # Mostrar la plantilla con los detalles de la revista
    return render_template('revista_detalle.html', revista=revista)

@app.route('/resumen')
def resumen():
    total = len(sistema.revistas)
    promedio = sum(r.h_index for r in sistema.revistas.values()) / total if total > 0 else 0
    return render_template('resumen.html', total=total, promedio=promedio)

@app.route('/guardados')
def creditos():
    if 'usuario' not in session:
        flash("Debes iniciar sesión para ver tus revistas guardadas.")
        return redirect(url_for('login'))

    usuario = session['usuario']
    ruta_archivo = os.path.join(RUTA_GUARDADOS, f"{usuario}.json")
    if os.path.exists(ruta_archivo):
        with open(ruta_archivo, "r", encoding="utf-8") as f:
            revistas = json.load(f)
    else:
        revistas = []

    return render_template("guardados.html", revistas=revistas)


@app.route('/guardar/<titulo>')
def guardar(titulo):
    if 'usuario' not in session:
        flash("Debes iniciar sesión para guardar revistas.")
        return redirect(url_for('login'))
    
    usuario = session['usuario']
    exito = guardar_revista(usuario, titulo)
    if exito:
        flash(f"Revista '{titulo}' guardada correctamente.")
    else:
        flash(f"La revista '{titulo}' ya estaba guardada.")
    return redirect(url_for('revista_detalle', titulo=titulo))

if __name__ == '__main__':
    app.run(debug=True)
