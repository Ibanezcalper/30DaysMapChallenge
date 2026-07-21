"""
Descarga y prepara insumos del Día 8 (HD):
1. Afluencia diaria Metro (Datos Abiertos CDMX)
2. Estaciones STC Metro (shapefile)
3. Nube de puntos HD = abordajes virtuales ponderados por afluencia
"""

from __future__ import annotations

import re
import unicodedata
import urllib.request
import zipfile
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parent
AFLUENCIA_CSV = OUT / "afluencia_metro_simple.csv"
SHP_ZIP = OUT / "stcmetro_shp.zip"
SHP_DIR = OUT / "stcmetro_shp"
NUBE_PARQUET = OUT / "nube_abordajes_hd.parquet"
ESTACIONES_JOIN = OUT / "estaciones_afluencia_mes.csv"

UA = {"User-Agent": "30DaysMapChallenge/1.0 (educational)"}

# Periodo reciente para el mapa HD (un mes completo)
ANIO, MES = 2025, 11  # noviembre 2025
PUNTOS_POR_MIL = 8  # ~8 puntos por cada 1,000 pasajeros/mes → nube densa
MAX_PUNTOS = 250_000
JITTER_M = 180  # metros de dispersión alrededor de la estación


def _get(url: str, dest: Path) -> None:
    print(f"Descargando {url}")
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=180) as r:
        dest.write_bytes(r.read())
    print(f"  -> {dest} ({dest.stat().st_size:,} bytes)")


def descargar_afluencia() -> None:
    if AFLUENCIA_CSV.exists() and AFLUENCIA_CSV.stat().st_size > 1_000_000:
        print(f"Afluencia ya existe: {AFLUENCIA_CSV}")
        return
    api = "https://datos.cdmx.gob.mx/api/3/action/package_show?id=afluencia-diaria-del-metro-cdmx"
    import json

    req = urllib.request.Request(api, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        pkg = json.load(r)
    url = pkg["result"]["resources"][0]["url"]
    _get(url, AFLUENCIA_CSV)


def descargar_estaciones() -> None:
    shp = SHP_DIR / "STC_Metro_estaciones_utm14n.shp"
    if shp.exists():
        print(f"Shapefile ya existe: {shp}")
        return
    api = "https://datos.cdmx.gob.mx/api/3/action/package_show?id=lineas-y-estaciones-del-metro"
    import json

    req = urllib.request.Request(api, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        pkg = json.load(r)
    url = pkg["result"]["resources"][0]["url"]
    _get(url, SHP_ZIP)
    with zipfile.ZipFile(SHP_ZIP, "r") as z:
        z.extractall(OUT)
    print(f"Extraído en {SHP_DIR}")


def fix_mojibake(s: str) -> str:
    try:
        return s.encode("latin-1").decode("utf-8")
    except Exception:
        return s


def norm_name(s: str) -> str:
    s = fix_mojibake(str(s)).lower().strip()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[^a-z0-9]+", "", s)
    aliases = {
        "ninosheroes": "ninoheroes",
        "mixiuhca": "mixhiuca",
        "lavillabasilica": "lavillabasilica",
    }
    return aliases.get(s, s)


def generar_nube() -> None:
    df = pd.read_csv(AFLUENCIA_CSV, encoding="utf-8")
    df["estacion"] = df["estacion"].map(fix_mojibake)
    df["fecha"] = pd.to_datetime(df["fecha"])
    mes = df[(df["fecha"].dt.year == ANIO) & (df["fecha"].dt.month == MES)].copy()
    if mes.empty:
        # fallback: último mes disponible
        last = df["fecha"].max()
        mes = df[(df["fecha"].dt.year == last.year) & (df["fecha"].dt.month == last.month)].copy()
        print(f"Mes {ANIO}-{MES:02d} vacío; usando {last.year}-{last.month:02d}")
    else:
        print(f"Usando afluencia {ANIO}-{MES:02d}: {len(mes):,} filas")

    agg = (
        mes.groupby("estacion", as_index=False)["afluencia"]
        .sum()
        .rename(columns={"afluencia": "afluencia_mes"})
    )
    agg["key"] = agg["estacion"].map(norm_name)

    gdf = gpd.read_file(SHP_DIR / "STC_Metro_estaciones_utm14n.shp")
    gdf = gdf.to_crs(epsg=4326)
    gdf["key"] = gdf["NOMBRE"].map(norm_name)
    # Un punto por estación (si hay duplicados por línea, tomamos el primero)
    gdf_u = gdf.drop_duplicates(subset="key", keep="first")

    joined = agg.merge(
        gdf_u[["key", "NOMBRE", "LINEA", "geometry"]],
        on="key",
        how="inner",
    )
    print(f"Estaciones unidas: {len(joined)} / {len(agg)}")
    joined_gdf = gpd.GeoDataFrame(joined, geometry="geometry", crs="EPSG:4326")
    joined_gdf.to_crs(epsg=4326).drop(columns="geometry").assign(
        lon=joined_gdf.geometry.x, lat=joined_gdf.geometry.y
    ).to_csv(ESTACIONES_JOIN, index=False)

    # Proyectar a metros para jitter
    metric = joined_gdf.to_crs(epsg=32614)
    total_pax = metric["afluencia_mes"].sum()
    # Escala de puntos
    n_target = int(min(MAX_PUNTOS, max(50_000, total_pax / 1000 * PUNTOS_POR_MIL)))
    weights = metric["afluencia_mes"] / total_pax
    counts = np.maximum(1, np.round(weights * n_target).astype(int))
    # Ajuste fino al tope
    while counts.sum() > MAX_PUNTOS:
        counts = np.maximum(1, (counts * 0.95).astype(int))

    rng = np.random.default_rng(42)
    xs, ys, estaciones, lineas, pesos = [], [], [], [], []
    for row, n in zip(metric.itertuples(), counts):
        jx = rng.normal(0, JITTER_M / 2.5, size=n)
        jy = rng.normal(0, JITTER_M / 2.5, size=n)
        xs.append(row.geometry.x + jx)
        ys.append(row.geometry.y + jy)
        estaciones.extend([row.NOMBRE] * n)
        lineas.extend([str(row.LINEA)] * n)
        pesos.extend([row.afluencia_mes] * n)

    x = np.concatenate(xs)
    y = np.concatenate(ys)
    cloud = gpd.GeoDataFrame(
        {
            "estacion": estaciones,
            "linea": lineas,
            "afluencia_mes_estacion": pesos,
        },
        geometry=gpd.points_from_xy(x, y),
        crs="EPSG:32614",
    ).to_crs(epsg=4326)
    cloud["lon"] = cloud.geometry.x
    cloud["lat"] = cloud.geometry.y

    # Guardar sin geometría (más ligero) + columnas lon/lat
    out_df = pd.DataFrame(
        {
            "lon": cloud["lon"].astype("float32"),
            "lat": cloud["lat"].astype("float32"),
            "estacion": cloud["estacion"],
            "linea": cloud["linea"],
            "afluencia_mes_estacion": cloud["afluencia_mes_estacion"].astype("int32"),
        }
    )
    out_df.to_parquet(NUBE_PARQUET, index=False)
    print(f"Nube HD: {len(out_df):,} puntos -> {NUBE_PARQUET}")
    print(f"Top 5 estaciones por afluencia del mes:")
    print(
        joined.nlargest(5, "afluencia_mes")[["NOMBRE", "afluencia_mes"]].to_string(index=False)
    )


def main() -> None:
    descargar_afluencia()
    descargar_estaciones()
    generar_nube()


if __name__ == "__main__":
    main()
