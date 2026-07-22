"""
Descarga subset Sentinel-2 (Earth Search / AWS COGs) para el Día 9.
Bandas: blue, green, red, nir — zona Centro/Poniente CDMX.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import rasterio
from pystac_client import Client
from rasterio.warp import transform_bounds
from rasterio.windows import from_bounds

OUT = Path(__file__).resolve().parent
TIF = OUT / "sentinel2_cdmx_subset.tif"
META = OUT / "sentinel2_meta.txt"

BBOX = [-99.22, 19.30, -99.08, 19.42]  # WGS84
BANDS = ["blue", "green", "red", "nir"]


def descargar() -> Path:
    if TIF.exists() and TIF.stat().st_size > 1_000_000:
        print(f"Ya existe: {TIF}")
        return TIF

    catalog = Client.open("https://earth-search.aws.element84.com/v1")
    search = catalog.search(
        collections=["sentinel-2-l2a"],
        bbox=BBOX,
        datetime="2024-03-01/2024-05-31",
        query={"eo:cloud_cover": {"lt": 15}},
        max_items=10,
    )
    item = sorted(
        list(search.items()), key=lambda it: it.properties.get("eo:cloud_cover", 99)
    )[0]
    print(f"Item: {item.id} | nube={item.properties.get('eo:cloud_cover')}")

    arrays = []
    profile = None
    for name in BANDS:
        href = item.assets[name].href
        with rasterio.open(href) as src:
            left, bottom, right, top = transform_bounds("EPSG:4326", src.crs, *BBOX)
            window = from_bounds(left, bottom, right, top, transform=src.transform)
            data = src.read(1, window=window).astype("float32")
            win_transform = src.window_transform(window)
            arrays.append(data)
            if profile is None:
                profile = src.profile.copy()
                profile.update(
                    {
                        "height": data.shape[0],
                        "width": data.shape[1],
                        "count": 4,
                        "dtype": "float32",
                        "transform": win_transform,
                        "compress": "lzw",
                        "driver": "GTiff",
                    }
                )

    h = min(a.shape[0] for a in arrays)
    w = min(a.shape[1] for a in arrays)
    arrays = [a[:h, :w] for a in arrays]
    profile.update(height=h, width=w)

    with rasterio.open(TIF, "w", **profile) as dst:
        for i, (a, name) in enumerate(zip(arrays, BANDS), 1):
            dst.write(a, i)
            dst.set_band_description(i, name)

    META.write_text(
        f"item={item.id}\ncloud={item.properties.get('eo:cloud_cover')}\n"
        f"date={item.datetime}\nbbox={BBOX}\ncrs={profile['crs']}\nshape={h}x{w}\n"
    )
    print(f"Guardado: {TIF} ({TIF.stat().st_size:,} bytes)")
    return TIF


if __name__ == "__main__":
    descargar()
