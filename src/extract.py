"""
Modulo de extraccion de datos crudos.

Responsabilidad unica: leer los archivos fuente de la ECV 2025 sin aplicar
ninguna transformacion, limpieza o regla de negocio. Los datos se devuelven
exactamente como vienen en el archivo original, con todas las columnas
como texto para no perder ceros a la izquierda en los codigos.
"""

from pathlib import Path

import pandas as pd

# Raiz del proyecto, calculada desde la ubicacion de este archivo. Esto
# hace que las rutas funcionen sin importar desde donde se ejecute el
# codigo (notebook, main.py, o cualquier otro punto de entrada).
RAIZ_PROYECTO = Path(__file__).resolve().parent.parent

# Rutas de los archivos fuente. Los nombres incluyen espacios porque asi
# se descargan del portal DANE, y se dejan intactos para mantener trazabilidad
# directa con la fuente.
RUTA_VIVIENDA = RAIZ_PROYECTO / 'data' / 'raw' / 'Datos de la vivienda.csv'
RUTA_SERVICIOS_HOGAR = RAIZ_PROYECTO / 'data' / 'raw' / 'Servicios del hogar.csv'
RUTA_CONDICIONES_VIDA = RAIZ_PROYECTO / 'data' / 'raw' / 'Condiciones de vida del hogar y tenencia de bienes.csv'


def leer_csv_crudo(ruta):
    """
    Lee un archivo CSV de la ECV 2025 con los parametros validados durante
    el perfilamiento: separador punto y coma, todas las columnas como texto,
    y codificacion utf-8 con BOM.
    """
    return pd.read_csv(ruta, sep=';', dtype=str, encoding='utf-8-sig')


def extraer_vivienda():
    """Lee la tabla de datos de la vivienda (nivel: vivienda, llave: DIRECTORIO)."""
    return leer_csv_crudo(RUTA_VIVIENDA)


def extraer_servicios_hogar():
    """Lee la tabla de servicios del hogar (nivel: hogar, llave: DIRECTORIO + ORDEN)."""
    return leer_csv_crudo(RUTA_SERVICIOS_HOGAR)


def extraer_condiciones_vida():
    """Lee la tabla de condiciones de vida (nivel: hogar, llave: DIRECTORIO + ORDEN)."""
    return leer_csv_crudo(RUTA_CONDICIONES_VIDA)
