"""
Descarga MOLA MEGDR (NASA/PDS) 4 ppd y lo convierte a GeoTIFF con CRS de Marte.
"""

from __future__ import annotations

import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd
import rasterio
from pyproj import CRS
from rasterio.transform import from_bounds

OUT = Path(__file__).resolve().parent
UA = {"User-Agent": "30DaysMapChallenge/1.0 (educational)"}
BASE = "https://pds-geosciences.wustl.edu/mgs/mgs-m-mola-5-megdr-l3-v1/mgsl_300x/meg004/"
TIF = OUT / "mars_mola_dem_4ppd.tif"


def descargar() -> Path:
    for name in ["megt90n000cb.img", "megt90n000cb.lbl"]:
        dest = OUT / name
        if dest.exists() and dest.stat().st_size > 1000:
            continue
        print(f"Descargando {name}...")
        req = urllib.request.Request(BASE + name, headers=UA)
        with urllib.request.urlopen(req, timeout=180) as r:
            dest.write_bytes(r.read())
        print(f"  -> {dest.stat().st_size:,} bytes")
    return convertir()


def convertir() -> Path:
    raw = np.fromfile(OUT / "megt90n000cb.img", dtype=">i2").reshape(720, 1440).astype(
        "float32"
    )
    mars_geog = CRS.from_proj4("+proj=longlat +R=3396190 +no_defs +type=crs")
    mars_eq = CRS.from_proj4(
        "+proj=eqc +lat_ts=0 +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +R=3396190 +units=m +no_defs +type=crs"
    )
    transform = from_bounds(0.0, -90.0, 360.0, 90.0, 1440, 720)
    profile = {
        "driver": "GTiff",
        "height": 720,
        "width": 1440,
        "count": 1,
        "dtype": "float32",
        "crs": mars_geog,
        "transform": transform,
        "compress": "lzw",
    }
    with rasterio.open(TIF, "w", **profile) as dst:
        dst.write(raw, 1)
        dst.update_tags(
            BODY="Mars",
            SOURCE="NASA MGS MOLA MEGDR megt90n000cb",
            COORDINATE_SYSTEM="IAU2000 Planetocentric",
            UNIT="meters relative to GMM3 areoid",
        )
    (OUT / "mars_crs_geographic.wkt").write_text(mars_geog.to_wkt())
    (OUT / "mars_crs_equirectangular.wkt").write_text(mars_eq.to_wkt())

    sites = [
        ("Olympus Mons", 226.2, 18.65, "volcan"),
        ("Valles Marineris", 290.0, -14.0, "canyon"),
        ("Gale Crater (Curiosity)", 137.4, -5.4, "rover"),
        ("Jezero Crater (Perseverance)", 77.45, 18.44, "rover"),
        ("Hellas Basin", 70.0, -42.4, "basin"),
        ("North Pole Cap", 0.0, 85.0, "polo"),
        ("South Pole Cap", 0.0, -85.0, "polo"),
    ]
    pd.DataFrame(sites, columns=["nombre", "lon_este", "lat", "tipo"]).to_csv(
        OUT / "sitios_marte.csv", index=False
    )
    print(f"GeoTIFF: {TIF} ({TIF.stat().st_size:,} bytes)")
    print(f"Elevación: {raw.min():.0f} … {raw.max():.0f} m (areoid)")
    return TIF


if __name__ == "__main__":
    descargar()
