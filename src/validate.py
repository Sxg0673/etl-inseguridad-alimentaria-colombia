"""
Modulo de validacion.

1. Recibe el modelo dimensional completo y la tabla transformada de la que se origino, y corre las 8 verificaciones de integridad. Lanza una excepcion en la primera que falle.
2. Verifica que ningun merge del modelado haya generado filas de mas (fan-out).
3. Verifica que la llave subrogada de cada dimension sea unica y sin nulos
4. Verifica que las banderas booleanas de R2 (acueducto, alcantarillado) nunca queden en nulo. Las banderas de choque y estrategia viven en las dimensiones, no en el hecho, y se validan aparte.
5. Verifica que los nulos de prob_ia_moderada_grave coincidan exactamente, fila por fila,
"""

TOLERANCIA_RECONCILIACION_DANE = 0.1
PREVALENCIA_OFICIAL_DANE = 21.1

COLUMNAS_CHOQUE = [
    'choque_jefe_perdio_empleo', 'choque_conyuge_perdio_empleo',
    'choque_otro_miembro_perdio_empleo', 'choque_cierre_negocio',
    'choque_no_vendio_produccion', 'choque_atraso_jardin_colegio',
    'choque_no_pago_universidad', 'choque_atraso_vivienda',
    'choque_atraso_administracion', 'choque_atraso_servicios_publicos',
    'choque_atraso_impuestos',
]

COLUMNAS_ESTRATEGIA = [
    'estrategia_empezaron_a_trabajar', 'estrategia_nuevas_fuentes_ingreso',
    'estrategia_vivir_con_familiares', 'estrategia_gastaron_ahorros',
    'estrategia_se_endeudaron', 'estrategia_vendieron_bienes',
    'estrategia_vendieron_vivienda', 'estrategia_retiro_escolar',
    'estrategia_retiro_universidad', 'estrategia_disminuyeron_gasto_alimentos',
    'estrategia_ayuda_gobierno', 'estrategia_ayuda_familiares_amigos',
    'estrategia_subsidio_desempleo', 'estrategia_otra',
]

QUINTILES_ESPERADOS = {'Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Dato inconsistente'}
SEVERIDADES_ESPERADAS = {'Seguridad alimentaria', 'Inseguridad leve',
                          'Inseguridad moderada', 'Inseguridad grave', 'Sin dato'}


def _validar_sin_fan_out(fact, df_transformado):
    """
    Verifica que ningun merge del modelado haya generado filas de mas.
    El hecho debe tener exactamente una fila por cada fila de la tabla
    transformada, ni una mas ni una menos.
    """
    if len(fact) != len(df_transformado):
        raise ValueError(
            f'El hecho tiene {len(fact)} filas, se esperaban {len(df_transformado)}. '
            f'Algun merge probablemente genero un fan-out por llaves duplicadas '
            f'en una dimension.'
        )

    if fact['id_hogar'].duplicated().any():
        raise ValueError('id_hogar tiene valores duplicados en el hecho.')

    if fact.duplicated(subset=['directorio', 'orden']).any():
        raise ValueError('La llave natural (directorio, orden) tiene duplicados en el hecho.')

    print('OK - Sin fan-out: el hecho tiene', len(fact), 'filas, sin duplicados de llave.')


def _validar_llaves_dimensiones(modelo):
    """
    Verifica que la llave subrogada de cada dimension sea unica y sin nulos.
    """
    llaves_por_dimension = {
        'dim_geografia': 'id_geografia',
        'dim_nivel_ingreso': 'id_nivel_ingreso',
        'dim_nivel_severidad_ia': 'id_nivel_severidad_ia',
        'dim_choque_economico': 'id_choque_economico',
        'dim_estrategia_afrontamiento': 'id_estrategia_afrontamiento',
    }

    for nombre_tabla, nombre_llave in llaves_por_dimension.items():
        dim = modelo[nombre_tabla]

        if dim[nombre_llave].isna().any():
            raise ValueError(f'{nombre_llave} tiene nulos en {nombre_tabla}.')

        if dim[nombre_llave].duplicated().any():
            raise ValueError(f'{nombre_llave} tiene duplicados en {nombre_tabla}.')

    print('OK - Las 5 llaves subrogadas de las dimensiones son unicas y sin nulos.')


def _validar_banderas_sin_nulos(fact):
    """
    Verifica que las banderas booleanas de R2 (acueducto, alcantarillado)
    nunca queden en nulo. Las banderas de choque y estrategia viven en las
    dimensiones, no en el hecho, y se validan aparte.
    """
    for columna in ['tiene_acueducto', 'tiene_alcantarillado']:
        if fact[columna].isna().any():
            raise ValueError(f'La bandera {columna} tiene valores nulos en el hecho.')

    print('OK - Las banderas booleanas de R2 no tienen nulos.')


def _validar_banderas_dimensiones_sin_nulos(modelo):
    """
    Verifica que las banderas de choque y estrategia, dentro de sus propias
    dimensiones, tampoco tengan nulos.
    """
    for columna in COLUMNAS_CHOQUE:
        if modelo['dim_choque_economico'][columna].isna().any():
            raise ValueError(f'La bandera {columna} tiene nulos en dim_choque_economico.')

    for columna in COLUMNAS_ESTRATEGIA:
        if modelo['dim_estrategia_afrontamiento'][columna].isna().any():
            raise ValueError(f'La bandera {columna} tiene nulos en dim_estrategia_afrontamiento.')

    print('OK - Las banderas de choque y estrategia no tienen nulos en sus dimensiones.')


def _validar_consistencia_sin_dato(fact, modelo):
    """
    Verifica que los nulos de prob_ia_moderada_grave coincidan exactamente,
    fila por fila, con los hogares clasificados como severidad Sin dato.
    """
    con_severidad = fact.merge(
        modelo['dim_nivel_severidad_ia'][['id_nivel_severidad_ia', 'nombre_severidad']],
        on='id_nivel_severidad_ia',
        how='left'
    )

    es_sin_dato = con_severidad['nombre_severidad'] == 'Sin dato'
    es_nulo = con_severidad['prob_ia_moderada_grave'].isna()

    if not (es_sin_dato == es_nulo).all():
        raise ValueError(
            'Los nulos de prob_ia_moderada_grave no coinciden exactamente '
            'con los hogares clasificados como Sin dato.'
        )

    print(f'OK - Consistencia Sin dato verificada: {es_sin_dato.sum()} hogares.')


def _validar_dominios(modelo):
    """
    Verifica que las dimensiones de ingreso y severidad tengan exactamente
    las categorias esperadas, ni de mas ni de menos.
    """
    quintiles_reales = set(modelo['dim_nivel_ingreso']['codigo_quintil'])
    if quintiles_reales != QUINTILES_ESPERADOS:
        raise ValueError(
            f'dim_nivel_ingreso tiene categorias inesperadas. '
            f'Esperado: {QUINTILES_ESPERADOS}, encontrado: {quintiles_reales}'
        )

    severidades_reales = set(modelo['dim_nivel_severidad_ia']['nombre_severidad'])
    if severidades_reales != SEVERIDADES_ESPERADAS:
        raise ValueError(
            f'dim_nivel_severidad_ia tiene categorias inesperadas. '
            f'Esperado: {SEVERIDADES_ESPERADAS}, encontrado: {severidades_reales}'
        )

    print('OK - Los dominios de ingreso y severidad son exactamente los esperados.')


def _validar_regla_choque_estrategia(fact, modelo):
    """
    Verifica la regla de negocio: un hogar sin ningun choque debe tener
    tambien cero estrategias, y viceversa. Confirmado durante el
    perfilamiento: la pregunta de estrategias esta condicionada a haber
    reportado algun choque.
    """
    con_choque = fact.merge(
        modelo['dim_choque_economico'][['id_choque_economico', 'numero_choques']],
        on='id_choque_economico', how='left'
    )
    con_estrategia = con_choque.merge(
        modelo['dim_estrategia_afrontamiento'][['id_estrategia_afrontamiento', 'numero_estrategias']],
        on='id_estrategia_afrontamiento', how='left'
    )

    sin_choque = con_estrategia['numero_choques'] == 0
    sin_estrategia = con_estrategia['numero_estrategias'] == 0

    if not (sin_choque == sin_estrategia).all():
        raise ValueError(
            'La regla de negocio choque-estrategia no se cumple: hay hogares '
            'sin choque con alguna estrategia marcada, o viceversa.'
        )

    print(f'OK - Regla choque-estrategia consistente: {sin_choque.sum()} hogares sin ninguno de los dos.')


def _validar_conteos_banderas(modelo):
    """
    Verifica que numero_choques y numero_estrategias coincidan con la suma
    real de sus propias banderas en cada fila de la dimension.
    """
    dim_choque = modelo['dim_choque_economico']
    suma_real = dim_choque[COLUMNAS_CHOQUE].sum(axis=1)
    if not (dim_choque['numero_choques'] == suma_real).all():
        raise ValueError('numero_choques no coincide con la suma real de banderas en dim_choque_economico.')

    dim_estrategia = modelo['dim_estrategia_afrontamiento']
    suma_real = dim_estrategia[COLUMNAS_ESTRATEGIA].sum(axis=1)
    if not (dim_estrategia['numero_estrategias'] == suma_real).all():
        raise ValueError('numero_estrategias no coincide con la suma real de banderas en dim_estrategia_afrontamiento.')

    print('OK - numero_choques y numero_estrategias coinciden con sus banderas.')


def _validar_reconciliacion_dane(fact):
    """
    Recalcula la prevalencia ponderada de inseguridad alimentaria moderada
    o grave sobre el hecho final, y la compara contra la cifra oficial
    publicada por el DANE para 2025 (21.1 por ciento).
    """
    validos = fact['prob_ia_moderada_grave'].notna()

    prevalencia = (
        (fact.loc[validos, 'factor_expansion'] * fact.loc[validos, 'prob_ia_moderada_grave']).sum()
        / fact.loc[validos, 'factor_expansion'].sum()
    )

    diferencia = abs(prevalencia - PREVALENCIA_OFICIAL_DANE)

    if diferencia > TOLERANCIA_RECONCILIACION_DANE:
        raise ValueError(
            f'La prevalencia calculada ({prevalencia:.2f}%) difiere de la cifra '
            f'oficial del DANE ({PREVALENCIA_OFICIAL_DANE}%) en mas de '
            f'{TOLERANCIA_RECONCILIACION_DANE} puntos porcentuales.'
        )

    print(f'OK - Reconciliacion con el DANE: {prevalencia:.2f}% calculado vs {PREVALENCIA_OFICIAL_DANE}% oficial.')


def validar_pre_carga(modelo, df_transformado):
    """
    Punto de entrada de las validaciones pre-load. Recibe el modelo
    dimensional completo y la tabla transformada de la que se origino, y
    corre las 8 verificaciones de integridad. Lanza una excepcion en la
    primera que falle.
    """
    fact = modelo['fact_seguridad_alimentaria_hogar']

    _validar_sin_fan_out(fact, df_transformado)
    _validar_llaves_dimensiones(modelo)
    _validar_banderas_sin_nulos(fact)
    _validar_banderas_dimensiones_sin_nulos(modelo)
    _validar_consistencia_sin_dato(fact, modelo)
    _validar_dominios(modelo)
    _validar_regla_choque_estrategia(fact, modelo)
    _validar_conteos_banderas(modelo)
    _validar_reconciliacion_dane(fact)

    print()
    print('Todas las validaciones pre-carga pasaron correctamente.')
