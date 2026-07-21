"""
Descarga un DEM de la zona metropolitana de CDMX ensamblando tiles Terrarium
(AWS / Mapzen elevation tiles, derivados de SRTM y otras fuentes NASA/OSM).

Fuente: https://github.com/tilezen/joerd
"""

from __future__ import annotations

import io
import urllib.request
from pathlib import Path

import mercantile
import numpy as np
import rasterio
from PIL import Image
from rasterio.transform import from_bounds

OUT_DIR = Path(__file__).resolve().parent
OUT_TIF = OUT_DIR / "dem_cdmx_srtm_proxy.tif"

# Bounding box amplio: Valle de México + Ajusco / sierras
WEST, SOUTH, EAST, NORTH = -99.35, 19.05, -98.90, 19.60
ZOOM = 10
BASE_URL = "https://s3.amazonaws.com/elevation-tiles-prod/terrarium"


def terrarium_to_elev(rgb: np.ndarray) -> np.ndarray:
    r = rgb[:, :, 0].astype(np.float32)
    g = rgb[:, :, 1].astype(np.float32)
    b = rgb[:, :, 2].astype(np.float32)
    return (r * 256.0 + g + b / 256.0) - 32768.0


def descargar_dem() -> Path:
    tiles = list(mercantile.tiles(WEST, SOUTH, EAST, NORTH, zooms=ZOOM))
    xs = sorted({t.x for t in tiles})
    ys = sorted({t.y for t in tiles})
    min_x, max_x = xs[0], xs[-1]
    min_y, max_y = ys[0], ys[-1]
    n_cols = max_x - min_x + 1
    n_rows = max_y - min_y + 1
    tile_size = 256

    print(f"Descargando {len(tiles)} tiles Terrarium @ z={ZOOM}...")
    mosaic = np.full((n_rows * tile_size, n_cols * tile_size), np.nan, dtype=np.float32)

    for t in tiles:
        url = f"{BASE_URL}/{t.z}/{t.x}/{t.y}.png"
        with urllib.request.urlopen(url, timeout=60) as resp:
            img = Image.open(io.BytesIO(resp.read())).convert("RGB")
        elev = terrarium_to_elev(np.array(img))
        row0 = (t.y - min_y) * tile_size
        col0 = (t.x - min_x) * tile_size
        mosaic[row0 : row0 + tile_size, col0 : col0 + tile_size] = elev

    ul = mercantile.ul(min_x, min_y, ZOOM)
    br = mercantile.bounds(max_x, max_y, ZOOM)
    west, north = ul.lng, ul.lat
    east, south = br.east, br.south

    transform = from_bounds(west, south, east, north, mosaic.shape[1], mosaic.shape[0])
    nodata = -9999.0
    data = np.where(np.isnan(mosaic), nodata, mosaic).astype(np.float32)

    profile = {
        "driver": "GTiff",
        "height": data.shape[0],
        "width": data.shape[1],
        "count": 1,
        "dtype": "float32",
        "crs": "EPSG:4326",
        "transform": transform,
        "compress": "lzw",
        "nodata": nodata,
    }
    with rasterio.open(OUT_TIF, "w", **profile) as dst:
        dst.write(data, 1)

    valid = data[data != nodata]
    print(f"Guardado: {OUT_TIF}")
    print(f"Elevación: {valid.min():.0f} – {valid.max():.0f} m s.n.m.")
    return OUT_TIF


if __name__ == "__main__":
    descargar_dem()
