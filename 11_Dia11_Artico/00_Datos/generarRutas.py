"""
Genera rutas globales (geodésicas) para el Día 11:
- Ruta tradicional Europa–Asia vía Suez
- Ruta Ártica (Northern Sea Route / Paso del Noreste)
- Ruta de suministro Antártida (aprox. Punta Arenas → Base)

Fuente de geometrías de fondo: Natural Earth (descargarDatosNE.py).
"""

from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import pandas as pd
from pyproj import Geod
from shapely.geometry import LineString

OUT = Path(__file__).resolve().parent
GEOD = Geod(ellps="WGS84")


def geodesic_line(lon1, lat1, lon2, lat2, n=80) -> LineString:
    pts = GEOD.npts(lon1, lat1, lon2, lat2, n)
    coords = [(lon1, lat1), *pts, (lon2, lat2)]
    return LineString(coords)


def length_km(line: LineString) -> float:
    # suma de segmentos geodésicos
    coords = list(line.coords)
    total = 0.0
    for (x0, y0), (x1, y1) in zip(coords, coords[1:]):
        _, _, d = GEOD.inv(x0, y0, x1, y1)
        total += d
    return total / 1000.0


def multi_leg(waypoints: list[tuple[float, float]], n_per=40) -> LineString:
    parts = []
    for (a, b) in zip(waypoints, waypoints[1:]):
        seg = geodesic_line(a[0], a[1], b[0], b[1], n=n_per)
        parts.extend(list(seg.coords)[:-1])
    parts.append(waypoints[-1])
    return LineString(parts)


def main() -> None:
    # Rotterdam -> Shanghai
    rotterdam = (4.48, 51.92)
    shanghai = (121.47, 31.23)
    # Vía Suez (waypoints aproximados)
    suez = multi_leg(
        [
            rotterdam,
            (-5.0, 36.0),  # Gibraltar approach
            (10.0, 37.5),  # Med
            (32.3, 31.0),  # Suez
            (43.0, 12.5),  # Bab el-Mandeb
            (60.0, 15.0),  # Arabian Sea
            (80.0, 5.0),  # Indian Ocean
            (100.0, 5.0),  # Malacca approach
            (105.0, 2.0),
            shanghai,
        ]
    )
    # Northern Sea Route (Ártico)
    arctic = multi_leg(
        [
            rotterdam,
            (10.0, 60.0),  # North Sea / Norway
            (25.0, 70.0),  # Barents
            (45.0, 72.0),
            (70.0, 73.0),  # Kara
            (100.0, 74.0),  # Laptev
            (140.0, 72.0),  # East Siberian
            (170.0, 65.0),  # Bering approach
            (170.0, 55.0),
            (150.0, 45.0),
            shanghai,
        ]
    )
    # Antártida: Punta Arenas -> Amundsen-Scott (polo) / McMurdo approx
    punta_arenas = (-70.91, -53.16)
    mcmurdo = (166.67, -77.85)
    antarctic = geodesic_line(punta_arenas[0], punta_arenas[1], mcmurdo[0], mcmurdo[1], n=100)

    rows = [
        {
            "ruta": "Suez (tradicional)",
            "tipo": "comercio_europa_asia",
            "polo": "ninguno",
            "geometry": suez,
            "km": length_km(suez),
        },
        {
            "ruta": "Northern Sea Route (Ártico)",
            "tipo": "comercio_europa_asia",
            "polo": "artico",
            "geometry": arctic,
            "km": length_km(arctic),
        },
        {
            "ruta": "Punta Arenas → McMurdo (Antártida)",
            "tipo": "logistica_cientifica",
            "polo": "antartico",
            "geometry": antarctic,
            "km": length_km(antarctic),
        },
    ]
    gdf = gpd.GeoDataFrame(rows, crs="EPSG:4326")
    out = OUT / "rutas_globales.geojson"
    gdf.to_file(out, driver="GeoJSON")
    gdf.drop(columns="geometry").to_csv(OUT / "rutas_globales_resumen.csv", index=False)
    print(gdf[["ruta", "km", "polo"]].to_string(index=False))
    print(f"Guardado: {out}")

    # Ahorro Ártico vs Suez
    km_suez = float(gdf.loc[gdf["polo"] == "ninguno", "km"].iloc[0])
    km_arc = float(gdf.loc[gdf["polo"] == "artico", "km"].iloc[0])
    ahorro = (km_suez - km_arc) / km_suez * 100
    print(f"Ahorro NSR vs Suez: {ahorro:.1f}% ({km_suez - km_arc:.0f} km)")


if __name__ == "__main__":
    main()
