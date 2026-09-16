"""
Modulo de limpieza de datos.

1. Elimina columnas contenedoras vacias, que no contienen datos en si mismas.
2. Normaliza P1_DEPARTAMENTO a 2 digitos (estandar DIVIPOLA).
3. Marca (sin eliminar) los hogares con inconsistencia en PERCAPITA:
   PERCAPITA en cero con I_HOGAR positivo, detectado durante el
   perfilamiento (3 casos sobre 87060 hogares).
"""

import pandas as pd

# Columnas contenedoras de bateria, sin ningun dato en si mismas.
# La informacion vive exclusivamente en sus columnas hijas (ej. P8520S3, P8520S5).
COLUMNAS_VACIAS_VIVIENDA = ['P8520', 'P4065', 'P5661', 'P3157']

COLUMNAS_VACIAS_SERVICIOS_HOGAR = ['P1892', 'P5046S1', 'P5012', 'P3169', 'P3172', 'P3174']

COLUMNAS_VACIAS_CONDICIONES_VIDA = ['P9025', 'P3180', 'P9005', 'P784', 'P1072', 'P1077',
                                     'P795', 'P1913', 'P3202', 'P3203', 'P3516']


def limpiar_vivienda(df_vivienda):
    """
    Limpia la tabla de vivienda:
    - Elimina columnas contenedoras vacias.
    - Normaliza P1_DEPARTAMENTO a 2 digitos (estandar DIVIPOLA).
    """
    df = df_vivienda.drop(columns=COLUMNAS_VACIAS_VIVIENDA)
    df['P1_DEPARTAMENTO'] = df['P1_DEPARTAMENTO'].str.zfill(2)
    return df


def limpiar_servicios_hogar(df_servicios_hogar):
    """
    Limpia la tabla de servicios del hogar:
    - Elimina columnas contenedoras vacias.
    - Marca los hogares con inconsistencia en PERCAPITA:
      PERCAPITA en cero con I_HOGAR positivo, detectado durante el
      perfilamiento (3 casos sobre 87060 hogares).
    """
    df = df_servicios_hogar.drop(columns=COLUMNAS_VACIAS_SERVICIOS_HOGAR)

    percapita = pd.to_numeric(df['PERCAPITA'].str.replace(',', '.'), errors='coerce')
    i_hogar = pd.to_numeric(df['I_HOGAR'].str.replace(',', '.'), errors='coerce')

    df['ingreso_percapita_inconsistente'] = (percapita == 0) & (i_hogar != 0)

    return df


def limpiar_condiciones_vida(df_condiciones_vida):
    """
    Limpia la tabla de condiciones de vida:
    - Elimina columnas contenedoras vacias.
    """
    df = df_condiciones_vida.drop(columns=COLUMNAS_VACIAS_CONDICIONES_VIDA)
    return df