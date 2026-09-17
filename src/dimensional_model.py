"""
Modulo de modelado dimensional.

1. Recibe la tabla transformada y devuelve un diccionario con las 5 dimensiones y la tabla de hechos, listas para cargar en el Data Warehouse.
2. Construye las dimensiones de geografia, nivel de ingreso, severidad de inseguridad alimentaria, choques economicos y estrategias de afrontamiento.
3. Construye la tabla de hechos cruzando la tabla transformada contra cada dimension para obtener sus llaves foraneas. DIRECTORIO y ORDEN se conservan junto a id_hogar como llave natural de trazabilidad hacia el archivo original del DANE; no forman parte del modelo analitico en el diagrama, pero si existen en la base de datos.
4. Las dimensiones de choques y estrategias son junk
"""

import pandas as pd

# Las 11 banderas de choque economico, en el mismo orden en que las produce
# transform.py.
COLUMNAS_CHOQUE = [
    'choque_jefe_perdio_empleo',
    'choque_conyuge_perdio_empleo',
    'choque_otro_miembro_perdio_empleo',
    'choque_cierre_negocio',
    'choque_no_vendio_produccion',
    'choque_atraso_jardin_colegio',
    'choque_no_pago_universidad',
    'choque_atraso_vivienda',
    'choque_atraso_administracion',
    'choque_atraso_servicios_publicos',
    'choque_atraso_impuestos',
]

# Las 14 banderas de estrategia de afrontamiento.
COLUMNAS_ESTRATEGIA = [
    'estrategia_empezaron_a_trabajar',
    'estrategia_nuevas_fuentes_ingreso',
    'estrategia_vivir_con_familiares',
    'estrategia_gastaron_ahorros',
    'estrategia_se_endeudaron',
    'estrategia_vendieron_bienes',
    'estrategia_vendieron_vivienda',
    'estrategia_retiro_escolar',
    'estrategia_retiro_universidad',
    'estrategia_disminuyeron_gasto_alimentos',
    'estrategia_ayuda_gobierno',
    'estrategia_ayuda_familiares_amigos',
    'estrategia_subsidio_desempleo',
    'estrategia_otra',
]

# Orden logico fijo de los quintiles, independiente del orden en que
# aparezcan en los datos.
ORDEN_QUINTILES = ['Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Dato inconsistente']

NOMBRES_QUINTILES = {
    'Q1': 'Q1 - 20% de hogares con menor ingreso per capita',
    'Q2': 'Q2',
    'Q3': 'Q3',
    'Q4': 'Q4',
    'Q5': 'Q5 - 20% de hogares con mayor ingreso per capita',
    'Dato inconsistente': 'Dato inconsistente - excluido del analisis de ingreso',
}

# Orden logico fijo de los niveles de severidad, con los umbrales del
# puntaje FIES crudo (0 a 8) segun la clasificacion estandar de FAO.
# Fuente: FAO, "The Food Insecurity Experience Scale: Development of a
# Global Standard", Voices of the Hungry, Technical Paper v1.1.
NIVELES_SEVERIDAD = [
    {'nombre_severidad': 'Seguridad alimentaria', 'puntaje_fies_minimo': 0, 'puntaje_fies_maximo': 0},
    {'nombre_severidad': 'Inseguridad leve', 'puntaje_fies_minimo': 1, 'puntaje_fies_maximo': 3},
    {'nombre_severidad': 'Inseguridad moderada', 'puntaje_fies_minimo': 4, 'puntaje_fies_maximo': 6},
    {'nombre_severidad': 'Inseguridad grave', 'puntaje_fies_minimo': 7, 'puntaje_fies_maximo': 8},
    {'nombre_severidad': 'Sin dato', 'puntaje_fies_minimo': None, 'puntaje_fies_maximo': None},
]


def _construir_dim_geografia(df):
    """
    Extrae las combinaciones unicas de departamento, region y clase.
    El grano es departamento + clase, no solo departamento, porque Bogota
    tiene region distinta segun sea cabecera o rural (validado durante el
    diseno del modelo).
    """
    columnas = ['P1_DEPARTAMENTO', 'nombre_departamento', 'REGION',
                'nombre_region', 'CLASE', 'nombre_clase']

    dim = df[columnas].drop_duplicates().reset_index(drop=True)
    dim.insert(0, 'id_geografia', range(1, len(dim) + 1))

    dim = dim.rename(columns={
        'P1_DEPARTAMENTO': 'codigo_departamento',
        'REGION': 'codigo_region',
        'CLASE': 'codigo_clase',
    })

    return dim


def _construir_dim_nivel_ingreso():
    """
    Construye la dimension de quintiles con un orden logico fijo, no con
    el orden en que las categorias aparezcan en los datos.
    """
    dim = pd.DataFrame({'codigo_quintil': ORDEN_QUINTILES})
    dim['nombre_quintil'] = dim['codigo_quintil'].map(NOMBRES_QUINTILES)
    dim.insert(0, 'id_nivel_ingreso', range(1, len(dim) + 1))

    return dim


def _construir_dim_nivel_severidad_ia():
    """
    Construye la dimension de severidad con los umbrales oficiales FAO
    como atributos descriptivos.
    """
    dim = pd.DataFrame(NIVELES_SEVERIDAD)
    dim.insert(0, 'id_nivel_severidad_ia', range(1, len(dim) + 1))

    return dim


def _construir_dim_choque_economico(df):
    """
    Junk dimension de choques economicos: una fila por cada combinacion de
    las 11 banderas que realmente ocurre en los datos, sin generar el
    producto cartesiano teorico completo.
    """
    dim = df[COLUMNAS_CHOQUE].drop_duplicates().reset_index(drop=True)
    dim.insert(0, 'id_choque_economico', range(1, len(dim) + 1))
    dim['numero_choques'] = dim[COLUMNAS_CHOQUE].sum(axis=1)

    return dim


def _construir_dim_estrategia_afrontamiento(df):
    """
    Junk dimension de estrategias de afrontamiento: mismo criterio que
    dim_choque_economico, solo combinaciones reales.
    """
    dim = df[COLUMNAS_ESTRATEGIA].drop_duplicates().reset_index(drop=True)
    dim.insert(0, 'id_estrategia_afrontamiento', range(1, len(dim) + 1))
    dim['numero_estrategias'] = dim[COLUMNAS_ESTRATEGIA].sum(axis=1)

    return dim


def _construir_hecho(df, dim_geografia, dim_nivel_ingreso, dim_nivel_severidad_ia,
                      dim_choque_economico, dim_estrategia_afrontamiento):
    """
    Construye la tabla de hechos cruzando la tabla transformada contra cada
    dimension para obtener sus llaves foraneas. DIRECTORIO y ORDEN se
    conservan junto a id_hogar como llave natural de trazabilidad hacia el
    archivo original del DANE; no forman parte del modelo analitico en el
    diagrama, pero si existen en la base de datos.
    """
    columnas_geografia_dim = ['id_geografia', 'codigo_departamento', 'codigo_region', 'codigo_clase']
    geografia_para_unir = dim_geografia[columnas_geografia_dim].rename(columns={
        'codigo_departamento': 'P1_DEPARTAMENTO',
        'codigo_region': 'REGION',
        'codigo_clase': 'CLASE',
    })

    hecho = df.merge(
        geografia_para_unir,
        on=['P1_DEPARTAMENTO', 'REGION', 'CLASE'],
        how='left'
    )

    hecho = hecho.merge(
        dim_nivel_ingreso[['id_nivel_ingreso', 'codigo_quintil']]
        .rename(columns={'codigo_quintil': 'quintil_ingreso'}),
        on='quintil_ingreso',
        how='left'
    )

    hecho = hecho.merge(
        dim_nivel_severidad_ia[['id_nivel_severidad_ia', 'nombre_severidad']]
        .rename(columns={'nombre_severidad': 'nivel_severidad_ia'}),
        on='nivel_severidad_ia',
        how='left'
    )

    hecho = hecho.merge(
        dim_choque_economico[['id_choque_economico'] + COLUMNAS_CHOQUE],
        on=COLUMNAS_CHOQUE,
        how='left'
    )

    hecho = hecho.merge(
        dim_estrategia_afrontamiento[['id_estrategia_afrontamiento'] + COLUMNAS_ESTRATEGIA],
        on=COLUMNAS_ESTRATEGIA,
        how='left'
    )

    hecho.insert(0, 'id_hogar', range(1, len(hecho) + 1))

    columnas_finales = [
        'id_hogar', 'DIRECTORIO', 'ORDEN',
        'id_geografia', 'id_nivel_ingreso', 'id_nivel_severidad_ia',
        'id_choque_economico', 'id_estrategia_afrontamiento',
        'tiene_acueducto', 'tiene_alcantarillado',
        'factor_expansion', 'prob_ia_moderada_grave', 'prob_ia_grave',
    ]

    return hecho[columnas_finales]


def modelar(df_transformado):
    """
    Punto de entrada del modulo. Recibe la tabla preparada por transform.py
    y devuelve un diccionario con las 5 dimensiones y la tabla de hechos,
    listas para cargar en el Data Warehouse.
    """
    dim_geografia = _construir_dim_geografia(df_transformado)
    dim_nivel_ingreso = _construir_dim_nivel_ingreso()
    dim_nivel_severidad_ia = _construir_dim_nivel_severidad_ia()
    dim_choque_economico = _construir_dim_choque_economico(df_transformado)
    dim_estrategia_afrontamiento = _construir_dim_estrategia_afrontamiento(df_transformado)

    fact_seguridad_alimentaria_hogar = _construir_hecho(
        df_transformado, dim_geografia, dim_nivel_ingreso, dim_nivel_severidad_ia,
        dim_choque_economico, dim_estrategia_afrontamiento
    )

    return {
        'dim_geografia': dim_geografia,
        'dim_nivel_ingreso': dim_nivel_ingreso,
        'dim_nivel_severidad_ia': dim_nivel_severidad_ia,
        'dim_choque_economico': dim_choque_economico,
        'dim_estrategia_afrontamiento': dim_estrategia_afrontamiento,
        'fact_seguridad_alimentaria_hogar': fact_seguridad_alimentaria_hogar,
    }
