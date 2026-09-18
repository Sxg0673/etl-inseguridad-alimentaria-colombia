#Exporta los resultados R1--R5 desde la tabla transformada existente.

# Sirve para generar los CSV de consultas cuando 


from pathlib import Path

import pandas as pd

from dimensional_model import COLUMNAS_CHOQUE, COLUMNAS_ESTRATEGIA, NOMBRES_QUINTILES, ORDEN_QUINTILES


BASE_DIR = Path(__file__).resolve().parent.parent
ENTRADA = BASE_DIR / "data" / "processed" / "datos_transformados.csv"
SALIDA = BASE_DIR / "results"


def _prevalencias(df, grupos):
    """Replica las prevalencias ponderadas de R1, R2, R3 y R5."""
    validos = df[df["prob_ia_moderada_grave"].notna()].copy()
    validos["ponderador_mg"] = validos["factor_expansion"] * validos["prob_ia_moderada_grave"]
    validos["ponderador_grave"] = validos["factor_expansion"] * validos["prob_ia_grave"]
    resultado = validos.groupby(grupos, dropna=False).agg(
        hogares=("factor_expansion", "size"),
        factor_expansion=("factor_expansion", "sum"),
        ponderador_mg=("ponderador_mg", "sum"),
        ponderador_grave=("ponderador_grave", "sum"),
    ).reset_index()
    resultado["prevalencia_moderada_grave_pct"] = (
        resultado.pop("ponderador_mg") / resultado["factor_expansion"]
    ).round(2)
    resultado["prevalencia_grave_pct"] = (
        resultado.pop("ponderador_grave") / resultado["factor_expansion"]
    ).round(2)
    return resultado.drop(columns="factor_expansion")


def main():
    if not ENTRADA.exists():
        raise FileNotFoundError(f"No existe el archivo transformado: {ENTRADA}")

    df = pd.read_csv(ENTRADA)
    for columna in ["tiene_acueducto", "tiene_alcantarillado", *COLUMNAS_CHOQUE, *COLUMNAS_ESTRATEGIA]:
        df[columna] = df[columna].astype(str).str.lower().eq("true")

    SALIDA.mkdir(exist_ok=True)

    r1 = _prevalencias(df, ["nombre_region", "nombre_departamento"])
    r1 = r1.rename(columns={"nombre_region": "region", "nombre_departamento": "departamento"})
    r1 = r1.sort_values("prevalencia_moderada_grave_pct", ascending=False)

    r2 = _prevalencias(df, ["tiene_acueducto", "tiene_alcantarillado"])
    r2 = r2.sort_values(["tiene_acueducto", "tiene_alcantarillado"], ascending=False)

    df["numero_choques"] = df[COLUMNAS_CHOQUE].sum(axis=1)
    r3 = _prevalencias(df, ["numero_choques"]).sort_values("numero_choques")

    df["numero_estrategias"] = df[COLUMNAS_ESTRATEGIA].sum(axis=1)
    r4 = df.groupby(["nivel_severidad_ia", "numero_estrategias"], dropna=False).agg(
        hogares=("factor_expansion", "size"), factor_expansion=("factor_expansion", "sum")
    ).reset_index()
    r4["distribucion_ponderada_pct"] = (
        100 * r4["factor_expansion"] /
        r4.groupby("nivel_severidad_ia")["factor_expansion"].transform("sum")
    ).round(2)
    r4 = r4.drop(columns="factor_expansion").rename(columns={"nivel_severidad_ia": "severidad"})
    r4 = r4.sort_values(["severidad", "numero_estrategias"])

    r5 = _prevalencias(df, ["quintil_ingreso"])
    r5["nombre_quintil"] = r5["quintil_ingreso"].map(NOMBRES_QUINTILES)
    r5["_orden"] = r5["quintil_ingreso"].map({valor: indice for indice, valor in enumerate(ORDEN_QUINTILES)})
    r5 = r5.sort_values("_orden").drop(columns="_orden")

    for nombre, resultado in (("R1_distribucion_territorial.csv", r1), ("R2_servicios_publicos.csv", r2),
                              ("R3_choques_economicos.csv", r3), ("R4_estrategias_por_severidad.csv", r4),
                              ("R5_ingreso_y_vulnerabilidad.csv", r5)):
        ruta = SALIDA / nombre
        resultado.to_csv(ruta, index=False, encoding="utf-8-sig")
        print(f"Guardado: {ruta} ({len(resultado)} filas)")


if __name__ == "__main__":
    main()