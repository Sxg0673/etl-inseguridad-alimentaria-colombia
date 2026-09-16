# Hallazgos del perfilamiento — ECV 2025

Documento de referencia técnica con los hallazgos verificados durante el perfilamiento de las tres tablas fuente (Datos de la vivienda, Servicios del hogar, Condiciones de vida del hogar y tenencia de bienes). Cada punto fue confirmado con código sobre el archivo completo (87.060 hogares), no sobre muestras. Sirve como insumo directo para `clean.py`, `transform.py` y el README del proyecto.

## 1. Integridad de las llaves

- **Vivienda**: llave primaria `DIRECTORIO`. 86.848 filas, sin duplicados.
- **Servicios del hogar** y **Condiciones de vida**: llave primaria compuesta `(DIRECTORIO, ORDEN)`. 87.060 filas cada una, sin duplicados en la llave compuesta. `DIRECTORIO` solo tiene 212 duplicados, correspondientes a las 181 viviendas con más de un hogar.
- El diccionario de datos del DANE declara llaves incorrectas para estas tablas (marca `SECUENCIA_P` como PK, que en la práctica es constante = 1 en todas las filas). La llave real fue determinada empíricamente, no a partir del diccionario.

## 2. Integración de las tres tablas

- Unión `condiciones_vida → servicios_hogar` por `(DIRECTORIO, ORDEN)`, y el resultado `→ vivienda` por `DIRECTORIO`.
- 87.060 filas antes y después de ambas uniones. Cero pérdida de filas, cero duplicación por explosión, cero filas sin correspondencia en ninguna de las tres tablas.
- La tabla integrada resultante tiene 286 columnas.

## 3. Columnas estructuralmente vacías

- 21 columnas de la tabla integrada están 100% vacías: `P9025, P3180, P9005, P784, P1072, P1077, P795, P1913, P3202, P3203, P3516, P1892, P5046S1, P5012, P3169, P3172, P3174, P8520, P4065, P5661, P3157`.
- Verificado contra el diccionario: las 21 son preguntas "contenedoras" que introducen una batería de subítems (ejemplo: `P3202` es el encabezado de `P3202S1` a `P3202S12`). El dato vive exclusivamente en los subítems, nunca en la columna contenedora.
- Acción: se descartan en `clean.py`. No se tratan como datos faltantes.

## 4. Nulos en baterías de selección múltiple

- Los subítems de una batería (`P3202S*`, `P3203S*`, `P795S*`, entre otros) usan codificación `1` = marcado / vacío = no marcado. El nulo en estos casos **no es un dato faltante**, es la ausencia de esa opción específica.
- Distinto del resto de variables categóricas simples de la encuesta, que usan codificación explícita `1`/`2` (Sí/No) sin nulos (ejemplo: `P8520S5`, acueducto).
- Confundir estos dos patrones de codificación llevaría a tratar como "faltante" un dato que en realidad es válido.

## 5. Choques económicos (P3202) — variable núcleo de R3

- `P3202S12` = "Ninguno de las anteriores", con 74.125 marcas. Verificado que ningún hogar marca `S12` junto con otro choque (0 casos de solapamiento).
- Excluyendo `S12` del conteo: **74.125 hogares sin ningún choque económico (85,1%)**, **12.935 hogares con al menos uno (14,9%)**.
- Máximo de choques simultáneos en un mismo hogar: 11 (un solo caso).
- Choque más frecuente: `S10` "Se atrasaron en el pago de la vivienda" no es el más común; el de mayor frecuencia real fuera de "Ninguno" es `S1` "El jefe/a de hogar perdió su empleo" (3.355 casos), seguido de S10.

## 6. Estrategias de afrontamiento (P3203) — variable núcleo de R4

- No existe una opción "Ninguna" explícita en esta batería (llega hasta `S14` = "Otra").
- Verificado que la ausencia de estrategia coincide de forma exacta con la ausencia de choque: los 74.125 hogares sin choque tienen también 0 estrategias marcadas, y los 12.935 con algún choque tienen todos al menos una estrategia. Cero casos inconsistentes en cualquier dirección.
- `P3203S10` = "Disminuyeron el gasto en alimentos" (2.608 casos). Queda señalada para tratamiento diferenciado en el análisis de R4, por su cercanía conceptual directa con la variable dependiente (inseguridad alimentaria), a diferencia del resto de estrategias que son conductas distintas y no una redefinición del fenómeno medido.

## 7. Territorio — variables núcleo de R1

- `REGION`: 9 categorías, la más pequeña (San Andrés, código 8) con 889 hogares. Ninguna celda regional es demasiado pequeña para un análisis confiable.
- `CLASE`: prácticamente balanceada (44.351 cabecera / 42.709 centros poblados y rural disperso).
- `P1_DEPARTAMENTO`: 33 códigos únicos, correctos en cantidad, pero **sin ceros a la izquierda en 6.365 filas** (longitud de 1 carácter en vez de 2). El estándar DIVIPOLA usa 2 dígitos. Acción: normalizar con `zfill(2)` en `clean.py` antes de cualquier cruce con la tabla de referencia DIVIPOLA.
- Tabla de referencia DIVIPOLA (33 departamentos) validada por separado: cruce perfecto 33/33 contra los códigos presentes en la ECV, sin sobrantes ni faltantes.
- Decisión de alcance: `DIM_GEOGRAFIA` se construye solo hasta nivel departamento. Municipio queda fuera de alcance para esta fase del proyecto.

## 8. Servicios públicos de la vivienda — variables núcleo de R2

- `P8520S5` (acueducto) y `P8520S3` (alcantarillado): codificación `1`/`2` explícita, sin nulos. No requieren tratamiento de calidad adicional.

## 9. Ingreso del hogar — variable núcleo de R5

- `PERCAPITA` sin nulos, pero con 681 hogares en cero. De estos, 678 tienen también `I_HOGAR = 0` (consistente: hogar sin ingreso reportado).
- **3 hogares presentan inconsistencia real**: `PERCAPITA = 0` con `I_HOGAR` positivo (2.608.333, 1.200.000 y 1.050.000, con 4, 3 y 4 personas en el hogar respectivamente). La división `I_HOGAR / CANT_PERSONAS_HOGAR` no da cero en ninguno de los tres casos, confirmando que el campo `PERCAPITA` del DANE está mal calculado para estos 3 registros específicos.
- Decisión: no se recalcula (no hay certeza de que el DANE use una división simple; existe también `I_UGASTO`, que sugiere una metodología por unidad de gasto, no por persona). Se marcan como inconsistentes en `clean.py` y se excluyen únicamente del análisis de R5 en `transform.py`. Siguen siendo válidos para R1, R2, R3 y R4.
- Valores altos de `PERCAPITA` (hasta 255.000.000) verificados uno por uno: la aritmética `I_HOGAR / CANT_PERSONAS_HOGAR` se cumple exactamente en los 5 casos que superan 50 millones. Son hogares de ingreso extremo pero válidos, no errores de captura.

## 10. Medidas de inseguridad alimentaria (FIES)

- `PROB_IAMG` y `PROB_IAG` (probabilidades del modelo Rasch de FIES, escala 0-100) no están documentadas en el diccionario de datos, pero se validaron por comportamiento: nulas en exactamente 718 hogares.
- Verificado que esos 718 nulos coinciden de forma exacta (no aproximada) con los hogares que registran al menos una respuesta "3" (no sabe/no informa) en las 8 preguntas FIES (`P3516S1` a `P3516S8`). Coincidencia confirmada al 100%.
- **Validación contra la cifra oficial**: la prevalencia ponderada de inseguridad alimentaria moderada o grave, calculada como `SUM(FEX_C × PROB_IAMG) / SUM(FEX_C)` sobre los hogares con dato válido, da **21,10%**, contra el **21,1%** publicado oficialmente por el DANE para 2025. Esta reconciliación confirma que el tratamiento de las medidas base (ponderación por factor de expansión, exclusión de los 718 hogares sin dato válido) es correcto.
- Prevalencia ponderada de inseguridad alimentaria grave (`PROB_IAG`): 3,42%.

## 11. Cobertura real del diccionario de datos frente a las variables usadas

- De las ~39 variables núcleo que alimentan los 5 requerimientos, solo 4 tienen dominio documentado directamente en la columna "Dominios" del diccionario (`REGION`, `CLASE`, `P8520S5`, `P8520S3`).
- Las 26 variables de choques y estrategias (`P3202S*`, `P3203S*`) no tienen dominio documentado, pero su etiqueta se puede extraer de la columna "Descripción de la variable", que usa el mismo formato `N. Texto` que la columna de dominios.
- `P1_DEPARTAMENTO` no trae los nombres de departamento en el diccionario; se resuelve con la tabla de referencia DIVIPOLA externa.
- Conclusión operativa: el archivo de mapeo de decodificación se genera por parseo automático de dos columnas del diccionario (Dominios y Descripción) más una tabla de referencia externa (DIVIPOLA). No requiere mapeos escritos a mano.

## 12. Nomenclatura real de archivos y columnas

- Los tres archivos CSV en `data/raw/` tienen nombres con espacios y sin guiones bajos (ejemplo: `Datos de la vivienda.csv`), distinto de lo inicialmente asumido.
- La columna de clase de área en la tabla de vivienda es `CLASE` en mayúsculas, no `Clase`.
- Ambos casos se detectaron por verificación directa contra el sistema de archivos y las columnas reales, no por inferencia. Se documentan aquí para dejar registro de que el código referencia los nombres exactos verificados, no una convención asumida.
