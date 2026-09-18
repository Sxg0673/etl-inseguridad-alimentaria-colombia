"""
Modulo de analitica sobre el modelo dimensional cargado.

Ejecuta una consulta por cada requerimiento analitico (R1-R5) y muestra en
consola los resultados agregados del hecho con sus dimensiones. Las medidas de
inseguridad alimentaria se calculan de forma ponderada con factor_expansion.
"""

import pandas as pd
import psycopg2

from config import DB_CONFIG


CONSULTAS = {
	'R1 - Distribucion territorial': """
		SELECT g.nombre_region AS region, g.nombre_departamento AS departamento,
			   COUNT(*) AS hogares,
			   ROUND((SUM(f.factor_expansion * f.prob_ia_moderada_grave)
			   / NULLIF(SUM(f.factor_expansion), 0))::numeric, 2)
			   AS prevalencia_moderada_grave_pct,
			   ROUND((SUM(f.factor_expansion * f.prob_ia_grave)
			   / NULLIF(SUM(f.factor_expansion), 0))::numeric, 2)
			   AS prevalencia_grave_pct
		FROM fact_seguridad_alimentaria_hogar f
		JOIN dim_geografia g ON g.id_geografia = f.id_geografia
		WHERE f.prob_ia_moderada_grave IS NOT NULL
		GROUP BY g.nombre_region, g.nombre_departamento
		ORDER BY prevalencia_moderada_grave_pct DESC
	""",
	'R2 - Servicios publicos': """
		SELECT f.tiene_acueducto, f.tiene_alcantarillado, COUNT(*) AS hogares,
			   ROUND((SUM(f.factor_expansion * f.prob_ia_moderada_grave)
			   / NULLIF(SUM(f.factor_expansion), 0))::numeric, 2)
			   AS prevalencia_moderada_grave_pct,
			   ROUND((SUM(f.factor_expansion * f.prob_ia_grave)
			   / NULLIF(SUM(f.factor_expansion), 0))::numeric, 2)
			   AS prevalencia_grave_pct
		FROM fact_seguridad_alimentaria_hogar f
		WHERE f.prob_ia_moderada_grave IS NOT NULL
		GROUP BY f.tiene_acueducto, f.tiene_alcantarillado
		ORDER BY f.tiene_acueducto DESC, f.tiene_alcantarillado DESC
	""",
	'R3 - Choques economicos': """
		SELECT c.numero_choques, COUNT(*) AS hogares,
			   ROUND((SUM(f.factor_expansion * f.prob_ia_moderada_grave)
			   / NULLIF(SUM(f.factor_expansion), 0))::numeric, 2)
			   AS prevalencia_moderada_grave_pct,
			   ROUND((SUM(f.factor_expansion * f.prob_ia_grave)
			   / NULLIF(SUM(f.factor_expansion), 0))::numeric, 2)
			   AS prevalencia_grave_pct
		FROM fact_seguridad_alimentaria_hogar f
		JOIN dim_choque_economico c ON c.id_choque_economico = f.id_choque_economico
		WHERE f.prob_ia_moderada_grave IS NOT NULL
		GROUP BY c.numero_choques
		ORDER BY c.numero_choques
	""",
	'R4 - Estrategias por severidad': """
		SELECT s.nombre_severidad AS severidad, e.numero_estrategias,
			   COUNT(*) AS hogares,
			   ROUND((SUM(f.factor_expansion) / NULLIF(
			   SUM(SUM(f.factor_expansion)) OVER (PARTITION BY s.nombre_severidad), 0
			   ))::numeric * 100, 2) AS distribucion_ponderada_pct
		FROM fact_seguridad_alimentaria_hogar f
		JOIN dim_nivel_severidad_ia s ON s.id_nivel_severidad_ia = f.id_nivel_severidad_ia
		JOIN dim_estrategia_afrontamiento e
		  ON e.id_estrategia_afrontamiento = f.id_estrategia_afrontamiento
		GROUP BY s.nombre_severidad, e.numero_estrategias
		ORDER BY s.nombre_severidad, e.numero_estrategias
	""",
	'R5 - Ingreso y vulnerabilidad': """
		SELECT i.codigo_quintil AS quintil_ingreso, i.nombre_quintil,
			   COUNT(*) AS hogares,
			   ROUND((SUM(f.factor_expansion * f.prob_ia_moderada_grave)
			   / NULLIF(SUM(f.factor_expansion), 0))::numeric, 2)
			   AS prevalencia_moderada_grave_pct,
			   ROUND((SUM(f.factor_expansion * f.prob_ia_grave)
			   / NULLIF(SUM(f.factor_expansion), 0))::numeric, 2)
			   AS prevalencia_grave_pct
		FROM fact_seguridad_alimentaria_hogar f
		JOIN dim_nivel_ingreso i ON i.id_nivel_ingreso = f.id_nivel_ingreso
		WHERE f.prob_ia_moderada_grave IS NOT NULL
		GROUP BY i.id_nivel_ingreso, i.codigo_quintil, i.nombre_quintil
		ORDER BY i.id_nivel_ingreso
	""",
}


def ejecutar_analitica():
	"""Ejecuta e imprime las consultas R1-R5 sobre la base cargada."""
	print('\nRESULTADOS ANALITICOS')
	print('=' * 70)
	try:
		with psycopg2.connect(**DB_CONFIG) as conexion:
			for requerimiento, consulta in CONSULTAS.items():
				resultado = pd.read_sql_query(consulta, conexion)
				print(f'\n{requerimiento}')
				print('-' * 70)
				print(resultado.to_string(index=False))
	except psycopg2.Error as error:
		raise RuntimeError(f'No fue posible ejecutar las consultas analiticas: {error}') from error
