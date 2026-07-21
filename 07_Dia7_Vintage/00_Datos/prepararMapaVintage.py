"""
Georreferencia el mapa vintage con Thin Plate Spline (TPS / rubber-sheet).

A diferencia de un affine (que solo traslada/rota/escala el rectángulo),
el TPS deforma el grabado para que CADA GCP caiga en su lon/lat real.
El mapa antiguo pierde proporciones: es el costo de anclarlo al mundo moderno.
"""

from __future__ import annotations

import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd
import rasterio
from PIL import Image, ImageEnhance, ImageOps
from rasterio.transform import from_bounds
from skimage.transform import ThinPlateSplineTransform, warp

OUT_DIR = Path(__file__).resolve().parent
SRC_NAME = "tenochtitlan_1524_nuremberg.jpg"
WORK_NAME = "mapa_vintage_tenochtitlan.png"
GCP_NAME = "gcps_vintage.csv"
GEOTIFF_4326 = "tenochtitlan_1524_tps_4326.tif"
GEOTIFF_3857 = "tenochtitlan_1524_tps_3857.tif"

WIKI_URL = (
    "https://upload.wikimedia.org/wikipedia/commons/thumb/"
    "c/c3/Map_of_Tenochtitlan%2C_1524.jpg/"
    "1920px-Map_of_Tenochtitlan%2C_1524.jpg"
)

# Canvas geográfico de salida (Valle / isla + calzadas)
WEST, EAST = -99.175, -99.085
SOUTH, NORTH = 19.395, 19.475
OUT_W, OUT_H = 1800, 1600


def descargar_si_falta() -> Path:
    dest = OUT_DIR / SRC_NAME
    if dest.exists() and dest.stat().st_size > 100_000:
        return dest
    req = urllib.request.Request(
        WIKI_URL, headers={"User-Agent": "30DaysMapChallenge/1.0 (educational)"}
    )
    with urllib.request.urlopen(req, timeout=90) as resp:
        dest.write_bytes(resp.read())
    return dest


def preparar_imagen(src: Path) -> Image.Image:
    """Recorta panel de la isla y orienta Norte arriba, Oeste a la izquierda."""
    img = Image.open(src).convert("RGB")
    w, h = img.size
    crop = img.crop((int(w * 0.48), 0, w, h))
    # Original: Oeste arriba → ROTATE_90 (CCW) ⇒ Norte arriba, Oeste izquierda
    north_up = crop.transpose(Image.Transpose.ROTATE_90)
    north_up = ImageOps.autocontrast(north_up, cutoff=1)
    north_up = ImageEnhance.Color(north_up).enhance(0.88)
    north_up = ImageEnhance.Contrast(north_up).enhance(1.05)
    north_up.save(OUT_DIR / WORK_NAME, format="PNG")
    return north_up


def lonlat_to_dst(lon: float, lat: float) -> tuple[float, float]:
    """lon/lat → píxel en el canvas de salida (col, row)."""
    col = (lon - WEST) / (EAST - WEST) * (OUT_W - 1)
    row = (NORTH - lat) / (NORTH - SOUTH) * (OUT_H - 1)
    return col, row


def generar_gcps(width: int, height: int) -> pd.DataFrame:
    """
    GCPs: píxeles del grabado (orientado N-arriba) ↔ coordenadas modernas.

    El grabado es esquemático; los puntos fuerzan el rubber-sheet aunque
    distorsionen distancias del mapa antiguo.
    """
    # --- píxeles aproximados en el grabado (N↑ O←) ---
    # Centro del recinto sagrado / Templo Mayor
    cx, cy = width * 0.50, height * 0.48
    # Extremos de calzadas en el borde de la isla circular (~radio 0.28 del frame)
    rx, ry = width * 0.28, height * 0.30

    rows = [
        # nombre, px, py, lon, lat (coords modernas WGS84)
        ("templo_mayor", cx, cy, -99.1317, 19.4346),
        # Calzadas hacia los rumbos históricos
        ("calzada_norte_tepeyac", cx, cy - ry, -99.1310, 19.4580),
        ("calzada_sur_iztapalapa", cx, cy + ry, -99.1305, 19.4120),
        ("calzada_oeste_tacuba", cx - rx, cy, -99.1550, 19.4335),
        ("calzada_este_texcoco", cx + rx, cy, -99.1080, 19.4350),
        # Orillas / pueblos del lago (anclan el círculo del agua)
        ("orilla_NO", cx - rx * 0.85, cy - ry * 0.85, -99.1500, 19.4520),
        ("orilla_NE", cx + rx * 0.85, cy - ry * 0.85, -99.1120, 19.4520),
        ("orilla_SO", cx - rx * 0.85, cy + ry * 0.85, -99.1500, 19.4180),
        ("orilla_SE", cx + rx * 0.85, cy + ry * 0.85, -99.1120, 19.4180),
        # Mercado / plaza junto al recinto
        ("plaza_mercado", cx - width * 0.06, cy + height * 0.02, -99.1365, 19.4330),
        # Chapultepec / acueducto (Oeste, un poco al sur)
        ("acueducto_oeste", cx - rx * 1.15, cy + ry * 0.25, -99.1620, 19.4250),
        # Extremo norte del lago (dique / orilla lejana)
        ("orilla_norte_lago", cx, height * 0.08, -99.1310, 19.4700),
    ]

    df = pd.DataFrame(rows, columns=["nombre", "pixel_x", "pixel_y", "longitud", "latitud"])
    df["pixel_x"] = df["pixel_x"].round(1)
    df["pixel_y"] = df["pixel_y"].round(1)
    df["longitud"] = df["longitud"].round(6)
    df["latitud"] = df["latitud"].round(6)
    return df


def warp_tps(img: Image.Image, gcps: pd.DataFrame) -> np.ndarray:
    """
    Rubber-sheet TPS: deforma el grabado para que cada GCP caiga en su lon/lat.

    skimage warp necesita un mapa salida→entrada.
    Estimamos TPS: destino(geográfico) → origen(píxel vintage).
    """
    src_xy = gcps[["pixel_x", "pixel_y"]].to_numpy(dtype=float)  # en imagen vintage
    dst_xy = np.array(
        [lonlat_to_dst(lon, lat) for lon, lat in zip(gcps["longitud"], gcps["latitud"])],
        dtype=float,
    )

    # from_estimate(src, dst): aprende src→dst
    # Queremos salida(dst)→entrada(src) ⇒ estimate(dst_xy, src_xy)
    tps = ThinPlateSplineTransform.from_estimate(dst_xy, src_xy)

    rgba = np.array(img.convert("RGBA"), dtype=np.float64) / 255.0
    warped = warp(
        rgba,
        tps,
        output_shape=(OUT_H, OUT_W),
        order=1,
        mode="constant",
        cval=0,
        preserve_range=True,
    )
    warped_u8 = np.clip(warped * 255.0, 0, 255).astype(np.uint8)
    return warped_u8


def escribir_geotiffs(warped_rgba: np.ndarray) -> None:
    transform = from_bounds(WEST, SOUTH, EAST, NORTH, OUT_W, OUT_H)
    profile = {
        "driver": "GTiff",
        "height": OUT_H,
        "width": OUT_W,
        "count": 4,
        "dtype": "uint8",
        "crs": "EPSG:4326",
        "transform": transform,
        "compress": "lzw",
    }
    path_4326 = OUT_DIR / GEOTIFF_4326
    with rasterio.open(path_4326, "w", **profile) as dst:
        for i in range(4):
            dst.write(warped_rgba[:, :, i], i + 1)
    print(f"GeoTIFF TPS 4326: {path_4326}")

    # Reproyecto a 3857 para basemap
    from rasterio.warp import calculate_default_transform, reproject, Resampling

    path_3857 = OUT_DIR / GEOTIFF_3857
    with rasterio.open(path_4326) as src:
        t3857, w3857, h3857 = calculate_default_transform(
            src.crs, "EPSG:3857", src.width, src.height, *src.bounds
        )
        kwargs = src.meta.copy()
        kwargs.update(
            {
                "crs": "EPSG:3857",
                "transform": t3857,
                "width": w3857,
                "height": h3857,
                "compress": "lzw",
            }
        )
        with rasterio.open(path_3857, "w", **kwargs) as dst:
            for i in range(1, 5):
                reproject(
                    source=rasterio.band(src, i),
                    destination=rasterio.band(dst, i),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=t3857,
                    dst_crs="EPSG:3857",
                    resampling=Resampling.bilinear,
                )
    print(f"GeoTIFF TPS 3857: {path_3857}")


def main() -> None:
    src = descargar_si_falta()
    img = preparar_imagen(src)
    w, h = img.size
    print(f"Mapa de trabajo: {w}x{h}")

    gcps = generar_gcps(w, h)
    gcps.to_csv(OUT_DIR / GCP_NAME, index=False)
    print(f"GCPs ({len(gcps)}):")
    print(gcps.to_string(index=False))

    print("Warping TPS (rubber-sheet)...")
    warped = warp_tps(img, gcps)
    # Preview PNG del resultado deformado
    Image.fromarray(warped, mode="RGBA").save(OUT_DIR / "mapa_vintage_tps_preview.png")
    escribir_geotiffs(warped)
    print("Listo: el grabado ya está deformado y georreferenciado.")


if __name__ == "__main__":
    main()
