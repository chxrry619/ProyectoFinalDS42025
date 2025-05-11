import csv
from hashlib import sha256

class Publicacion:
    def __init__(self, id_pub, titulo, h_index, area_categoria, editorial, issn, widget, tipo_publicacion, sitio_web):
        self.id_pub = int(id_pub)
        self.titulo = titulo
        self.h_index = int(h_index)
        self.area_categoria = area_categoria
        self.editorial = editorial
        self.issn = issn
        self.widget = widget
        self.tipo_publicacion = tipo_publicacion
        self.sitio_web = sitio_web

    def to_dict(self):
        return {
            'id_pub': self.id_pub,
            'titulo': self.titulo,
            'h_index': self.h_index,
            'area_categoria': self.area_categoria,
            'editorial': self.editorial,
            'issn': self.issn,
            'widget': self.widget,
            'tipo_publicacion': self.tipo_publicacion,
            'sitio_web': self.sitio_web
        }

    def __str__(self):
        return f"{self.titulo} ({self.tipo_publicacion}) - H-Index: {self.h_index}"


class Usuario:
    def __init__(self, username, nombre_completo, email, password):
        self.username = username
        self.nombre_completo = nombre_completo
        self.email = email
        self.password = self.hash_password(password)

    def hash_password(self, password):
        return sha256(password.encode()).hexdigest()

    def to_dict(self):
        return {
            'username': self.username,
            'nombre_completo': self.nombre_completo,
            'email': self.email,
            'password': self.password
        }


class SistemaPublicaciones:
    def __init__(self):
        self.publicaciones = {}
        self.usuarios = {}
        self.usuario_actual = None
        self.idx_pub = 0

    def login(self, username, password):
        """Método para iniciar sesión del usuario"""
        user = self.usuarios.get(username)
        if user and user.password == sha256(password.encode()).hexdigest():
            self.usuario_actual = user
            return True
        return False

    def agregar_usuario(self, username, nombre_completo, email, password):
        """Método para agregar un usuario"""
        if username not in self.usuarios:
            self.usuarios[username] = Usuario(username, nombre_completo, email, password)

    def agregar_publicacion(self, titulo, h_index, area_categoria, editorial, issn, widget, tipo_publicacion, sitio_web):
        """Método para agregar una publicación"""
        if self.usuario_actual:
            new_id = self.idx_pub + 1
            self.idx_pub = new_id
            pub = Publicacion(new_id, titulo, h_index, area_categoria, editorial, issn, widget, tipo_publicacion, sitio_web)
            self.publicaciones[pub.id_pub] = pub

    def buscar_publicaciones_por_titulo(self, titulo_parcial):
        """Método para buscar publicaciones por título"""
        return [p for p in self.publicaciones.values() if titulo_parcial.lower() in p.titulo.lower()]

    def guardar_csv(self, archivo, objetos):
        """Método para guardar objetos en un archivo CSV"""
        if not objetos:
            return
        with open(archivo, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=next(iter(objetos.values())).to_dict().keys())
            writer.writeheader()
            for obj in objetos.values():
                writer.writerow(obj.to_dict())

    def cargar_csv(self, archivo, clase):
        """Método para cargar objetos desde un archivo CSV"""
        with open(archivo, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if clase == Publicacion:
                    pub = Publicacion(**row)
                    self.publicaciones[pub.id_pub] = pub
                elif clase == Usuario:
                    user = Usuario(**row)
                    user.password = user.password  # Ya viene hasheado
                    self.usuarios[user.username] = user
        if clase == Publicacion:
            self.idx_pub = max(self.publicaciones.keys()) if self.publicaciones else 0

# Ejemplo de uso
if __name__ == '__main__':
    sistema = SistemaPublicaciones()
    sistema.agregar_usuario("admin", "Administrador", "admin@uni.edu", "admin123")
    
    exito = sistema.login("admin", "admin123")
    print("Login exitoso:", exito)

    if exito:
        sistema.agregar_publicacion("Libro de Ciencias", 45, "Ciencias Naturales - Biología", "Springer", "1234-5678", "widget123", "Libro", "https://ejemplo.com/libro")
        for pub in sistema.publicaciones.values():
            print(pub)
