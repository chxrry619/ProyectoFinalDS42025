''' Programa principal de movieDatabase '''
from flask import Flask, render_template, request, redirect, url_for, session, flash
import random
import os
import movie_clases as mc

app = Flask(__name__)
app.secret_key = os.urandom(24) # Clave secreta para sesiones
sistema = mc.SistemaCine()
ruta = 'datos/movies_db - '
actores_csv = ruta + 'actores.csv'
peliculas_csv = ruta + 'peliculas.csv'
relaciones_csv = ruta + 'relacion.csv'
users_csv = ruta + 'users_hashed.csv'
sistema.cargar_csv(actores_csv,mc.Actor)
sistema.cargar_csv(peliculas_csv,mc.Pelicula)
sistema.cargar_csv(relaciones_csv,mc.Relacion)
sistema.cargar_csv(users_csv,mc.User)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/actores')
def actores():
    ''' Muestra la lista de actores '''
    lista_actores = sistema.actores.values()
    return render_template('actores.html', actores=lista_actores)

@app.route('/peliculas')
def peliculas():
    ''' Muestra la lista de peliculas '''
    lista_peliculas = sistema.peliculas.values()
    return render_template('peliculas.html', peliculas=lista_peliculas)

@app.route('/actor/<int:id_actor>')
def actor(id_actor):
    ''' Muestra la información de un actor '''
    actor = sistema.actores[id_actor]
    personajes = sistema.obtener_personajes_por_estrella(id_actor)
    return render_template('actor.html', actor=actor,lista_peliculas=personajes)

@app.route('/pelicula/<int:id_pelicula>')
def pelicula(id_pelicula):
    ''' Muestra la información de una pelicula '''
    pelicula = sistema.peliculas[id_pelicula]
    actores = sistema.obtener_personajes_por_pelicula(id_pelicula)
    return render_template('pelicula.html', pelicula=pelicula, lista_actores=actores)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        exito  = sistema.login(username, password)  
        if exito:
            session['logged_in'] = True
            session['username'] = sistema.usuario_actual.nombre_completo
            flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('index'))
            #return render_template('index.html')
        else:
            flash('Usuario o contraseña incorrectos', 'danger')
            return render_template('login.html')
    return render_template('login.html')

@app.route('/logout')
def logout():
    ''' Cierra la sesión del usuario '''
    session.clear()
    sistema.usuario_actual = None
    flash('Has cerrado sesión correctamente', 'info')
    return redirect(url_for('index'))

@app.route('/agregar_relacion', methods=['GET','POST'])
def agregar_relacion():
    ''' Agrega una relación entre un actor y una película '''
    if sistema.usuario_actual is None:
        flash('Debes iniciar sesión para agregar relaciones', 'warning')
        return redirect(url_for('login'))
    if request.method == 'GET':
        actores_list=[]
        for actor in sistema.actores.values():
            actores_list.append({
                'id_estrella': actor.id_estrella,
                'nombre': actor.nombre
            })
            sorted_actores = sorted(actores_list, key=lambda x: x['nombre'])
        peliculas_list=[]
        for pelicula in sistema.peliculas.values():
            peliculas_list.append({
                'id_pelicula': pelicula.id_pelicula,
                'titulo': pelicula.titulo_pelicula
            })
            sorted_peliculas = sorted(peliculas_list, key=lambda x: x['titulo'])
        return render_template('agregar_relacion.html', actores=sorted_actores, peliculas=sorted_peliculas)
    if request.method == 'POST':
        id_actor = int(request.form['actorSelect'])
        id_pelicula = int(request.form['movieSelect'])
        personaje  = request.form['character']
        sistema.agregar_relacion(id_pelicula, id_actor,personaje)
        sistema.guardar_csv(relaciones_csv,sistema.relaciones)
        flash('Relación agregada correctamente', 'success')
        #return redirect(url_for('index'))
        return redirect(url_for('actor', id_actor=id_actor))
    
@app.route('/agregar_peliculas', methods=['GET','POST'])    
@app.route('/agregar_peliculas', methods=['GET','POST'])
def agregar_pelicula():
    ''' Agrega una película '''
    if sistema.usuario_actual is None:
        flash('Debes iniciar sesión para agregar películas', 'warning')
        return redirect(url_for('login'))
    if request.method == 'GET':
        return render_template('agregar_pelicula.html')
    if request.method == 'POST':
        titulo = request.form.get('titulo')
        fecha_lanzamiento = request.form.get('fecha_lanzamiento')
        url_poster = request.form.get('url_poster')
        sistema.agregar_pelicula(titulo,fecha_lanzamiento,url_poster)
        sistema.guardar_csv(peliculas_csv,sistema.peliculas)
        return redirect(url_for('peliculas'))
    
@app.route('/agregar_actores', methods=['GET','POST'])
@app.route('/agregar_actor', methods=['GET','POST'])  
def agregar_actor():
    ''' Agrega un actor '''
    if sistema.usuario_actual is None:
        flash('Debes iniciar sesión para agregar actores', 'warning')
        return redirect(url_for('login'))
    if request.method == 'GET':
        return render_template('agregar_actor.html')
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        fecha_nacimiento = request.form.get('fecha_nacimiento')
        lugar_nacimiento = request.form.get('lugar_nacimiento')
        url_imagen = request.form.get('url_imagen')
        sistema.agregar_actor(nombre,fecha_nacimiento,lugar_nacimiento,url_imagen)
        sistema.guardar_csv(actores_csv,sistema.actores)
        return redirect(url_for('actores'))  


if __name__ == '__main__':
    app.run(debug=True)
