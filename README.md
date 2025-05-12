# Catálogo de Revistas Académicas - Universidad de Sonora
## Requerimientos
- **Flask 2.0.0 o superior**: Para gestionar el servidor y las rutas.
- **Bootstrap 1.3.0 o superior**: Para el diseño y la estructura de la interfaz de usuario.
- **Jinja2 2.26.0 o superior**: Para la integración de datos dinámicos en las plantillas HTML.
- **Python 3.12 o superior**: Para la lógica de backend.
- **BeautifulSoup 4.9.3 o superior**: Para la extracción de datos desde páginas web de SCIMAGO.
- **pandas**: Para la manipulación y procesamiento de archivos CSV.

## Integrantes del Equipo
- Fuentes Padilla Aarón Esteban
- Pacheco Olivas Juan Pablo Valentin
- Camargo Loaiza Miguel Ángel
## Estructura del Proyecto
ProyectoFinalDS42025/
├── datos/
│ ├── json/
│ └── csv/
│ ├── areas/
│ └── catalogos/
├── static/
│ ├── css/
│ ├── img/
│ ├── js/
├── Templates/
├── scraper.py
├── revistasjson.py
├── app.py
└── README.md

## Descripción

Búhoteca es una plataforma web creada con **Flask** y **Bootstrap**, diseñada para explorar información sobre revistas científicas. La aplicación permite buscar revistas según su área temática, catálogo de indexación y realizar búsquedas específicas. Además, los datos de las revistas se enriquecen con información proveniente de **SCIMAGOJR**.

Este proyecto consta de tres partes principales para gestionar y visualizar información de revistas académicas:

### Parte 1: Procesamiento de CSV a JSON
*Procesador de datos*: Convierte archivos CSV en un formato JSON estructurado
Objetivo: Leer archivos CSV de áreas y catálogos, y generar un archivo JSON unificado.  
Estructura de entrada:
  Para esta primera parte hice revistajson.py. Este código lee archivos CSV de áreas y catálogos de revistas científicas y genera un archivo JSON con la información organizada por revista. Usa pandas para manejar los datos,   chardet para detectar la codificación de los archivos y unicodedata para normalizar los textos. Primero, carga los archivos CSV de áreas y catálogos, limpia los datos y asigna las áreas y catálogos correspondientes a cada     revista. Luego, guarda la información estructurada en un archivo JSON. El código también maneja distintas codificaciones posibles para asegurar que los archivos CSV se lean correctamente.
  
### Parte 2: Scraper de ScimagoJR
Recolector de datos externos: Extrae información relevante del sitio web Scimago Journal & Country Rank.

Objetivo: Enriquecer los datos con información extraída de SCIMAGOJR, como H-Index, Publisher, ISSN, etc.

El archivo scraper.py se encarga de leer varios archivos CSV que contienen listas de revistas científicas organizadas por áreas y catálogos, y con esa información genera un archivo JSON unificado. Para lograrlo, primero detecta automáticamente la codificación de cada archivo y limpia los nombres para evitar errores. Luego, normaliza los títulos de las revistas para que no haya repeticiones por diferencias de mayúsculas, acentos o espacios. Después, agrupa toda la información en un solo diccionario, asegurándose de que cada revista tenga registradas todas las áreas y catálogos a los que pertenece, sin duplicados. Al final, guarda este diccionario en formato JSON para que pueda usarse fácilmente en otras partes del proyecto, como el scraper web o la aplicación en Flask. Todo esto sucede automáticamente al ejecutar el script.
Cuenta con dos archivos scraper, uno que funciona para almacenar los archivos en un sistema Windows y otro que lo almacena en Ubuntu.

El archivo enriquecido revistas_scimagojr.json se guarda en datos/json/.

### Parte 3: Sitio front-end para consultar las revistas
Interfaz web interactiva: Presenta la información de las revistas de forma clara y accesible para los usuarios.

Objetivo: Permitir a estudiantes e investigadores consultar el catálogo de revistas académicas con filtros y búsqueda por nombre, área o cuartil.
Se creó una aplicación web utilizando el framework Flask junto con Bootstrap para el diseño responsivo. La aplicación carga los datos desde el archivo JSON generado en las fases anteriores y los muestra en una tabla interactiva. Se implementaron funciones para buscar revistas por palabra clave, filtrar por cuartil o área temática, y visualizar detalles relevantes como el ranking y la categoría. La interfaz está pensada para facilitar el acceso a información académica actualizada y confiable.

##Funcionalidades
Inicio
Muestra una introducción al sitio y la fecha de la última actualización. Si los datos no se actualizan hace más de un mes, el sistema pedirá una actualización.

Área
Permite explorar revistas por área temática. Al hacer clic en un área, se muestra una lista de revistas con su H-Index. Los títulos de las revistas son enlaces que llevan a la información detallada.

Catálogos
Permite explorar las revistas por catálogos (como SCOPUS o JCR). Similar a la sección de áreas, muestra revistas y sus respectivos H-Index. Al hacer clic en el catálogo, se muestra una lista con todas las revistas que pertenecen a ese catálogo.

Explorar
Permite navegar alfabéticamente por todas las revistas disponibles. Al seleccionar una letra, se muestran revistas cuyo título empieza con esa letra, junto con sus áreas, catálogos y H-Index.

Búsqueda
Permite buscar revistas por palabras clave. El sistema realiza una búsqueda por coincidencias parciales y muestra los resultados en una tabla con el título de la revista, las áreas, los catálogos y el H-Index.

Créditos
Sección con información sobre los desarrolladores del proyecto y las herramientas utilizadas, incluyendo ChatGPT y GitHub Copilot para optimizar el desarrollo.
   
# Reconocimientos
Este proyecto utilizó GitHub Copilot Y ChatGPT para:

- Asistencia en la estructura del proyecto

- Optimización de consultas de scraping

- Implementación de componentes de Bootstrap 
