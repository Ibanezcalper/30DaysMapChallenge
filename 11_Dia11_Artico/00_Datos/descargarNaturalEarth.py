"""Descarga capas Natural Earth 110m para el Día 11."""

from __future__ import annotations

import urllib.request
import zipfile
from pathlib import Path

OUT = Path(__file__).resolve().parent
UA = {"User-Agent": "30DaysMapChallenge/1.0 (educational)"}

FILES = {
    "ne_110m_land.zip": "https://naciscdn.org/naturalearth/110m/physical/ne_110m_land.zip",
    "ne_110m_coastline.zip": "https://naciscdn.org/naturalearth/110m/physical/ne_110m_coastline.zip",
    "ne_110m_admin_0_countries.zip": "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip",
    "ne_110m_graticules_30.zip": "https://naciscdn.org/naturalearth/110m/physical/ne_110m_graticules_30.zip",
}


def main() -> None:
    for name, url in FILES.items():
        dest = OUT / name
        folder = OUT / name.replace(".zip", "")
        if (folder / f"{folder.name}.shp").exists() or any(folder.glob("*.shp")):
            print(f"OK {folder.name}")
            continue
        print(f"Descargando {name}...")
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=120) as r:
            dest.write_bytes(r.read())
        with zipfile.ZipFile(dest) as z:
            z.extractall(folder)
        print(f"  -> {folder}")


if __name__ == "__main__":
    main()
