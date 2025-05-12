# Catálogo de Revistas Académicas - Universidad de Sonora
## Requerimientos
- Flask: 2.0.0 o superior
- pandas_ 1.3.0
- requests: 2.26.0
- beautifulsoup: 4.9.3

## Integrantes del Equipo
- Fuentes Padilla Aarón Esteban
- Pacheco Olivas Juan Pablo Valentin
- Miguel Ángel Camargo Loaiza

## Descripción del Proyecto
Este proyecto consta de tres partes principales para gestionar y visualizar información de revistas académicas:

### Parte 1: Procesamiento de CSV a JSON
**Procesador de datos**: Convierte archivos CSV en un formato JSON estructurado
*Objetivo*: Leer archivos CSV de áreas y catálogos, y generar un archivo JSON unificado.  
*Estructura de entrada*:
  Para esta primera parte hice revistajson.py. Este código lee archivos CSV de áreas y catálogos de revistas científicas y genera un archivo JSON con la información organizada por revista. Usa pandas para manejar los datos,   chardet para detectar la codificación de los archivos y unicodedata para normalizar los textos. Primero, carga los archivos CSV de áreas y catálogos, limpia los datos y asigna las áreas y catálogos correspondientes a cada     revista. Luego, guarda la información estructurada en un archivo JSON. El código también maneja distintas codificaciones posibles para asegurar que los archivos CSV se lean correctamente.

  ### Parte 2: Scraper de scimagojr



   ### Parte 3: Sitio front-end para consultar las revistas
# Reconocimientos
Este proyecto utilizó GitHub Copilot Y ChatGPT para:

- Asistencia en la estructura del proyecto

- Optimización de consultas de scraping

- Implementación de componentes de Bootstrap
