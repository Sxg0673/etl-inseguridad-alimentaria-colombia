"""
Modulo de extraccion de datos.

1. Lee los archivos CSV descargados del portal DANE, con los parametros de separador, codificacion y tipo de datos validados durante el perfilamiento.
"""

import pandas as pd

# Rutas de los archivos fuente. Los nombres incluyen espacios porque asi
# se descargan del portal DANE, y se dejan intactos para mantener trazabilidad
# directa con la fuente.
RUTA_VIVIENDA = 'data/raw/Datos de la vivienda.csv'
RUTA_SERVICIOS_HOGAR = 'data/raw/Servicios del hogar.csv'
RUTA_CONDICIONES_VIDA = 'data/raw/Condiciones de vida del hogar y tenencia de bienes.csv'


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