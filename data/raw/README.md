# Datos crudos — Encuesta Nacional de Calidad de Vida (ECV) 2025

Los archivos de esta carpeta no se incluyen en el repositorio por su tamaño. Para reproducir el pipeline, descárgalos siguiendo estos pasos.

## Fuente

- **Operación estadística:** Encuesta Nacional de Calidad de Vida - ECV - 2025
- **Productor:** DANE, Dirección de Metodología y Producción Estadística (DIMPE)
- **Catálogo:** DANE-DIMPE-ECV-2025

## Cómo descargar

1. Ingresa a: https://microdatos.dane.gov.co/index.php/catalog/905/get-microdata
2. Si el portal lo solicita, completa el registro simple (nombre, correo, propósito de uso).
3. Descarga los siguientes tres archivos exactamente con estos nombres:

| Archivo en el portal DANE | Guardar como |
|---|---|
| DBF-ECV-Datos_vivienda-2025 | `Datos de la vivienda.csv` |
| DBF-ECV-Servicios_hogar-2025 | `Servicios del hogar.csv` |
| DBF-ECV-Condiciones_vida_hogar_tenencia_bienes-2025 | `Condiciones de vida del hogar y tenencia de bienes.csv` |

4. Coloca los tres archivos `.csv` directamente en esta carpeta (`data/raw/`), sin subcarpetas.

## Formato esperado

- Separador: `;`
- Codificación: `utf-8-sig`
- Todas las columnas deben leerse como texto (`dtype=str`) para no perder ceros a la izquierda en los códigos.
