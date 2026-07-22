"""
Genera bocetos tipo pen & paper (storyboard) para el Día 10.

Narrativa de negocio: '¿Dónde abrir un dark store en CDMX?'
Cada viñeta es un paso del análisis espacial antes de tocar código.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

OUT = Path(__file__).resolve().parent
W, H = 900, 700
INK = "#1a1a1a"
ACCENT = "#C0392B"
SOFT = "#5D6D7E"
PAPER = (245, 236, 214)


def try_font(size: int, bold: bool = False):
    candidates = [
        "/usr/share/fonts/TTF/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/noto/NotoSans-Regular.ttf",
    ]
    if bold:
        candidates = [
            "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ] + candidates
    for p in candidates:
        if Path(p).exists():
            return ImageFont.truetype(p, size=size)
    return ImageFont.load_default()


def paper_bg(rng: np.random.Generator) -> Image.Image:
    arr = np.ones((H, W, 3), dtype=np.uint8)
    arr[:, :] = PAPER
    noise = rng.integers(-10, 10, size=(H, W, 3))
    arr = np.clip(arr.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    img = Image.fromarray(arr, "RGB")
    # manchas suaves
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for _ in range(8):
        x, y = int(rng.integers(0, W)), int(rng.integers(0, H))
        r = int(rng.integers(20, 80))
        od.ellipse([x - r, y - r, x + r, y + r], fill=(210, 190, 150, 25))
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")


def wavy_line(draw, p0, p1, rng, width=3, fill=INK, n=16):
    xs = np.linspace(p0[0], p1[0], n)
    ys = np.linspace(p0[1], p1[1], n)
    pts = [(x + rng.normal(0, 1.2), y + rng.normal(0, 1.2)) for x, y in zip(xs, ys)]
    draw.line(pts, fill=fill, width=width, joint="curve")


def box(draw, xy, rng, width=3, fill=None):
    x0, y0, x1, y1 = xy
    pts = [
        (x0 + rng.normal(0, 1), y0 + rng.normal(0, 1)),
        (x1 + rng.normal(0, 1), y0 + rng.normal(0, 1)),
        (x1 + rng.normal(0, 1), y1 + rng.normal(0, 1)),
        (x0 + rng.normal(0, 1), y1 + rng.normal(0, 1)),
        (x0 + rng.normal(0, 1), y0 + rng.normal(0, 1)),
    ]
    if fill:
        draw.polygon(pts[:-1], fill=fill)
    draw.line(pts, fill=INK, width=width)


def arrow(draw, p0, p1, rng, fill=ACCENT):
    wavy_line(draw, p0, p1, rng, width=4, fill=fill, n=12)
    # punta
    ang = np.arctan2(p1[1] - p0[1], p1[0] - p0[0])
    for da in (-0.5, 0.5):
        x = p1[0] - 18 * np.cos(ang + da)
        y = p1[1] - 18 * np.sin(ang + da)
        draw.line([p1, (x, y)], fill=fill, width=3)


def frame_header(draw, title: str, step: int, rng):
    font_t = try_font(26, bold=True)
    font_s = try_font(14)
    draw.text((40, 28), f"Viñeta {step}/6", fill=SOFT, font=font_s)
    draw.text((40, 52), title, fill=INK, font=font_t)
    wavy_line(draw, (40, 95), (W - 40, 98), rng, width=2, fill=SOFT)


# ---------- Viñetas ----------

def vignette_1(rng) -> Image.Image:
    img = paper_bg(rng)
    d = ImageDraw.Draw(img)
    frame_header(d, "1. La pregunta de negocio", 1, rng)
    font = try_font(20)
    font_b = try_font(22, bold=True)
    box(d, (80, 140, 820, 280), rng, fill=(255, 250, 240))
    d.text((110, 170), "¿Dónde abrir un dark store", fill=INK, font=font_b)
    d.text((110, 210), "en CDMX… sin quemar CAPEX?", fill=INK, font=font_b)
    d.text((110, 320), "Stakeholders:", fill=SOFT, font=try_font(16))
    for i, who in enumerate(["Ops", "Finance", "Expansion", "Data"]):
        x = 110 + i * 170
        box(d, (x, 360, x + 140, 430), rng)
        d.text((x + 25, 380), who, fill=INK, font=font)
    d.text((80, 500), "Entregable del storyboard: 1 mapa que se explique solo.", fill=ACCENT, font=try_font(18))
    d.text((80, 560), "(Antes de abrir Jupyter.)", fill=SOFT, font=try_font(16))
    return img


def vignette_2(rng) -> Image.Image:
    img = paper_bg(rng)
    d = ImageDraw.Draw(img)
    frame_header(d, "2. Datos sucios (auditoría GPS)", 2, rng)
    # puntos locos
    for _ in range(40):
        x, y = int(rng.integers(100, 800)), int(rng.integers(150, 450))
        r = int(rng.integers(3, 8))
        d.ellipse([x - r, y - r, x + r, y + r], outline=ACCENT, width=2)
    box(d, (120, 180, 520, 420), rng)
    d.text((150, 200), "CSV de ubicaciones", fill=INK, font=try_font(18, True))
    d.text((150, 250), "• lat/lon invertidos", fill=INK, font=try_font(16))
    d.text((150, 290), "• signos rotos", fill=INK, font=try_font(16))
    d.text((150, 330), "• outliers en el océano", fill=INK, font=try_font(16))
    arrow(d, (540, 300), (720, 300), rng)
    box(d, (730, 240, 860, 360), rng, fill=(220, 245, 220))
    d.text((750, 280), "LIMPIO", fill="#1F7A1F", font=try_font(18, True))
    d.text((80, 520), "Regla: no hay mapa de negocio sin gate de calidad.", fill=ACCENT, font=try_font(18))
    return img


def vignette_3(rng) -> Image.Image:
    img = paper_bg(rng)
    d = ImageDraw.Draw(img)
    frame_header(d, "3. Croquis de campo → GIS", 3, rng)
    # calle grid sketch
    for x in (180, 320, 460, 600):
        wavy_line(d, (x, 160), (x, 480), rng, width=2)
    for y in (220, 320, 420):
        wavy_line(d, (120, y), (680, y), rng, width=2)
    d.ellipse([300, 250, 500, 390], outline="#1F5C3A", width=3)
    d.text((340, 300), "Parque", fill="#1F5C3A", font=try_font(16))
    # X candidato
    cx, cy = 180, 320
    d.line([(cx - 15, cy - 15), (cx + 15, cy + 15)], fill=ACCENT, width=4)
    d.line([(cx - 15, cy + 15), (cx + 15, cy - 15)], fill=ACCENT, width=4)
    d.text((200, 300), "AQUÍ", fill=ACCENT, font=try_font(18, True))
    arrow(d, (700, 280), (820, 280), rng)
    d.text((720, 320), "GCPs", fill=INK, font=try_font(16, True))
    d.text((720, 350), "→ lat/lon", fill=INK, font=try_font(16))
    d.text((80, 540), "El papel solo escala si nace con puntos de control.", fill=ACCENT, font=try_font(18))
    return img


def vignette_4(rng) -> Image.Image:
    img = paper_bg(rng)
    d = ImageDraw.Draw(img)
    frame_header(d, "4. Relieve: pendiente × elevación", 4, rng)
    # mountains sketch
    pts = [(80, 420), (180, 220), (280, 360), (400, 180), (520, 340), (650, 200), (820, 420)]
    wavy_line(d, pts[0], pts[1], rng, width=3)
    for a, b in zip(pts, pts[1:]):
        wavy_line(d, a, b, rng, width=3)
    wavy_line(d, (80, 420), (820, 420), rng, width=2, fill=SOFT)
    box(d, (200, 450, 700, 560), rng, fill=(255, 250, 240))
    d.text((230, 470), "Aptitud = slope ≤ 5°  ∩  fuera del vaso bajo", fill=INK, font=try_font(17, True))
    d.text((230, 510), "DEM → álgebra de mapas → máscara de candidatos", fill=SOFT, font=try_font(15))
    return img


def vignette_5(rng) -> Image.Image:
    img = paper_bg(rng)
    d = ImageDraw.Draw(img)
    frame_header(d, "5. Demanda HD (Metro / afluencia)", 5, rng)
    # metro lines sketch
    for color, pts in [
        (ACCENT, [(100, 200), (300, 280), (500, 260), (750, 320)]),
        ("#2E86C1", [(120, 450), (280, 380), (480, 400), (700, 360)]),
        ("#27AE60", [(200, 500), (400, 300), (600, 200), (780, 180)]),
    ]:
        for a, b in zip(pts, pts[1:]):
            wavy_line(d, a, b, rng, width=4, fill=color)
        for p in pts:
            d.ellipse([p[0] - 6, p[1] - 6, p[0] + 6, p[1] + 6], outline=INK, width=2)
    # density cloud
    for _ in range(120):
        x = int(rng.normal(520, 90))
        y = int(rng.normal(300, 70))
        if 80 < x < 850 and 140 < y < 520:
            d.point((x, y), fill=ACCENT)
            d.ellipse([x - 1, y - 1, x + 1, y + 1], fill=ACCENT)
    d.text((100, 560), "Nube densa = presión de pasajeros = catchment comercial", fill=ACCENT, font=try_font(17))
    return img


def vignette_6(rng) -> Image.Image:
    img = paper_bg(rng)
    d = ImageDraw.Draw(img)
    frame_header(d, "6. Decisión: 1 mapa, 1 mensaje", 6, rng)
    # funnel
    box(d, (120, 160, 400, 230), rng)
    d.text((150, 180), "Candidatos crudos", fill=INK, font=try_font(16))
    arrow(d, (260, 240), (260, 290), rng)
    box(d, (140, 300, 380, 370), rng)
    d.text((165, 320), "Filtros espaciales", fill=INK, font=try_font(16))
    arrow(d, (260, 380), (260, 430), rng)
    box(d, (160, 440, 360, 520), rng, fill=(220, 245, 220))
    d.text((185, 465), "GO / NO-GO", fill="#1F7A1F", font=try_font(18, True))
    # sticky insight
    box(d, (480, 200, 840, 480), rng, fill=(255, 248, 220))
    d.text((510, 230), "INSIGHT", fill=ACCENT, font=try_font(20, True))
    d.text((510, 280), "Terreno plano", fill=INK, font=try_font(16))
    d.text((510, 320), "+ demanda Metro", fill=INK, font=try_font(16))
    d.text((510, 360), "+ GPS limpio", fill=INK, font=try_font(16))
    d.text((510, 400), "= shortlist real", fill=INK, font=try_font(16, True))
    d.text((80, 580), "El storyboard es el contrato con el negocio.", fill=ACCENT, font=try_font(18))
    return img


def add_footer(img: Image.Image, caption: str) -> Image.Image:
    d = ImageDraw.Draw(img)
    d.text((40, H - 40), caption, fill=SOFT, font=try_font(13))
    return img


def main() -> None:
    rng = np.random.default_rng(10)
    makers = [
        vignette_1,
        vignette_2,
        vignette_3,
        vignette_4,
        vignette_5,
        vignette_6,
    ]
    paths = []
    for i, fn in enumerate(makers, 1):
        img = fn(rng)
        img = add_footer(img, "#30DayMapChallenge · Día 10 · Pen & Paper · boceto manual")
        img = ImageEnhance.Contrast(img).enhance(1.05)
        img = img.filter(ImageFilter.SMOOTH)
        path = OUT / f"boceto_0{i}.png"
        img.save(path, format="PNG")
        paths.append(path)
        print(f"Guardado: {path}")

    # Storyboard collage 2x3
    cols, rows = 3, 2
    thumb_w, thumb_h = 480, 373
    canvas = Image.new("RGB", (cols * thumb_w + 40, rows * thumb_h + 80), (30, 30, 30))
    draw = ImageDraw.Draw(canvas)
    draw.text((20, 20), "STORYBOARD — Dark store CDMX (antes del código)", fill=(245, 236, 214), font=try_font(22, True))
    for i, path in enumerate(paths):
        r, c = divmod(i, cols)
        im = Image.open(path).resize((thumb_w - 10, thumb_h - 10))
        canvas.paste(im, (20 + c * thumb_w, 60 + r * thumb_h))
    collage = OUT / "storyboard_completo.png"
    canvas.save(collage)
    print(f"Collage: {collage}")


if __name__ == "__main__":
    main()
