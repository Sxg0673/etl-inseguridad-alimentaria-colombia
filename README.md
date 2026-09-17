# Factores socioeconómicos asociados a la inseguridad alimentaria en los hogares colombianos

<p align="center">
  <strong>Proyecto académico de integración de datos, perfilamiento y diseño de un almacén de datos</strong><br>
  Encuesta Nacional de Calidad de Vida (ECV) 2025 · Colombia
</p>


## Índice

- [1. Contexto y problema](#1-contexto-y-problema)
- [2. Stakeholders](#2-stakeholders)
- [3. Alineación con los ODS](#3-alineación-con-los-ods)
- [4. Arquitectura propuesta](#4-arquitectura-propuesta)
- [5. ETL](#5-etl)
- [6. Modelamiento dimensional](#6-modelamiento-dimensional)
- [7. Consultas analíticas y KPIs](#7-consultas-analíticas-y-kpis)
- [8. Instrucciones de implementación](#8-instrucciones-de-implementación)
- [9. Tecnologías](#9-tecnologías)
- [10. Estructura del proyecto](#10-estructura-del-proyecto)
- [11. Dashboard](#11-dashboard)
- [12. Main findings, limitaciones y supuestos](#12-main-findings-limitaciones-y-supuestos)
- [13. Integrantes y responsabilidades](#13-integrantes-y-responsabilidades)

## 1. Contexto y problema


![Diagrama de contexto del problema](./diagrams/contexto_problema.png)

En Colombia, la **Encuesta Nacional de Calidad de Vida (ECV) 2025**, producida por el **Departamento Administrativo Nacional de Estadística (DANE)**, ofrece información socioeconómica y territorial a nivel de hogar. Esta fuente permite estudiar conjuntamente las condiciones de vida y las medidas de inseguridad alimentaria derivadas de la escala FIES, con una cobertura nacional y una unidad de observación adecuada para los requerimientos del proyecto.

El presente caso de estudio busca responder a la siguiente pregunta:

> **¿Qué factores socioeconómicos, territoriales y de condiciones de vida están asociados con una mayor prevalencia de inseguridad alimentaria en los hogares colombianos?**


## 2. Stakeholders

| Stakeholder | Interés en el problema | Uso potencial de los resultados |
|---|---|---|
| DANE | Producir, evaluar y divulgar estadísticas oficiales sobre condiciones de vida. | Contrastar resultados, fortalecer análisis estadísticos y orientar futuras mediciones. |
| Entidades nacionales de política social | Identificar población y territorios en situación de vulnerabilidad. | Priorizar programas de seguridad alimentaria, transferencias y atención social. |
| Gobernaciones y alcaldías | Comprender diferencias territoriales dentro de sus jurisdicciones. | Apoyar diagnósticos territoriales y focalizar intervenciones. |
| Organizaciones humanitarias y sociales | Reconocer hogares expuestos a inseguridad alimentaria y choques. | Orientar acciones de acompañamiento, prevención y respuesta. |
| Comunidad académica | Estudiar factores asociados a la inseguridad alimentaria. | Reproducir, ampliar y discutir los resultados con criterios metodológicos. |
| Ciudadanía | Conocer la magnitud y distribución de una problemática social. | Promover control social y comprensión de las brechas territoriales. |

## 4. Alineación con los ODS

| ODS | Relación con el proyecto | Contribución concreta |
|---|---|---|
| **ODS 2: Hambre Cero** | Es el objetivo principal, pues aborda la seguridad alimentaria, la nutrición y la identificación de hogares vulnerables. | Genera evidencia descriptiva sobre la prevalencia de inseguridad alimentaria y sus asociaciones con condiciones socioeconómicas. |
| **ODS 1: Fin de la pobreza** | Los ingresos y los choques económicos son dimensiones relevantes de la vulnerabilidad del hogar. | Permite observar cómo los niveles de ingreso y las crisis económicas se relacionan con la inseguridad alimentaria. |
| **ODS 10: Reducción de las desigualdades** | Las diferencias territoriales y de acceso a servicios pueden expresar brechas estructurales. | Facilita comparaciones entre regiones, departamentos y tipos de área para visibilizar desigualdades. |
| **ODS 11: Ciudades y comunidades sostenibles** | La vivienda y el acceso a servicios básicos forman parte de las condiciones materiales del hogar. | Aporta evidencia para interpretar la relación entre entorno habitacional, servicios y bienestar alimentario. |


## 5. Arquitectura propuesta

La arquitectura prevista seguirá el flujo **fuentes crudas → extracción → limpieza y transformación → carga al almacén de datos → consultas analíticas → visualización**. La implementación definitiva se documentará cuando se completen las etapas de transformación y carga.

### Espacio reservado para el diagrama de arquitectura

> **Pendiente:** insertar aquí el diagrama de arquitectura del pipeline ETL, sus componentes, entradas, salidas y mecanismos de almacenamiento.

`[ Espacio reservado para imagen: diagrams/arquitectura_etl.png ]`

## 6. ETL

### 6.1 Extracción: fuente de datos

| Elemento | Descripción |
|---|---|
| Operación estadística | Encuesta Nacional de Calidad de Vida (ECV) 2025. |
| Productor y propietario | Departamento Administrativo Nacional de Estadística (DANE), Dirección de Metodología y Producción Estadística (DIMPE). |
| Catálogo | DANE-DIMPE-ECV-2025, catálogo 905. |
| Fuente oficial | [Portal de microdatos del DANE](https://microdatos.dane.gov.co/index.php/catalog/905/get-microdata). |
| Fuente del diccionario | [Diccionario de la tabla de condiciones de vida](https://microdatos.dane.gov.co/index.php/catalog/905/data-dictionary/F51?file_name=Condiciones%20de%20vida%20del%20hogar%20y%20tenencia%20de%20bienes). |
| Formato | CSV delimitado por punto y coma (`;`). |
| Codificación esperada | `utf-8-sig`. |
| Lectura | Todas las columnas se leen como texto (`dtype=str`) para conservar códigos con ceros a la izquierda. |
| Unidad de observación | Hogar, asociado a una vivienda. |

#### Archivos utilizados

| Archivo descargado | Nombre esperado en `data/raw/` | Nivel principal | Llave identificada |
|---|---|---|---|
| DBF-ECV-Datos_vivienda-2025 | `Datos de la vivienda.csv` | Vivienda | `DIRECTORIO` |
| DBF-ECV-Servicios_hogar-2025 | `Servicios del hogar.csv` | Hogar | (`DIRECTORIO`, `ORDEN`) |
| DBF-ECV-Condiciones_vida_hogar_tenencia_bienes-2025 | `Condiciones de vida del hogar y tenencia de bienes.csv` | Hogar | (`DIRECTORIO`, `ORDEN`) |

#### Adquisición y reproducibilidad

Los archivos crudos no se distribuyen en el repositorio debido a su tamaño y a las condiciones de descarga del portal. Para reproducir el pipeline, se deben descargar los tres archivos desde el catálogo oficial, conservar exactamente los nombres indicados y ubicarlos directamente en `data/raw/`. Las instrucciones completas se encuentran en [data/raw/README.md](data/raw/README.md).

### 6.2 Evaluación de idoneidad del conjunto de datos

| Criterio | Evaluación |
|---|---|
| Institución / propietario | DANE. Fuente oficial y pertinente para el contexto colombiano. |
| Acceso | Portal oficial de microdatos del DANE; requiere seguir sus condiciones de descarga. |
| Formato | Tres archivos CSV con separador `;`, codificación `utf-8-sig`. |
| Número de hogares integrados | 87.060 filas a nivel de hogar, después de las uniones. |
| Número de atributos | 286 columnas en la tabla integrada antes de la depuración. |
| Cobertura geográfica | Colombia; 9 regiones, 33 códigos departamentales y áreas de cabecera / centros poblados y rural disperso. |
| Cobertura temporal | ECV 2025; corresponde a una medición de corte transversal. |
| Medidas numéricas relevantes | `PROB_IAMG`, `PROB_IAG`, `PERCAPITA`, `I_HOGAR`, `FEX_C`, número de personas y conteos de choques o estrategias. |
| Atributos categóricos relevantes | Región, departamento, clase de área, acceso a acueducto y alcantarillado, choques y estrategias de afrontamiento. |
| Relación con R1-R5 | La fuente contiene variables suficientes para responder los cinco requerimientos definidos. |
| Idoneidad para modelamiento dimensional | Alta para un modelo a nivel de hogar, con dimensiones territoriales, de servicios, vulnerabilidad e ingreso por definir. |
| Unidad de observación | Un registro representa un hogar encuestado, relacionado con una vivienda mediante `DIRECTORIO`. |

### 6.3 Data profiling y evaluación de calidad

El perfilamiento se ejecutó sobre los archivos completos y se documentó en [notebooks/hallazgos_perfilamiento.md](notebooks/hallazgos_perfilamiento.md). Los resultados siguientes son hallazgos verificados, no supuestos.

#### Resumen estructural

| Aspecto evaluado | Resultado verificado | Implicación para el ETL |
|---|---|---|
| Registros | 87.060 hogares integrados. | El modelo debe conservar el nivel de hogar. |
| Columnas integradas | 286. | Se requiere seleccionar variables analíticas y retirar campos estructuralmente vacíos. |
| Llave de vivienda | `DIRECTORIO`: 86.848 filas, sin duplicados. | Puede relacionar hogares con su vivienda. |
| Llave de hogar | (`DIRECTORIO`, `ORDEN`): 87.060 filas, sin duplicados. | Es la llave compuesta operativa para servicios y condiciones de vida. |
| Integración | 87.060 filas antes y después de las uniones; cero pérdidas, duplicaciones o faltantes de correspondencia. | La integración propuesta es consistente. |
| Columnas 100% vacías | 21 columnas contenedoras. | Se descartan; no se interpretan como faltantes. |

#### Cobertura, dominios y calidad

| Dominio | Hallazgo | Tratamiento previsto |
|---|---|---|
| Territorio | `REGION`: 9 categorías; `P1_DEPARTAMENTO`: 33 códigos. En 6.365 filas faltan ceros a la izquierda. | Normalizar el departamento con `zfill(2)` y cruzar con DIVIPOLA. |
| DIVIPOLA | Los 33 códigos presentes en la ECV cruzan correctamente con la tabla de referencia. | Usar la referencia para obtener nombres y validar códigos. |
| Área | `CLASE`: 44.351 hogares en cabecera y 42.709 en centros poblados y rural disperso. | Conservar como dimensión o atributo de segmentación. |
| Servicios | Acueducto (`P8520S5`) y alcantarillado (`P8520S3`) usan 1/2 y no presentan nulos. | Decodificar y documentar las categorías. |
| Choques económicos | 12.935 hogares (14,9%) reportan al menos un choque; 74.125 (85,1%) no reportan choques. | Convertir baterías a indicadores o estructura analítica justificada. |
| Estrategias de afrontamiento | La ausencia de estrategias coincide exactamente con la ausencia de choques. | Validar consistencia y conservar la relación con R3 y R4. |
| Ingreso | `PERCAPITA` tiene 681 ceros; 3 son inconsistentes frente a `I_HOGAR` positivo. | Marcar los 3 casos y excluirlos únicamente de R5. |
| Valores extremos | Los 5 valores de `PERCAPITA` superiores a 50 millones cumplen la aritmética observada. | No eliminarlos automáticamente; documentar su tratamiento analítico. |
| FIES | `PROB_IAMG` y `PROB_IAG` son nulas en 718 hogares, coincidiendo con respuestas “no sabe/no informa”. | Excluir esos hogares de las prevalencias FIES y documentar el denominador. |

#### Resultados de validación de inseguridad alimentaria

| Indicador | Resultado |
|---|---:|
| Prevalencia ponderada de inseguridad alimentaria moderada o grave | **21,10%** |
| Prevalencia ponderada de inseguridad alimentaria grave | **3,42%** |
| Método de ponderación | `SUM(FEX_C × PROB_IAMG) / SUM(FEX_C)` sobre hogares con dato válido. |
| Comparación externa | El 21,10% reconcilia con el 21,1% publicado oficialmente por el DANE para 2025. |

#### Consideraciones de interpretación

- En las baterías de selección múltiple, un vacío puede significar que la opción no fue marcada y no necesariamente un dato faltante.
- `P3202S12` representa “Ninguno de los anteriores”; no debe contarse como un choque económico.
- `P3203S10` (“Disminuyeron el gasto en alimentos”) requiere una interpretación diferenciada por su cercanía conceptual con la inseguridad alimentaria.
- El diccionario documenta directamente solo una parte de las variables núcleo. Para decodificar categorías se combinarán los dominios, las descripciones de variables y la tabla DIVIPOLA.

(Colocar acá la parte del clean)

## 7. Modelamiento dimensional

El modelo dimensional se documentará mediante las siguientes fases. A la fecha, se cuenta con los requerimientos y la declaración preliminar del grano; las dimensiones, los hechos y el diagrama se encuentran pendientes de definición formal.

### 7.1 Requerimientos

| ID | Requerimiento |
|---|---|
| R1 | Caracterizar la distribución territorial de la inseguridad alimentaria. |
| R2 | Analizar la asociación entre el acceso a servicios públicos básicos de la vivienda y la vulnerabilidad alimentaria. |
| R3 | Analizar la relación entre los choques económicos recientes del hogar y su inseguridad alimentaria. |
| R4 | Caracterizar las estrategias de afrontamiento según la severidad de la inseguridad alimentaria. |
| R5 | Evaluar el gradiente de vulnerabilidad alimentaria según el nivel de ingreso del hogar. |


### 7.2 Declaración del grano

**Grano propuesto:** una fila de la tabla de hechos representa un hogar encuestado en la ECV 2025, identificado por (`DIRECTORIO`, `ORDEN`), asociado con una vivienda y con sus características territoriales, de servicios, choques, estrategias, ingreso y medidas de inseguridad alimentaria.

Este grano debe validarse antes de la carga para evitar duplicaciones, agregaciones indebidas o mezcla de niveles vivienda-hogar.

### 7.3 Dimensiones

| Dimensión candidata | Propósito | Atributos candidatos | Clave sustituta | Estado |
|---|---|---|---|---|
|  |  |  |  | Pendiente |
|  |  |  |  | Pendiente |
|  |  |  |  | Pendiente |

### 7.4 Facts

| Tabla de hechos candidata | Grano | Medidas | Claves foráneas | Estado |
|---|---|---|---|---|
|  |  |  |  | Pendiente |

### 7.5 Estrategia de claves sustitutas

| Elemento | Decisión de diseño | Estado |
|---|---|---|
| Generación de claves sustitutas |  | Pendiente |
| Retención de llaves naturales DANE | Conservar (`DIRECTORIO`, `ORDEN`) para trazabilidad, aunque no sustituyan la clave dimensional. | Por confirmar |
| Manejo de registros desconocidos |  | Pendiente |
| Integridad referencial |  | Pendiente |
| Historización de dimensiones | La ECV 2025 es transversal; la necesidad de SCD deberá justificarse si se incorporan nuevas rondas. | Por confirmar |

### 7.6 Diagrama dimensional

> **Pendiente:** insertar aquí el diagrama final con dimensiones, tabla(s) de hechos, cardinalidades y claves.

`[ Espacio reservado para imagen: diagrams/modelo_dimensional.png ]`

## 8. Consultas analíticas y KPIs

Las consultas y los KPIs todavía no han sido implementados. La siguiente tabla organiza el trabajo pendiente sin asumir un modelo dimensional que aún no ha sido aprobado.

| Requerimiento | Pregunta analítica | Dimensiones requeridas | Medidas / indicadores | Consulta o KPI final |
|---|---|---|---|---|
| R1 | ¿Cómo se distribuye la inseguridad alimentaria por región y departamento? |  |  |  |
| R2 | ¿Qué relación se observa entre servicios públicos y vulnerabilidad alimentaria? |  |  |  |
| R3 | ¿Cómo se relacionan los choques económicos con la inseguridad alimentaria? |  |  |  |
| R4 | ¿Qué estrategias de afrontamiento se observan según la severidad? |  |  |  |
| R5 | ¿Cómo cambia la vulnerabilidad alimentaria según el ingreso per cápita? |  |  |  |

### Espacio para evidencia del dashboard

`[ Espacio reservado para imagen: dashboard/dashboard_final.png ]`

## 9. Instrucciones de implementación

### Requisitos previos

1. Instalar Python 3.x.
2. Clonar o descargar este repositorio.
3. Crear y activar un entorno virtual.
4. Instalar las dependencias con:

```bash
pip install -r requirements.txt
```

5. Descargar los tres archivos de la ECV 2025 y ubicarlos en `data/raw/` con los nombres indicados.
6. Ejecutar el pipeline desde la raíz del proyecto:

```bash
python src/main.py
```

> **Estado actual:** `src/main.py`, la transformación completa, la carga y el modelamiento dimensional aún requieren implementación. El comando anterior queda como punto de entrada previsto para la ejecución integral.

## 10. Tecnologías

| Tecnología / paquete | Uso previsto |
|---|---|
| Python | Implementación del pipeline ETL y análisis. |
| pandas | Lectura, integración, limpieza y transformación de datos tabulares. |
| NumPy | Operaciones numéricas y derivación de indicadores. |
| SQLAlchemy | Conexión y operaciones con el almacén de datos. |
| psycopg2-binary | Conectividad con PostgreSQL. |
| python-dotenv | Gestión de variables de entorno. |
| Jupyter / IPython Kernel | Exploración y perfilamiento reproducible. |
| Matplotlib / Seaborn | Visualización exploratoria. |
| PyYAML | Lectura de configuraciones estructuradas. |
| openpyxl | Interoperabilidad con archivos de Excel. |

Las dependencias corresponden al contenido actual de [requirements.txt](requirements.txt).

## 11. Estructura del proyecto

```text
.
├── README.md
├── requirements.txt
├── dashboard/                         # Espacio para el dashboard final
├── data/
│   ├── raw/                           # CSV de la ECV descargados del DANE
│   └── reference/                     # Diccionario y referencia DIVIPOLA
├── diagrams/                          # Diagramas del problema y arquitectura
├── notebooks/
│   ├── data_profiling.ipynb            # Exploración y perfilamiento
│   └── hallazgos_perfilamiento.md      # Resultados verificados del perfilamiento
├── results/                            # Resultados generados
├── sql/
│   ├── analytical_queries.sql          # Consultas analíticas, pendiente
│   └── create_tables.sql               # DDL del modelo, pendiente
└── src/
    ├── analytics.py                   # Analítica, pendiente de completar
    ├── clean.py                       # Limpieza, en desarrollo
    ├── dimensional_model.py           # Modelo dimensional, pendiente
    ├── extract.py                     # Lectura de archivos crudos
    ├── load.py                        # Carga, pendiente de completar
    ├── main.py                        # Punto de entrada previsto
    ├── transform.py                   # Transformación, en desarrollo
    └── validate.py                    # Validaciones, en desarrollo
```

## 12. Dashboard

El dashboard aún no ha sido construido. Esta sección se completará con la herramienta utilizada, las vistas implementadas, los filtros, los KPIs, la fecha de actualización y capturas de evidencia.

`[ Espacio reservado para descripción y capturas del dashboard ]`

## 13. Main findings, limitaciones y supuestos

<!-- Esta sección se deja intencionalmente en blanco hasta finalizar el ETL, el modelo dimensional, las consultas y el dashboard. -->

## 14. Integrantes y responsabilidades

| Integrante(s) | Responsabilidades |
|---|---|
| Santiago Castillo y Julián Aguilar | Modelamiento dimensional y desarrollo del código. |
| Valeria Jiménez Bedoya | Estructura de la documentación y contextualización del problema. |
| Danna Isabella Mosquera Mosquera | Modelado gráfico del dashboard. |

## Referencias

- [DANE. Catálogo de microdatos de la ECV 2025](https://microdatos.dane.gov.co/index.php/catalog/905/get-microdata)
- [DANE. Diccionario de datos: Condiciones de vida del hogar y tenencia de bienes](https://microdatos.dane.gov.co/index.php/catalog/905/data-dictionary/F51?file_name=Condiciones%20de%20vida%20del%20hogar%20y%20tenencia%20de%20bienes)
- [Naciones Unidas. Objetivo de Desarrollo Sostenible 2: Hambre Cero](https://www.un.org/sustainabledevelopment/es/hunger/)
- [Naciones Unidas en Colombia. Información sobre inseguridad alimentaria](https://colombia.un.org/es/316567-colombia-redujo-en-779-mil-personas-la-inseguridad-alimentaria-grave-en-2025)