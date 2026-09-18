-- =====================================================================
-- DDL del Data Warehouse 
-- Esquema: public
-- 1. Borrar tablas si existen (para desarrollo iterativo)
-- 2. Crear tablas de dimensiones y hechos
-- =====================================================================

-- El orden de DROP es inverso al de CREATE: el hecho depende de las
-- dimensiones, asi que se elimina primero para no violar las llaves
-- foraneas. Permite correr este script varias veces durante el desarrollo.
DROP TABLE IF EXISTS fact_seguridad_alimentaria_hogar;
DROP TABLE IF EXISTS dim_geografia;
DROP TABLE IF EXISTS dim_nivel_ingreso;
DROP TABLE IF EXISTS dim_nivel_severidad_ia;
DROP TABLE IF EXISTS dim_choque_economico;
DROP TABLE IF EXISTS dim_estrategia_afrontamiento;


-- ---------------------------------------------------------------------
-- DIM_GEOGRAFIA
-- Grano: una fila por combinacion de departamento y clase de area.
-- La region depende de ambas, no solo del departamento (caso Bogota).
-- ---------------------------------------------------------------------
CREATE TABLE dim_geografia (
    id_geografia            INTEGER NOT NULL,
    codigo_departamento     VARCHAR(2) NOT NULL,
    nombre_departamento     TEXT NOT NULL,
    codigo_region           VARCHAR(1) NOT NULL,
    nombre_region           TEXT NOT NULL,
    codigo_clase            VARCHAR(1) NOT NULL,
    nombre_clase            TEXT NOT NULL,
    CONSTRAINT pk_dim_geografia PRIMARY KEY (id_geografia)
);


-- ---------------------------------------------------------------------
-- DIM_NIVEL_INGRESO
-- Grano: una fila por quintil de ingreso per capita del hogar.
-- Incluye la categoria "Dato inconsistente" para los hogares con
-- PERCAPITA invalido, detectados durante la limpieza.
-- ---------------------------------------------------------------------
CREATE TABLE dim_nivel_ingreso (
    id_nivel_ingreso        INTEGER NOT NULL,
    codigo_quintil          VARCHAR(20) NOT NULL,
    nombre_quintil          TEXT NOT NULL,
    CONSTRAINT pk_dim_nivel_ingreso PRIMARY KEY (id_nivel_ingreso)
);


-- ---------------------------------------------------------------------
-- DIM_NIVEL_SEVERIDAD_IA
-- Grano: una fila por nivel de severidad de inseguridad alimentaria.
-- Cortes segun el puntaje FIES crudo (0 a 8), estandar FAO.
-- La categoria "Sin dato" no tiene rango numerico definido.
-- ---------------------------------------------------------------------
CREATE TABLE dim_nivel_severidad_ia (
    id_nivel_severidad_ia   INTEGER NOT NULL,
    nombre_severidad        TEXT NOT NULL,
    puntaje_fies_minimo     INTEGER,
    puntaje_fies_maximo     INTEGER,
    CONSTRAINT pk_dim_nivel_severidad_ia PRIMARY KEY (id_nivel_severidad_ia)
);


-- ---------------------------------------------------------------------
-- DIM_CHOQUE_ECONOMICO (junk dimension)
-- Grano: una fila por cada combinacion de choques economicos que
-- realmente ocurre en los datos. No se genera el producto cartesiano
-- teorico completo, solo las combinaciones observadas.
-- ---------------------------------------------------------------------
CREATE TABLE dim_choque_economico (
    id_choque_economico                    INTEGER NOT NULL,
    choque_jefe_perdio_empleo              BOOLEAN NOT NULL,
    choque_conyuge_perdio_empleo           BOOLEAN NOT NULL,
    choque_otro_miembro_perdio_empleo      BOOLEAN NOT NULL,
    choque_cierre_negocio                  BOOLEAN NOT NULL,
    choque_no_vendio_produccion            BOOLEAN NOT NULL,
    choque_atraso_jardin_colegio           BOOLEAN NOT NULL,
    choque_no_pago_universidad             BOOLEAN NOT NULL,
    choque_atraso_vivienda                 BOOLEAN NOT NULL,
    choque_atraso_administracion           BOOLEAN NOT NULL,
    choque_atraso_servicios_publicos       BOOLEAN NOT NULL,
    choque_atraso_impuestos                BOOLEAN NOT NULL,
    numero_choques                         INTEGER NOT NULL,
    CONSTRAINT pk_dim_choque_economico PRIMARY KEY (id_choque_economico)
);


-- ---------------------------------------------------------------------
-- DIM_ESTRATEGIA_AFRONTAMIENTO (junk dimension)
-- Grano: una fila por cada combinacion de estrategias de afrontamiento
-- que realmente ocurre en los datos. Condicionada a dim_choque_economico:
-- un hogar sin choque tiene siempre cero estrategias.
-- ---------------------------------------------------------------------
CREATE TABLE dim_estrategia_afrontamiento (
    id_estrategia_afrontamiento            INTEGER NOT NULL,
    estrategia_empezaron_a_trabajar        BOOLEAN NOT NULL,
    estrategia_nuevas_fuentes_ingreso      BOOLEAN NOT NULL,
    estrategia_vivir_con_familiares        BOOLEAN NOT NULL,
    estrategia_gastaron_ahorros            BOOLEAN NOT NULL,
    estrategia_se_endeudaron               BOOLEAN NOT NULL,
    estrategia_vendieron_bienes            BOOLEAN NOT NULL,
    estrategia_vendieron_vivienda          BOOLEAN NOT NULL,
    estrategia_retiro_escolar              BOOLEAN NOT NULL,
    estrategia_retiro_universidad          BOOLEAN NOT NULL,
    estrategia_disminuyeron_gasto_alimentos BOOLEAN NOT NULL,
    estrategia_ayuda_gobierno              BOOLEAN NOT NULL,
    estrategia_ayuda_familiares_amigos     BOOLEAN NOT NULL,
    estrategia_subsidio_desempleo          BOOLEAN NOT NULL,
    estrategia_otra                        BOOLEAN NOT NULL,
    numero_estrategias                     INTEGER NOT NULL,
    CONSTRAINT pk_dim_estrategia_afrontamiento PRIMARY KEY (id_estrategia_afrontamiento)
);


-- ---------------------------------------------------------------------
-- FACT_SEGURIDAD_ALIMENTARIA_HOGAR
-- Grano: un hogar encuestado en la ECV 2025.
-- directorio y orden son la llave natural del DANE, conservada para
-- trazabilidad hacia el archivo original. No forman parte del diagrama
-- del modelo dimensional, pero si existen en la base de datos.
--
-- prob_ia_moderada_grave y prob_ia_grave aceptan nulo: 718 hogares no
-- tienen dato valido porque respondieron "no sabe / no informa" en al
-- menos una de las 8 preguntas FIES.
-- ---------------------------------------------------------------------
CREATE TABLE fact_seguridad_alimentaria_hogar (
    id_hogar                        INTEGER NOT NULL,
    directorio                      VARCHAR(10) NOT NULL,
    orden                           VARCHAR(2) NOT NULL,
    id_geografia                    INTEGER NOT NULL,
    id_nivel_ingreso                INTEGER NOT NULL,
    id_nivel_severidad_ia           INTEGER NOT NULL,
    id_choque_economico             INTEGER NOT NULL,
    id_estrategia_afrontamiento     INTEGER NOT NULL,
    tiene_acueducto                 BOOLEAN NOT NULL,
    tiene_alcantarillado            BOOLEAN NOT NULL,
    factor_expansion                DECIMAL(15, 9) NOT NULL,
    prob_ia_moderada_grave          DECIMAL(12, 9),
    prob_ia_grave                   DECIMAL(12, 9),

    CONSTRAINT pk_fact_seguridad_alimentaria_hogar PRIMARY KEY (id_hogar), 

    CONSTRAINT uq_fact_directorio_orden UNIQUE (directorio, orden),

    CONSTRAINT fk_hecho_geografia
        FOREIGN KEY (id_geografia) REFERENCES dim_geografia (id_geografia),

    CONSTRAINT fk_hecho_nivel_ingreso
        FOREIGN KEY (id_nivel_ingreso) REFERENCES dim_nivel_ingreso (id_nivel_ingreso),

    CONSTRAINT fk_hecho_nivel_severidad_ia
        FOREIGN KEY (id_nivel_severidad_ia) REFERENCES dim_nivel_severidad_ia (id_nivel_severidad_ia),

    CONSTRAINT fk_hecho_choque_economico
        FOREIGN KEY (id_choque_economico) REFERENCES dim_choque_economico (id_choque_economico),

    CONSTRAINT fk_hecho_estrategia_afrontamiento
        FOREIGN KEY (id_estrategia_afrontamiento) REFERENCES dim_estrategia_afrontamiento (id_estrategia_afrontamiento)
);
