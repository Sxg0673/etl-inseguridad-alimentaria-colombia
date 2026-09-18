-- Consultas analiticas del modelo estrella.
-- Las prevalencias se calculan con factor_expansion y probabilidades FIES
-- expresadas en porcentaje. Se excluyen los hogares sin dato FIES.

-- R1. Distribucion territorial de la inseguridad alimentaria.
SELECT
	g.nombre_region AS region,
	g.nombre_departamento AS departamento,
	COUNT(*) AS hogares,
	ROUND(
		(SUM(f.factor_expansion * f.prob_ia_moderada_grave)
		 / NULLIF(SUM(f.factor_expansion), 0))::numeric, 2
	) AS prevalencia_moderada_grave_pct,
	ROUND(
		(SUM(f.factor_expansion * f.prob_ia_grave)
		 / NULLIF(SUM(f.factor_expansion), 0))::numeric, 2
	) AS prevalencia_grave_pct
FROM fact_seguridad_alimentaria_hogar f
JOIN dim_geografia g ON g.id_geografia = f.id_geografia
WHERE f.prob_ia_moderada_grave IS NOT NULL
GROUP BY g.nombre_region, g.nombre_departamento
ORDER BY prevalencia_moderada_grave_pct DESC;

-- R2. Asociacion entre servicios publicos y vulnerabilidad alimentaria.
SELECT
	f.tiene_acueducto,
	f.tiene_alcantarillado,
	COUNT(*) AS hogares,
	ROUND(
		(SUM(f.factor_expansion * f.prob_ia_moderada_grave)
		 / NULLIF(SUM(f.factor_expansion), 0))::numeric, 2
	) AS prevalencia_moderada_grave_pct,
	ROUND(
		(SUM(f.factor_expansion * f.prob_ia_grave)
		 / NULLIF(SUM(f.factor_expansion), 0))::numeric, 2
	) AS prevalencia_grave_pct
FROM fact_seguridad_alimentaria_hogar f
WHERE f.prob_ia_moderada_grave IS NOT NULL
GROUP BY f.tiene_acueducto, f.tiene_alcantarillado
ORDER BY f.tiene_acueducto DESC, f.tiene_alcantarillado DESC;

-- R3. Relacion entre cantidad de choques economicos e inseguridad alimentaria.
SELECT
	c.numero_choques,
	COUNT(*) AS hogares,
	ROUND(
		(SUM(f.factor_expansion * f.prob_ia_moderada_grave)
		 / NULLIF(SUM(f.factor_expansion), 0))::numeric, 2
	) AS prevalencia_moderada_grave_pct,
	ROUND(
		(SUM(f.factor_expansion * f.prob_ia_grave)
		 / NULLIF(SUM(f.factor_expansion), 0))::numeric, 2
	) AS prevalencia_grave_pct
FROM fact_seguridad_alimentaria_hogar f
JOIN dim_choque_economico c ON c.id_choque_economico = f.id_choque_economico
WHERE f.prob_ia_moderada_grave IS NOT NULL
GROUP BY c.numero_choques
ORDER BY c.numero_choques;

-- R4. Estrategias de afrontamiento segun severidad.
SELECT
	s.nombre_severidad AS severidad,
	e.numero_estrategias,
	COUNT(*) AS hogares,
	ROUND(
		(SUM(f.factor_expansion) / NULLIF(SUM(SUM(f.factor_expansion)) OVER
			(PARTITION BY s.nombre_severidad), 0))::numeric * 100, 2
	) AS distribucion_ponderada_pct
FROM fact_seguridad_alimentaria_hogar f
JOIN dim_nivel_severidad_ia s
	ON s.id_nivel_severidad_ia = f.id_nivel_severidad_ia
JOIN dim_estrategia_afrontamiento e
	ON e.id_estrategia_afrontamiento = f.id_estrategia_afrontamiento
GROUP BY s.nombre_severidad, e.numero_estrategias
ORDER BY s.nombre_severidad, e.numero_estrategias;

-- R5. Gradiente de vulnerabilidad segun quintil de ingreso.
SELECT
	i.codigo_quintil AS quintil_ingreso,
	i.nombre_quintil,
	COUNT(*) AS hogares,
	ROUND(
		(SUM(f.factor_expansion * f.prob_ia_moderada_grave)
		 / NULLIF(SUM(f.factor_expansion), 0))::numeric, 2
	) AS prevalencia_moderada_grave_pct,
	ROUND(
		(SUM(f.factor_expansion * f.prob_ia_grave)
		 / NULLIF(SUM(f.factor_expansion), 0))::numeric, 2
	) AS prevalencia_grave_pct
FROM fact_seguridad_alimentaria_hogar f
JOIN dim_nivel_ingreso i ON i.id_nivel_ingreso = f.id_nivel_ingreso
WHERE f.prob_ia_moderada_grave IS NOT NULL
GROUP BY i.id_nivel_ingreso, i.codigo_quintil, i.nombre_quintil
ORDER BY i.id_nivel_ingreso;
