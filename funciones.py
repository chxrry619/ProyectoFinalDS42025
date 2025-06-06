import csv
import os
import json
from hashlib import sha256

class Revista:
    def __init__(self, nombre, site, h_index, subject_area_category, publisher, issn, widget, publication_type, url, id_):
        self.nombre = nombre
        self.site = site
        self.h_index = int(h_index) if isinstance(h_index, (int, float, str)) and str(h_index).isdigit() else 0
        self.subject_area_category = subject_area_category
        self.publisher = publisher
        self.issn = issn
        self.widget = widget
        self.publication_type = publication_type
        self.url = url
        self.id = id_
        self.catalogos = []

    def to_dict(self):
        return {
            'nombre': self.nombre,
            'site': self.site,
            'h_index': self.h_index,
            'subject_area_category': self.subject_area_category,
            'publisher': self.publisher,
            'issn': self.issn,
            'widget': self.widget,
            'publication_type': self.publication_type,
            'url': self.url,
            'id': self.id
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
    def __init__(self):
        self.revistas = {}
        self.usuarios = {}
        self.usuario_actual = None
        self.areas_data = {}
        self.catalogos_data = {}
        self.scimagojr = {}

        # Configurar rutas
        base_path = r'C:\Users\YUGEN\Documents\ProyectoFinalDS42025\datos'
        self.cargar_json(os.path.join(base_path, 'json', 'revistas_scimagojr.json'))
        self.cargar_catalogos_desde_csv(os.path.join(base_path, 'csv', 'catalogos'))
        self.cargar_areas_desde_csv(os.path.join(base_path, 'csv', 'areas'))
        RUTA_GUARDADOS = r'C:\Users\YUGEN\Documents\ProyectoFinalDS42025\datos\guardados' 

    def cargar_json(self, ruta_archivo):
        try:
            with open(ruta_archivo, 'r', encoding='utf-8') as file:
                data = json.load(file)
                for nombre, revista_data in data.items():
                    # Aquí incluimos los nuevos campos
                    revista = Revista(
                        nombre=nombre,
                        site=revista_data['site'],
                        h_index=revista_data['h_index'],
                        subject_area_category=revista_data['subject_area_category'],
                        publisher=revista_data.get('publisher', 'Desconocido'),
                        issn=revista_data.get('issn', 'Desconocido'),
                        widget=revista_data.get('widget', 'Desconocido'),
                        publication_type=revista_data.get('publication_type', 'Desconocido'),
                        url=revista_data.get('url', 'Desconocido'),
                        id_=revista_data.get('id', 'Desconocido')
                    )
                    self.revistas[nombre.lower()] = revista
            print(f"Revistas cargadas: {len(self.revistas)}")
        except Exception as e:
            print(f"Error cargando JSON: {e}")
            
            

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

        for filename in os.listdir(carpeta_areas):
            if filename in mapeo_nombres:
                area_nombre = mapeo_nombres[filename]
                ruta = os.path.join(carpeta_areas, filename)
                try:
                    with open(ruta, 'r', encoding='latin1') as f:
                        lector = csv.DictReader(f)
                        revistas_area = []
                        for fila in lector:
                            # Obtener nombre de la revista con manejo de columnas alternativas
                            nombre = fila.get('TITULO:') or fila.get('Título') or fila.get('Title') or "Desconocido"
                            nombre_limpio = nombre.strip().lower()
                            

                            revista = self.revistas.get(nombre_limpio)
                            h_index = revista.h_index if revista else 0
                            
                            revistas_area.append({
                                'nombre': revista.nombre if revista else nombre,
                                'h_index': h_index
                            })
                        self.areas_data[area_nombre] = revistas_area
                    print(f"Área cargada: {area_nombre} ({len(revistas_area)} revistas)")
                except Exception as e:
                    print(f"Error cargando área {area_nombre}: {e}")


    def cargar_catalogos_desde_csv(self, carpeta_catalogos):
        mapeo_catalogos = {
            'CONACYT_RadGridExport.csv': 'CONACYT',
            'JCR_RadGridExport.csv': 'JCR',
            'MLA_RadGridExport.csv': 'MLA',
            'SCIELO_RadGridExport.csv': 'SciELO',
            'SCOPUS_RadGridExport.csv': 'Scopus'
        }

        for filename in os.listdir(carpeta_catalogos):
            if filename in mapeo_catalogos:
                catalogo_nombre = mapeo_catalogos[filename]
                ruta = os.path.join(carpeta_catalogos, filename)
                try:
                    with open(ruta, 'r', encoding='latin1') as f:
                        lector = csv.DictReader(f)
                        registros = []
                        for fila in lector:
                            nombre = fila.get('Nombre de la revista') or \
                                     fila.get('TITULO:') or \
                                     fila.get('Revista') or \
                                     fila.get('Title') or \
                                     "Desconocido"
                            registros.append({
                                'nombre': nombre.strip(),
                                'h_index': int(fila.get('H-Index', 0)) if fila.get('H-Index', '0').isdigit() else 0
                            })
                        self.catalogos_data[catalogo_nombre] = registros
                    print(f"Catálogo cargado: {catalogo_nombre} ({len(registros)} revistas)")
                except Exception as e:
                    print(f"Error cargando catálogo {catalogo_nombre}: {e}")

    def get_revista(self, titulo):
        """Devuelve los detalles completos de una revista por su nombre."""
        return self.revistas.get(titulo.lower())

    def revistas_por_area(self, area):
        return sorted(
            self.areas_data.get(area, []),
            key=lambda x: x['h_index'],
            reverse=True
        )
    
    def guardar_revista(usuario, revista):
        ruta_archivo = os.path.join(RUTA_GUARDADOS, f"{usuario}.json")
    
        # Cargar datos previos
        if os.path.exists(ruta_archivo):
            with open(ruta_archivo, "r", encoding="utf-8") as f:
                guardadas = json.load(f)
        else:
            guardadas = []

        # Evitar duplicados
        if revista not in guardadas:
            guardadas.append(revista)
            with open(ruta_archivo, "w", encoding="utf-8") as f:
                json.dump(guardadas, f, indent=4, ensure_ascii=False)
            return True
        return False

    def revistas_por_catalogo(self, catalogo):
        """Obtiene las revistas asociadas a un catálogo específico con su h_index y área."""
        if catalogo in self.catalogos_data:
            revistas = []
            for revista_data in self.catalogos_data[catalogo]:
                nombre = revista_data['nombre'].strip().lower()
                # Buscar la revista completa en el diccionario de revistas
                revista_completa = self.revistas.get(nombre)
                if revista_completa:
                    # Obtener el h_index y área si se encuentra la revista completa
                    revistas.append({
                        'nombre': revista_completa.nombre,
                        'h_index': revista_completa.h_index,
                        'subject_area_category': revista_completa.subject_area_category
                    })
                else:
                    # Si no se encuentra la revista, solo mostrar nombre y h_index
                    revistas.append({
                        'nombre': revista_data['nombre'],
                        'h_index': revista_data['h_index'],
                        'subject_area_category': "Desconocida"
                    })
            return revistas
        return []  # Retorna una lista vacía si el catálogo no existe

    def catalogos_disponibles(self):
        return list(self.catalogos_data.keys())

    def areas_disponibles(self):
        return list(self.areas_data.keys())

    def login(self, username, password):
        usuario = self.usuarios.get(username)
        if usuario and usuario.password == sha256(password.encode()).hexdigest():
            self.usuario_actual = usuario
            return True
        return False
    
    def cargar_usuarios_desde_csv(self, ruta_archivo):
        """Cargar usuarios desde un archivo CSV."""
        try:
            with open(ruta_archivo, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    username = row['username']
                    nombre_completo = row['nombre_completo']
                    email = row['email']
                    password = row['password']
                    # Almacenar los usuarios en un diccionario (o en otro formato según lo necesites)
                    self.usuarios[username] = Usuario(username, nombre_completo, email, password)
            print("Usuarios cargados correctamente.")
        except FileNotFoundError:
            print(f"Error: El archivo {ruta_archivo} no se encuentra.")
        except Exception as e:
            print(f"Error al cargar el archivo CSV: {e}")

    def top_revistas_por_indice(self, top_n=10):
        return sorted(
            self.revistas.values(),
            key=lambda r: r.h_index,
            reverse=True
        )[:top_n]

    def exportar_json(self, archivo_salida='revistas_actualizadas.json'):
        data = {r.nombre: r.to_dict() for r in self.revistas.values()}
        with open(archivo_salida, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Datos exportados a {archivo_salida}")

# Ejemplo de uso
if __name__ == "__main__":
    sistema = SistemaRevistas()
    print("Áreas disponibles:", sistema.areas_disponibles())
    print("Top 10 revistas:", [str(r) for r in sistema.top_revistas_por_indice(10)])
