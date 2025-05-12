# Catálogo de Revistas Académicas - Universidad de Sonora
## Requerimientos
- Flask: 2.0.0 o superior
- pandas_ 1.3.0
- requests: 2.26.0
- beautifulsoup: 4.9.3

## Integrantes del Equipo
- Fuentes Padilla Aarón Esteban
@@ -9,5 +14,21 @@
Este proyecto consta de tres partes principales para gestionar y visualizar información de revistas académicas:

### Parte 1: Procesamiento de CSV a JSON
*Procesador de datos*: Convierte archivos CSV en un formato JSON estructurado
Objetivo: Leer archivos CSV de áreas y catálogos, y generar un archivo JSON unificado.  
Estructura de entrada:
  Para esta primera parte hice revistajson.py. Este código lee archivos CSV de áreas y catálogos de revistas científicas y genera un archivo JSON con la información organizada por revista. Usa pandas para manejar los datos,   chardet para detectar la codificación de los archivos y unicodedata para normalizar los textos. Primero, carga los archivos CSV de áreas y catálogos, limpia los datos y asigna las áreas y catálogos correspondientes a cada     revista. Luego, guarda la información estructurada en un archivo JSON. El código también maneja distintas codificaciones posibles para asegurar que los archivos CSV se lean correctamente.
### Parte 2: Scraper de ScimagoJR

Recolector de datos externos: Extrae información relevante del sitio web Scimago Journal & Country Rank.
Objetivo: Obtener el cuartil (Q1, Q2, etc.), categoría temática y ranking de las revistas científicas listadas.
Para esta segunda parte se desarrolló un scraper utilizando requests y BeautifulSoup que accede al sitio de Scimago, realiza búsquedas automatizadas por nombre de revista y extrae datos clave como el cuartil, categoría y posición en el ranking. El código está diseñado para detectar posibles inconsistencias en los nombres y aplicar estrategias de normalización para mejorar la coincidencia con los resultados obtenidos en la web. Los datos extraídos se integran al archivo JSON generado en la Parte 1, enriqueciendo así la información disponible para cada revista.

### Parte 3: Sitio front-end para consultar las revistas
Interfaz web interactiva: Presenta la información de las revistas de forma clara y accesible para los usuarios.
Objetivo: Permitir a estudiantes e investigadores consultar el catálogo de revistas académicas con filtros y búsqueda por nombre, área o cuartil.
Se creó una aplicación web utilizando el framework Flask junto con Bootstrap para el diseño responsivo. La aplicación carga los datos desde el archivo JSON generado en las fases anteriores y los muestra en una tabla interactiva. Se implementaron funciones para buscar revistas por palabra clave, filtrar por cuartil o área temática, y visualizar detalles relevantes como el ranking y la categoría. La interfaz está pensada para facilitar el acceso a información académica actualizada y confiable.
   
# Reconocimientos
Este proyecto utilizó GitHub Copilot Y ChatGPT para:

- Asistencia en la estructura del proyecto

- Optimización de consultas de scraping

- Implementación de componentes de Bootstrap 
