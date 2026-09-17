"""
Modulo de transformacion.

1. Recibe las tres tablas limpias y devuelve una tabla unica a nivel hogar, con las reglas de negocio aplicadas y las variables derivadas listas para el modelo dimensional.
2. Traduce los codigos geograficos a sus nombres de negocio, usando el diccionario del DANE y la tabla de referencia DIVIPOLA.
3. Convierte a booleano las variables binarias, respetando que la encuesta usa dos codificaciones distintas: servicios publicos (1 = Si, 2 = No) y choques/estrategias (1 = marcado, vacio = no marcado).
4. Calcula el puntaje FIES crudo (0 a 8) y lo clasifica segun los cortes estandar FAO / DANE. Si el hogar respondio "no sabe / no informa" (codigo 3) en alguna de las 8 preguntas, el puntaje no es calculable y se clasifica como sin dato.
5. Asigna cada hogar a un quintil de ingreso per capita, ponderado por el factor de expansion. Los hogares con PERCAPITA inconsistente quedan fuera del calculo de los cortes y en una categoria aparte, para que no distorsionen los limites de los quintiles ni aparezcan como el 20% mas pobre siendo un error del dato.
6. Convierte a numerico las medidas base, que vienen con coma como separador decimal, que es el formato de exportacion del DANE.
7. Deja solo las columnas de negocio. Las variables crudas del DANE ya cumplieron su funcion como insumo y no continuan en el pipeline. DIRECTORIO y ORDEN se conservan como llave natural para trazabilidad hacia el archivo original; dimensional_model.py las reemplaza por la llave subrogada.
"""

import re
from pathlib import Path

import pandas as pd

RAIZ_PROYECTO = Path(__file__).resolve().parent.parent

RUTA_DICCIONARIO = RAIZ_PROYECTO / 'data' / 'reference' / 'Plantilla_Diccionario_Datos.csv'
RUTA_DIVIPOLA = RAIZ_PROYECTO / 'data' / 'reference' / 'divipola_departamentos.csv'

# Los dominios del diccionario vienen como texto con formato "1. Etiqueta",
# una opcion por linea. Este patron extrae el codigo y su etiqueta.
PATRON_DOMINIO = re.compile(r'^\s*(\d+)\s*\.\s*(.+?)\s*$')

# Columnas a seleccionar de cada tabla. Solo lo que alimenta los 5
# requerimientos: nada mas entra al pipeline.
# P8520S5 (acueducto) y P8520S3 (alcantarillado) pertenecen a la tabla de
# vivienda, verificado durante el perfilamiento previo a clean.py.
COLUMNAS_VIVIENDA = ['DIRECTORIO', 'P1_DEPARTAMENTO', 'REGION', 'CLASE',
                     'P8520S5', 'P8520S3']

COLUMNAS_SERVICIOS_HOGAR = ['DIRECTORIO', 'ORDEN', 'PERCAPITA',
                            'ingreso_percapita_inconsistente']

# Los 11 tipos de choque economico (R3). Se excluye P3202S12 porque es
# "Ninguno de las anteriores", que se deduce de la ausencia de los demas.
CHOQUES = {
    'P3202S1': 'choque_jefe_perdio_empleo',
    'P3202S2': 'choque_conyuge_perdio_empleo',
    'P3202S3': 'choque_otro_miembro_perdio_empleo',
    'P3202S4': 'choque_cierre_negocio',
    'P3202S5': 'choque_no_vendio_produccion',
    'P3202S6': 'choque_atraso_jardin_colegio',
    'P3202S7': 'choque_no_pago_universidad',
    'P3202S8': 'choque_atraso_vivienda',
    'P3202S9': 'choque_atraso_administracion',
    'P3202S10': 'choque_atraso_servicios_publicos',
    'P3202S11': 'choque_atraso_impuestos',
}

# Las 14 estrategias de afrontamiento (R4).
ESTRATEGIAS = {
    'P3203S1': 'estrategia_empezaron_a_trabajar',
    'P3203S2': 'estrategia_nuevas_fuentes_ingreso',
    'P3203S3': 'estrategia_vivir_con_familiares',
    'P3203S4': 'estrategia_gastaron_ahorros',
    'P3203S5': 'estrategia_se_endeudaron',
    'P3203S6': 'estrategia_vendieron_bienes',
    'P3203S7': 'estrategia_vendieron_vivienda',
    'P3203S8': 'estrategia_retiro_escolar',
    'P3203S9': 'estrategia_retiro_universidad',
    'P3203S10': 'estrategia_disminuyeron_gasto_alimentos',
    'P3203S11': 'estrategia_ayuda_gobierno',
    'P3203S12': 'estrategia_ayuda_familiares_amigos',
    'P3203S13': 'estrategia_subsidio_desempleo',
    'P3203S14': 'estrategia_otra',
}

# Las 8 preguntas de la escala FIES. Son insumo para calcular el puntaje
# crudo y no se conservan en la tabla final.
COLUMNAS_FIES = [f'P3516S{i}' for i in range(1, 9)]

# Etiquetas de las categorias derivadas.
SEVERIDAD_SIN_DATO = 'Sin dato'
QUINTIL_INCONSISTENTE = 'Dato inconsistente'


def _cargar_diccionario():
    """Carga el diccionario de datos del DANE como tabla de consulta."""
    return pd.read_csv(RUTA_DICCIONARIO, sep=';', dtype=str, encoding='utf-8-sig')


def _extraer_mapeo(df_diccionario, nombre_variable):
    """
    Extrae el mapeo codigo -> etiqueta de una variable, parseando la columna
    de dominios del diccionario. Evita escribir los mapeos a mano en el codigo.
    """
    fila = df_diccionario[
        df_diccionario['Nombre de la variable o la columna'] == nombre_variable
    ]
    texto_dominio = str(fila.iloc[0]['Dominios (categorías, valores permitidos)'])

    mapeo = {}
    for linea in texto_dominio.split('\n'):
        coincidencia = PATRON_DOMINIO.match(linea)
        if coincidencia:
            mapeo[coincidencia.group(1)] = coincidencia.group(2)
    return mapeo


def _cargar_mapeo_departamentos():
    """
    Carga los nombres de departamento desde la tabla de referencia DIVIPOLA.
    El diccionario del DANE no incluye estos nombres, solo indica que el
    codigo corresponde a DIVIPOLA.
    """
    divipola = pd.read_csv(RUTA_DIVIPOLA, dtype=str)
    return dict(zip(divipola['Código Departamento'], divipola['Nombre Departamento']))


def _seleccionar_e_integrar(df_vivienda, df_servicios_hogar, df_condiciones_vida):
    """
    Selecciona de cada tabla solo las columnas necesarias y las integra.
    Llaves validadas durante el perfilamiento: las tablas a nivel hogar se
    unen por DIRECTORIO + ORDEN, y la de vivienda por DIRECTORIO.
    """
    columnas_condiciones = (
        ['DIRECTORIO', 'ORDEN']
        + list(CHOQUES.keys())
        + list(ESTRATEGIAS.keys())
        + COLUMNAS_FIES
        + ['FEX_C', 'PROB_IAMG', 'PROB_IAG']
    )

    df = df_condiciones_vida[columnas_condiciones].merge(
        df_servicios_hogar[COLUMNAS_SERVICIOS_HOGAR],
        on=['DIRECTORIO', 'ORDEN'],
        how='left'
    )

    df = df.merge(
        df_vivienda[COLUMNAS_VIVIENDA],
        on='DIRECTORIO',
        how='left'
    )

    return df


def _decodificar_geografia(df, df_diccionario):
    """
    Traduce los codigos geograficos a sus nombres de negocio.
    Region y clase salen del diccionario del DANE; el nombre del
    departamento sale de la tabla de referencia DIVIPOLA.
    """
    mapeo_region = _extraer_mapeo(df_diccionario, 'REGION')
    mapeo_clase = _extraer_mapeo(df_diccionario, 'Clase')
    mapeo_departamento = _cargar_mapeo_departamentos()

    df['nombre_region'] = df['REGION'].map(mapeo_region)
    df['nombre_clase'] = df['CLASE'].map(mapeo_clase)
    df['nombre_departamento'] = df['P1_DEPARTAMENTO'].map(mapeo_departamento)

    return df


def _convertir_banderas(df):
    """
    Convierte a booleano las variables binarias, respetando que la encuesta
    usa dos codificaciones distintas:
    - Servicios publicos: 1 = Si, 2 = No (respuesta explicita).
    - Choques y estrategias: 1 = marcado, vacio = no marcado (seleccion
      multiple, donde el vacio no es un dato faltante).
    """
    df['tiene_acueducto'] = df['P8520S5'] == '1'
    df['tiene_alcantarillado'] = df['P8520S3'] == '1'

    for columna_origen, nombre_destino in CHOQUES.items():
        df[nombre_destino] = df[columna_origen] == '1'

    for columna_origen, nombre_destino in ESTRATEGIAS.items():
        df[nombre_destino] = df[columna_origen] == '1'

    return df


def _calcular_severidad_ia(df, df_diccionario):
    """
    Calcula el puntaje FIES crudo (0 a 8) contando respuestas afirmativas y
    lo clasifica segun los cortes estandar FAO / DANE.

    Si el hogar respondio "no sabe / no informa" (codigo 3) en alguna de las
    8 preguntas, el puntaje no es calculable y se clasifica como sin dato.
    Esto reproduce el criterio del DANE, que deja PROB_IAMG nulo en esos
    mismos hogares.
    """
    respuestas = df[COLUMNAS_FIES]

    tiene_no_informa = (respuestas == '3').any(axis=1)
    puntaje = (respuestas == '1').sum(axis=1).where(~tiene_no_informa)

    def clasificar(valor):
        if pd.isna(valor):
            return SEVERIDAD_SIN_DATO
        if valor == 0:
            return 'Seguridad alimentaria'
        if valor <= 3:
            return 'Inseguridad leve'
        if valor <= 6:
            return 'Inseguridad moderada'
        return 'Inseguridad grave'

    df['nivel_severidad_ia'] = puntaje.map(clasificar)

    return df


def _calcular_quintil_ingreso(df):
    """
    Asigna cada hogar a un quintil de ingreso per capita, ponderado por el
    factor de expansion. El corte se hace sobre la poblacion expandida y no
    sobre la muestra, de modo que cada quintil represente al 20% de los
    hogares del pais.

    Los hogares con PERCAPITA inconsistente, detectados en clean.py, quedan
    fuera del calculo de los cortes y en una categoria aparte, para que no
    distorsionen los limites de los quintiles ni aparezcan como el 20% mas
    pobre siendo un error del dato.
    """
    percapita = pd.to_numeric(df['PERCAPITA'].str.replace(',', '.'), errors='coerce')
    factor = pd.to_numeric(df['FEX_C'].str.replace(',', '.'), errors='coerce')

    es_valido = ~df['ingreso_percapita_inconsistente']

    quintil = pd.Series(QUINTIL_INCONSISTENTE, index=df.index)

    ordenados = pd.DataFrame({
        'percapita': percapita[es_valido],
        'factor': factor[es_valido],
    }).sort_values('percapita')

    proporcion_acumulada = ordenados['factor'].cumsum() / ordenados['factor'].sum()

    etiquetas = pd.cut(
        proporcion_acumulada,
        bins=[0, 0.2, 0.4, 0.6, 0.8, 1.0],
        labels=['Q1', 'Q2', 'Q3', 'Q4', 'Q5'],
        include_lowest=True
    )

    quintil.loc[etiquetas.index] = etiquetas.astype(str)
    df['quintil_ingreso'] = quintil

    return df


def _convertir_medidas(df):
    """
    Convierte a numerico las medidas base. Vienen con coma como separador
    decimal, que es el formato de exportacion del DANE.
    """
    df['factor_expansion'] = pd.to_numeric(
        df['FEX_C'].str.replace(',', '.'), errors='coerce')
    df['prob_ia_moderada_grave'] = pd.to_numeric(
        df['PROB_IAMG'].str.replace(',', '.'), errors='coerce')
    df['prob_ia_grave'] = pd.to_numeric(
        df['PROB_IAG'].str.replace(',', '.'), errors='coerce')

    return df


def _seleccionar_columnas_finales(df):
    """
    Deja solo las columnas de negocio. Las variables crudas del DANE ya
    cumplieron su funcion como insumo y no continuan en el pipeline.

    DIRECTORIO y ORDEN se conservan como llave natural para trazabilidad
    hacia el archivo original; dimensional_model.py las reemplaza por la
    llave subrogada.
    """
    columnas_finales = (
        ['DIRECTORIO', 'ORDEN']
        + ['P1_DEPARTAMENTO', 'nombre_departamento', 'REGION', 'nombre_region',
           'CLASE', 'nombre_clase']
        + ['tiene_acueducto', 'tiene_alcantarillado']
        + list(CHOQUES.values())
        + list(ESTRATEGIAS.values())
        + ['nivel_severidad_ia', 'quintil_ingreso']
        + ['factor_expansion', 'prob_ia_moderada_grave', 'prob_ia_grave']
    )

    return df[columnas_finales]


def transformar(df_vivienda, df_servicios_hogar, df_condiciones_vida):
    """
    Punto de entrada del modulo. Recibe las tres tablas ya limpias y devuelve
    una tabla unica a nivel hogar, con las reglas de negocio aplicadas y las
    variables derivadas listas para el modelo dimensional.
    """
    df_diccionario = _cargar_diccionario()

    df = _seleccionar_e_integrar(df_vivienda, df_servicios_hogar, df_condiciones_vida)
    df = _decodificar_geografia(df, df_diccionario)
    df = _convertir_banderas(df)
    df = _calcular_severidad_ia(df, df_diccionario)
    df = _calcular_quintil_ingreso(df)
    df = _convertir_medidas(df)
    df = _seleccionar_columnas_finales(df)

    return df
