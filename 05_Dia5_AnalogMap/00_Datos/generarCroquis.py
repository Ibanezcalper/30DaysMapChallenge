"""
Genera un croquis 'a mano' de la Colonia Condesa (CDMX) y sus Ground Control Points.

Simula el escaneo de un croquis de campo para el Día 5 (Analog Map).
El área geográfica aproximada cubre Parque México y calles aledañas.
"""

from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

OUT_DIR = Path(__file__).resolve().parent
WIDTH, HEIGHT = 1000, 800

# Extensión geográfica real (WGS84) — Condesa / Parque México
LON_W, LON_E = -99.1780, -99.1650
LAT_S, LAT_N = 19.4080, 19.4200


def jitter(coords, rng, amp=2.5):
    """Añade temblor de mano a una polilínea."""
    out = []
    for x, y in coords:
        out.append((x + rng.normal(0, amp), y + rng.normal(0, amp)))
    return out


def draw_wavy_line(draw, p0, p1, rng, width=3, fill="#2C2C2C", n=18):
    xs = np.linspace(p0[0], p1[0], n)
    ys = np.linspace(p0[1], p1[1], n)
    pts = jitter(list(zip(xs, ys)), rng, amp=1.8)
    draw.line(pts, fill=fill, width=width, joint="curve")


def try_font(size: int):
    candidates = [
        "/usr/share/fonts/TTF/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/noto/NotoSans-Regular.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


def crear_croquis(seed: int = 7) -> Image.Image:
    rng = np.random.default_rng(seed)

    # Papel crema con ruido
    base = np.ones((HEIGHT, WIDTH, 3), dtype=np.uint8)
    base[:, :, 0] = 242
    base[:, :, 1] = 232
    base[:, :, 2] = 210
    noise = rng.integers(-12, 12, size=(HEIGHT, WIDTH, 3))
    paper = np.clip(base.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    img = Image.fromarray(paper, mode="RGB")
    draw = ImageDraw.Draw(img)

    font_title = try_font(28)
    font_label = try_font(18)
    font_small = try_font(14)

    # Marco irregular tipo hoja
    draw.rectangle([18, 18, WIDTH - 18, HEIGHT - 18], outline="#5A4632", width=3)

    # Título
    draw.text((40, 32), "CROQUIS DE CAMPO — Condesa, CDMX", fill="#3D2B1F", font=font_title)
    draw.text((40, 68), "Visita comercial · Punto propuesto para dark store", fill="#6B5344", font=font_small)

    # Calles principales (coords en píxeles del croquis)
    # Verticales (N-S): Amsterdam, Mazatlán, Medellín
    calles_v = [
        (220, 120, 220, 720, "Amsterdam"),
        (500, 120, 500, 720, "Mazatlán"),
        (780, 120, 780, 720, "Medellín"),
    ]
    # Horizontales (E-O): Michoacán, Sonora, Campeche
    calles_h = [
        (80, 220, 920, 220, "Michoacán"),
        (80, 400, 920, 400, "Sonora"),
        (80, 580, 920, 580, "Campeche"),
    ]

    for x0, y0, x1, y1, _ in calles_v:
        draw_wavy_line(draw, (x0, y0), (x1, y1), rng, width=4, fill="#2A2A2A")
    for x0, y0, x1, y1, _ in calles_h:
        draw_wavy_line(draw, (x0, y0), (x1, y1), rng, width=4, fill="#2A2A2A")

    # Parque México (óvalo irregular)
    park_box = [320, 280, 680, 520]
    for _ in range(3):
        jittered = [
            park_box[0] + rng.normal(0, 3),
            park_box[1] + rng.normal(0, 3),
            park_box[2] + rng.normal(0, 3),
            park_box[3] + rng.normal(0, 3),
        ]
        draw.ellipse(jittered, outline="#1F5C3A", width=3)
    # Relleno suave del parque
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.ellipse(park_box, fill=(90, 150, 90, 55))
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(img)
    draw.text((430, 385), "Parque México", fill="#1F5C3A", font=font_label)

    # Etiquetas de calles
    draw.text((230, 130), "Amsterdam", fill="#444", font=font_small)
    draw.text((510, 130), "Mazatlán", fill="#444", font=font_small)
    draw.text((790, 130), "Medellín", fill="#444", font=font_small)
    draw.text((820, 200), "Michoacán", fill="#444", font=font_small)
    draw.text((820, 380), "Sonora", fill="#444", font=font_small)
    draw.text((820, 560), "Campeche", fill="#444", font=font_small)

    # Punto de interés propuesto (esquina Amsterdam x Sonora ~)
    poi = (220, 400)
    r = 14
    draw.ellipse([poi[0] - r, poi[1] - r, poi[0] + r, poi[1] + r], outline="#C0392B", width=4)
    draw.line([(poi[0] - 18, poi[1]), (poi[0] + 18, poi[1])], fill="#C0392B", width=3)
    draw.line([(poi[0], poi[1] - 18), (poi[0], poi[1] + 18)], fill="#C0392B", width=3)
    draw.text((poi[0] + 22, poi[1] - 18), "AQUÍ ← local candidato", fill="#C0392B", font=font_label)

    # Norte
    nx, ny = 900, 100
    draw.polygon([(nx, ny - 35), (nx - 12, ny), (nx + 12, ny)], fill="#2C2C2C")
    draw.line([(nx, ny), (nx, ny + 28)], fill="#2C2C2C", width=3)
    draw.text((nx - 10, ny + 32), "N", fill="#2C2C2C", font=font_label)

    # Escala aproximada
    draw.line([(60, 740), (210, 740)], fill="#2C2C2C", width=3)
    draw.line([(60, 732), (60, 748)], fill="#2C2C2C", width=2)
    draw.line([(210, 732), (210, 748)], fill="#2C2C2C", width=2)
    draw.text((70, 750), "~150 m (aprox.)", fill="#444", font=font_small)

    # Firma / nota de campo
    draw.text(
        (40, HEIGHT - 48),
        "Levantado a mano · sin GPS · georreferenciar en oficina",
        fill="#6B5344",
        font=font_small,
    )

    # Ligera desaturación / blur para simular escaneo
    img = ImageEnhance.Contrast(img).enhance(0.95)
    img = img.filter(ImageFilter.SMOOTH)
    return img


def pixel_to_lonlat(col: float, row: float) -> tuple[float, float]:
    """Mapeo lineal del croquis a lon/lat (esquinas del papel = bbox geográfico)."""
    lon = LON_W + (col / (WIDTH - 1)) * (LON_E - LON_W)
    lat = LAT_N - (row / (HEIGHT - 1)) * (LAT_N - LAT_S)
    return lon, lat


def generar_gcps() -> pd.DataFrame:
    """GCPs en esquinas + puntos interiores (calles) para la transformación."""
    points = [
        ("esquina_NO", 0, 0),
        ("esquina_NE", WIDTH - 1, 0),
        ("esquina_SO", 0, HEIGHT - 1),
        ("esquina_SE", WIDTH - 1, HEIGHT - 1),
        ("amsterdam_sonora", 220, 400),
        ("mazatlan_michoacan", 500, 220),
        ("medellin_campeche", 780, 580),
        ("parque_centro", 500, 400),
    ]
    rows = []
    for name, col, row in points:
        lon, lat = pixel_to_lonlat(col, row)
        rows.append(
            {
                "nombre": name,
                "pixel_x": col,
                "pixel_y": row,
                "longitud": round(lon, 6),
                "latitud": round(lat, 6),
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    croquis = crear_croquis()
    croquis_path = OUT_DIR / "croquis_condesa_campo.png"
    croquis.save(croquis_path, format="PNG")

    gcps = generar_gcps()
    gcp_path = OUT_DIR / "gcps_croquis.csv"
    gcps.to_csv(gcp_path, index=False)

    # Metadatos del bbox para el notebook
    meta = pd.DataFrame(
        [
            {"clave": "lon_w", "valor": LON_W},
            {"clave": "lon_e", "valor": LON_E},
            {"clave": "lat_s", "valor": LAT_S},
            {"clave": "lat_n", "valor": LAT_N},
            {"clave": "width_px", "valor": WIDTH},
            {"clave": "height_px", "valor": HEIGHT},
        ]
    )
    meta.to_csv(OUT_DIR / "bbox_croquis.csv", index=False)

    print(f"Croquis: {croquis_path}")
    print(f"GCPs:    {gcp_path}")
    print(gcps.to_string(index=False))


if __name__ == "__main__":
    main()
