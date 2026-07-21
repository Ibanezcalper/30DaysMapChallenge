"""
Genera un dataset sintético de puntos de entrega (dark stores) en CDMX
con errores típicos de GPS: coordenadas invertidas, signos rotos, nulos y outliers.

Fuente: datos propios (sintéticos) inspirados en el bounding box urbano de CDMX.
"""

from pathlib import Path

import numpy as np
import pandas as pd

N_TOTAL = 500
SEED = 42
OUTPUT = Path(__file__).resolve().parent / "puntos_entrega_sucios.csv"

# Bounding box aproximado de CDMX (WGS84)
LAT_MIN, LAT_MAX = 19.05, 19.55
LON_MIN, LON_MAX = -99.35, -98.95

ALCALDIAS = [
    "Cuauhtémoc",
    "Miguel Hidalgo",
    "Benito Juárez",
    "Coyoacán",
    "Álvaro Obregón",
    "Iztapalapa",
    "Gustavo A. Madero",
    "Tlalpan",
    "Azcapotzalco",
    "Venustiano Carranza",
]


def generar_puntos_limpios(n: int, rng: np.random.Generator) -> pd.DataFrame:
    """Simula dark stores con coordenadas válidas dentro de CDMX."""
    lat = rng.uniform(LAT_MIN, LAT_MAX, n)
    lon = rng.uniform(LON_MIN, LON_MAX, n)
    return pd.DataFrame(
        {
            "id_punto": [f"DS-{i:04d}" for i in range(1, n + 1)],
            "alcaldia": rng.choice(ALCALDIAS, n),
            "latitud": lat,
            "longitud": lon,
            "error_inyectado": "ninguno",
            "latitud_real": lat,
            "longitud_real": lon,
        }
    )


def inyectar_errores(df: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    """Corrompe ~25% de los registros con fallas típicas de captura GPS."""
    out = df.copy()
    n = len(out)
    idx = np.arange(n)
    rng.shuffle(idx)

    # Particiones de corrupción (aprox. 25% del dataset)
    n_swap = int(n * 0.08)  # lat/lon intercambiados
    n_sign = int(n * 0.05)  # longitud positiva (signo perdido)
    n_null = int(n * 0.04)  # nulos o ceros
    n_outlier = int(n * 0.05)  # puntos fuera de México
    n_typo = int(n * 0.03)  # tipazo decimal (orden de magnitud)

    cursor = 0

    # 1) Coordenadas invertidas (lat <-> lon)
    slice_idx = idx[cursor : cursor + n_swap]
    cursor += n_swap
    for i in slice_idx:
        out.loc[i, "latitud"], out.loc[i, "longitud"] = (
            out.loc[i, "longitud"],
            out.loc[i, "latitud"],
        )
        out.loc[i, "error_inyectado"] = "coordenadas_invertidas"

    # 2) Signo perdido en longitud (CDMX queda en Asia)
    slice_idx = idx[cursor : cursor + n_sign]
    cursor += n_sign
    for i in slice_idx:
        out.loc[i, "longitud"] = abs(out.loc[i, "longitud"])
        out.loc[i, "error_inyectado"] = "signo_longitud"

    # 3) Nulos / ceros
    slice_idx = idx[cursor : cursor + n_null]
    cursor += n_null
    for j, i in enumerate(slice_idx):
        if j % 2 == 0:
            out.loc[i, "latitud"] = np.nan
            out.loc[i, "longitud"] = np.nan
            out.loc[i, "error_inyectado"] = "nulos"
        else:
            out.loc[i, "latitud"] = 0.0
            out.loc[i, "longitud"] = 0.0
            out.loc[i, "error_inyectado"] = "ceros"

    # 4) Outliers geográficos extremos
    outliers = [
        (0.0, -90.0),  # Golfo de Guinea
        (40.71, -74.00),  # Nueva York
        (-33.45, -70.66),  # Santiago de Chile
        (35.68, 139.69),  # Tokio
        (19.43, 0.0),  # Meridiano de Greenwich
        (90.0, -99.13),  # Polo Norte
        (19.43, -180.0),  # Antimeridiano
        (25.67, -100.31),  # Monterrey (fuera de CDMX)
    ]
    slice_idx = idx[cursor : cursor + n_outlier]
    cursor += n_outlier
    for j, i in enumerate(slice_idx):
        lat, lon = outliers[j % len(outliers)]
        # Pequeño ruido para no duplicar exactamente
        out.loc[i, "latitud"] = lat + rng.normal(0, 0.05)
        out.loc[i, "longitud"] = lon + rng.normal(0, 0.05)
        out.loc[i, "error_inyectado"] = "outlier_geografico"

    # 5) Tipazo: latitud con un dígito de más (194.x en vez de 19.4)
    slice_idx = idx[cursor : cursor + n_typo]
    for i in slice_idx:
        out.loc[i, "latitud"] = out.loc[i, "latitud"] * 10
        out.loc[i, "error_inyectado"] = "tipazo_decimal"

    return out


def main() -> None:
    rng = np.random.default_rng(SEED)
    limpio = generar_puntos_limpios(N_TOTAL, rng)
    sucio = inyectar_errores(limpio, rng)

    # Columnas "reales" solo para auditoría interna; el notebook no las usa
    # como verdad absoluta en la limpieza (simula producción).
    export_cols = ["id_punto", "alcaldia", "latitud", "longitud"]
    sucio[export_cols].to_csv(OUTPUT, index=False, encoding="utf-8")

    # Guardamos también la versión con etiquetas de error para validar el pipeline
    audit_path = OUTPUT.with_name("puntos_entrega_sucios_auditoria.csv")
    sucio.to_csv(audit_path, index=False, encoding="utf-8")

    print(f"Dataset sucio: {OUTPUT}")
    print(f"Auditoría:     {audit_path}")
    print("\nDistribución de errores inyectados:")
    print(sucio["error_inyectado"].value_counts().to_string())


if __name__ == "__main__":
    main()
