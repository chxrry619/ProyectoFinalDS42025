''' Clases del sistema de películas, actores y actrices'''
import csv
from hashlib import sha256
from datetime import datetime

class Actor:
    ''' Clase Actor'''
    def __init__(self,id_estrella,nombre,fecha_nacimiento,ciudad_nacimiento,url_imagen,username):
        self.id_estrella       = int(id_estrella)
        self.nombre            = nombre
        self.fecha_nacimiento  = datetime.strptime(fecha_nacimiento, '%Y-%m-%d')
        self.ciudad_nacimiento = ciudad_nacimiento
        self.url_imagen        = url_imagen
        self.username          = username
    
    def to_dict(self):
        ''' Retorna un diccionario con los atributos del objeto'''
        return {
            'id_estrella': self.id_estrella,
            'nombre': self.nombre,
            'fecha_nacimiento': self.fecha_nacimiento.strftime('%Y-%m-%d'),
            'ciudad_nacimiento': self.ciudad_nacimiento,
            'url_imagen': self.url_imagen,
            'username': self.username
        }
    def __str__(self):
        ''' Método para imprimir el objeto Actor'''
        return self.nombre
    
class Pelicula:
    ''' Clase Película'''
    def __init__(self, id_pelicula,titulo_pelicula,fecha_lanzamiento,url_poster):
        ''' Constructor de la clase Película'''
        self.id_pelicula       = int(id_pelicula)
        self.titulo_pelicula   = titulo_pelicula
        self.fecha_lanzamiento = datetime.strptime(fecha_lanzamiento, '%Y-%m-%d')
        self.url_poster        = url_poster
    
    def to_dict(self):
        ''' Retorna un diccionario con los atributos del objeto Película'''
        return {
            'id_pelicula': self.id_pelicula,
            'titulo_pelicula': self.titulo_pelicula,
            'fecha_lanzamiento': self.fecha_lanzamiento.strftime('%Y-%m-%d'),
            'url_poster': self.url_poster
        }
    def __str__(self):
        ''' Método para imprimir el objeto Película'''
        return f'{self.titulo_pelicula} ({self.fecha_lanzamiento.year})'
    
class Relacion:
    ''' Clase Relación: Relación entre actores y películas'''
    def __init__(self,id_relacion,id_pelicula,id_estrella, personaje):
        ''' Constructor de la clase Relación'''
        self.id_relacion = int(id_relacion)
        self.id_pelicula = int(id_pelicula)  
        self.id_estrella = int(id_estrella)
        self.personaje   = personaje
    
    def to_dict(self):
        ''' Retorna un diccionario con los atributos del objeto Relación'''
        return {
            'id_relacion': self.id_relacion,
            'id_pelicula': self.id_pelicula,
            'id_estrella': self.id_estrella,
            'personaje'  : self.personaje
        }

class User:
    ''' Clase User: Usuario del sistema'''
    def __init__(self,username,nombre_completo,email,password):
        ''' Constructor de la clase User'''
        self.username = username
        self.nombre_completo = nombre_completo
        self.email = email
        self.password = password
    
    def hash_password(self,password):
        ''' Método para encriptar la contraseña'''
        return sha256(password.encode()).hexdigest()
    
    def to_dict(self):
        ''' Retorna un diccionario con los atributos del objeto User'''
        return {
            'username': self.username,
            'nombre_completo': self.nombre_completo,
            'email': self.email,
            'password': self.password
        }
    
class SistemaCine:
    ''' Clase SistemaCine: Sistema de películas'''
    def __init__(self):
        ''' Constructor de la clase SistemaCine'''
        self.actores = {}
        self.peliculas = {}
        self.relaciones = {}
        self.usuarios = {}
        self.usuario_actual = None
        self.idx_actor = 0
        self.idx_pelicula = 0
        self.idx_relacion = 0
    
    def cargar_csv(self, archivo, clase):
        ''' Método para cargar datos desde un archivo CSV'''
        print(f"Cargando datos desde {archivo}")
        with open(archivo, mode='r', encoding='utf8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if clase == Actor:
                    actor = Actor(**row)
                    self.actores[actor.id_estrella] = actor
                elif clase == Pelicula:
                    pelicula = Pelicula(**row)
                    self.peliculas[pelicula.id_pelicula] = pelicula
                elif clase == Relacion:
                    print(row)
                    relacion = Relacion(**row)
                    self.relaciones[relacion.id_relacion] = relacion
                elif clase == User:
                    user = User(**row)
                    self.usuarios[user.username] = user
        if clase == Actor:
            self.idx_actor = max(self.actores.keys()) if self.actores else 0
        elif clase == Pelicula:
            self.idx_pelicula = max(self.peliculas.keys()) if self.peliculas else 0
        elif clase == Relacion:
            self.idx_relacion = max(self.relaciones.keys()) if self.relaciones else 0

    def guardar_csv(self, archivo, objetos):
        if not objetos:
            return
        with open(archivo, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=next(iter(objetos.values())).to_dict().keys())
            writer.writeheader()
            for obj in objetos.values():
                writer.writerow(obj.to_dict())

    def obtener_peliculas_por_actor(self, id_estrella):
        ''' Método para obtener las películas de un actor'''
        ids_peliculas = [relacion.id_pelicula for relacion in self.relaciones.values() if relacion.id_estrella == id_estrella]
        return [self.peliculas[id_pelicula] for id_pelicula in ids_peliculas] 

    def obtener_actores_por_pelicula(self, id_pelicula):
        ''' Método para obtener los actores de una película'''
        ids_actores = [relacion.id_estrella for relacion in self.relaciones.values() if relacion.id_pelicula == id_pelicula]
        return [self.actores[id_estrella] for id_estrella in ids_actores]

    def login(self, username, password):
        user = self.usuarios.get(username)
        if user and user.password == user.hash_password(password):
            self.usuario_actual = user
            return True
        return False

    def agregar_actor(self, nombre, fecha_nacimiento, ciudad_nacimiento, url_imagen):
        if self.usuario_actual:
            new_id = self.idx_actor + 1
            self.idx_actor = new_id
            actor = Actor(new_id, nombre, fecha_nacimiento, ciudad_nacimiento, url_imagen, self.usuario_actual.username)
            self.actores[actor.id_estrella] = actor

    def agregar_pelicula(self, titulo_pelicula, fecha_lanzamiento, url_poster):
        if self.usuario_actual:
            new_id = self.idx_pelicula + 1
            self.idx_pelicula = new_id
            pelicula = Pelicula(new_id, titulo_pelicula, fecha_lanzamiento, url_poster)
            self.peliculas[pelicula.id_pelicula] = pelicula
    
    def agregar_relacion(self, id_pelicula, id_estrella,personaje):
        if self.usuario_actual:
            new_id = self.idx_relacion + 1
            self.idx_relacion = new_id
            relacion = Relacion(new_id, id_pelicula, id_estrella,personaje)
            self.relaciones[relacion.id_relacion] = relacion
    
    def agregar_usuario(self, username, nombre_completo, email, password):
        if self.usuario_actual:
            if username not in self.usuarios:
                user = User(username, nombre_completo, email, password)
                user.password = user.hash_password(user.password)
                self.usuarios[user.username] = user
    def buscar_peliculas_por_titulo(self, titulo_parcial):
        return [pelicula for pelicula in self.peliculas.values() if titulo_parcial.lower() in pelicula.titulo_pelicula.lower()]
    
    def buscar_actores_por_nombre(self, nombre_parcial):
        return [actor for actor in self.actores.values() if nombre_parcial.lower() in actor.nombre.lower()]
    
    def obtener_personajes_por_estrella(self, id_estrella):
        personajes = []
        for rel in self.relaciones.values():
            if rel.id_estrella == id_estrella:
                pelicula = self.peliculas.get(rel.id_pelicula)
                if pelicula:
                    personajes.append({"personaje": rel.personaje, "pelicula": pelicula})
        return personajes
    
    def obtener_personajes_por_pelicula(self, id_pelicula):
        ''' Método para obtener los personajes de una película'''
        actores = []
        for rel in self.relaciones.values():
            if rel.id_pelicula == id_pelicula:
                actor = self.actores.get(rel.id_estrella)
                if actor:
                    actores.append({"personaje": rel.personaje,"actor":actor})
        return actores
    
if __name__ == '__main__':
    sistema = SistemaCine()
    archivo_actores = 'datos/movies_db - actores.csv'
    archivo_peliculas = 'datos/movies_db - peliculas.csv'
    archivo_relaciones = 'datos/movies_db - relacion.csv'
    archivo_usuarios = 'datos/movies_db - users_hashed.csv'
    sistema.cargar_csv(archivo_actores, Actor)
    sistema.cargar_csv(archivo_peliculas, Pelicula)
    sistema.cargar_csv(archivo_relaciones, Relacion)
    sistema.cargar_csv(archivo_usuarios, User)
    lista_peliculas = sistema.obtener_peliculas_por_actor(1)
    for pelicula in lista_peliculas:
        print(f"{pelicula.id_pelicula}:{pelicula.titulo_pelicula} ({pelicula.fecha_lanzamiento.year})")
    #print(sistema.actores)
    #print(sistema.peliculas)
    #print(sistema.relaciones)
    #print(sistema.usuarios)
    print("---------------------")
    lista_actores = sistema.obtener_actores_por_pelicula(1)
    for actor in lista_actores:
        print(f"{actor.id_estrella}:{actor.nombre} ({actor.fecha_nacimiento.year})")
    print("---------------------")
    #for u in sistema.usuarios.values():
    #    u.password = u.hash_password(u.password)
    #archivo_hashed = 'datos/movies_db - users_hashed.csv'
    #sistema.guardar_csv(archivo_hashed, sistema.usuarios)
    #print(f"Archivo {archivo_hashed} guardado")
    #
    #
    u = sistema.usuarios['fcirettg']
    print(u.username)
    print(u.nombre_completo)
    exito = sistema.login('fcirettg','12345')
    print(exito)
    if exito:
        #sistema.agregar_usuario('messi10','Lionel Messi','messi@gmail.com','12345')
        #sistema.guardar_csv(archivo_usuarios, sistema.usuarios)
        #print(f"Usuario agregado")
        sistema.agregar_relacion(69,36,'Rita')
        sistema.guardar_csv(archivo_relaciones, sistema.relaciones)
        print(f"Relación agregada")
    print("-----------------")
    pelis = sistema.buscar_peliculas_por_titulo('star')
    for p in pelis:
        print(p)
    print("-----------------")
    actores = sistema.buscar_actores_por_nombre('ar')
    for a in actores:
        print(a)
    print("-----------------")
    personajes = sistema.obtener_personajes_por_estrella(4)
    for p in personajes:
        print(f"{p['personaje']} - {p['pelicula']}")
    print("Listo!")