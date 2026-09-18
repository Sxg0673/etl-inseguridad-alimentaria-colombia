"""
Modulo de carga al almacen de datos.

1. Verifica que exista la base de datos PostgreSQL configurada y la crea si
    es necesario, conectandose temporalmente a la base administrativa postgres.
2. Crea las tablas del modelo dimensional usando el DDL versionado del
    proyecto.
3. Recibe el diccionario producido por dimensional_model.py, que contiene
    las cinco dimensiones y la tabla de hechos listas para cargar.
4. Limpia las tablas existentes antes de cada ejecucion para permitir cargas
    repetibles durante el desarrollo y evita conflictos con claves anteriores.
5. Carga primero las dimensiones y despues la tabla de hechos, respetando las
    claves foraneas del modelo dimensional.
6. Inserta los DataFrames por lotes y convierte los valores nulos de pandas
    en NULL para que PostgreSQL los almacene correctamente.
7. Ejecuta la carga dentro de una transaccion: si ocurre un error, los cambios
    se revierten y no queda una carga parcial en la base de datos.
"""

from pathlib import Path

import pandas as pd
import psycopg2
from psycopg2 import Error, sql
from psycopg2.extras import execute_values

from config import DB_CONFIG, DB_SERVER_CONFIG

PROJECT_ROOT = Path(__file__).parent.parent
RUTA_DDL = PROJECT_ROOT / 'sql' / 'create_tables.sql'
# El nombre se toma de la configuracion para evitar diferencias entre la
# base que se crea y la base a la que se conecta el pipeline.
DB_NAME = DB_CONFIG['database']

# Las dimensiones deben cargarse antes del hecho porque este tiene claves
# foraneas que apuntan a ellas.
TABLAS_MODELO = [
    'dim_geografia',
    'dim_nivel_ingreso',
    'dim_nivel_severidad_ia',
    'dim_choque_economico',
    'dim_estrategia_afrontamiento',
    'fact_seguridad_alimentaria_hogar',
]



def get_db_connection():
    """Obtiene una conexion a la base de datos del almacen."""
    try:
        return psycopg2.connect(**DB_CONFIG)
    except Error as e:
        print(f"✗ Error de conexión: {e}")
        return None

def create_database_if_not_exists():
    """Crea la base configurada usando la base administrativa de PostgreSQL."""
    connection = None
    cursor = None
    try:
        config = DB_SERVER_CONFIG.copy()
        connection = psycopg2.connect(**config, database="postgres")
        connection.autocommit = True
        cursor = connection.cursor()
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
        if cursor.fetchone() is None:
            cursor.execute(f'CREATE DATABASE "{DB_NAME}"')
            print(f"✓ Base de datos '{DB_NAME}' creada")
        else:
            print(f"✓ Base de datos '{DB_NAME}' lista para usar")
    
    except Error as e:
        print(f"✗ Error al crear la base de datos: {e}")
        raise
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()



def _crear_tablas(cursor):
    """Ejecuta el DDL que define dimensiones, hecho y claves foraneas."""
    cursor.execute(RUTA_DDL.read_text(encoding='utf-8'))


def _cargar_dataframe(cursor, nombre_tabla, df):
    """Inserta un DataFrame completo en PostgreSQL mediante una carga por lote."""
    columnas = list(df.columns)
    filas = [
        tuple(None if pd.isna(valor) else valor for valor in fila)
        for fila in df.itertuples(index=False, name=None)
    ]
    consulta = sql.SQL('INSERT INTO {} ({}) VALUES %s').format(
        sql.Identifier(nombre_tabla),
        sql.SQL(', ').join(sql.Identifier(columna) for columna in columnas),
    )
    execute_values(cursor, consulta.as_string(cursor.connection), filas)


def cargar_modelo(modelo):
    """Crea y carga las dimensiones y el hecho producidos por ``modelar``.

    El orden de ``TABLAS_MODELO`` garantiza que las referencias del hecho
    existan cuando se inserten sus registros.
    """
    tablas_faltantes = set(TABLAS_MODELO) - set(modelo)
    if tablas_faltantes:
        raise ValueError(f'Faltan tablas en el modelo: {sorted(tablas_faltantes)}')

    create_database_if_not_exists()
    conn = get_db_connection()
    if conn is None:
        raise ConnectionError('No fue posible conectar con la base de datos.')

    try:
        with conn:
            with conn.cursor() as cursor:
                _crear_tablas(cursor)
                # Se reinicia el esquema para que cada corrida represente una
                # carga completa y consistente del conjunto de datos.
                for nombre_tabla in TABLAS_MODELO:
                    cursor.execute(
                        sql.SQL('TRUNCATE TABLE {} CASCADE').format(
                            sql.Identifier(nombre_tabla)
                        )
                    )

                for nombre_tabla in TABLAS_MODELO:
                    _cargar_dataframe(cursor, nombre_tabla, modelo[nombre_tabla])
                    print(
                        f'✓ {nombre_tabla} cargada: '
                        f'{len(modelo[nombre_tabla])} registros'
                    )
    except Error as error:
        raise RuntimeError(f'Error al cargar el modelo dimensional: {error}') from error
    finally:
        conn.close()
        