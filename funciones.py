import csv
import os
import json
from hashlib import sha256

class Revista:
    def __init__(self, nombre, site, h_index, subject_area_category):
        self.nombre = nombre
        self.site = site
        self.h_index = int(h_index) if isinstance(h_index, (int, float)) else 0
        self.subject_area_category = subject_area_category
        self.catalogos = []  # Si lo necesitas más adelante

    def to_dict(self):
        return {
            'nombre': self.nombre,
            'site': self.site,
            'h_index': self.h_index,
            'subject_area_category': self.subject_area_category
        }

    def __str__(self):
        return f"{self.nombre} ({self.h_index})"


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


class SistemaRevistas:
    def __init__(self, ruta_json=None):
        self.revistas = {}
        self.usuarios = {}
        self.usuario_actual = None
        self.areas_data = {}  # Nuevo: para guardar revistas por área
        self.scimagojr_data = {}  # Esto debe cargarse externamente
        if ruta_json:
            self.cargar_json(ruta_json)

    def cargar_json(self, ruta_archivo):
        try:
            with open(ruta_archivo, mode='r', encoding='latin1') as file:
                data = json.load(file)
                for nombre, revista_data in data.items():
                    revista = Revista(
                        nombre=nombre,
                        site=revista_data['site'],
                        h_index=revista_data['h_index'],
                        subject_area_category=revista_data['subject_area_category']
                    )
                    self.revistas[nombre.lower()] = revista
            print("Revistas cargadas correctamente.")
        except FileNotFoundError:
            print(f"Error: El archivo {ruta_archivo} no se encuentra.")
        except json.JSONDecodeError:
            print("Error al decodificar el archivo JSON.")
        except Exception as e:
            print(f"Error al cargar el archivo JSON: {e}")

    def guardar_json(self, ruta_archivo):
        with open(ruta_archivo, 'w', encoding='latin1') as f:
            json.dump({r.nombre: r.to_dict() for r in self.revistas.values()}, f, indent=2, ensure_ascii=False)

    def cargar_usuarios_desde_csv(self, ruta_archivo):
        try:
            with open(ruta_archivo, mode='r', encoding='latin1') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    username = row['username']
                    self.usuarios[username] = Usuario(
                        username, row['nombre_completo'], row['email'], row['password']
                    )
            print("Usuarios cargados correctamente.")
        except FileNotFoundError:
            print(f"Error: El archivo {ruta_archivo} no se encuentra.")
        except Exception as e:
            print(f"Error al cargar el archivo CSV: {e}")

    def login(self, username, password):
        usuario = self.usuarios.get(username)
        if usuario and usuario.password == sha256(password.encode()).hexdigest():
            self.usuario_actual = usuario
            return True
        return False

    def agregar_usuario(self, username, nombre_completo, email, password):
        if username not in self.usuarios:
            self.usuarios[username] = Usuario(username, nombre_completo, email, password)

    def agregar_revista(self, nombre, site, h_index, subject_area_category):
        if self.usuario_actual:
            self.revistas[nombre.lower()] = Revista(nombre, site, h_index, subject_area_category)


    def cargar_areas_desde_csv(self, carpeta_areas):
        mapeo_nombres = {
            'CIENCIAS_BIO RadGridExport.csv': 'Ciencias Biológicas',
            'CIENCIAS_ECO RadGridExport.csv': 'Ciencias Económicas',
            'CIENCIAS_EXA RadGridExport.csv': 'Ciencias Exactas',
            'CIENCIAS_SOC RadGridExport.csv': 'Ciencias Sociales',
            'ED_INST RadGridExport.csv': 'Educación Institucional',
            'ED_LIB RadGridExport.csv': 'Educación Libre',
            'HUMAN_Y_ART RadGridExport.csv': 'Humanidades y Artes',
            'ING RadGridExport.csv': 'Ingeniería',
            'MULTI RadGridExport.csv': 'Multidisciplinario'
        }

        self.areas_data = {}
        for filename in os.listdir(carpeta_areas):
            if filename.endswith(".csv") and filename in mapeo_nombres:
                area_nombre = mapeo_nombres[filename]
                ruta = os.path.join(carpeta_areas, filename)
                with open(ruta, encoding='latin1') as f:
                    lector = csv.DictReader(f)
                    self.areas_data[area_nombre] = [fila for fila in lector]

    def buscar_revistas_por_nombre(self, fragmento):
        return [r for r in self.revistas.values() if fragmento.lower() in r.nombre.lower()]

    def revistas_por_area(self, nombre_area):
        return self.areas_data.get(nombre_area, [])

    def areas_disponibles(self):
        return list(self.areas_data.keys())

    def top_revistas_por_indice(self, top_n=10):
        return sorted(self.revistas.values(), key=lambda r: r.h_index, reverse=True)[:top_n]

    def revistas_por_hindex_minimo(self, minimo):
        return [r for r in self.revistas.values() if r.h_index >= minimo]

    def ordenar_revistas_por_hindex(self, descendente=True):
        return sorted(self.revistas.values(), key=lambda r: r.h_index, reverse=descendente)

    def top_revistas_por_area(self, area, limite=10):
        filtradas = self.revistas_por_area(area)
        return sorted(filtradas, key=lambda r: r.h_index, reverse=True)[:limite]

    def exportar_json(self, archivo_salida='revistas_exportadas.json'):
        data = {r.nombre: r.to_dict() for r in self.revistas.values()}
        with open(archivo_salida, 'w', encoding='latin1') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Revistas exportadas a {archivo_salida}")

    def resumen_general(self):
        total = len(self.revistas)
        promedio_hindex = sum(r.h_index for r in self.revistas.values()) / total if total > 0 else 0
        print(f"Total de revistas: {total}")
        print(f"H-Index promedio: {promedio_hindex:.2f}")
