from pathlib import Path

from clean import (
    limpiar_condiciones_vida,
    limpiar_servicios_hogar,
    limpiar_vivienda,
)
from dimensional_model import modelar
from analytics import ejecutar_analitica
from extract import (
    extraer_condiciones_vida,
    extraer_servicios_hogar,
    extraer_vivienda,
)
from load import cargar_modelo
from transform import transformar
from validate import validar_post_carga


BASE_DIR = Path(__file__).resolve().parent.parent
RUTA_SALIDA = BASE_DIR / 'data' / 'processed' / 'datos_transformados.csv'

def main():
    print("=" * 70)
    print("ETL PIPELINE - INSEGURIDAD ALIMENTARIA")
    print("=" * 70)

    print("\n[1/5] EXTRACCIÓN DE DATOS...")
    print("-" * 70)
    df_vivienda = extraer_vivienda()
    df_servicios_hogar = extraer_servicios_hogar()
    df_condiciones_vida = extraer_condiciones_vida()
    print(f"✓ Vivienda: {len(df_vivienda)} registros")
    print(f"✓ Servicios del hogar: {len(df_servicios_hogar)} registros")
    print(f"✓ Condiciones de vida: {len(df_condiciones_vida)} registros")

    print("\n[2/5] LIMPIEZA DE DATOS...")
    print("-" * 70)
    df_vivienda = limpiar_vivienda(df_vivienda)
    df_servicios_hogar = limpiar_servicios_hogar(df_servicios_hogar)
    df_condiciones_vida = limpiar_condiciones_vida(df_condiciones_vida)
    print("✓ Limpieza completada")

    print("\n[3/5] TRANSFORMACIÓN DE DATOS...")
    print("-" * 70)
    df_transformado = transformar(
        df_vivienda,
        df_servicios_hogar,
        df_condiciones_vida,
    )

    RUTA_SALIDA.parent.mkdir(parents=True, exist_ok=True)
    df_transformado.to_csv(RUTA_SALIDA, index=False, encoding='utf-8-sig')
    print(f"✓ Transformación completada: {len(df_transformado)} registros")
    print(f"✓ Resultado guardado en: {RUTA_SALIDA}")

    print("\n[4/5] MODELADO DIMENSIONAL...")
    print("-" * 70)
    modelo = modelar(df_transformado)
    print(f"✓ Modelo dimensional construido: {len(modelo)} tablas")

    print("\n[5/5] CARGA EN LA BASE DE DATOS...")
    print("-" * 70)
    cargar_modelo(modelo)
    validar_post_carga(modelo)
    ejecutar_analitica()
    print("\n✓ Pipeline ETL y analítica completados")


if __name__ == "__main__":
    main()